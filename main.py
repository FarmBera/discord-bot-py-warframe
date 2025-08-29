import discord
from discord.ext import tasks


from translator import ts, language
from TOKEN import TOKEN as BOT_TOKEN
from TOKEN import DEFAULT_JSON_PATH
from variables.times import alert_times
from variables.color import color
from variables.keys import (
    keys,
    SETTING_FILE_LOC,
    CHANNEL_FILE_LOC,
    HELP_FILE_LOC,
    ANNOUNCE_FILE_LOC,
    PATCHNOTE_FILE_LOC,
    POLICY_FILE_LOC,
    FOOTER_FILE_LOC,
    MSG_BOT,
)
from module.api_request import API_Request
from module.save_log import save_log

from module.yaml_open import yaml_open
from module.json_load import json_load
from module.json_save import json_save
from module.get_obj import get_obj
from module.set_obj import set_obj
from module.cmd_obj_check import cmd_obj_check
from module.get_emoji import get_emoji
from module.open_file import open_file
from module.return_err import err_embed

from module.parser.alerts import w_alerts
from module.parser.news import w_news
from module.parser.cetusCycle import w_cetusCycle
from module.parser.sortie import w_sortie
from module.parser.archonHunt import w_archonHunt
from module.parser.voidTraders import w_voidTraders, w_voidTradersItem
from module.parser.steelPath import w_steelPath
from module.parser.duviriCycle import w_duviriCycle
from module.parser.deepArchimedea import w_deepArchimedea
from module.parser.temporalArchimedea import w_temporalArchimedia
from module.parser.fissures import w_fissures
from module.parser.calendar import w_calendar
from module.parser.cambionCycle import w_cambionCycle
from module.parser.dailyDeals import w_dailyDeals
from module.parser.invasions import w_invasions


def _check_void_trader_update(prev, new):
    """Checks for updates regardless of the data structure (dict or list) of voidTraders."""
    prev_data = prev[-1] if isinstance(prev, list) and prev else prev
    new_data = new[-1] if isinstance(new, list) and new else new
    if not isinstance(prev_data, dict) or not isinstance(new_data, dict):
        # perform a simple comparison. data structure is diff than normal
        return prev != new

    return (prev_data.get("activation"), prev_data.get("active")) != (
        new_data.get("activation"),
        new_data.get("active"),
    )


DATA_HANDLERS = {
    "alerts": {
        "parser": w_alerts,
        "special_logic": "handle_missing_items",
    },
    "news": {
        "parser": w_news,
        "special_logic": "handle_missing_items",
        "channel_key": "news",
    },
    "cetusCycle": {
        "parser": w_cetusCycle,
        "update_check": lambda prev, new: prev.get("state") != new.get("state"),
    },
    "sortie": {
        "parser": w_sortie,
        "update_check": lambda prev, new: prev.get("id") != new.get("id"),
        "channel_key": "sortie",
    },
    "archonHunt": {
        "parser": w_archonHunt,
        "update_check": lambda prev, new: prev.get("activation")
        != new.get("activation"),
        "channel_key": "sortie",
    },
    # TODO: improve
    "voidTraders": {
        "parser": w_voidTraders,
        "update_check": _check_void_trader_update,
    },
    "steelPath": {
        "parser": w_steelPath,
        "update_check": lambda prev, new: prev.get("currentReward")
        != new.get("currentReward"),
    },
    "duviriCycle": {
        "parser": w_duviriCycle,
        "update_check": lambda prev, new: prev.get("state") != new.get("state"),
    },
    "deepArchimedea": {
        "parser": w_deepArchimedea,
        "update_check": lambda prev, new: prev.get("activation")
        != new.get("activation"),
    },
    "temporalArchimedea": {
        "parser": w_temporalArchimedia,
        "update_check": lambda prev, new: prev.get("activation")
        != new.get("activation"),
    },
    "calendar": {
        "parser": lambda data: w_calendar(data, ts.get("cmd.calendar.choice-prize")),
        "update_check": lambda prev, new: prev
        and new
        and prev[0].get("activation") != new[0].get("activation"),
        "channel_key": "hex-cal",
    },
    "cambionCycle": {
        "parser": w_cambionCycle,
        "update_check": lambda prev, new: prev.get("state") != new.get("state"),
    },
    "dailyDeals": {
        "parser": w_dailyDeals,
        "update_check": lambda prev, new: prev
        and new
        and prev[0].get("item") != new[0].get("item"),
    },
    "invasions": {
        "parser": w_invasions,
        "special_logic": "handle_missing_invasions",
    },
}


class DiscordBot(discord.Client):
    async def on_ready(self):
        print(
            f"{color['blue']}[info] {color['yellow']}{ts.get('start.sync')}...{color['default']}",
            end="",
        )
        await self.wait_until_ready()
        await tree.sync()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("start.bot-status-msg")),
        )
        print(
            f"{color['cyan']}{ts.get('start.final')} <<{color['white']}{self.user}{color['cyan']}>>{color['default']}",
        )

        save_log(cmd="bot.BOOTED", user=MSG_BOT, msg="[info] Bot booted up.")  # VAR

        self.auto_send_msg_request.start()
        self.auto_noti.start()

        print(f"{color['green']}{ts.get('start.coroutine')}{color['default']}")

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
            print(color["yellow"], msg, color["default"], sep="")
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
                notification = True
                should_save_data = True
                parsed_content = handler["parser"](obj_new)

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
                        f"{color['red']}[err] target channel is Empty! > {target_ch}{color['default']}"
                    )  # VAR

            if should_save_data:  # save data
                set_obj(obj_new, key)

        return  # End Of auto_send_msg_request()

    # sortie alert
    @tasks.loop(time=alert_times)
    async def auto_noti(self):
        await self.send_alert(
            w_sortie(get_obj(keys[3])), yaml_open(CHANNEL_FILE_LOC)["sortie"]
        )


# init discord bot
intents = discord.Intents.default()
intents.message_content = True
bot_client = DiscordBot(intents=intents)
tree = discord.app_commands.CommandTree(bot_client)


# commands
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


# help command
@tree.command(name=ts.get(f"cmd.help.cmd"), description=f"{ts.get('cmd.help.desc')}")
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
@tree.command(name=ts.get(f"cmd.alerts.cmd"), description=ts.get(f"cmd.alerts.desc"))
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
@tree.command(name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc"))
async def cmd_sortie(interact: discord.Interaction):
    await cmd_helper(interact, key=keys[3], parser_func=w_sortie, isUserViewOnly=True)


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
    name=ts.get(f"cmd.void-traders.cmd"), description=ts.get(f"cmd.void-traders.desc")
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
        discord.app_commands.Choice(name=ts.get("cmd.calendar.choice-all"), value=1),
        discord.app_commands.Choice(name=ts.get("cmd.calendar.choice-to-do"), value=2),
        discord.app_commands.Choice(name=ts.get("cmd.calendar.choice-over"), value=3),
        discord.app_commands.Choice(name=ts.get("cmd.calendar.choice-prize"), value=4),
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
@tree.command(name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc"))
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


# run bot
bot_client.run(BOT_TOKEN)
