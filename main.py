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
    TYPE_EMBED,
    TYPE_TUPLE,
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
        print(f"{color['yellow']}{ts.get('start.sync')}...{color['default']}", end="")
        await self.wait_until_ready()
        await tree.sync()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("start.bot-status-msg")),
        )
        print(
            f"{color['cyan']}{ts.get('start.final')} <<{color['white']}{self.user}{color['cyan']}>>{color['default']}",
        )

        save_log(cmd="bot.BOOTED", user=MSG_BOT, msg="Booted")

        self.auto_send_msg_request.start()
        self.auto_noti.start()

        print(f"{color['green']}{ts.get('start.coroutine')}{color['default']}")

    async def send_alert(self, value, channel_list):
        if not channel_list or channel_list is None:
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
        setting = json_load(SETTING_FILE_LOC)  # open setting file
        channels = yaml_open(CHANNEL_FILE_LOC)

        code = API_Request("auto_send_msg_request()")  # VAR
        if code != 200:
            msg = f"{color['yellow']}response code < {code} > Task Aborted. (from auto_send_msg_request){color['default']}"
            save_log(type="warn", cmd="auto_send_msg_request()", user=MSG_BOT, msg=msg)
            print(msg)
            return

        latest_data = json_load(DEFAULT_JSON_PATH)

        # check for new content & send alert
        for key, handler in DATA_HANDLERS.items():
            obj_prev = get_obj(key)
            obj_new = latest_data[key]

            # if not obj_new or not obj_prev:
            #     if obj_new:
            #         set_obj(obj_new, key)
            #     continue

            notification: bool = False
            parsed_content = None
            should_save_data = False

            special_logic = handler.get("special_logic")

            # missing-item: check new content with missing item (parsing)
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
            # default: check new content (parsing)
            elif handler["update_check"](obj_prev, obj_new):
                notification = True
                should_save_data = True
                parsed_content = handler["parser"](obj_new)

            # FINAL; fetch channel & send msg
            if notification and parsed_content:
                # isEnabled alerts
                if not setting["noti"]["list"][key]:
                    continue

                # fetch channel
                ch_key = handler.get("channel_key", "channel")
                target_ch = channels.get(ch_key)
                if target_ch:  # send msg
                    await self.send_alert(parsed_content, channel_list=target_ch)
                else:
                    print(
                        f"{color['red']}[err] target channel is Empty! > {target_ch}{color['default']}"
                    )

            if should_save_data:
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


# help command
@tree.command(name=ts.get(f"cmd.help.cmd"), description=f"{ts.get('cmd.help.desc')}")
async def cmd_help(interact: discord.Interaction):
    txt = open_file(HELP_FILE_LOC)
    eb = discord.Embed(description=txt, color=0xCEFF00)
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=txt,
    )


# announcement command
@tree.command(
    name=ts.get(f"cmd.announcement.cmd"),
    description=f"{ts.get('cmd.announcement.desc')}",
)
async def cmd_announcement(interact: discord.Interaction):
    txt = open_file(ANNOUNCE_FILE_LOC)
    eb = discord.Embed(description=txt, color=0xCEFF00)
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.announcement.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=txt,
    )


# patch-note command
@tree.command(
    name=ts.get(f"cmd.patch-note.cmd"),
    description=f"{ts.get('cmd.patch-note.desc')}",
)
async def cmd_patch_note(interact: discord.Interaction):
    txt = open_file(PATCHNOTE_FILE_LOC)
    eb = discord.Embed(description=txt, color=0xCEFF00)
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.patch-note.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=txt,
    )


# privacy-policy command
@tree.command(
    name=ts.get(f"cmd.privacy-policy.cmd"),
    description=f"{ts.get('cmd.privacy-policy.desc')}",
)
async def cmd_privacy_policy(interact: discord.Interaction):
    txt = open_file(POLICY_FILE_LOC)
    eb = discord.Embed(description=txt, color=0xCEFF00)
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.privacy-policy.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=txt,
    )


# news command
@tree.command(name=ts.get(f"cmd.news.cmd"), description=ts.get(f"cmd.news.desc"))
async def cmd_news(interact: discord.Interaction):
    eb = w_news(cmd_obj_check(keys[1]), language)
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.news.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# alerts command
@tree.command(name=ts.get(f"cmd.alerts.cmd"), description=ts.get(f"cmd.alerts.desc"))
async def cmd_alerts(interact: discord.Interaction):
    eb = w_alerts(get_obj(keys[0]))
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.alerts.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# cetus command (cetusCycle)
@tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
async def cmd_cetus(interact: discord.Interaction):
    await interact.response.defer()

    API_Request("cmd.cetus")
    set_obj(json_load()[keys[2]], keys[2])
    eb, f = w_cetusCycle(cmd_obj_check(keys[2]), language)
    if f is None:
        await interact.followup.send(embed=eb)
    else:
        await interact.followup.send(embed=eb, file=f)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.cetus.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# sortie command
@tree.command(name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc"))
async def cmd_sortie(interact: discord.Interaction):
    text_obj = w_sortie(cmd_obj_check(keys[3]), language)
    await interact.response.send_message(text_obj)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.sortie.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=text_obj,
    )


# archon hunt command
@tree.command(
    name=ts.get(f"cmd.archon-hunt.cmd"), description=ts.get(f"cmd.archon-hunt.desc")
)
async def cmd_archon_hunt(interact: discord.Interaction):
    text_obj = w_archonHunt(cmd_obj_check(keys[4]), language)
    await interact.response.send_message(text_obj)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.archon-hunt.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=text_obj,
    )


# void traders command
@tree.command(
    name=ts.get(f"cmd.void-traders.cmd"), description=ts.get(f"cmd.void-traders.desc")
)
async def cmd_voidTraders(interact: discord.Interaction):
    await interact.response.defer()

    API_Request("cmd.voidTraders")
    set_obj(json_load()[keys[5]], keys[5])
    eb, f = w_voidTraders(cmd_obj_check(keys[5]), language)
    await interact.followup.send(embed=eb, file=f)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.void-traders.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# steel path reward command
@tree.command(
    name=ts.get(f"cmd.steel-path-reward.cmd"),
    description=ts.get(f"cmd.steel-path-reward.desc"),
)
async def cmd_steel_reward(interact: discord.Interaction):
    eb, f = w_steelPath(cmd_obj_check(keys[6]), language)
    if f is None:
        await interact.response.send_message(embed=eb)
    else:
        await interact.response.send_message(embed=eb, file=f)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.steel-path-reward.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# fissures command
@tree.command(
    name=ts.get(f"cmd.fissures.cmd"), description=ts.get(f"cmd.fissures.desc")
)
async def cmd_fissures(interact: discord.Interaction):
    await interact.response.defer()

    API_Request("cmd.fissures")
    set_obj(json_load()[keys[10]], keys[10])
    text_obj = w_fissures(cmd_obj_check(keys[10]))
    await interact.followup.send(text_obj)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.fissures.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=text_obj,
    )


# duviriCycle command
@tree.command(
    name=ts.get(f"cmd.duviri-cycle.cmd"),
    description=ts.get(f"cmd.duviri-cycle.desc"),
)
async def cmd_temporal_archimedea(interact: discord.Interaction):
    await interact.response.defer()

    API_Request("cmd.cetus")
    set_obj(json_load()[keys[7]], keys[7])
    eb = w_duviriCycle(cmd_obj_check(keys[7]), language)
    await interact.followup.send(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.duviri-cycle.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# deep archimedea command
@tree.command(
    name=ts.get(f"cmd.deep-archimedea.cmd"),
    description=ts.get(f"cmd.deep-archimedea.desc"),
)
async def cmd_deep_archimedea(interact: discord.Interaction):
    text_obj = w_deepArchimedea(cmd_obj_check(keys[8]), language)
    await interact.response.send_message(text_obj)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.deep-archimedea.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=text_obj,
    )


# temporal archimedea reward command
@tree.command(
    name=ts.get(f"cmd.temporal-archimedea.cmd"),
    description=ts.get(f"cmd.temporal-archimedea.desc"),
)
async def cmd_temporal_archimedea(interact: discord.Interaction):
    text_obj = w_temporalArchimedia(cmd_obj_check(keys[9]), language)
    await interact.response.send_message(text_obj)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.temporal-archimedea.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=text_obj,
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
    text_obj = w_calendar(cmd_obj_check(keys[11]), types.name, language)
    await interact.response.send_message(text_obj)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.calendar.cmd')}.{type}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=text_obj,
    )


# cambion command (cambionCycle)
@tree.command(name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc"))
async def cmd_cambion(interact: discord.Interaction):
    await interact.response.defer()

    API_Request("cmd.cambion")
    set_obj(json_load()[keys[12]], keys[12])
    eb, f = w_cambionCycle(cmd_obj_check(keys[12]), language)
    if f is None:
        await interact.followup.send(embed=eb)
    else:
        await interact.followup.send(embed=eb, file=f)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.cambion.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# dailyDeals command
@tree.command(
    name=ts.get(f"cmd.dailyDeals.cmd"), description=ts.get(f"cmd.dailyDeals.desc")
)
async def cmd_dailyDeals(interact: discord.Interaction):
    await interact.response.defer()

    API_Request("cmd.dailyDeals")
    set_obj(json_load()[keys[13]], keys[13])
    eb = w_dailyDeals(cmd_obj_check(keys[13]), language)
    await interact.followup.send(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.dailyDeals.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# invasions command
@tree.command(
    name=ts.get(f"cmd.invasions.cmd"), description=ts.get(f"cmd.invasions.desc")
)
async def cmd_invasions(interact: discord.Interaction):
    await interact.response.defer()

    API_Request("cmd.invasions")
    set_obj(json_load()[keys[14]], keys[14])
    eb = w_invasions(cmd_obj_check(keys[14]), language)
    await interact.followup.send(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.invasions.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# voidTrader item command
@tree.command(
    name=ts.get(f"cmd.void-traders-item.cmd"),
    description=ts.get(f"cmd.void-traders-item.desc"),
)
async def cmd_traders_item(interact: discord.Interaction):
    await interact.response.defer()

    API_Request("cmd.void-traders-item")
    set_obj(json_load()[keys[5]], keys[5])
    eb = w_voidTradersItem(cmd_obj_check(keys[5]), language)
    await interact.followup.send(embed=eb)  # , file=f)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.void-traders-item.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        obj=eb.description,
    )


# run bot
bot_client.run(BOT_TOKEN)
