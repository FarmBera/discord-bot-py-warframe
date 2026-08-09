import asyncio
from functools import partial
from typing import Callable, NamedTuple, Optional

import orjson
from discord.ext import tasks, commands

from config.config import LOG_TYPE, language as lang, Lang
from src.constants.color import C
from src.constants.keys import SPECIAL_ITEM_LIST
from src.handler.handle_error import handleParseError
from src.handler.handler_config import DATA_HANDLERS, HandlerSpec, Logic
from src.parser.archimedea import (
    CT_LAB,
    CT_HEX,
    getDeepArchimedea,
    getTemporalArchimedea,
    setDeepArchimedea,
    setTemporalArchimedea,
)
from src.parser.bounty import handleNewBounty
from src.parser.duviriRotation import (
    getDuvWarframe,
    getDuvIncarnon,
    setDuvWarframe,
    setDuvIncarnon,
)
from src.parser.voidTraders import isBaroActive
from src.translator import ts, get_ts_by_lang
from src.utils.api_request import API_Request
from src.utils.content_diff import checkMissingIds, checkMissingItem
from src.utils.data_manager import get_obj_async, set_obj_async, SETTINGS, getLanguage


class HandlerResult(NamedTuple):
    """Unified return value for every content handler."""

    content_factory: Optional[Callable]  # per-language content builder, or None
    should_save: bool  # True -> re-save obj_new into the api cache


# no notification, no save
SKIP = HandlerResult(None, False)

# --- void trader (Baro) events ---
EVENT_BARO_NEW = {
    "text_key": "cmd.void-traders.baro-new",
    "embed_color": 0xFFDD00,
    "have_custom_msg": False,
}
EVENT_BARO_APPEAR = {
    "text_key": "cmd.void-traders.baro-appear",
    "embed_color": None,
    "have_custom_msg": True,
}


def _extract_timestamp(value) -> int:
    """Normalize the various api timestamp shapes into an int (epoch ms)."""
    if isinstance(value, dict) and "$date" in value:
        date_val = value["$date"]
        if isinstance(date_val, dict) and "$numberLong" in date_val:
            return int(date_val["$numberLong"])
        return int(date_val)
    return int(value)


# --- module-level helpers ---


def _make_factory(parser, *args, seed: Optional[dict] = None) -> Callable:
    """Create a per-language content factory.

    Parsers are pure functions, so results are memoized per language:
    with N subscribers sharing a language the parser runs only once.
    A parse failure yields None for that language (skipped by broadcast).
    """
    cache: dict = dict(seed) if seed else {}

    def factory(subscriber_lang: str):
        if subscriber_lang not in cache:
            try:
                _ts = get_ts_by_lang(subscriber_lang)
                cache[subscriber_lang] = parser(*args, ts=_ts, lang=subscriber_lang)
            except Exception:
                cache[subscriber_lang] = None
        return cache[subscriber_lang]

    return factory


def _make_lang_arg_func(arg_func) -> Optional[Callable]:
    """Wrap an arg_func so it receives per-language ts/lang when supported."""
    if arg_func is None:
        return None

    def lang_arg_func(subscriber_lang: str):
        _ts = get_ts_by_lang(subscriber_lang)
        try:
            return arg_func(ts=_ts, lang=subscriber_lang)
        except TypeError:  # legacy arg_func without ts/lang parameters
            return arg_func()

    return lang_arg_func


def _make_voidtrader_factory(parser, obj_new, event) -> Callable:
    """Per-event factory for void trader alerts (text/color differ per event)."""
    text_key = event["text_key"]
    color = event["embed_color"]
    cache: dict = {}

    def factory(subscriber_lang: str):
        if subscriber_lang not in cache:
            _ts = get_ts_by_lang(subscriber_lang)
            cache[subscriber_lang] = parser(
                obj_new, _ts.get(text_key), color, ts=_ts, lang=subscriber_lang
            )
        return cache[subscriber_lang]

    return factory


def _filter_news_by_language(items: list) -> list:
    """Keep only news items that have at least one EN/KO message."""
    wanted = {Lang.EN, Lang.KO}
    return [
        item
        for item in items
        if any(msg["LanguageCode"] in wanted for msg in item["Messages"])
    ]


def _has_special_item(invasion: dict) -> bool:
    """Whether any attacker/defender reward contains an item on SPECIAL_ITEM_LIST."""
    for reward in (invasion.get("AttackerReward"), invasion.get("DefenderReward")):
        if not (isinstance(reward, dict) and "countedItems" in reward):
            continue
        for counted in reward["countedItems"]:
            item_name = getLanguage(counted["ItemType"]).lower()
            if any(special in item_name for special in SPECIAL_ITEM_LIST):
                return True
    return False


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class TASKcheck_new_content(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Baro active-state flag lives on the cog, so it resets on bot restart
        # (a duplicate "appear" alert is possible right after a restart while
        # Baro is active).
        self._baro_was_active: bool = False
        self._dispatch: dict = {
            Logic.MISSING: self._handle_missing,
            Logic.NEWS: self._handle_news,
            Logic.INVASIONS: self._handle_invasions,
            Logic.FISSURES: self._handle_fissures,
            Logic.DUVIRI_WARFRAME: partial(
                self._handle_duviri_rotation,
                choice_index=0,
                get_cached=getDuvWarframe,
                set_cached=setDuvWarframe,
            ),
            Logic.DUVIRI_INCARNON: partial(
                self._handle_duviri_rotation,
                choice_index=1,
                get_cached=getDuvIncarnon,
                set_cached=setDuvIncarnon,
            ),
            Logic.VOIDTRADERS: self._handle_voidtraders,
            Logic.DEEP_ARCHIMEDEA: partial(
                self._handle_archimedea,
                content_type=CT_LAB,
                get_cached=getDeepArchimedea,
                save_fn=setDeepArchimedea,
            ),
            Logic.TEMPORAL_ARCHIMEDEA: partial(
                self._handle_archimedea,
                content_type=CT_HEX,
                get_cached=getTemporalArchimedea,
                save_fn=setTemporalArchimedea,
            ),
            Logic.NO_ARGS: self._handle_no_args,
            # Logic.BOUNTY: self._handle_bounty,
            Logic.SEASONINFO: self._handle_seasoninfo,
        }

    # --- shared helpers ---

    async def _safe_parse(self, spec: HandlerSpec, log_key: str, *args):
        """Validate the parser once with the default language, then return a
        memoized per-language factory (seeded with the validated result).
        Returns None when the initial parse fails or yields None."""
        parser = spec.parser
        try:
            first_result = parser(*args, ts=ts, lang=lang)
            if first_result is None:
                return None
        except Exception as e:
            msg = f"Data parsing error in {parser}/{e}"
            await handleParseError(self.bot.db, msg, log_key)
            return None
        return _make_factory(parser, *args, seed={lang: first_result})

    # --- content handlers ---
    # All handlers share the signature
    #   (spec, origin_key, cache_key, obj_prev, obj_new) -> HandlerResult
    # origin_key: DATA_HANDLERS key (also the notification-settings key)
    # cache_key : api cache / api response key (spec.cache_key or origin_key)

    async def _handle_missing(self, spec, origin_key, cache_key, obj_prev, obj_new):
        changed, added_ids = checkMissingIds(obj_prev, obj_new)
        if not added_ids:
            return HandlerResult(None, changed)
        added_items = checkMissingItem(obj_new, added_ids)
        factory = await self._safe_parse(spec, origin_key, added_items)
        return HandlerResult(factory, changed)

    async def _handle_news(self, spec, origin_key, cache_key, obj_prev, obj_new):
        obj_prev = _filter_news_by_language(obj_prev)
        obj_new = _filter_news_by_language(obj_new)
        return await self._handle_missing(
            spec, origin_key, cache_key, obj_prev, obj_new
        )

    async def _handle_invasions(self, spec, origin_key, cache_key, obj_prev, obj_new):
        changed, added_ids = checkMissingIds(obj_prev, obj_new)
        new_invasions = checkMissingItem(obj_new, added_ids)
        special_invasions = [inv for inv in new_invasions if _has_special_item(inv)]
        if not special_invasions:
            # still report `changed` so the cache stays in sync even when
            # no special invasion appeared (previously the save flag was lost
            # here, causing stale caches and batched late alerts)
            return HandlerResult(None, changed)
        factory = await self._safe_parse(spec, origin_key, special_invasions)
        return HandlerResult(factory, changed)

    async def _handle_fissures(self, spec, origin_key, cache_key, obj_prev, obj_new):
        changed, _ = checkMissingIds(obj_prev, obj_new)
        return HandlerResult(None, changed)

    async def _handle_duviri_rotation(
        self,
        spec,
        origin_key,
        cache_key,
        obj_prev,
        obj_new,
        *,
        choice_index,
        get_cached,
        set_cached,
    ):
        category = obj_new[0]["CategoryChoices"][choice_index]
        if get_cached()["Choices"] == category["Choices"]:
            return SKIP
        try:
            await set_cached(category)
        except Exception as e:
            msg = f"parse error in {origin_key} {spec.parser}/{e}"
            await handleParseError(self.bot.db, msg, cache_key)
            return SKIP
        return HandlerResult(_make_factory(spec.parser, obj_new), True)

    async def _handle_archimedea(
        self,
        spec,
        origin_key,
        cache_key,
        obj_prev,
        obj_new,
        *,
        content_type,
        get_cached,
        save_fn,
    ):
        # pick the entry matching this content type; skip if absent
        entry = next((i for i in obj_new if i.get("Type") == content_type), None)
        if entry is None:
            return SKIP
        cached = get_cached()
        is_new = (
            cached["Activation"]["$date"]["$numberLong"]
            != entry["Activation"]["$date"]["$numberLong"]
        )
        if not is_new:
            return SKIP
        try:
            await save_fn(entry)
        except Exception as e:
            msg = f"parse error in {origin_key} {spec.parser}/{e}"
            await handleParseError(self.bot.db, msg, cache_key)
            return SKIP
        return HandlerResult(_make_factory(spec.parser, entry), True)

    def _detect_baro_events(self, prev, new) -> list:
        """Detect Baro events. Returns a list of event dicts (possibly empty).

        Two independent events can fire:
          1. a new visit got scheduled (Activation changed)
          2. Baro just became active (inactive -> active transition)
        """
        prev_data: dict = prev[-1] if isinstance(prev, list) and prev else prev
        new_data: dict = new[-1] if isinstance(new, list) and new else new
        events: list = []

        prev_act = _extract_timestamp(prev_data.get("Activation"))
        new_act = _extract_timestamp(new_data.get("Activation"))
        new_exp = _extract_timestamp(new_data.get("Expiry"))

        # 1. new visit scheduled
        if prev_act != new_act:
            events.append(EVENT_BARO_NEW)

        # 2. Baro just became active
        curr_active = isBaroActive(new_act, new_exp)
        if not self._baro_was_active and curr_active:
            events.append(EVENT_BARO_APPEAR)
        self._baro_was_active = curr_active

        return events

    async def _handle_voidtraders(self, spec, origin_key, cache_key, obj_prev, obj_new):
        events = self._detect_baro_events(obj_prev, obj_new)
        if not events:
            return SKIP
        # broadcasting happens here (per event); the main loop only saves
        if SETTINGS["noti"]["list"][origin_key]:
            for event in events:
                arg_func = (
                    _make_lang_arg_func(spec.arg_func)
                    if event.get("have_custom_msg")
                    else None
                )
                await self.bot.broadcast_webhook(
                    origin_key,
                    content_factory=_make_voidtrader_factory(
                        spec.parser, obj_new, event
                    ),
                    arg_func=arg_func,
                )
        return HandlerResult(None, True)

    async def _handle_no_args(self, spec, origin_key, cache_key, obj_prev, obj_new):
        if not spec.update_check():
            return SKIP
        # cycle states keep their own cache; nothing to save here
        return HandlerResult(_make_factory(spec.parser), False)

    async def _handle_bounty(self, spec, origin_key, cache_key, obj_prev, obj_new):
        obj_bounty, is_new = await handleNewBounty(self.bot.db)
        if not obj_bounty:
            await handleParseError(self.bot.db, "error with bounty object", cache_key)
            return SKIP
        if not is_new:
            return SKIP
        # saved here directly: obj_bounty differs from the loop's obj_new
        await set_obj_async(obj_bounty, cache_key)
        return HandlerResult(_make_factory(spec.parser, obj_bounty), False)

    async def _handle_seasoninfo(self, spec, origin_key, cache_key, obj_prev, obj_new):
        if obj_prev is None:
            # first run: just persist, don't spam every active challenge
            return HandlerResult(None, True)

        prev_challenges = obj_prev.get("ActiveChallenges", [])
        new_challenges = obj_new.get("ActiveChallenges", [])
        changed = prev_challenges != new_challenges

        # identify newly added challenges by their Challenge path
        # (future alternative: match by _id.$oid instead)
        prev_paths = {c.get("Challenge") for c in prev_challenges}
        added = [c for c in new_challenges if c.get("Challenge") not in prev_paths]
        if not added:
            return HandlerResult(None, changed)

        obj_for_parse = {**obj_new, "ActiveChallenges": added}
        factory = await self._safe_parse(spec, cache_key, obj_for_parse)
        return HandlerResult(factory, changed)

    async def _handle_default(self, spec, origin_key, cache_key, obj_prev, obj_new):
        if not spec.update_check(obj_prev, obj_new):
            return SKIP
        factory = await self._safe_parse(spec, cache_key, obj_new)
        # save even if parsing failed, to keep the cache in sync
        return HandlerResult(factory, True)

    # --- cog lifecycle ---

    async def cog_load(self):
        if not self.check_new_content.is_running():
            self.check_new_content.start()
            print(
                f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.crt-each')}",
                "check_new_content",
            )

    async def cog_unload(self):
        self.check_new_content.cancel()

    # --- main loop ---

    async def _preload_cache(self) -> dict:
        """Load all required api_cache objects in parallel."""
        keys = list(
            {
                spec.cache_key or origin_key
                for origin_key, spec in DATA_HANDLERS.items()
                if spec.needs_cache
            }
        )
        loaded = await asyncio.gather(*(get_obj_async(k) for k in keys))
        return dict(zip(keys, loaded))

    # auto api request & check new contents
    @tasks.loop(minutes=5.0)
    async def check_new_content(self) -> None:
        response = await API_Request(self.bot.db)
        if not response or response.status_code != 200:
            return
        latest_data = orjson.loads(response.content)

        prev_cache = await self._preload_cache()

        for origin_key, spec in DATA_HANDLERS.items():
            cache_key = spec.cache_key or origin_key

            obj_prev, obj_new = None, None
            if spec.needs_cache:
                try:
                    obj_prev = prev_cache.get(cache_key)
                    obj_new = latest_data[cache_key]
                except Exception as e:
                    msg = (
                        "Error with loading original data "
                        f"(from check_new_content/DATA_HANDLERS for loop){e}"
                    )
                    await handleParseError(self.bot.db, msg, cache_key)
                    continue

            handle_fn = self._dispatch.get(spec.logic, self._handle_default)
            result: HandlerResult = await handle_fn(
                spec, origin_key, cache_key, obj_prev, obj_new
            )

            if result.should_save:
                await set_obj_async(obj_new, cache_key)

            if result.content_factory and SETTINGS["noti"]["list"][origin_key]:
                await self.bot.broadcast_webhook(
                    origin_key,
                    content_factory=result.content_factory,
                    arg_func=_make_lang_arg_func(spec.arg_func),
                )


async def setup(bot):
    await bot.add_cog(TASKcheck_new_content(bot))
