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
from src.parser.duviriRotation import setDuvWarframe, setDuvIncarnon
from src.translator import ts
from src.utils.api_request import API_Request
from src.utils.data_manager import get_obj_async, set_obj_async, SETTINGS
from src.utils.file_io import json_load_async
from src.utils.logging_utils import save_log


class TASKcheck_new_content(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # check new content
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
            latest_data: requests.Response | None = await API_Request(
                self.bot.db, "check_new_content()"
            )
            if not latest_data or latest_data.status_code != 200:
                return

            latest_data = latest_data.json()
        else:
            latest_data: dict = await json_load_async(WF_JSON_PATH)

        # check for new content & send alert
        for key, handler in DATA_HANDLERS.items():
            origin_key = key
            special_key = handler.get("key")
            if special_key:
                key = special_key

            special_logic = handler.get("special_logic")
            if special_logic != LOGIC.no_args:
                try:
                    obj_prev = await get_obj_async(key)
                    obj_new = latest_data[key]
                except Exception as e:
                    msg = f"Error with loading original data (from check_new_content/DATA_HANDLERS for loop){e}"
                    await handleParseError(self.bot.db, msg, key)
                    continue

            # init variables
            notify: bool = False
            parsed_content = None
            should_save_data: bool = False

            # alerts, news
            if special_logic == LOGIC.missing or special_logic == LOGIC.news:
                if special_logic == LOGIC.news:  # news process
                    obj_prev, obj_new = processNews(obj_prev, obj_new)

                should_save_data, newly_added_ids = checkMissingIds(obj_prev, obj_new)
                if not newly_added_ids:
                    continue

                missing_items = checkMissingItem(obj_new, newly_added_ids)
                if not missing_items:
                    continue

                try:
                    parsed_content = handler["parser"](missing_items)
                    notify = True
                except Exception as e:
                    msg = f"Data parsing error in {handler['parser']}/{e}"
                    await handleParseError(self.bot.db, msg, origin_key)

            elif special_logic == "handle_missing_invasions":
                should_save_data, special_invasions, missing_invasions = checkInvasions(
                    obj_prev, obj_new
                )
                # send invasions alert if exists
                if not special_invasions:
                    continue
                try:
                    parsed_content = handler["parser"](missing_invasions)
                    notify = True
                    # should_save_data = True
                except Exception as e:
                    msg = f"Data parsing error in {handler['parser']}/{e}"
                    await handleParseError(self.bot.db, msg, key)

            elif special_logic == "handle_fissures":
                should_save_data, missing = checkMissingIds(obj_prev, obj_new)
                await save_log(
                    pool=self.bot.db,
                    type=LOG_TYPE.debug,
                    cmd="check_new_content()",
                    user="test",
                    msg="handle_fissures",
                    obj=f"should_save_data: {should_save_data}\n{missing}",
                )

            elif special_logic == "handle_duviri_rotation-1":  # circuit-warframe
                if not checkCircuitWarframe(obj_new):
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notify = True
                    should_save_data = True
                    await setDuvWarframe(obj_new[0])
                except Exception as e:
                    msg = f"parse error in handle_duviri_rotation-1 {handler['parser']}/{e}"
                    await handleParseError(self.bot.db, msg, key)

            elif special_logic == "handle_duviri_rotation-2":  # circuit-incarnon
                if not checkCircuitIncarnon(obj_new):
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notify = True
                    should_save_data = True
                    await setDuvIncarnon(obj_new[1])
                except Exception as e:
                    msg = f"parse error in handle_duviri_rotation-2 {handler['parser']}/{e}"
                    await handleParseError(self.bot.db, msg, key)

            elif special_logic == "handle_voidtraders":
                events = handleVoidTrader(obj_prev, obj_new)
                if not events:
                    continue

                should_save_data = True

                # process events
                for event in events:
                    text_arg = ts.get(event["text_key"])
                    embed_color = event["embed_color"]
                    # check noti enabled
                    if not SETTINGS["noti"]["list"][key]:
                        continue

                    # Parse content
                    parsed_content = handler["parser"](obj_new, text_arg, embed_color)
                    if not parsed_content:
                        msg = f"parse error in handle_voidtraders {handler['parser']}"
                        await handleParseError(self.bot.db, msg, key)
                        continue

                    await self.bot.broadcast_webhook(origin_key, parsed_content)

            elif special_logic == "handle_deep_archimedea":
                obj_new, is_new = handleDeepArchimedea(obj_new)
                if not is_new:
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notify = True
                    should_save_data = True
                    await setDeepArchimedea(obj_new)
                except Exception as e:
                    msg = (
                        f"parse error in handle_deep_archimedea {handler['parser']}/{e}"
                    )
                    await handleParseError(self.bot.db, msg, key)

            elif special_logic == "handle_temporal_archimedea":
                obj_new, is_new = handleTemporalArchimedea(obj_new)
                if not is_new:
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notify = True
                    should_save_data = True
                    await setTemporalArchimedea(obj_new)
                except Exception as e:
                    msg = f"parse error in handle_temporal_archimedea {handler['parser']}/{e}"
                    await handleParseError(self.bot.db, msg, key)

            elif special_logic == LOGIC.no_args:
                if handler["update_check"]():
                    parsed_content = handler["parser"]()
                    notify = True

            # parsing: default
            elif handler["update_check"](obj_prev, obj_new):
                try:
                    parsed_content = handler["parser"](obj_new)
                except Exception as e:
                    msg = f"Data parsing error in {handler['parser']}/{e}"
                    await handleParseError(self.bot.db, msg, key)
                notify = True
                should_save_data = True

            if should_save_data:
                await set_obj_async(obj_new, key)

            if notify and parsed_content:
                # is alerts enabled global
                if not SETTINGS["noti"]["list"][origin_key]:
                    continue

                await self.bot.broadcast_webhook(
                    origin_key, parsed_content, handler.get("arg_func")
                )

        return


async def setup(bot):
    await bot.add_cog(TASKcheck_new_content(bot))
