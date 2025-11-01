import discord
from discord.ext import tasks
import datetime as dt
import requests
import asyncio

from src.translator import ts
from config.TOKEN import DEFAULT_JSON_PATH
from src.constants.times import alert_times, timeNowDT
from src.constants.color import C
from src.constants.keys import (
    # config file
    SETTING_FILE_LOC,
    CHANNEL_FILE_LOC,
    # other var
    SPECIAL_ITEM_LIST,
    MSG_BOT,
    # cmd obj
    SORTIE,
    STEELPATH,
)
from src.utils.api_request import API_Request
from src.utils.logging_utils import save_log
from src.utils.file_io import yaml_open, json_load
from src.utils.data_manager import get_obj, set_obj, getLanguage

from src.handler.handler_config import DATA_HANDLERS

from src.parser.sortie import w_sortie

from src.commands.cmd_create_thread import PartyView


class DiscordBot(discord.Client):
    def __init__(self, *, intents: discord.Intents, log_lock: asyncio.Lock, **options):
        super().__init__(intents=intents, **options)
        self.tree = None
        self.db = None
        self.log_lock = log_lock

    async def setup_hook(self) -> None:
        self.add_view(PartyView())
        print(f"{C.green}Persistent Views successfully registered.{C.default}")

    async def on_ready(self):
        print(
            f"{C.blue}[info] {C.yellow}{ts.get('start.sync')}...{C.default}",
            end="",
        )
        await self.wait_until_ready()
        if self.tree:
            await self.tree.sync()
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
            obj=timeNowDT(),
        )  # VAR

        self.auto_send_msg_request.start()
        self.auto_noti.start()
        self.weekly_task.start()

        print(f"{C.green}{ts.get('start.coroutine')}{C.default}")

    async def send_alert(self, value, channel_list=None, setting=None) -> None:
        if not setting:
            setting = json_load(SETTING_FILE_LOC)
        if not setting["noti"]["isEnabled"]:
            return

        if not channel_list:
            channel_list = yaml_open(CHANNEL_FILE_LOC)["channel"]

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
                return

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
    @tasks.loop(minutes=5.0)  # var
    async def auto_send_msg_request(self) -> None:
        setting = json_load(SETTING_FILE_LOC)
        channels = yaml_open(CHANNEL_FILE_LOC)

        latest_data: requests.Response = await API_Request(
            self.log_lock, "auto_send_msg_request()"
        )

        if not latest_data or latest_data.status_code != 200:
            return

        latest_data = latest_data.json()

        # check for new content & send alert
        for key, handler in DATA_HANDLERS.items():
            try:
                obj_prev = get_obj(key)
                obj_new = latest_data[key]
            except Exception as e:
                msg = f"[err] Error with loading original data"
                print(timeNowDT(), C.red, key, msg, e, C.default)
                await save_log(
                    lock=self.log_lock,
                    type="err",
                    cmd="auto_send_msg_request()",
                    user=MSG_BOT,
                    msg=msg,
                    obj=e,
                )
                continue

            notification: bool = False
            parsed_content = None
            should_save_data: bool = False

            special_logic = handler.get("special_logic")

            if special_logic == "handle_missing_items":  # alerts, news
                prev_ids = {item["_id"]["$oid"] for item in obj_prev}
                new_ids = {item["_id"]["$oid"] for item in obj_new}

                if prev_ids != new_ids:
                    should_save_data = True

                # check newly added items
                newly_added_ids = new_ids - prev_ids
                if newly_added_ids:
                    missing_items = [
                        item
                        for item in obj_new
                        if item["_id"]["$oid"] in newly_added_ids
                    ]
                    if missing_items:
                        try:
                            parsed_content = handler["parser"](missing_items)
                        except Exception as e:
                            msg = f"[err] Data parsing error in {handler['parser']}/{e}"
                            print(timeNowDT(), C.red, msg, e, C.default)
                            await save_log(
                                lock=self.log_lock,
                                type="err",
                                cmd="auto_send_msg_request()",
                                user=MSG_BOT,
                                msg=msg,
                                obj=e,
                            )
                            continue
                        notification = True

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
                if special_invasions:  # missing_invasions:
                    try:
                        parsed_content = handler["parser"](missing_invasions)
                    except Exception as e:
                        msg = f"[err] Data parsing error in {handler['parser']}/{e}"
                        print(timeNowDT(), C.red, msg, e, C.default)
                        await save_log(
                            lock=self.log_lock,
                            type="err",
                            cmd="auto_send_msg_request()",
                            user=MSG_BOT,
                            msg=msg,
                            obj=e,
                        )
                        continue
                    notification = True
                    should_save_data = True

            elif special_logic == "handle_fissures":  # fissures
                should_save_data = True

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
                        cmd="auto_send_msg_request()",
                        user=MSG_BOT,
                        msg=msg,
                        obj=e,
                    )
                    continue
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
                    parsed_content, channel_list=target_ch, setting=setting
                )

        return  # End Of auto_send_msg_request()ㄹ

    # sortie alert
    @tasks.loop(time=alert_times)
    async def auto_noti(self) -> None:
        ch_list = yaml_open("config/channel")

        try:
            ch_list = ch_list["sortie"]
        except Exception:
            ch_list = ch_list["channel"]

        await self.send_alert(w_sortie(get_obj(SORTIE)), ch_list)

    # weekly reset task
    @tasks.loop(time=dt.time(hour=9, minute=0))
    async def weekly_task(self) -> None:
        # weekday() returns integer: 0: Monday, 1: Tuesday, ..., 6: Sunday
        if dt.datetime.now(dt.timezone.utc).weekday() != 0:
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
