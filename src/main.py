import discord
from discord.ext import tasks
import datetime as dt
import asyncio
import sys
import logging


from src.translator import ts, language
from config.TOKEN import TOKEN as BOT_TOKEN
from config.TOKEN import DEFAULT_JSON_PATH
from src.constants.times import alert_times, JSON_DATE_PAT, time_format
from src.constants.color import C
from src.constants.keys import (
    keys,
    SETTING_FILE_LOC,
    CHANNEL_FILE_LOC,
    HELP_FILE_LOC,
    ANNOUNCE_FILE_LOC,
    PATCHNOTE_FILE_LOC,
    POLICY_FILE_LOC,
    FOOTER_FILE_LOC,
    STARTED_TIME_FILE_LOC,
    DELTA_TIME_LOC,
    MSG_BOT,
)
from src.utils.api_request import API_Request
from src.utils.logging_utils import save_log

from src.utils.file_io import yaml_open
from src.utils.file_io import json_load
from src.utils.data_manager import get_obj
from src.utils.data_manager import set_obj
from src.utils.data_manager import cmd_obj_check
from src.utils.file_io import open_file
from src.utils.return_err import err_embed
from src.utils.file_io import save_file

from src.handler.handler_config import DATA_HANDLERS

from src.parser.alerts import w_alerts
from src.parser.news import w_news
from src.parser.cetusCycle import w_cetusCycle
from src.parser.sortie import w_sortie
from src.parser.archonHunt import w_archonHunt
from src.parser.voidTraders import w_voidTraders, w_voidTradersItem
from src.parser.steelPath import w_steelPath
from src.parser.duviriCycle import w_duviriCycle
from src.parser.deepArchimedea import w_deepArchimedea
from src.parser.temporalArchimedea import w_temporalArchimedia
from src.parser.fissures import w_fissures
from src.parser.calendar import w_calendar
from src.parser.cambionCycle import w_cambionCycle
from src.parser.dailyDeals import w_dailyDeals
from src.parser.invasions import w_invasions


discord.utils.setup_logging(level=logging.INFO, root=False)


class DiscordBot(discord.Client):
    async def on_ready(self):
        print(
            f"{C.blue}[info] {C.yellow}{ts.get('start.sync')}...{C.default}",
            end="",
        )
        await self.wait_until_ready()
        await tree.sync()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("start.bot-status-msg")),
        )
        print(
            f"{C.cyan}{ts.get('start.final')} <<{C.white}{self.user}{C.cyan}>>{C.default}",
        )

        save_log(cmd="bot.BOOTED", user=MSG_BOT, msg="[info] Bot booted up.")  # VAR

        self.auto_send_msg_request.start()
        self.auto_noti.start()

        print(f"{C.green}{ts.get('start.coroutine')}{C.default}")

    async def send_alert(self, value, channel_list, setting=None):
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
                save_log(
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
                save_log(
                    type="msg",
                    cmd="auto_sent_message",
                    user=MSG_BOT,
                    guild=channel.guild,
                    channel=channel.name,
                    obj=eb.description,
                )
                await channel.send(embed=eb, file=f)

            else:  # string type
                save_log(
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
    async def auto_send_msg_request(self):
        setting = json_load(SETTING_FILE_LOC)
        channels = yaml_open(CHANNEL_FILE_LOC)

        code = API_Request("auto_send_msg_request()")  # VAR
        if code != 200:
            msg = f"[warn] response code error < {code} > Task Aborted. (from auto_send_msg_request)"  # VAR
            save_log(
                type="warn",
                cmd="auto_send_msg_request()",  # VAR
                user=MSG_BOT,
                msg=msg,
                obj=code,
            )
            print(C.yellow, msg, C.default, sep="")
            return

        latest_data = json_load(DEFAULT_JSON_PATH)

        # check for new content & send alert
        for key, handler in DATA_HANDLERS.items():
            obj_prev = get_obj(key)
            obj_new = latest_data[key]

            # if not obj_new or not obj_prev:
            #     if obj_new: set_obj(obj_new, key)
            #     continue

            notification: bool = False
            parsed_content = None
            should_save_data: bool = False

            special_logic = handler.get("special_logic")

            if special_logic == "handle_missing_items":  # alerts, news
                prev_ids = {item["id"] for item in obj_prev}
                new_ids = {item["id"] for item in obj_new}

                if prev_ids != new_ids:
                    should_save_data = True

                # check newly added items
                newly_added_ids = new_ids - prev_ids
                if newly_added_ids:
                    missing_items = [
                        item for item in obj_new if item["id"] in newly_added_ids
                    ]
                    if missing_items:
                        notification = True
                        parsed_content = handler["parser"](missing_items)

            elif special_logic == "handle_missing_invasions":  # invasions
                prev_ids = {item["id"] for item in obj_prev}
                # filter not completed invasion
                missing_items = [
                    item
                    for item in obj_new
                    if item["id"] not in prev_ids and not item.get("completed", False)
                ]
                if missing_items:
                    notification = True
                    should_save_data = True
                    parsed_content = handler["parser"](missing_items)
            # parsing: default
            elif handler["update_check"](obj_prev, obj_new):
                # tmep = handler["update_check"](obj_prev, obj_new)
                # print(key, tmep)
                # if not tmep:
                #     continue

                notification = True
                should_save_data = True
                parsed_content = handler["parser"](obj_new)

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
                if target_ch:  # send msg
                    await self.send_alert(
                        parsed_content, channel_list=target_ch, setting=setting
                    )
                else:
                    print(
                        f"{C.red}[err] target channel is Empty! > {target_ch}{C.default}"
                    )  # VAR

        return  # End Of auto_send_msg_request()

    # sortie alert
    @tasks.loop(time=alert_times)
    async def auto_noti(self):
        await self.send_alert(
            w_sortie(get_obj(keys[3])), yaml_open(CHANNEL_FILE_LOC)["sortie"]
        )


class MaintanceBot(discord.Client):
    async def on_ready(self):
        print(
            f"{C.blue}[info] {C.yellow}{ts.get('start.sync')}...{C.default}",
            end="",
        )
        await self.wait_until_ready()
        await tree.sync()
        await self.change_presence(
            status=discord.Status.do_not_disturb,
            activity=discord.Game(ts.get("maintenance.bot-status-msg")),
        )
        print(
            f"{C.cyan}{ts.get('start.final')} <<{C.white}{self.user}{C.cyan}>>{C.default}",
        )

        save_file(
            STARTED_TIME_FILE_LOC,
            dt.datetime.strftime(dt.datetime.now(), JSON_DATE_PAT),
        )

        print(f"{C.magenta}[info] Bot is on Maintance Mode!{C.default}")

        save_log(
            cmd="bot.BOOTED",
            user=MSG_BOT,
            msg="[info] Bot booted up with maintance mode",
        )  # VAR


# init discord bot
tree = None

# commands helper


async def cmd_helper(
    interact: discord.Interaction,
    key: str,
    parser_func,
    isFollowUp: bool = False,
    need_api_call: bool = False,
    parser_args=None,
    isUserViewOnly: bool = False,
):
    if isFollowUp:  # delay response if needed
        await interact.response.defer(ephemeral=isUserViewOnly)

    if need_api_call:  # API request if needed
        API_Request(f"cmd.{key}")
        set_obj(json_load()[key], key)

    # load objects
    if parser_args:
        obj = parser_func(cmd_obj_check(key), parser_args)
    else:
        obj = parser_func(cmd_obj_check(key))

    # send message
    resp_head = interact.followup if isFollowUp else interact.response

    if isinstance(obj, discord.Embed):  # embed only
        if isFollowUp:
            await resp_head.send(embed=obj, ephemeral=isUserViewOnly)
        else:
            await resp_head.send_message(embed=obj, ephemeral=isUserViewOnly)
        log_obj = obj.description
    elif isinstance(obj, tuple):  # embed with file
        eb, file = obj
        if isFollowUp:
            await resp_head.send(embed=eb, file=file, ephemeral=isUserViewOnly)
        else:
            await resp_head.send_message(embed=eb, file=file, ephemeral=isUserViewOnly)
        log_obj = eb.description
    else:  # text only
        if isFollowUp:
            await resp_head.send(obj, ephemeral=isUserViewOnly)
        else:
            await resp_head.send_message(obj, ephemeral=isUserViewOnly)
        log_obj = obj

    save_log(
        type="cmd",
        cmd=f"cmd.{key}{f'-{parser_args}' if parser_args else ''}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used",  # VAR
        obj=log_obj,
    )


async def cmd_helper_txt(
    interact: discord.Interaction, file_name: str, isUserViewOnly: bool = False
):
    try:
        txt1 = open_file(file_name)
        txt2 = open_file(FOOTER_FILE_LOC)
        txt = txt1 + txt2
    except Exception as e:
        msg: str = "open_file err in cmd_helper_txt"  # VAR
        await interact.response.send_message(embed=err_embed(msg), ephemeral=True)
        save_log(
            type="err",
            cmd="cmd_helper_txt",
            time=interact.created_at,
            user=interact.user,
            guild=interact.guild,
            channel=interact.channel,
            msg=msg,
            obj=e,
        )
        return

    # send message
    await interact.response.send_message(
        embed=discord.Embed(description=txt, color=0xCEFF00),  # VAR: color
        ephemeral=isUserViewOnly,
    )

    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used",  # VAR
        obj=txt,
    )


async def cmd_helper_maintenance(interact: discord.Interaction):
    time_target = dt.datetime.strptime(
        open_file(STARTED_TIME_FILE_LOC), JSON_DATE_PAT
    ) + dt.timedelta(minutes=int(open_file(DELTA_TIME_LOC)))
    time_left = time_target - dt.datetime.now()

    txt = f"""# 서버 점검 중

지금은 서버 점검 및 패치 작업으로 인하여 명령어를 사용할 수 없습니다.
이용에 불편을 드려 죄송합니다.

> 종료까지 **{time_format(time_left)}** 남았습니다.
> 예상 완료 시간: {dt.datetime.strftime(time_target,"%Y-%m-%d %H:%M")}

패치 작업은 조기 종료 될 수 있으며, 또한 지연될 수 있음을 알립니다.
"""

    # send message
    await interact.response.send_message(
        embed=discord.Embed(description=txt, color=0xFF0000),  # VAR: color
        ephemeral=True,
    )

    save_log(
        type="cmd/maintenance",
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used in maintenance mode",  # VAR
    )


# register commands


async def register_main_commands(tree: discord.app_commands.CommandTree):
    # help command
    @tree.command(
        name=ts.get(f"cmd.help.cmd"), description=f"{ts.get('cmd.help.desc')}"
    )
    async def cmd_help(interact: discord.Interaction):
        await cmd_helper_txt(interact, file_name=HELP_FILE_LOC, isUserViewOnly=True)

    # announcement command
    @tree.command(
        name=ts.get(f"cmd.announcement.cmd"),
        description=f"{ts.get('cmd.announcement.desc')}",
    )
    async def cmd_announcement(interact: discord.Interaction):
        await cmd_helper_txt(interact, file_name=ANNOUNCE_FILE_LOC)

    # patch-note command
    @tree.command(
        name=ts.get(f"cmd.patch-note.cmd"),
        description=f"{ts.get('cmd.patch-note.desc')}",
    )
    async def cmd_patch_note(interact: discord.Interaction):
        await cmd_helper_txt(interact, file_name=PATCHNOTE_FILE_LOC)

    # privacy-policy command
    @tree.command(
        name=ts.get(f"cmd.privacy-policy.cmd"),
        description=f"{ts.get('cmd.privacy-policy.desc')}",
    )
    async def cmd_privacy_policy(interact: discord.Interaction):
        await cmd_helper_txt(interact, file_name=POLICY_FILE_LOC, isUserViewOnly=True)

    # news command
    @tree.command(name=ts.get(f"cmd.news.cmd"), description=ts.get(f"cmd.news.desc"))
    async def cmd_news(interact: discord.Interaction, number_of_news: int = 20):
        await cmd_helper(
            interact,
            key=keys[1],
            parser_func=w_news,
            parser_args=number_of_news,
            isUserViewOnly=True,
        )

    # alerts command
    @tree.command(
        name=ts.get(f"cmd.alerts.cmd"), description=ts.get(f"cmd.alerts.desc")
    )
    async def cmd_alerts(interact: discord.Interaction):
        await cmd_helper(
            interact=interact, key=keys[0], parser_func=w_alerts, isUserViewOnly=True
        )

    # cetus command (cetusCycle)
    @tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
    async def cmd_cetus(interact: discord.Interaction):
        await cmd_helper(
            interact=interact,
            key=keys[2],
            parser_func=w_cetusCycle,
            isFollowUp=True,
            need_api_call=True,
            isUserViewOnly=True,
        )

    # sortie command
    @tree.command(
        name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc")
    )
    async def cmd_sortie(interact: discord.Interaction):
        await cmd_helper(
            interact, key=keys[3], parser_func=w_sortie, isUserViewOnly=True
        )

    # archon hunt command
    @tree.command(
        name=ts.get(f"cmd.archon-hunt.cmd"), description=ts.get(f"cmd.archon-hunt.desc")
    )
    async def cmd_archon_hunt(interact: discord.Interaction):
        await cmd_helper(
            interact, key=keys[4], parser_func=w_archonHunt, isUserViewOnly=True
        )

    # void traders command
    @tree.command(
        name=ts.get(f"cmd.void-traders.cmd"),
        description=ts.get(f"cmd.void-traders.desc"),
    )
    async def cmd_voidTraders(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=keys[5],
            parser_func=w_voidTraders,
            isFollowUp=True,
            need_api_call=True,
            isUserViewOnly=True,
        )

    # steel path reward command
    @tree.command(
        name=ts.get(f"cmd.steel-path-reward.cmd"),
        description=ts.get(f"cmd.steel-path-reward.desc"),
    )
    async def cmd_steel_reward(interact: discord.Interaction):
        await cmd_helper(
            interact, key=keys[6], parser_func=w_steelPath, isUserViewOnly=True
        )

    # fissures command
    @tree.command(
        name=ts.get(f"cmd.fissures.cmd"), description=ts.get(f"cmd.fissures.desc")
    )
    async def cmd_fissures(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=keys[10],
            parser_func=w_fissures,
            isFollowUp=True,
            need_api_call=True,
            isUserViewOnly=True,
        )

    # duviriCycle command
    @tree.command(
        name=ts.get(f"cmd.duviri-cycle.cmd"),
        description=ts.get(f"cmd.duviri-cycle.desc"),
    )
    async def cmd_temporal_archimedea(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=keys[7],
            parser_func=w_duviriCycle,
            isFollowUp=True,
            need_api_call=True,
            isUserViewOnly=True,
        )

    # deep archimedea command
    @tree.command(
        name=ts.get(f"cmd.deep-archimedea.cmd"),
        description=ts.get(f"cmd.deep-archimedea.desc"),
    )
    async def cmd_deep_archimedea(interact: discord.Interaction):
        await cmd_helper(
            interact, key=keys[8], parser_func=w_deepArchimedea, isUserViewOnly=True
        )

    # temporal archimedea reward command
    @tree.command(
        name=ts.get(f"cmd.temporal-archimedea.cmd"),
        description=ts.get(f"cmd.temporal-archimedea.desc"),
    )
    async def cmd_temporal_archimedea(interact: discord.Interaction):
        await cmd_helper(
            interact, key=keys[9], parser_func=w_temporalArchimedia, isUserViewOnly=True
        )

    # hex calendar reward command
    @tree.command(
        name=ts.get(f"cmd.calendar.cmd"),
        description=ts.get(f"cmd.calendar.desc"),
    )
    @discord.app_commands.choices(
        types=[
            discord.app_commands.Choice(
                name=ts.get("cmd.calendar.choice-all"), value=1
            ),
            discord.app_commands.Choice(
                name=ts.get("cmd.calendar.choice-to-do"), value=2
            ),
            discord.app_commands.Choice(
                name=ts.get("cmd.calendar.choice-over"), value=3
            ),
            discord.app_commands.Choice(
                name=ts.get("cmd.calendar.choice-prize"), value=4
            ),
        ]
    )
    async def cmd_calendar(
        interact: discord.Interaction, types: discord.app_commands.Choice[int]
    ):
        await cmd_helper(
            interact,
            key=keys[11],
            parser_func=w_calendar,
            parser_args=types.name,
            isUserViewOnly=True,
        )

    # cambion command (cambionCycle)
    @tree.command(
        name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc")
    )
    async def cmd_cambion(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=keys[12],
            parser_func=w_cambionCycle,
            isFollowUp=True,
            need_api_call=True,
            isUserViewOnly=True,
        )

    # dailyDeals command
    @tree.command(
        name=ts.get(f"cmd.dailyDeals.cmd"), description=ts.get(f"cmd.dailyDeals.desc")
    )
    async def cmd_dailyDeals(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=keys[13],
            parser_func=w_dailyDeals,
            isFollowUp=True,
            need_api_call=True,
            isUserViewOnly=True,
        )

    # invasions command
    @tree.command(
        name=ts.get(f"cmd.invasions.cmd"), description=ts.get(f"cmd.invasions.desc")
    )
    async def cmd_invasions(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=keys[14],
            parser_func=w_invasions,
            isFollowUp=True,
            need_api_call=True,
            isUserViewOnly=True,
        )

    # voidTrader item command
    @tree.command(
        name=ts.get(f"cmd.void-traders-item.cmd"),
        description=ts.get(f"cmd.void-traders-item.desc"),
    )
    async def cmd_traders_item(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=keys[5],
            parser_func=w_voidTradersItem,
            isFollowUp=True,
            need_api_call=True,
            isUserViewOnly=True,
        )


async def register_maintenance_commands(tree: discord.app_commands.CommandTree):
    @tree.command(
        name=ts.get(f"cmd.help.cmd"), description=f"{ts.get('cmd.help.desc')}"
    )
    async def cmd_help(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.announcement.cmd"),
        description=f"{ts.get('cmd.announcement.desc')}",
    )
    async def cmd_announcement(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.patch-note.cmd"),
        description=f"{ts.get('cmd.patch-note.desc')}",
    )
    async def cmd_patch_note(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.privacy-policy.cmd"),
        description=f"{ts.get('cmd.privacy-policy.desc')}",
    )
    async def cmd_privacy_policy(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(name=ts.get(f"cmd.news.cmd"), description=ts.get(f"cmd.news.desc"))
    async def cmd_news(interact: discord.Interaction, number_of_news: int = 20):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.alerts.cmd"), description=ts.get(f"cmd.alerts.desc")
    )
    async def cmd_alerts(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
    async def cmd_cetus(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc")
    )
    async def cmd_sortie(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.archon-hunt.cmd"), description=ts.get(f"cmd.archon-hunt.desc")
    )
    async def cmd_archon_hunt(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.void-traders.cmd"),
        description=ts.get(f"cmd.void-traders.desc"),
    )
    async def cmd_voidTraders(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.steel-path-reward.cmd"),
        description=ts.get(f"cmd.steel-path-reward.desc"),
    )
    async def cmd_steel_reward(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.fissures.cmd"), description=ts.get(f"cmd.fissures.desc")
    )
    async def cmd_fissures(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.duviri-cycle.cmd"),
        description=ts.get(f"cmd.duviri-cycle.desc"),
    )
    async def cmd_temporal_archimedea(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.deep-archimedea.cmd"),
        description=ts.get(f"cmd.deep-archimedea.desc"),
    )
    async def cmd_deep_archimedea(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.temporal-archimedea.cmd"),
        description=ts.get(f"cmd.temporal-archimedea.desc"),
    )
    async def cmd_temporal_archimedea(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.calendar.cmd"),
        description=ts.get(f"cmd.calendar.desc"),
    )
    async def cmd_calendar(
        interact: discord.Interaction, types: discord.app_commands.Choice[int]
    ):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc")
    )
    async def cmd_cambion(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.dailyDeals.cmd"), description=ts.get(f"cmd.dailyDeals.desc")
    )
    async def cmd_dailyDeals(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.invasions.cmd"), description=ts.get(f"cmd.invasions.desc")
    )
    async def cmd_invasions(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.void-traders-item.cmd"),
        description=ts.get(f"cmd.void-traders-item.desc"),
    )
    async def cmd_traders_item(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)


# main thread


async def console_input_listener():
    """
    wait for console input and returns the specified keyword when it is entered.
    """
    while True:
        command = await asyncio.to_thread(sys.stdin.readline)
        command = command.strip().lower()

        if command in ["maintenance", "main", "exit"]:
            print(f"[info] Console input detected! '{command}'")  # VAR
            return command


async def main_manager():
    """
    manage bot state, and switch bot status depends on console input
    """
    global tree

    bot_mode = "main"  # init mode

    while bot_mode != "exit":
        if bot_mode == "main":
            print(f"{C.cyan}[info] Starting Main Bot...{C.default}")  # VAR
            intents = discord.Intents.default()
            intents.message_content = True
            current_bot = DiscordBot(intents=intents)
            tree = discord.app_commands.CommandTree(current_bot)
            await register_main_commands(tree)

        elif bot_mode == "maintenance":
            print(f"{C.magenta}Starting Maintenance Bot...{C.default}")  # VAR
            intents = discord.Intents.default()
            intents.message_content = True
            current_bot = MaintanceBot(intents=intents)
            tree = discord.app_commands.CommandTree(current_bot)
            await register_maintenance_commands(tree)

        else:
            break

        # create execution task: bot run / console input handler
        bot_task = asyncio.create_task(current_bot.start(BOT_TOKEN))
        console_task = asyncio.create_task(console_input_listener())

        # wait until at least one of the two tasks is completed.
        done, pending = await asyncio.wait(
            [bot_task, console_task], return_when=asyncio.FIRST_COMPLETED
        )

        # verify the completed task is a console input task
        if console_task in done:
            # get input command
            new_mode = console_task.result()
            if new_mode != "exit":  # VAR
                print(f"Switching Bot... '{bot_mode}' into '{new_mode}'")  # VAR
            bot_mode = new_mode
        else:
            print(
                f"{C.red}[err] The Bot has unexpectedly terminated!{C.default}"
            )  # VAR
            # bot_mode = "exit"  # exit loop

        # quit currently running bot & skip to next loop
        print(f"{C.default}[info] Terminating current bot...")  # VAR
        await current_bot.close()
        for task in pending:  # cancel remaining task
            task.cancel()

        if bot_mode != "exit":  # VAR
            for i in range(4, 0, -1):
                print(
                    f"{C.yellow}[info] Executes in {i}s  ",
                    end="\r",
                    flush=True,
                )  # VAR
                await asyncio.sleep(0.98)

    print("[info] Exiting Program...")  # VAR


if __name__ == "__main__":
    try:
        asyncio.run(main_manager())
    except KeyboardInterrupt:
        print(f"\n{C.yellow}Force Quitted!")  # VAR
