import discord
from discord.ext import tasks
import datetime as dt


from TOKEN import TOKEN as BOT_TOKEN
from TOKEN import DEFAULT_JSON_PATH
from variables.keys import keys

from translator import ts, language
from times import alert_times
from variables.color import color
from module.api_request import API_Request
from module.save_log import save_log

from module.yaml_open import yaml_open
from module.json_load import json_load
from module.get_obj import get_obj
from module.set_obj import set_obj
from module.cmd_obj_check import cmd_obj_check

from module.parser.w_alerts import W_Alerts
from module.parser.w_news import W_news
from module.parser.w_cetus_cycle import W_CetusCycle
from module.parser.w_sortie import W_Sortie
from module.parser.w_archon_hunt import W_archonHunt
from module.parser.w_void_traders import W_VoidTraders
from module.parser.w_steelPath import W_SteelPathReward
from module.parser.w_duviri_cycle import W_duviriCycle
from module.parser.w_deep_archimedea import W_DeepArchimedea
from module.parser.w_temporal_archimedea import W_TemporalArchimedia
from module.parser.w_fissures import W_Fissures


class DiscordBot(discord.Client):
    async def on_ready(self):
        await self.wait_until_ready()
        await tree.sync()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("start.bot-status-msg")),
        )
        # print(color["green"], ts.get("start.connected"))
        print(f"{color["cyan"]}Logged on as {self.user}!{color['default']}")  # VAR

        self.auto_send_msg_request.start()
        self.auto_noti.start()

    async def send_alert(self, value):
        # send message
        channel_list = yaml_open("channel")["channel"]
        for ch in channel_list:
            # embed type
            if str(type(value)) == "<class 'discord.embeds.Embed'>":  # VAR
                channel = await self.fetch_channel(ch)
                save_log(
                    cmd="auto_sent_message",
                    user="bot.self",  # VAR
                    guild=channel.guild,
                    channel=channel.name,
                    # msg=item,
                    obj=value.description,
                )
                await channel.send(embed=value)
                return

            # string type
            channel = await self.fetch_channel(ch)
            save_log(
                cmd="auto_sent_message",
                user="bot.self",  # VAR
                guild=channel.guild,
                channel=channel.name,
                # msg=item,
                obj=value,
            )
            await channel.send(value)

    # auto api request & check new contents
    @tasks.loop(minutes=5.0)
    async def auto_send_msg_request(self):
        # open setting file
        setting = json_load("setting.json")  # VAR

        API_Request("auto_send_msg_request()")  # VAR

        def empty_check(obj, item):
            if obj == []:
                set_obj(obj, item)
                return True
            return False

        async def send_alert(value):
            # checks alert is enabled in setting file
            if not setting["noti"]["list"][item]:
                return

            # send message
            channel_list = yaml_open("channel")["channel"]  # VAR
            for ch in channel_list:
                # embed type
                if str(type(value)) == "<class 'discord.embeds.Embed'>":  # VAR
                    channel = await self.fetch_channel(ch)
                    save_log(
                        cmd="auto_sent_message",
                        user="bot.self",  # VAR
                        guild=channel.guild,
                        channel=channel.name,
                        msg=item,
                        obj=value.description,
                    )
                    await channel.send(embed=value)
                    return

                # string type
                channel = await self.fetch_channel(ch)
                save_log(
                    cmd="auto_sent_message",  # VAR
                    user="bot.self",  # VAR
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

            # TODO: alerts; test
            if item == keys[0]:  # alerts
                if empty_check(obj_new, item):
                    continue
                try:
                    if get_obj(item)[-1]["id"] == obj_new[-1]["id"]:
                        continue
                except:
                    is_new_content = True
                    await send_alert(W_Alerts(obj_new))

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
                    await send_alert(W_news(missing))

            elif item == keys[2]:  # cetusCycle
                if get_obj(item)["state"] == obj_new["state"]:
                    continue
                is_new_content = True
                await send_alert(W_CetusCycle(obj_new))

            elif item == keys[3]:  # sortie
                if get_obj(item)["activation"] == obj_new["activation"]:
                    continue
                is_new_content = True
                # await send_alert(W_Sortie(obj_new))

            elif item == keys[4]:  # archonHunt
                if get_obj(item)["activation"] == obj_new["activation"]:
                    continue
                is_new_content = True
                await send_alert(W_archonHunt(obj_new))

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
                await send_alert(W_VoidTraders(obj_new))

            # elif item=='voidTraderItem':
            # elif item == keys[10]:  # fissures

            elif item == keys[6]:  # steelPath
                if get_obj(item)["currentReward"] == obj_new["currentReward"]:
                    continue
                is_new_content = True
                await send_alert(W_SteelPathReward(obj_new))

            elif item == keys[7]:  # duviriCycle
                if get_obj(item)["state"] == obj_new["state"]:
                    continue
                is_new_content = True
                await send_alert(W_duviriCycle(obj_new))

            elif item == keys[8]:  # deepArchimedea
                if get_obj(item)["activation"] == obj_new["activation"]:
                    continue
                is_new_content = True
                await send_alert(W_DeepArchimedea(obj_new))

            elif item == keys[9]:  # temporalArchimedea
                if get_obj(item)["activation"] == obj_new["activation"]:
                    continue
                is_new_content = True
                await send_alert(W_TemporalArchimedia(obj_new))

            if is_new_content:  # update json file
                set_obj(obj_new, item)

        return  # End Of auto_send_msg_request()

    @tasks.loop(time=alert_times)
    async def auto_noti(self):  # auto alert; sortie
        await self.send_alert(W_Sortie(get_obj(keys[3])))

    # async def on_message(self, message):
    #     if message.author == self.user:
    #         return

    #     trim_text = message.content.replace(" ", "")
    #     usrname = message.author.display_name

    #     await message.delete()
    #     await message.channel.send(f"response: {trim_text}")
    #     save_log(
    #         cmd=trim_text,
    #         user=usrname,
    #         time=message.created_at,
    #         guild=message.guild,
    #         channel=message.channel,
    #     )


# init discord bot
intents = discord.Intents.default()
intents.message_content = True
bot_client = DiscordBot(intents=intents)
tree = discord.app_commands.CommandTree(bot_client)


# commands
# TODO: convert to create discord embed and return only embed object!


# news command
@tree.command(name=ts.get(f"cmd.news.cmd"), description=ts.get(f"cmd.news.desc"))
async def cmd_news(interact: discord.Interaction):
    save_log(
        cmd="cmd.news",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(embed=W_news(cmd_obj_check(keys[1]), language))


# alerts command
@tree.command(name=ts.get(f"cmd.alerts.cmd"), description=ts.get(f"cmd.alerts.desc"))
async def cmd_alerts(interact: discord.Interaction):
    save_log(
        cmd="cmd.alerts",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(embed=W_Alerts(get_obj(keys[0])))


# cetus command (cetusCycle)
@tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
async def cmd_cetus(interact: discord.Interaction):
    API_Request("cmd.cetus")
    set_obj(json_load()[keys[2]], keys[2])
    save_log(
        cmd="cmd.cetus",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(W_CetusCycle(cmd_obj_check(keys[2]), language))


# sortie command
@tree.command(name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc"))
async def cmd_sortie(interact: discord.Interaction):
    save_log(
        cmd="cmd.sortie",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(W_Sortie(cmd_obj_check(keys[3]), language))


# archon hunt command
@tree.command(
    name=ts.get(f"cmd.archon-hunt.cmd"), description=ts.get(f"cmd.archon-hunt.desc")
)
async def cmd_archon_hunt(interact: discord.Interaction):
    save_log(
        cmd="cmd.archon-hunt",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(W_archonHunt(cmd_obj_check(keys[4]), language))


# void traders command
@tree.command(
    name=ts.get(f"cmd.void-traders.cmd"), description=ts.get(f"cmd.void-traders.desc")
)
async def cmd_void_traders(interact: discord.Interaction):
    API_Request("cmd.voidTraders")
    set_obj(json_load()[keys[5]], keys[5])
    save_log(
        cmd="cmd.void-traders",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(
        embed=W_VoidTraders(cmd_obj_check(keys[5]), language)
    )


# steel path reward command
@tree.command(
    name=ts.get(f"cmd.steel-path-reward.cmd"),
    description=ts.get(f"cmd.steel-path-reward.desc"),
)
async def cmd_steel_reward(interact: discord.Interaction):
    save_log(
        cmd="cmd.steel-path",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(
        W_SteelPathReward(cmd_obj_check(keys[6]), language)
    )


# fissures command
@tree.command(
    name=ts.get(f"cmd.fissures.cmd"), description=ts.get(f"cmd.fissures.desc")
)
async def cmd_fissures(interact: discord.Interaction):
    API_Request("cmd.fissures")
    set_obj(json_load()[keys[10]], keys[10])
    save_log(
        cmd="cmd.fissures",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(W_Fissures(cmd_obj_check(keys[10])))


# duviriCycle command
@tree.command(
    name=ts.get(f"cmd.duviri-cycle.cmd"),
    description=ts.get(f"cmd.duviri-cycle.desc"),
)
async def cmd_temporal_archimedea(interact: discord.Interaction):
    save_log(
        cmd="cmd.duviri-cycle",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(
        embed=W_duviriCycle(cmd_obj_check(keys[7]), language)
    )


# deep archimedea command
@tree.command(
    name=ts.get(f"cmd.deep-archimedea.cmd"),
    description=ts.get(f"cmd.deep-archimedea.desc"),
)
async def cmd_deep_archimedea(interact: discord.Interaction):
    save_log(
        cmd="cmd.deep-archimedea",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(
        W_DeepArchimedea(cmd_obj_check(keys[8]), language)
    )


# temporal archimedea reward command
@tree.command(
    name=ts.get(f"cmd.temporal-archimedea.cmd"),
    description=ts.get(f"cmd.temporal-archimedea.desc"),
)
async def cmd_temporal_archimedea(interact: discord.Interaction):
    save_log(
        cmd="cmd.temporal-archimedea",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(
        W_TemporalArchimedia(cmd_obj_check(keys[9]), language)
    )


# run bot
bot_client.run(BOT_TOKEN)
