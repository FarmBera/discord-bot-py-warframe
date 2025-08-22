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
from module.get_obj import get_obj
from module.set_obj import set_obj
from module.cmd_obj_check import cmd_obj_check
from module.get_emoji import get_emoji
from module.open_file import open_file

from module.parser.w_alerts import w_alerts
from module.parser.w_news import w_news
from module.parser.w_cetusCycle import w_cetusCycle
from module.parser.w_sortie import w_sortie
from module.parser.w_archonHunt import w_archonHunt
from module.parser.w_voidTraders import w_voidTraders
from module.parser.w_steelPath import w_steelPath
from module.parser.w_duviriCycle import w_duviriCycle
from module.parser.w_deepArchimedea import w_deepArchimedea
from module.parser.w_temporalArchimedea import w_temporalArchimedia
from module.parser.w_fissures import w_fissures
from module.parser.w_calendar import w_calendar
from module.parser.w_cambionCycle import w_cambionCycle
from module.parser.w_dailyDeals import w_dailyDeals
from module.parser.w_invasions import w_invasions


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

    async def send_alert_(self, value, channel_list=None):
        if channel_list is None:
            channel_list = yaml_open(CHANNEL_FILE_LOC)["channel"]

        # send message
        for ch in channel_list:
            channel = await self.fetch_channel(ch)

            # embed type
            if str(type(value)) == TYPE_EMBED:
                save_log(
                    type="msg",
                    cmd="auto_sent_message",
                    user=MSG_BOT,
                    guild=channel.guild,
                    channel=channel.name,
                    # msg=item,
                    obj=value.description,
                )
                await channel.send(embed=value)
                return

            # embed with file or thumbnail
            elif str(type(value)) == TYPE_TUPLE:
                eb, f = value
                save_log(
                    type="msg",
                    cmd="auto_sent_message",
                    user=MSG_BOT,
                    guild=channel.guild,
                    channel=channel.name,
                    # msg=item,
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
                    # msg=item,
                    obj=value,
                )
                await channel.send(value)

    # auto api request & check new contents
    @tasks.loop(minutes=5.0)
    async def auto_send_msg_request(self):
        setting = json_load(SETTING_FILE_LOC)  # open setting file

        code = API_Request("auto_send_msg_request()")  # VAR
        if code != 200:
            msg = f"{color['yellow']}response code < {code} > Task Aborted. (from auto_send_msg_request){color['default']}"
            save_log(type="warn", cmd="auto_send_msg_request()", user=MSG_BOT, msg=msg)
            print(msg)
            return

        def empty_check(obj, item):
            if obj == []:
                set_obj(obj, item)
                return True
            return False

        async def send_alert(value, channel_list=None):
            # checks alert is enabled in setting file
            if not setting["noti"]["list"][item]:
                return

            if channel_list is None:
                channel_list = yaml_open(CHANNEL_FILE_LOC)["channel"]  # VAR

            # send message
            for ch in channel_list:
                # embed type
                channel = await self.fetch_channel(ch)

                if str(type(value)) == TYPE_EMBED:
                    save_log(
                        type="msg",
                        cmd="auto_sent_message",
                        user=MSG_BOT,
                        guild=channel.guild,
                        channel=channel.name,
                        msg=item,
                        obj=value.description,
                    )
                    await channel.send(embed=value)

                # embed with file or thumbnail
                elif str(type(value)) == TYPE_TUPLE:
                    eb, f = value
                    save_log(
                        type="msg",
                        cmd="auto_sent_message",
                        user=MSG_BOT,
                        guild=channel.guild,
                        channel=channel.name,
                        msg=item,
                        obj=eb.description,
                    )
                    await channel.send(embed=eb, file=f)

                else:  # string type
                    save_log(
                        type="msg",
                        cmd="auto_sent_message",  # VAR
                        user=MSG_BOT,
                        guild=channel.guild,
                        channel=channel.name,
                        msg=item,
                        obj=value,
                    )
                    await channel.send(value)

        # check for new content & send alert
        for item in keys:
            is_new_content: bool = False
            obj_prev = get_obj(item)
            obj_new = json_load(DEFAULT_JSON_PATH)[item]

            if item == keys[0]:  # alerts
                if empty_check(obj_new, item):
                    continue
                try:
                    if get_obj(item)[-1]["id"] == obj_new[-1]["id"]:
                        continue
                except:
                    is_new_content = True
                    await send_alert(w_alerts(obj_new))

            elif item == keys[1]:  # news
                if get_obj(item)[-1]["id"] == obj_new[-1]["id"]:
                    continue

                missing_id = [
                    item
                    for item in [item["id"] for item in obj_new]
                    if item not in [item["id"] for item in obj_prev]
                ]
                if not missing_id:
                    continue

                missing = []
                for id in missing_id:
                    for jtem in obj_new:
                        if id != jtem["id"]:  # skip if not equal id
                            continue
                        missing.append(jtem)

                if missing:
                    is_new_content = True
                    await send_alert(
                        w_news(missing), yaml_open(CHANNEL_FILE_LOC)["news"]
                    )

            elif item == keys[2]:  # cetusCycle
                if get_obj(item)["state"] == obj_new["state"]:
                    continue
                is_new_content = True
                await send_alert(w_cetusCycle(obj_new))

            elif item == keys[3]:  # sortie
                if get_obj(item)["activation"] == obj_new["activation"]:
                    continue
                is_new_content = True
                # await send_alert(W_Sortie(obj_new), yaml_open(CHANNEL_FILE_LOC)["sortie"])

            elif item == keys[4]:  # archonHunt
                if get_obj(item)["activation"] == obj_new["activation"]:
                    continue
                is_new_content = True
                await send_alert(
                    w_archonHunt(obj_new), yaml_open(CHANNEL_FILE_LOC)["sortie"]
                )

            elif item == keys[5]:  # voidTraders
                try:  # prev content
                    val_prev = get_obj(item)[-1]["activation"]
                    val_prev_act = get_obj(item)[-1]["active"]
                except:
                    val_prev = get_obj(item)["activation"]
                    val_prev_act = get_obj(item)["active"]

                try:  # new content
                    val_new = obj_new[-1]["activation"]
                    val_new_act = obj_new[-1]["active"]
                except:
                    val_new = obj_new["activation"]
                    val_new_act = obj_new["active"]

                # check
                if (val_prev == val_new) and (val_prev_act == val_new_act):
                    continue
                if empty_check(obj_new, item):
                    continue
                is_new_content = True
                await send_alert(w_voidTraders(obj_new))

            # elif item=='voidTraderItem':

            elif item == keys[6]:  # steelPath
                if get_obj(item)["currentReward"] == obj_new["currentReward"]:
                    continue
                is_new_content = True
                await send_alert(w_steelPath(obj_new))

            elif item == keys[7]:  # duviriCycle
                if get_obj(item)["state"] == obj_new["state"]:
                    continue
                is_new_content = True
                await send_alert(w_duviriCycle(obj_new))

            elif item == keys[8]:  # deepArchimedea
                if get_obj(item)["activation"] == obj_new["activation"]:
                    continue
                is_new_content = True
                await send_alert(w_deepArchimedea(obj_new))

            elif item == keys[9]:  # temporalArchimedea
                if get_obj(item)["activation"] == obj_new["activation"]:
                    continue
                is_new_content = True
                await send_alert(w_temporalArchimedia(obj_new))

            # elif item == keys[10]:  # fissures
            # deprecated

            elif item == keys[11]:  # calendar
                if get_obj(item)[0]["activation"] == obj_new[0]["activation"]:
                    continue
                is_new_content = True
                await send_alert(
                    w_calendar(obj_new, ts.get("cmd.calendar.choice-prize")),
                    yaml_open(CHANNEL_FILE_LOC)["hex-cal"],
                )

            elif item == keys[12]:  # cambionCycle
                if get_obj(item)["state"] == obj_new["state"]:
                    continue
                is_new_content = True
                await send_alert(w_cambionCycle(obj_new))

            elif item == keys[13]:  # dailyDeals
                if get_obj(item)[0]["item"] == obj_new[0]["item"]:
                    continue
                is_new_content = True
                await send_alert(w_dailyDeals(obj_new))

            elif item == keys[14]:  # invasions
                missing_id = [
                    item
                    for item in [item["id"] for item in obj_new]
                    if item not in [item["id"] for item in obj_prev]
                ]
                if not missing_id:
                    continue

                missing = []
                for id in missing_id:
                    for jtem in obj_new:
                        if id != jtem["id"]:  # skip if not equal id
                            continue
                        missing.append(jtem)

                if missing:
                    is_new_content = True
                    await send_alert(w_invasions(missing))

            if is_new_content:  # update json file
                set_obj(obj_new, item)

        return  # End Of auto_send_msg_request()

    # sortie alert
    @tasks.loop(time=alert_times)
    async def auto_noti(self):
        await self.send_alert_(
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
        # obj=eb.description,
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
        # obj=eb.description,
    )


# cetus command (cetusCycle)
@tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
async def cmd_cetus(interact: discord.Interaction):
    API_Request("cmd.cetus")
    set_obj(json_load()[keys[2]], keys[2])
    eb, f = w_cetusCycle(cmd_obj_check(keys[2]), language)
    if f is None:
        await interact.response.send_message(embed=eb)
    else:
        await interact.response.send_message(embed=eb, file=f)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.cetus.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        # obj=eb.description,
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
        # obj=text_obj,
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
        # obj=text_obj,
    )


# void traders command
@tree.command(
    name=ts.get(f"cmd.void-traders.cmd"), description=ts.get(f"cmd.void-traders.desc")
)
async def cmd_voidTraders(interact: discord.Interaction):
    API_Request("cmd.voidTraders")
    set_obj(json_load()[keys[5]], keys[5])
    eb, f = w_voidTraders(cmd_obj_check(keys[5]), language)
    await interact.response.send_message(embed=eb, file=f)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.void-traders.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        # obj=eb.description,
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
        # obj=eb.description,
    )


# fissures command
@tree.command(
    name=ts.get(f"cmd.fissures.cmd"), description=ts.get(f"cmd.fissures.desc")
)
async def cmd_fissures(interact: discord.Interaction):
    API_Request("cmd.fissures")
    set_obj(json_load()[keys[10]], keys[10])
    text_obj = w_fissures(cmd_obj_check(keys[10]))
    await interact.response.send_message(text_obj)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.fissures.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        # obj=text_obj,
    )


# duviriCycle command
@tree.command(
    name=ts.get(f"cmd.duviri-cycle.cmd"),
    description=ts.get(f"cmd.duviri-cycle.desc"),
)
async def cmd_temporal_archimedea(interact: discord.Interaction):
    API_Request("cmd.cetus")
    set_obj(json_load()[keys[7]], keys[7])
    eb = w_duviriCycle(cmd_obj_check(keys[7]), language)
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.duviri-cycle.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        # obj=eb.description,
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
        # obj=text_obj,
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
        # obj=text_obj,
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
        # obj=text_obj,
    )


# cambion command (cambionCycle)
@tree.command(name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc"))
async def cmd_cambion(interact: discord.Interaction):
    API_Request("cmd.cambion")
    set_obj(json_load()[keys[12]], keys[12])
    eb, f = w_cambionCycle(cmd_obj_check(keys[12]), language)
    if f is None:
        await interact.response.send_message(embed=eb)
    else:
        await interact.response.send_message(embed=eb, file=f)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.cambion.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        # obj=eb.description,
    )


# dailyDeals command
@tree.command(
    name=ts.get(f"cmd.dailyDeals.cmd"), description=ts.get(f"cmd.dailyDeals.desc")
)
async def cmd_dailyDeals(interact: discord.Interaction):
    API_Request("cmd.dailyDeals")
    set_obj(json_load()[keys[13]], keys[13])
    eb = w_dailyDeals(cmd_obj_check(keys[13]), language)
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.dailyDeals.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        # obj=eb.description,
    )


# invasions command
@tree.command(
    name=ts.get(f"cmd.invasions.cmd"), description=ts.get(f"cmd.invasions.desc")
)
async def cmd_invasions(interact: discord.Interaction):
    API_Request("cmd.invasions")
    set_obj(json_load()[keys[14]], keys[14])
    eb = w_invasions(cmd_obj_check(keys[14]), language)
    await interact.response.send_message(embed=eb)
    save_log(
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.invasions.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        # obj=eb.description,
    )


# run bot
bot_client.run(BOT_TOKEN)
