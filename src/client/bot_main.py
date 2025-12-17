import discord
from discord.ext import tasks
import datetime as dt
import requests
import asyncio

from config.TOKEN import WF_JSON_PATH
from config.config import Lang, language as lang, LOG_TYPE
from config.roles import ROLES
from src.translator import ts
from src.utils.times import KST, alert_times, timeNowDT
from src.constants.color import C
from src.constants.keys import (
    # other var
    SPECIAL_ITEM_LIST,
    MSG_BOT,
    # cmd obj
    SORTIE,
    STEELPATH,
    DUVIRI_ROTATION,
    DUVIRI_CACHE,
    LFG_WEBHOOK_NAME,
)
from src.utils.api_request import API_Request
from src.utils.logging_utils import save_log
from src.utils.file_io import json_load
from src.utils.discord_file import img_file
from src.utils.db_helper import query_reader, transaction
from src.utils.return_err import return_test_err, print_test_err
from src.utils.data_manager import (
    get_obj,
    set_obj,
    SETTINGS,
    CHANNELS,
    getLanguage,
)

from src.handler.handler_config import DATA_HANDLERS

from src.parser.sortie import w_sortie
from src.parser.voidTraders import isBaroActive
from src.parser.steelPath import w_steelPath
from src.parser.duviriRotation import (
    setDuviriRotate,
    w_duviri_warframe,
    w_duviri_incarnon,
    duv_warframe,
    duv_incarnon,
    setDuvWarframe,
    setDuvIncarnon,
)

from src.commands.party import PartyView, build_party_embed_from_db
from src.commands.trade import TradeView


class DiscordBot(discord.Client):
    def __init__(self, *, intents: discord.Intents, log_lock: asyncio.Lock, **options):
        super().__init__(intents=intents, **options)
        self.tree = None
        self.db = None
        self.log_lock = log_lock

    async def setup_hooks(self) -> None:
        self.add_view(PartyView())
        self.add_view(TradeView())
        print(f"{C.green}Persistent Views successfully registered.{C.default}")

    async def on_ready(self) -> None:
        await self.setup_hooks()
        print(
            f"{C.blue}[info] {C.yellow}{ts.get('start.sync')}...{C.default}",
            end="",
        )
        await self.wait_until_ready()

        if self.tree:
            await self.tree.sync()
            print(f"{C.green}Synced Tree Commands")
        else:
            print(f"{C.red}Commands Not Synced!")

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("start.bot-status-msg")),
        )
        print(
            f"{C.cyan}{ts.get('start.final')} <<{C.white}{self.user}{C.cyan}>>{C.green} {ts.get(f'start.final2')}{C.default}",
        )
        await save_log(
            lock=self.log_lock,
            cmd="bot.BOOTED",
            user=MSG_BOT,
            msg="[info] Bot booted up.",
        )
        # start coroutune
        if not SETTINGS["noti"]["isEnabled"]:
            return

        # check new content
        if not self.check_new_content.is_running():
            self.check_new_content.start()
            print(f"{C.green}{ts.get('start.crt-each')}", "check_new_content")
        # alert daily sortie
        if lang == Lang.EN and not self.auto_noti.is_running():
            self.auto_noti.start()
            print(
                f"{C.green}{ts.get('start.crt-each')}",
                "auto_noti (for daily sortie alert)",
            )
        # weekly task (auto refresh)
        if lang == Lang.EN and not self.weekly_task.is_running():
            self.weekly_task.start()
            print(f"{C.green}{ts.get('start.crt-each')}", "weekly_task")
        # week start noti (for KO only)
        if lang == Lang.KO and not self.week_start_noti.is_running():
            self.week_start_noti.start()
            print(
                f"{C.green}{ts.get('start.crt-each')}",
                "week_start_noti (for KO only)",
            )
        if lang == Lang.KO and not self.auto_party_expire.is_running():
            self.auto_party_expire.start()
        print(f"{C.green}{ts.get('start.coroutine')}{C.default}")

    async def send_alert(
        self, value, channel_list=None, setting=None, key=None
    ) -> None:
        if not setting:
            setting = SETTINGS
        if not setting["noti"]["isEnabled"]:
            return

        if not channel_list:
            channel_list = CHANNELS["channel"]

        # send message
        for ch in channel_list:
            channel = await self.fetch_channel(ch)

            # embed type
            if isinstance(value, discord.Embed):
                await save_log(
                    lock=self.log_lock,
                    type="msg",
                    cmd="auto_sent_message",
                    user=MSG_BOT,
                    guild=channel.guild,
                    channel=channel.name,
                    obj=value.description,
                )
                await channel.send(embed=value)

            # embed with file or thumbnail
            elif isinstance(value, tuple):
                eb, f = value
                await save_log(
                    lock=self.log_lock,
                    type="msg",
                    cmd="auto_sent_message",
                    user=MSG_BOT,
                    guild=channel.guild,
                    channel=channel.name,
                    obj=eb.description,
                )
                f = img_file(f)
                await channel.send(embed=eb, file=f)

            else:  # string type
                await save_log(
                    lock=self.log_lock,
                    type="msg",
                    cmd="auto_sent_message",
                    user=MSG_BOT,
                    guild=channel.guild,
                    channel=channel.name,
                    obj=value,
                )
                await channel.send(value)

    # auto api request & check new contents
    @tasks.loop(minutes=5.0)
    async def check_new_content(self) -> None:
        setting = SETTINGS
        channels = CHANNELS

        if lang == Lang.EN:
            latest_data: requests.Response = await API_Request(
                self.log_lock, "check_new_content()"
            )
            if not latest_data or latest_data.status_code != 200:
                return

            latest_data = latest_data.json()
        else:
            latest_data = json_load(WF_JSON_PATH)

        # check for new content & send alert
        for key, handler in DATA_HANDLERS.items():
            try:
                obj_prev = get_obj(key)
                obj_new = latest_data[key]
            except Exception as e:
                msg = f"[err] Error with loading original data (from check_new_content/DATA_HANDLERS for loop)"
                print(timeNowDT(), C.red, key, msg, e, C.default)
                await save_log(
                    lock=self.log_lock,
                    type="err",
                    cmd="check_new_content()",
                    user=MSG_BOT,
                    msg=msg,
                    obj=e,
                )
                continue

            # init variables
            notification: bool = False
            parsed_content = None
            should_save_data: bool = False
            text_arg: str = ""
            key_arg: str = ""
            embed_color = None

            special_logic = handler.get("special_logic")

            if (
                special_logic == "handle_missing_items"
                or special_logic == "handle_new_news"
            ):  # alerts, news
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

                if prev_ids != new_ids:
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
                    msg = f"[err] Data parsing error in {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        lock=self.log_lock,
                        type="err",
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_test_err(),
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
                    msg = f"[err] Data parsing error in {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        lock=self.log_lock,
                        type="err",
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_test_err(),
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
                    msg = (
                        f"[err] parse error in handle_dailydeals {handler['parser']}/{e}",
                    )
                    print(timeNowDT(), C.red, msg, C.default)
                    await save_log(
                        lock=self.log_lock,
                        type="err",
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=e,
                    )

            elif special_logic == "handle_duviri_rotation-1":  # circuit-warframe
                is_new = set(duv_warframe["Choices"]) != set(obj_new[0]["Choices"])
                if not is_new:
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notification = True
                    should_save_data = True
                    setDuvWarframe(obj_new[0])
                except Exception as e:
                    msg = (
                        f"[err] parse error in handle_duviri_rotation-1 {handler['parser']}/{e}",
                    )
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        lock=self.log_lock,
                        type="err",
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=e,
                    )

            elif special_logic == "handle_duviri_rotation-2":  # circuit-incarnon
                is_new = set(duv_incarnon["Choices"]) != set(obj_new[1]["Choices"])
                if not is_new:
                    continue

                try:
                    parsed_content = handler["parser"](obj_new)
                    notification = True
                    should_save_data = True
                    setDuvIncarnon(obj_new[1])
                except Exception as e:
                    msg = (
                        f"[err] parse error in handle_duviri_rotation-2 {handler['parser']}/{e}",
                    )
                    print(timeNowDT(), C.red, msg, e, C.default)
                    await save_log(
                        lock=self.log_lock,
                        type="err",
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=e,
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
                if not isBaroActive(
                    prev_data["Activation"]["$date"]["$numberLong"],
                    prev_data["Expiry"]["$date"]["$numberLong"],
                ) and isBaroActive(
                    new_data["Activation"]["$date"]["$numberLong"],
                    new_data["Expiry"]["$date"]["$numberLong"],
                ):
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
                    if not setting["noti"]["list"][key]:
                        continue

                    # Parse content
                    parsed_content = handler["parser"](obj_new, text_arg, embed_color)
                    if not parsed_content:
                        msg = (
                            f"[err] parse error in handle_voidtraders {handler['parser']}",
                        )
                        print(timeNowDT(), C.red, msg, C.default)
                        await save_log(
                            lock=self.log_lock,
                            type="err",
                            cmd="check_new_content()",
                            user=MSG_BOT,
                            msg=msg,
                        )
                        continue
                    # fetch channel
                    target_ch = channels.get(handler.get("channel_key", "channel"))
                    # send msg
                    await self.send_alert(
                        parsed_content,
                        channel_list=target_ch,
                        setting=setting,
                        key=key_arg if key_arg else key,
                    )

            # parsing: default
            elif handler["update_check"](obj_prev, obj_new):
                try:
                    parsed_content = handler["parser"](obj_new)
                except Exception as e:
                    msg = f"[err] Data parsing error in {handler['parser']}/{e}"
                    print(timeNowDT(), C.red, msg, C.default)
                    await save_log(
                        lock=self.log_lock,
                        type="err",
                        cmd="check_new_content()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_test_err(),
                    )
                notification = True
                should_save_data = True

            if should_save_data:  # save data
                set_obj(obj_new, key)

            # send msg
            if notification and parsed_content:
                # isEnabled alerts
                if not setting["noti"]["list"][key]:
                    continue

                # fetch channel
                ch_key = handler.get("channel_key", "channel")
                target_ch = channels.get(ch_key)
                await self.send_alert(
                    parsed_content,
                    channel_list=target_ch,
                    setting=setting,
                    key=key_arg if key_arg else key,
                )

        return  # End Of check_new_content()

    # sortie alert
    @tasks.loop(time=alert_times)
    async def auto_noti(self) -> None:
        ch_list = CHANNELS

        try:
            ch_list = ch_list["sortie"]
        except Exception:
            ch_list = ch_list["channel"]

        await self.send_alert(w_sortie(get_obj(SORTIE)), ch_list)

    # weekly reset task
    @tasks.loop(time=dt.time(hour=8, minute=55, tzinfo=KST))
    async def weekly_task(self) -> None:
        await save_log(
            lock=self.log_lock,
            cmd="weekly_task()",
            user=MSG_BOT,
            msg="Executing weekly_task()",
        )
        # weekday() -> int // 0: Mon, 1: Tue, ..., 6: Sun
        if dt.datetime.now(tz=KST).weekday() != 0:
            return

        # update steelPath reward index
        try:
            steel_data: dict = get_obj(STEELPATH)
            rotation_list: list = steel_data["rotation"]
            curr_idx: int = steel_data["currentReward"]

            # increment & save index
            new_idx: int = (curr_idx + 1) % len(rotation_list)
            steel_data["currentReward"] = new_idx

            # save index
            set_obj(steel_data, STEELPATH)

            msg = f"[info] Steel Path reward index updated {curr_idx} -> {new_idx}"
            await save_log(
                lock=self.log_lock,
                cmd="bot.WEEKLY_TASK",
                user=MSG_BOT,
                msg=msg,
                obj=timeNowDT(),
            )
        except Exception as e:
            msg = f"[err] Failed to update Steel Path reward index: {C.red}{e}"
            print(C.yellow, msg, C.default)
            await save_log(
                lock=self.log_lock,
                cmd="bot.WEEKLY_TASK",
                user=MSG_BOT,
                msg=msg,
                obj=timeNowDT(),
            )

        # update duviri-rotation time
        duviri_data: dict = get_obj(DUVIRI_CACHE)
        curr = duviri_data["expiry"]
        duviri_data["expiry"] = (
            dt.datetime.fromtimestamp(duviri_data["expiry"]) + dt.timedelta(weeks=1)
        ).timestamp()
        set_obj(duviri_data, DUVIRI_CACHE)
        setDuviriRotate()
        msg = f"[info] Updated DuviriData Timestamp {curr}->{duviri_data['expiry']}"
        await save_log(
            lock=self.log_lock,
            cmd="bot.WEEKLY_TASK.duviri-cache",
            user=MSG_BOT,
            msg=msg,
            obj=timeNowDT(),
        )

    # weekly alert
    @tasks.loop(time=dt.time(hour=9, minute=10, tzinfo=KST))
    async def week_start_noti(self) -> None:
        await save_log(
            lock=self.log_lock,
            cmd="week_start_noti()",
            user=MSG_BOT,
            msg="Execute week_start_noti()",
        )
        # only Monday
        if dt.datetime.now(dt.timezone.utc).weekday() != 0:
            return

        # duviri notification
        setDuviriRotate()
        dlist: list = [
            w_duviri_warframe(get_obj(DUVIRI_ROTATION)),
            w_duviri_incarnon(get_obj(DUVIRI_ROTATION)),
        ]
        for i in range(len(dlist)):
            dlist[i].description = f"<@&{ROLES[i]}>\n" + dlist[i].description
            await self.send_alert(dlist[i])

        if lang == Lang.KO:
            return

        await self.send_alert(w_steelPath(get_obj(STEELPATH)))

    # party auto expire
    @tasks.loop(time=dt.time(hour=3, minute=0, tzinfo=KST))
    async def auto_party_expire(self) -> None:
        await save_log(
            lock=self.log_lock,
            type=LOG_TYPE.info,
            cmd="auto_party_expire",
            user=MSG_BOT,
            msg=f"START Party AutoDelete",
            obj=timeNowDT(),
        )
        async with query_reader(self.db) as cursor:
            await cursor.execute("SELECT value FROM vari WHERE name='party_exp_time'")
            party_exp_time = await cursor.fetchone()
            party_exp_time = int(party_exp_time["value"])

        # delete time
        expiration_time = timeNowDT() - dt.timedelta(days=party_exp_time)

        # fetch all message from db
        async with query_reader(self.db) as cursor:
            await cursor.execute(
                "SELECT id, thread_id, message_id FROM party WHERE created_at < %s",
                (expiration_time,),
            )
            expired_parties = await cursor.fetchall()

        for party in expired_parties:
            print(party["id"])
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
                    lock=self.log_lock,
                    type=LOG_TYPE.warn,
                    cmd="auto_party_expire",
                    user=MSG_BOT,
                    msg=f"Party AutoDelete",
                    obj=omsg,
                )
            except discord.NotFound:
                await save_log(
                    lock=self.log_lock,
                    type=LOG_TYPE.warn,
                    cmd="auto_party_expire",
                    user=MSG_BOT,
                    msg=f"Party AutoDelete, but msg not found",
                    obj=return_test_err(),
                )
                # msg deleted manually
                async with transaction(self.db) as cursor:
                    await cursor.execute(
                        "DELETE FROM party WHERE id = %s", (party["id"],)
                    )
            except Exception as e:
                await save_log(
                    lock=self.log_lock,
                    type=LOG_TYPE.err,
                    cmd="auto_party_expire",
                    user=MSG_BOT,
                    msg=f"Party AutoDelete, but error occurred!",
                    obj=return_test_err(),
                )
            await asyncio.sleep(15)

        await save_log(
            lock=self.log_lock,
            type=LOG_TYPE.info,
            cmd="auto_party_expire",
            user=MSG_BOT,
            msg=f"END Party AutoDelete",
            obj=timeNowDT(),
        )
