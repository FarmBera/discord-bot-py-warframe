import discord
from discord.ext import tasks
from discord.ext import commands
import datetime as dt
import os
import json
import asyncio
import aiohttp

from config.TOKEN import WF_JSON_PATH
from config.config import Lang, language as lang, LOG_TYPE
from config.roles import ROLES
from src.translator import ts
from src.bot_translator import BotTranslator
from src.utils.times import KST, timeNowDT
from src.constants.color import C
from src.constants.keys import (
    # other var
    SPECIAL_ITEM_LIST,
    MSG_BOT,
    # cmd obj
    STEELPATH,
    DUVIRI_ROTATION,
    DUVIRI_U_K_W,
    DUVIRI_U_K_I,
    DUVIRI_CACHE,
    LFG_WEBHOOK_NAME,
)
from src.utils.api_request import API_Request
from src.utils.logging_utils import save_log
from src.utils.file_io import json_load_async
from src.utils.db_helper import query_reader, transaction
from src.utils.return_err import return_traceback, print_test_err
from src.utils.data_manager import (
    get_obj_async,
    set_obj_async,
    SETTINGS,
    getLanguage,
)

from src.handler.handler_config import DATA_HANDLERS
from src.parser.voidTraders import isBaroActive
from src.parser.steelPath import w_steelPath
from src.parser.archimedea import (
    getDeepArchimedea,
    getTemporalArchimedea,
    setDeepArchimedea,
    setTemporalArchimedea,
    CT_LAB,
    CT_HEX,
)
from src.parser.duviriRotation import (
    setDuviriRotate,
    w_duviri_warframe,
    w_duviri_incarnon,
    getDuvWarframe,
    getDuvIncarnon,
    setDuvWarframe,
    setDuvIncarnon,
)

from src.views.party_view import PartyView, build_party_embed_from_db
from src.views.trade_view import TradeView, build_trade_embed_from_db
from src.commands.noti_channel import DB_COLUMN_MAP, PROFILE_CONFIG


class DiscordBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents, db, **options):
        super().__init__(command_prefix="!", intents=intents, **options)
        self.db = db
        self.webhook_cache = {}

    async def setup_hook(self) -> None:
        self.add_view(PartyView())
        self.add_view(TradeView())
        print(
            f"{C.blue}[{LOG_TYPE.info}] {C.green}Persistent Views successfully registered.{C.default}"
        )
        # load translator
        await self.tree.set_translator(BotTranslator())
        # load cogs
        cog_ext = ["register", "party", "trade", "complain", "user_warn"]
        for ext in cog_ext:
            try:
                await self.load_extension(f"src.cogs.{ext}")
                print(ext)
            except Exception as e:
                print(f"{C.red}Failed to load extension {ext}: {e}{C.default}")

    async def on_ready(self) -> None:
        print(
            f"{C.blue}[{LOG_TYPE.info}] {C.yellow}{ts.get('start.sync')}...{C.default}",
            end="",
        )
        await self.wait_until_ready()

        if self.tree:
            await self.tree.sync()
            print(f"{C.green}Synced Tree Commands")
        else:
            print(f"{C.blue}[{LOG_TYPE.info}] {C.red}Commands Not Synced!")

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("start.bot-status-msg")),
        )
        print(
            f"{C.blue}[{LOG_TYPE.info}] {C.cyan}{ts.get('start.final')} <<{C.white}{self.user}{C.cyan}>>"
        )
        print(f"{C.green}{ts.get(f'start.final2')}{C.default}")
        await save_log(
            pool=self.db,
            cmd="bot.BOOTED",
            user=MSG_BOT,
            msg=f"[{LOG_TYPE.info}] Bot booted up.",
        )
        # start coroutine
        if not SETTINGS["noti"]["isEnabled"]:
            return

        # check new content
        if not self.check_new_content.is_running():
            self.check_new_content.start()
            print(
                f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.crt-each')}",
                "check_new_content",
            )
        # weekly task (auto refresh)
        if lang == Lang.EN and not self.weekly_task.is_running():
            self.weekly_task.start()
            print(
                f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.crt-each')}",
                "weekly_task",
            )
        # week start noti (for KO only)
        if lang == Lang.KO and not self.week_start_noti.is_running():
            self.week_start_noti.start()
            print(
                f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.crt-each')}",
                "week_start_noti (for KO only)",
            )
        # automatic party delete
        if lang == Lang.KO and not self.auto_party_expire.is_running():
            self.auto_party_expire.start()
            print(
                f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.crt-each')}",
                "auto_party_expire",
            )
        # automatic trade delete
        if lang == Lang.KO and not self.auto_trade_expire.is_running():
            self.auto_trade_expire.start()
            print(
                f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.crt-each')}",
                "auto_trade_expire",
            )

        print(
            f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.coroutine')}{C.default}"
        )

    async def broadcast_webhook(self, noti_key: str, content) -> None:
        """
        search the webhook subscribed to that notification (noti_key) in the database and sends it.
        """
        # check db column mapping
        db_column = DB_COLUMN_MAP.get(noti_key)
        if not db_column:
            msg = f"[{LOG_TYPE.err}] Unmapped notification key: `{noti_key}` -> {db_column}"
            await save_log(
                pool=self.db,
                type=LOG_TYPE.err,
                cmd="broadcast_webhook",
                user=MSG_BOT,
                msg=msg,
            )
            print(C.yellow, msg, C.default, sep="")
            return

        # search subscribers in db
        async with query_reader(self.db) as cursor:
            await cursor.execute(
                f"SELECT webhook_url FROM webhooks WHERE {db_column} = 1"
            )
            subscribers = await cursor.fetchall()

        if not subscribers:
            return

        # initialize counters
        total_subscribers = len(subscribers)
        success_count = 0
        # prepare payload data
        embed_data = None
        text_content = ""
        files_to_upload = []
        content_file_name = "i.webp"

        # process embed
        if isinstance(content, discord.Embed):
            embed_data = content.to_dict()
            log_content = content.description

        # process tuple (embed, file)
        elif isinstance(content, tuple):
            eb, file_info = content
            embed_data = eb.to_dict()
            real_file_path = None

            log_content = f"IMG: {file_info}\n{eb.description}"
            # img path is string
            if isinstance(file_info, str):
                path = f"img/{file_info}.webp"
                if os.path.exists(path):
                    real_file_path = path
                    # content_file_name = "i.webp"
                # else:
                #     real_file_path = file_info
                #     content_file_name = os.path.basename(file_info)

            # read file
            if real_file_path:
                try:
                    with open(real_file_path, "rb") as f:
                        files_to_upload.append(
                            {
                                "name": "file",
                                "filename": content_file_name,
                                "data": f.read(),
                            }
                        )
                except Exception as e:
                    msg = f"Failed to read image file: {e}"
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="broadcast_webhook",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )
                    print(C.red, msg, C.default)

        # string only
        else:
            text_content = str(content)
            log_content = text_content

        # setup profile img
        bot_name = self.user.name
        bot_avatar_url = self.user.display_avatar.url if self.user else None

        # get setting
        profile_conf = PROFILE_CONFIG.get(noti_key)

        final_username = bot_name
        final_avatar_url = bot_avatar_url

        if profile_conf:
            final_username = profile_conf.get("name", bot_name)
            conf_avatar = profile_conf.get("avatar")

            if conf_avatar:
                # URL
                if conf_avatar.startswith("http"):
                    final_avatar_url = conf_avatar

                else:
                    msg = f"profile picture http only: {conf_avatar}"
                    print(C.red, msg, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="broadcast_webhook",
                        user=MSG_BOT,
                        msg=msg,
                    )

        # send alert & check result
        async with aiohttp.ClientSession() as session:
            eta_start: dt.datetime = timeNowDT()
            for row in subscribers:
                url = row["webhook_url"]
                # custom_msg = row.get("custom_msg", "")

                # verify URL
                if not url or not str(url).startswith("http"):
                    continue

                # combine msg
                # final_text = (
                #     f"{custom_msg}\n{text_content}" if custom_msg else text_content
                # )
                payload = {
                    "username": final_username,
                    "avatar_url": final_avatar_url,
                    "content": text_content.strip(),  # final_text
                }
                if embed_data:
                    payload["embeds"] = [embed_data]

                try:
                    if files_to_upload:
                        # [send file] multipart/form-data
                        form = aiohttp.FormData()
                        form.add_field("payload_json", json.dumps(payload))

                        # upload all file
                        for file_obj in files_to_upload:
                            form.add_field(
                                file_obj["name"],
                                file_obj["data"],
                                filename=file_obj["filename"],
                                content_type="application/octet-stream",
                            )

                        async with session.post(url, data=form) as response:
                            if 200 <= response.status < 300:
                                success_count += 1
                            else:
                                err_text = await response.text()
                                eta_end: dt.timedelta = timeNowDT() - eta_start
                                await save_log(
                                    pool=self.db,
                                    type=LOG_TYPE.err,
                                    cmd="broadcast_webhook",
                                    user=MSG_BOT,
                                    msg=f"Failed to send {noti_key} Multipart (code: {response.status}, eta: {eta_end})",
                                    obj=err_text,
                                )
                    else:  # general send (json)
                        async with session.post(url, json=payload) as response:
                            if 200 <= response.status < 300:
                                success_count += 1
                            else:
                                err_text = await response.text()
                                eta_end: dt.timedelta = timeNowDT() - eta_start
                                await save_log(
                                    pool=self.db,
                                    type=LOG_TYPE.err,
                                    cmd="broadcast_webhook",
                                    user=MSG_BOT,
                                    msg=f"Failed to send {noti_key} general (code: {response.status}, eta: {eta_end})",
                                    obj=err_text,
                                )

                except Exception as e:
                    eta_sending: dt.timedelta = timeNowDT() - eta_start
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="broadcast_webhook",
                        user=MSG_BOT,
                        msg=f"ERROR on sending msg: {noti_key} (eta: {eta_sending})\n{e}",
                        obj=return_traceback(),
                    )

        # logging
        eta_sending: dt.timedelta = timeNowDT() - eta_start
        log_msg = (
            f"{noti_key} sent. {success_count}/{total_subscribers} (eta: {eta_sending})"
        )
        await save_log(
            pool=self.db,
            type=LOG_TYPE.msg,
            cmd="broadcast_webhook",
            user=MSG_BOT,
            msg=log_msg,
            obj=f"{log_content}",
        )

    # auto api request & check new contents
    @tasks.loop(minutes=5.0)
    async def check_new_content(self) -> None:
        if lang == Lang.EN:
            latest_data = await API_Request(self.db, "check_new_content()")
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

            try:
                obj_prev = await get_obj_async(key)
                obj_new = latest_data[key]
            except Exception as e:
                msg = f"Error with loading original data (from check_new_content/DATA_HANDLERS for loop)"
                print(timeNowDT(), C.red, key, msg, e, C.default)
                await save_log(
                    pool=self.db,
                    type=LOG_TYPE.err,
                    cmd="check_new_content()",
                    user=MSG_BOT,
                    msg=msg,
                    obj=return_traceback(),
                )
                continue

            # init variables
            notification: bool = False
            parsed_content = None
            should_save_data: bool = False

            special_logic = handler.get("special_logic")

            # alerts, news
            if (
                special_logic == "handle_missing_items"
                or special_logic == "handle_new_news"
            ):
                if special_logic == "handle_new_news":  # news process
                    news_old: list = []
                    news_new: list = []

                    # extract selected language only
                    for item in obj_prev:
                        for msg in item["Messages"]:
                            if msg["LanguageCode"] in [Lang.EN, Lang.KO]:
                                news_old.append(item)
                                break
                    for item in obj_new:
                        for msg in item["Messages"]:
                            if msg["LanguageCode"] in [Lang.EN, Lang.KO]:
                                news_new.append(item)
                                break

                    obj_prev = news_old
                    obj_new = news_new
                # end of news process

                prev_ids = {item["_id"]["$oid"] for item in obj_prev}
                new_ids = {item["_id"]["$oid"] for item in obj_new}

                if obj_prev != obj_new:
                    should_save_data = True

                # check newly added items
                newly_added_ids = new_ids - prev_ids
                if not newly_added_ids:
                    continue

                missing_items = [
                    item for item in obj_new if item["_id"]["$oid"] in newly_added_ids
                ]
                if not missing_items:
                    continue

                try:
                    parsed_content = handler["parser"](missing_items)
                    notification = True
                except Exception as e:
                    msg = f"Data parsing error in {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )

            elif special_logic == "handle_missing_invasions":  # invasions
                prev_ids_set = {item["_id"]["$oid"] for item in obj_prev}

                # extract missing ids (new invasion's id)
                missed_ids = [
                    item["_id"]["$oid"]
                    for item in obj_new
                    if item["_id"]["$oid"] not in prev_ids_set
                ]
                # filter new invasions obj
                missing_invasions = [
                    item for item in obj_new if item["_id"]["$oid"] in missed_ids
                ]

                # filter invasions which having special items
                special_invasions = []
                for inv in missing_invasions:
                    special_item_exist: bool = False

                    item_list = [
                        getLanguage(item["ItemType"]).lower()
                        for reward in [
                            inv.get("AttackerReward"),
                            inv.get("DefenderReward"),
                        ]
                        if isinstance(reward, dict) and "countedItems" in reward
                        for item in reward["countedItems"]
                    ]

                    for item in item_list:
                        for se in SPECIAL_ITEM_LIST:
                            if se in item:
                                special_item_exist = True
                    if special_item_exist:
                        special_invasions.append(inv)

                # send invasions alert if exists
                if not special_invasions:  # missing_invasions:
                    continue
                try:
                    parsed_content = handler["parser"](missing_invasions)
                    notification = True
                    should_save_data = True
                except Exception as e:
                    msg = f"Data parsing error in {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )

            elif special_logic == "handle_fissures":  # fissures
                should_save_data = True

            elif special_logic == "handle_dailydeals":  # DailyDeals
                should_save_data = True

                is_new = obj_prev[0]["StoreItem"] != obj_new[0]["StoreItem"]
                try:
                    if is_new:
                        parsed_content = handler["parser"](obj_new)
                        notification = True
                except Exception as e:
                    msg = f"parse error in handle_dailydeals {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )

            elif special_logic == "handle_duviri_rotation-1":  # circuit-warframe
                is_new = getDuvWarframe()["Choices"] != obj_new[0]["Choices"]
                if not is_new:
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notification = True
                    should_save_data = True
                    await setDuvWarframe(obj_new[0])
                except Exception as e:
                    msg = f"parse error in handle_duviri_rotation-1 {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )

            elif special_logic == "handle_duviri_rotation-2":  # circuit-incarnon
                is_new = getDuvIncarnon()["Choices"] != obj_new[1]["Choices"]
                if not is_new:
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notification = True
                    should_save_data = True
                    await setDuvIncarnon(obj_new[1])
                except Exception as e:
                    msg = f"parse error in handle_duviri_rotation-2 {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )

            elif special_logic == "handle_voidtraders":
                prev_data = (
                    obj_prev[-1]
                    if isinstance(obj_prev, list) and obj_prev
                    else obj_prev
                )
                new_data = (
                    obj_new[-1] if isinstance(obj_new, list) and obj_new else obj_new
                )
                events: list = []

                # 1. is new baro scheduled (check new baro)
                if prev_data.get("Activation") != new_data.get("Activation"):
                    events.append(
                        {
                            "text_key": "cmd.void-traders.baro-new",
                            "embed_color": 0xFFDD00,
                        }
                    )

                # 2. check exist baro activated
                if not prev_data.get("Manifest") and new_data.get("Manifest"):
                    # if not isBaroActive(
                    #     prev_data.get("Activation")["$date"]["$numberLong"],
                    #     prev_data.get("Expiry")["$date"]["$numberLong"],
                    # ) and isBaroActive(
                    #     new_data.get("Activation")["$date"]["$numberLong"],
                    #     new_data.get("Expiry")["$date"]["$numberLong"],
                    # ):
                    events.append(
                        {
                            "text_key": "cmd.void-traders.baro-appear",
                            "embed_color": None,
                        }
                    )
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
                        print(timeNowDT(), C.red, msg, C.default)
                        await save_log(
                            pool=self.db,
                            type=LOG_TYPE.err,
                            cmd="check_new_content()",
                            user=MSG_BOT,
                            msg=msg,
                        )
                        continue

                    await self.broadcast_webhook(origin_key, parsed_content)

                    # legacy alert service
                    # # fetch channel
                    # target_ch = channels.get(handler.get("channel_key", "channel"))
                    # # send msg
                    # await self.send_alert(
                    #     parsed_content,
                    #     channel_list=target_ch,
                    #     setting=setting,
                    #     key=key_arg if key_arg else key
                    # )

            elif special_logic == "handle_deep_archimedea":
                obj_new = next(i for i in obj_new if i.get("Type") == CT_LAB)
                is_new = (
                    getDeepArchimedea()["Activation"]["$date"]["$numberLong"]
                    != obj_new["Activation"]["$date"]["$numberLong"]
                )
                if not is_new:
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notification = True
                    should_save_data = True
                    await setDeepArchimedea(obj_new)
                except Exception as e:
                    msg = (
                        f"parse error in handle_deep_archimedea {handler['parser']}/{e}"
                    )

                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )

            elif special_logic == "handle_temporal_archimedea":
                obj_new = next(i for i in obj_new if i.get("Type") == CT_HEX)
                is_new = getTemporalArchimedea()["Activation"]["$date"][
                    "$numberLong"
                ] != (obj_new["Activation"]["$date"]["$numberLong"])
                if not is_new:
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notification = True
                    should_save_data = True
                    await setTemporalArchimedea(obj_new)
                except Exception as e:
                    msg = f"parse error in handle_temporal_archimedea {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )

            # parsing: default
            elif handler["update_check"](obj_prev, obj_new):
                try:
                    parsed_content = handler["parser"](obj_new)
                except Exception as e:
                    msg = f"Data parsing error in {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, C.default)
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=print_test_err(),
                    )
                notification = True
                should_save_data = True

            if should_save_data:  # save data
                await set_obj_async(obj_new, key)

            if notification and parsed_content:
                # isEnabled alerts
                if not SETTINGS["noti"]["list"][origin_key]:
                    continue

                # # fetch channel
                # ch_key = handler.get("channel_key", "channel")
                # target_ch = channels.get(ch_key)
                # await self.send_alert(
                #     parsed_content,
                #     channel_list=target_ch,
                #     setting=setting,
                #     key=key_arg if key_arg else key
                # )

                await self.broadcast_webhook(origin_key, parsed_content)

        return  # End Of check_new_content()

    # weekly reset task
    @tasks.loop(time=dt.time(hour=8, minute=55, tzinfo=KST))
    async def weekly_task(self) -> None:
        await save_log(
            pool=self.db,
            cmd="weekly_task()",
            user=MSG_BOT,
            msg="Executing weekly_task()",
        )
        # weekday() -> int // 0: Mon, 1: Tue, ..., 6: Sun
        if dt.datetime.now(tz=KST).weekday() != 0:
            return

        # update steelPath reward index
        try:
            steel_data: dict = await get_obj_async(STEELPATH)
            rotation_list: list = steel_data["rotation"]
            curr_idx: int = steel_data["currentReward"]

            # increment & save index
            new_idx: int = (curr_idx + 1) % len(rotation_list)
            steel_data["currentReward"] = new_idx

            # save index
            await set_obj_async(steel_data, STEELPATH)

            msg = f"Steel Path reward index updated {curr_idx} -> {new_idx}"
            await save_log(
                pool=self.db,
                cmd="bot.WEEKLY_TASK.steelpath",
                user=MSG_BOT,
                msg=msg,
            )
        except Exception as e:
            msg = f"Failed to update Steel Path reward index: {C.red}{e}"
            print(C.red, msg, C.default)
            await save_log(
                pool=self.db,
                cmd="bot.WEEKLY_TASK.steelpath",
                user=MSG_BOT,
                msg=msg,
                obj=return_traceback(),
            )

        try:
            # update duviri-rotation time
            duviri_data: dict = await get_obj_async(DUVIRI_CACHE)
            curr = duviri_data["expiry"]
            duviri_data["expiry"] = (
                dt.datetime.fromtimestamp(duviri_data["expiry"]) + dt.timedelta(weeks=1)
            ).timestamp()
            await set_obj_async(duviri_data, DUVIRI_CACHE)
            await setDuviriRotate()
            msg = f"Updated DuviriData Timestamp {curr}->{duviri_data['expiry']}"
            await save_log(
                pool=self.db,
                cmd="bot.WEEKLY_TASK.duviri-cache",
                user=MSG_BOT,
                msg=msg,
            )
        except Exception:
            msg = f"Failed to update duviri-cache data"
            print(C.red, msg, C.default)
            await save_log(
                pool=self.db,
                cmd="bot.WEEKLY_TASK.duviri-cache",
                user=MSG_BOT,
                msg=msg,
                obj=return_traceback(),
            )

    # weekly alert
    @tasks.loop(time=dt.time(hour=9, minute=10, tzinfo=KST))
    async def week_start_noti(self) -> None:
        await save_log(
            pool=self.db,
            cmd="week_start_noti()",
            user=MSG_BOT,
            msg="Execute week_start_noti()",
        )
        # only Monday
        if dt.datetime.now(dt.timezone.utc).weekday() != 0:
            return

        # duviri notification
        await setDuviriRotate()
        data_key: list = [
            f"{DUVIRI_ROTATION}{DUVIRI_U_K_W}",
            f"{DUVIRI_ROTATION}{DUVIRI_U_K_I}",
        ]
        data_list: list = [
            w_duviri_warframe(await get_obj_async(DUVIRI_ROTATION)),
            w_duviri_incarnon(await get_obj_async(DUVIRI_ROTATION)),
        ]
        for i in range(0, len(data_list)):
            data_list[i].description = f"<@&{ROLES[i]}>\n" + data_list[i].description
            await self.broadcast_webhook(data_key[i], data_list[i])

        if lang == Lang.KO:
            return

        await self.broadcast_webhook(
            STEELPATH, w_steelPath(await get_obj_async(STEELPATH))
        )

    # party auto expire
    @tasks.loop(time=dt.time(hour=3, minute=0, tzinfo=KST))
    async def auto_party_expire(self) -> None:
        await save_log(
            pool=self.db,
            type=LOG_TYPE.info,
            cmd="auto_party_expire()",
            user=MSG_BOT,
            msg=f"START Party AutoDelete",
        )
        eta: dt.datetime = timeNowDT()

        async with query_reader(self.db) as cursor:
            await cursor.execute("SELECT value FROM vari WHERE name='party_exp_time'")
            party_exp_time = await cursor.fetchone()
            party_exp_time = int(party_exp_time["value"])

        # delete time
        expiration_time = timeNowDT() - dt.timedelta(days=party_exp_time)

        # fetch all message from db
        async with query_reader(self.db) as cursor:
            await cursor.execute(
                "SELECT id, thread_id, message_id FROM party WHERE updated_at < %s",
                (expiration_time,),
            )
            expired_parties = await cursor.fetchall()

        for party in expired_parties:
            try:
                thread = self.get_channel(party["thread_id"])
                await thread.edit(locked=True)  # lock thread

                msg = await thread.fetch_message(party["message_id"])
                try:  # edit thread starter (webhook) msg
                    webhook = discord.utils.get(
                        await thread.parent.webhooks(), name=LFG_WEBHOOK_NAME
                    )
                    if webhook and msg:
                        await webhook.edit_message(
                            message_id=party["message_id"],
                            content=ts.get(f"cmd.party.del-deleted"),
                        )
                except discord.NotFound:
                    pass  # starter msg not found, maybe deleted manually

                # disable all buttons on the original PartyView
                new_party_view = PartyView()
                for item in new_party_view.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True

                # refresh Embed
                new_embed = await build_party_embed_from_db(
                    party["message_id"], self.db, isDelete=True
                )
                await msg.edit(embed=new_embed, view=new_party_view)

                # remove from db
                async with transaction(self.db) as cursor:
                    await cursor.execute(
                        "DELETE FROM party WHERE id = %s", (party["id"],)
                    )
                omsg = f"Expired party {party['id']} deleted."
                await save_log(
                    pool=self.db,
                    type=LOG_TYPE.info,
                    cmd="auto_party_expire()",
                    user=MSG_BOT,
                    msg=omsg,
                )
            except discord.NotFound:
                await save_log(
                    pool=self.db,
                    type=LOG_TYPE.warn,
                    cmd="auto_party_expire()",
                    user=MSG_BOT,
                    msg=f"Party AutoDelete, but msg not found",
                    obj=return_traceback(),
                )
                # msg deleted manually
                async with transaction(self.db) as cursor:
                    await cursor.execute(
                        "DELETE FROM party WHERE id = %s", (party["id"],)
                    )
            except Exception:
                await save_log(
                    pool=self.db,
                    type=LOG_TYPE.err,
                    cmd="auto_party_expire()",
                    user=MSG_BOT,
                    msg=f"Party AutoDelete, but error occurred!",
                    obj=return_traceback(),
                )
            await asyncio.sleep(5)

        await save_log(
            pool=self.db,
            type=LOG_TYPE.info,
            cmd="auto_party_expire()",
            user=MSG_BOT,
            msg=f"END Party AutoDelete (eta: {timeNowDT()-eta})",
        )

    # trade auto expire
    @tasks.loop(time=dt.time(hour=4, minute=0, tzinfo=KST))
    async def auto_trade_expire(self) -> None:
        await save_log(
            pool=self.db,
            type=LOG_TYPE.info,
            cmd="auto_trade_expire()",
            user=MSG_BOT,
            msg=f"START Trade AutoDelete",
        )
        eta: dt.datetime = timeNowDT()

        async with query_reader(self.db) as cursor:
            await cursor.execute("SELECT value FROM vari WHERE name='trade_exp_time'")
            trade_exp_time = await cursor.fetchone()
            trade_exp_time = int(trade_exp_time["value"])

        # delete time
        expiration_time = timeNowDT() - dt.timedelta(days=trade_exp_time)

        # fetch all message from db
        async with query_reader(self.db) as cursor:
            await cursor.execute(
                "SELECT id, thread_id, message_id FROM trade WHERE updated_at < %s",
                (expiration_time,),
            )
            expired_trades = await cursor.fetchall()

        for trade in expired_trades:
            try:
                thread = self.get_channel(trade["thread_id"])
                await thread.edit(locked=True)  # lock thread

                msg = await thread.fetch_message(trade["message_id"])
                try:  # edit web hook msg
                    webhooks = await thread.parent.webhooks()
                    webhook = discord.utils.get(webhooks, name=LFG_WEBHOOK_NAME)

                    if webhook:
                        starter_message = await thread.parent.fetch_message(thread.id)
                        if starter_message:
                            await webhook.edit_message(
                                message_id=thread.id,
                                content=ts.get("cmd.trade.expired"),
                            )
                    else:  #  if webhook is not found
                        starter_message = await thread.parent.fetch_message(thread.id)
                        await starter_message.edit(content=ts.get("cmd.trade.expired"))
                except discord.NotFound:
                    pass

                # disable all buttons on the original TradeView
                new_trade_view = TradeView()
                for item in new_trade_view.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True

                # refresh Embed
                new_embed = await build_trade_embed_from_db(
                    trade["message_id"], self.db, isDelete=True
                )
                await msg.edit(embed=new_embed, view=new_trade_view)

                # remove from db
                async with transaction(self.db) as cursor:
                    await cursor.execute(
                        "DELETE FROM trade WHERE id = %s", (trade["id"],)
                    )
                omsg = f"Expired trade {trade['id']} deleted."
                await save_log(
                    pool=self.db,
                    type=LOG_TYPE.info,
                    cmd="auto_trade_expire()",
                    user=MSG_BOT,
                    msg=omsg,
                )
            except discord.NotFound:
                await save_log(
                    pool=self.db,
                    type=LOG_TYPE.warn,
                    cmd="auto_trade_expire()",
                    user=MSG_BOT,
                    msg=f"Trade AutoDelete, but msg not found: {trade['id']}",
                    obj=return_traceback(),
                )
                # msg deleted manually
                async with transaction(self.db) as cursor:
                    await cursor.execute(
                        "DELETE FROM trade WHERE id = %s", (trade["id"],)
                    )
            except Exception as e:
                await save_log(
                    pool=self.db,
                    type=LOG_TYPE.err,
                    cmd="auto_trade_expire()",
                    user=MSG_BOT,
                    msg=f"Trade AutoDelete, but error occurred! {e}",
                    obj=return_traceback(),
                )
            await asyncio.sleep(5)

        await save_log(
            pool=self.db,
            type=LOG_TYPE.info,
            cmd="auto_trade_expire()",
            user=MSG_BOT,
            msg=f"END Trade AutoDelete (eta: {timeNowDT()-eta})",
        )
