import asyncio

import requests
from discord.ext import tasks, commands

from config.TOKEN import WF_JSON_PATH
from config.config import LOG_TYPE, language as lang, Lang
from src.constants.color import C
from src.handler.handle_archimedea import handleDeepArchimedea, handleTemporalArchimedea
from src.handler.handle_duviri import checkCircuitWarframe, checkCircuitIncarnon
from src.handler.handle_error import handleParseError
from src.handler.handle_invasions import checkInvasions
from src.handler.handle_missing import checkMissingIds, checkMissingItem
from src.handler.handle_news import processNews
from src.handler.handle_voidtrader import handleVoidTrader
from src.handler.handler_config import DATA_HANDLERS, LOGIC
from src.parser.archimedea import setDeepArchimedea, setTemporalArchimedea
from src.parser.bounty import handleNewBounty
from src.parser.duviriRotation import setDuvWarframe, setDuvIncarnon
from src.translator import ts
from src.utils.api_request import API_Request
from src.utils.data_manager import get_obj_async, set_obj_async, SETTINGS
from src.utils.file_io import json_load_async


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class TASKcheck_new_content(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._dispatch = {
            LOGIC.missing: self._handle_missing,
            LOGIC.news: self._handle_news,
            LOGIC.invasions: self._handle_invasions,
            LOGIC.fissures: self._handle_fissures,
            LOGIC.duviri_wf: self._handle_duviri_wf,
            LOGIC.duviri_inc: self._handle_duviri_inc,
            LOGIC.voidtraders: self._handle_voidtraders,
            LOGIC.deep_archimedea: self._handle_deep_archimedea,
            LOGIC.temporal_archimedea: self._handle_temporal_archimedea,
            LOGIC.no_args: self._handle_no_args,
            LOGIC.bounty: self._handle_bounty,
        }

    # --- handler helpers ---

    async def _safe_parse(self, handler, log_key, *args):
        """Run parser safely. Returns parsed result, or None on error."""
        try:
            return handler["parser"](*args)
        except Exception as e:
            msg = f"Data parsing error in {handler['parser']}/{e}"
            await handleParseError(self.bot.db, msg, log_key)
            return None

    async def _handle_missing(self, handler, origin_key, key, obj_prev, obj_new):
        should_save, newly_added_ids = checkMissingIds(obj_prev, obj_new)
        if not newly_added_ids:
            return None
        missing_items = checkMissingItem(obj_new, newly_added_ids)
        if not missing_items:
            return None
        return await self._safe_parse(handler, origin_key, missing_items), should_save

    async def _handle_news(self, handler, origin_key, key, obj_prev, obj_new):
        obj_prev, obj_new = processNews(obj_prev, obj_new)
        return await self._handle_missing(handler, origin_key, key, obj_prev, obj_new)

    async def _handle_invasions(self, handler, origin_key, key, obj_prev, obj_new):
        should_save, special_invasions, missing_invasions = checkInvasions(
            obj_prev, obj_new
        )
        if not special_invasions:
            return None
        return await self._safe_parse(handler, key, missing_invasions), should_save

    async def _handle_fissures(self, handler, origin_key, key, obj_prev, obj_new):
        should_save, _ = checkMissingIds(obj_prev, obj_new)
        return None, should_save

    async def _handle_duviri_wf(self, handler, origin_key, key, obj_prev, obj_new):
        if not checkCircuitWarframe(obj_new):
            return None
        try:
            parsed_content = handler["parser"](obj_new)
            await setDuvWarframe(obj_new[0])
            return parsed_content, True
        except Exception as e:
            msg = f"parse error in handle_duviri_rotation-1 {handler['parser']}/{e}"
            await handleParseError(self.bot.db, msg, key)
            return None

    async def _handle_duviri_inc(self, handler, origin_key, key, obj_prev, obj_new):
        if not checkCircuitIncarnon(obj_new):
            return None
        try:
            parsed_content = handler["parser"](obj_new)
            await setDuvIncarnon(obj_new[1])
            return parsed_content, True
        except Exception as e:
            msg = f"parse error in handle_duviri_rotation-2 {handler['parser']}/{e}"
            await handleParseError(self.bot.db, msg, key)
            return None

    async def _handle_voidtraders(self, handler, origin_key, key, obj_prev, obj_new):
        events = handleVoidTrader(obj_prev, obj_new)
        if not events:
            return None
        for event in events:
            if not SETTINGS["noti"]["list"][key]:
                continue
            text_arg = ts.get(event["text_key"])
            embed_color = event["embed_color"]
            parsed_content = handler["parser"](obj_new, text_arg, embed_color)
            if not parsed_content:
                msg = f"parse error in handle_voidtraders {handler['parser']}"
                await handleParseError(self.bot.db, msg, key)
                continue
            if event.get("have_custom_msg"):
                await self.bot.broadcast_webhook(
                    origin_key, parsed_content, handler.get("arg_func")
                )
            else:
                await self.bot.broadcast_webhook(origin_key, parsed_content)
        # broadcast already done above; True = save voidtrader data
        return None, True

    async def _handle_deep_archimedea(
        self, handler, origin_key, key, obj_prev, obj_new
    ):
        obj_deep, is_new = handleDeepArchimedea(obj_new)
        if not is_new:
            return None
        try:
            parsed_content = handler["parser"](obj_deep)
            await setDeepArchimedea(obj_deep)
            return parsed_content, True
        except Exception as e:
            msg = f"parse error in handle_deep_archimedea {handler['parser']}/{e}"
            await handleParseError(self.bot.db, msg, key)
            return None

    async def _handle_temporal_archimedea(
        self, handler, origin_key, key, obj_prev, obj_new
    ):
        obj_temporal, is_new = handleTemporalArchimedea(obj_new)
        if not is_new:
            return None
        try:
            parsed_content = handler["parser"](obj_temporal)
            await setTemporalArchimedea(obj_temporal)
            return parsed_content, True
        except Exception as e:
            msg = f"parse error in handle_temporal_archimedea {handler['parser']}/{e}"
            await handleParseError(self.bot.db, msg, key)
            return None

    async def _handle_no_args(self, handler, origin_key, key, obj_prev, obj_new):
        if not handler["update_check"]():
            return None
        return handler["parser"](), False

    async def _handle_bounty(self, handler, origin_key, key, obj_prev, obj_new):
        obj_bounty, is_new = await handleNewBounty(self.bot.db)
        if not obj_bounty:
            await handleParseError(self.bot.db, "error with bounty object", key)
            return None
        if not is_new:
            return None
        parsed_content = handler["parser"](obj_bounty)
        await set_obj_async(obj_bounty, key)
        # already saved above (obj_bounty differs from outer obj_new)
        return parsed_content, False

    async def _handle_default(self, handler, origin_key, key, obj_prev, obj_new):
        if not handler["update_check"](obj_prev, obj_new):
            return None
        parsed_content = await self._safe_parse(handler, key, obj_new)
        # save even if parse failed, to keep cache in sync (matches original behavior)
        return parsed_content, True

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

    # auto api request & check new contents
    @tasks.loop(minutes=5.0)
    async def check_new_content(self) -> None:
        if lang == Lang.EN:
            latest_data: requests.Response | None = await API_Request(self.bot.db)
            if not latest_data or latest_data.status_code != 200:
                return
            latest_data = latest_data.json()
        else:
            latest_data: dict = await json_load_async(WF_JSON_PATH)

        # pre-load all required api_cache files in parallel
        keys_to_preload = set()
        for _origin_key, _handler in DATA_HANDLERS.items():
            if _handler.get("special_logic") not in [LOGIC.no_args, LOGIC.bounty]:
                keys_to_preload.add(_handler.get("key", _origin_key))
        keys_list = list(keys_to_preload)
        loaded = await asyncio.gather(*[get_obj_async(k) for k in keys_list])
        prev_cache = dict(zip(keys_list, loaded))

        # check for new content & send alert
        for key, handler in DATA_HANDLERS.items():
            origin_key = key
            special_key = handler.get("key")
            if special_key:
                key = special_key

            special_logic = handler.get("special_logic")
            obj_prev, obj_new = None, None
            if special_logic not in [LOGIC.no_args, LOGIC.bounty]:
                try:
                    obj_prev = prev_cache.get(key)
                    obj_new = latest_data[key]
                except Exception as e:
                    msg = f"Error with loading original data (from check_new_content/DATA_HANDLERS for loop){e}"
                    await handleParseError(self.bot.db, msg, key)
                    continue

            handle_fn = self._dispatch.get(special_logic, self._handle_default)
            # noinspection PyArgumentList
            result = await handle_fn(handler, origin_key, key, obj_prev, obj_new)
            if result is None:
                continue

            parsed_content, should_save = result
            if should_save:
                await set_obj_async(obj_new, key)

            if parsed_content and SETTINGS["noti"]["list"][origin_key]:
                await self.bot.broadcast_webhook(
                    origin_key, parsed_content, handler.get("arg_func")
                )


async def setup(bot):
    await bot.add_cog(TASKcheck_new_content(bot))
