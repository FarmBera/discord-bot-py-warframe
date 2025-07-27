# discord module
import discord
from discord.ext import tasks

# essential module
import datetime as dt

# import asyncio
# import yaml, csv, json, re

### custom module & variables ###
# essential variables
from TOKEN import TOKEN as BOT_TOKEN
from TOKEN import DEFAULT_JSON_PATH

# from TOKEN import channel_list  # notice channel list

# essential custom module
from translator import ts, language
from text import log_file_path
from module.color import color
from module.api_request import API_Request
from module.save_log import save_log

# for object save & load
from module.yaml_open import yaml_open
from module.json_load import json_load
from module.json_save import json_save
from module.get_obj import get_obj
from module.set_obj import set_obj
from module.cmd_obj_check import cmd_obj_check

# object parser
from module.parser.w_alerts import W_Alerts
from module.parser.w_news import W_news
from module.parser.w_cetus_cycle import W_CetusCycle
from module.parser.w_sortie import W_Sortie
from module.parser.w_archon_hunt import W_archonHunt
from module.parser.w_void_traders import W_VoidTraders
from module.parser.w_steelPath import W_SteelPathReward
from module.parser.w_deep_archimedea import W_DeepArchimedea
from module.parser.w_temporal_archimedea import W_TemporalArchimedia
from module.parser.w_fissures import W_Fissures


kst = dt.timezone(dt.timedelta(hours=9))
alert_times = [
    dt.time(hour=7, minute=0, tzinfo=kst),
    dt.time(hour=7, minute=30, tzinfo=kst),
    dt.time(hour=9, minute=0, tzinfo=kst),
]
keys = [
    ["alerts", W_Alerts],
    ["news", W_news],
    ["cetusCycle", W_CetusCycle],
    ["sortie", W_Sortie],
    ["archonHunt", W_archonHunt],
    ["voidTraders", W_VoidTraders],
    ## ['voidTraderItem',],
    ["steelPath", W_SteelPathReward],
    # ["fissures", W_Fissures],
    ## ['invasions',],
    ## ['duviriCycle'],
    ["deepArchimedea", W_DeepArchimedea],
    ["temporalArchimedea", W_TemporalArchimedia],
]


class DiscordBot(discord.Client):
    async def on_ready(self):
        await self.wait_until_ready()
        await tree.sync()
        # change bot state
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("init.bot-status-msg")),
        )
        # self.auto_send_notice.start()
        print(color["green"], ts.get("init.connected"))
        print(f"{color["default"]}Logged on as {self.user}!")

        self.auto_send_msg_request.start()

        # send dm to specific user ???
        # user = await client.fetch_user()
        # await user.send("Bot Running Start!")

    # send to message at specific channels
    async def send_message_to(msg, ch_list):
        return

    # auto api request & check new contents
    @tasks.loop(minutes=5.0)
    async def auto_send_msg_request(self):
        # open setting file
        setting = json_load("setting.json")

        API_Request("auto_send_msg_request()")

        def empty_check(obj, item):
            if obj == []:
                set_obj(obj, item)
                return True
            return False

        async def send_alert(value):
            # checks alert is enabled in setting file
            if not setting["noti"]["list"][item[0]]:
                return

            # send message
            channel_list = yaml_open("channel")["channel"]
            for ch in channel_list:
                # print(ch, value)
                channel = await self.fetch_channel(ch)
                save_log(
                    cmd="auto_sent_message",
                    user="bot.self",
                    guild=channel.guild,
                    channel=channel.name,
                    msg=item,
                    obj=value,
                )
                await channel.send(value)

        # send alert if notification flag (settings.json) is true
        for item in keys:
            # print(item[0])
            is_new_content: bool = False
            obj_prev = get_obj(item[0])
            obj_new = json_load(DEFAULT_JSON_PATH)[item[0]]

            # compare = [item for item in obj_new if item not in obj_prev]
            # print(compare)

            # TODO: test
            if item[0] == "alerts":
                if get_obj(item[0]) == obj_new:
                    # print("alerts: equal obj")
                    continue
                if empty_check(obj_new, item[0]):
                    # print("alerts: empty")
                    continue

            elif item[0] == "news":
                if get_obj(item[0])[-1] == obj_new[-1]:
                    # print("news: equal")
                    continue
                missing = [item for item in obj_new if item not in obj_prev]
                if missing:
                    is_new_content = True
                    await send_alert(W_news(missing))

            elif item[0] == "cetusCycle":
                if get_obj(item[0])["state"] == obj_new["state"]:
                    # print("cetusCycle: equal")
                    continue
                is_new_content = True
                await send_alert(W_CetusCycle(obj_new))

            elif item[0] == "sortie":
                if get_obj(item[0])["activation"] == obj_new["activation"]:
                    # print("sortie: equal")
                    continue
                is_new_content = True
                await send_alert(W_Sortie(obj_new))

            # TODO: test later
            elif item[0] == "archonHunt":
                if get_obj("archonHunt")["activation"] == obj_new["activation"]:
                    # print("archonHunt: equal")
                    continue
                is_new_content = True
                await send_alert(W_archonHunt(obj_new))

            elif item[0] == "voidTraders":
                # prev contetnt
                try:
                    val_prev = get_obj("voidTraders")[-1]
                except:
                    val_prev = get_obj("voidTraders")

                # new content
                try:
                    val_new = obj_new[-1]
                except:
                    val_new = obj_new

                # check
                if val_prev == val_new:
                    # print("voidTraders: equal")
                    continue
                if empty_check(obj_new, item[0]):
                    # print("voidTraders: empty")
                    continue
                is_new_content = True
                await send_alert(W_VoidTraders(obj_new))

            # elif item[0]=='voidTraderItem':
            # elif item[0]=='fissures':

            elif item[0] == "steelPath":
                if get_obj("steelPath")["currentReward"] == obj_new["currentReward"]:
                    # print("steelPath: equal")
                    continue
                is_new_content = True
                await send_alert(W_SteelPathReward(obj_new))

            elif item[0] == "deepArchimedea":
                if get_obj("deepArchimedea")["activation"] == obj_new["activation"]:
                    # print("deepArchimedea: equal")
                    continue
                is_new_content = True
                await send_alert(W_DeepArchimedea(obj_new))

            elif item[0] == "temporalArchimedea":
                if get_obj("temporalArchimedea")["activation"] == obj_new["activation"]:
                    # print("temporalArchimedea: equal")
                    continue
                is_new_content = True
                await send_alert(W_TemporalArchimedia(obj_new))

            # else:
            #     print("~ else:")

            if is_new_content:
                set_obj(obj_new, item[0])

            return  # End Of auto_send_msg_request()

    # todo-delay: 특정 시간에 메시지 보내기 (공지)
    # alert specific time
    # @tasks.loop(time=alert_times)#TODO: implements
    async def auto_notification(self):
        channel_list = yaml_open("channel")["channel"]
        for ch in channel_list:
            channel = await self.fetch_channel(ch)
            # await channel.send()

    # TEMP: temporary disabled
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
    await interact.response.send_message(embed=W_news(cmd_obj_check("news"), language))


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
    await interact.response.send_message(W_Alerts(get_obj("alerts")))


# cetus command (cetusCycle)
@tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
async def cmd_cetus(interact: discord.Interaction):
    API_Request("cmd.cetus")
    set_obj(json_load()["cetusCycle"], "cetusCycle")
    save_log(
        cmd="cmd.cetus",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(
        W_CetusCycle(cmd_obj_check("cetusCycle"), language)
    )


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
    await interact.response.send_message(W_Sortie(cmd_obj_check("sortie"), language))


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
    await interact.response.send_message(
        W_archonHunt(cmd_obj_check("archonHunt"), language)
    )


# void traders command
@tree.command(
    name=ts.get(f"cmd.void-traders.cmd"), description=ts.get(f"cmd.void-traders.desc")
)
async def cmd_void_traders(interact: discord.Interaction):
    API_Request("cmd.voidTraders")
    set_obj(json_load()["voidTraders"], "voidTraders")
    save_log(
        cmd="cmd.void-traders",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(
        W_VoidTraders(cmd_obj_check("voidTraders"), language)
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
        W_SteelPathReward(cmd_obj_check("steelPath"), language)
    )


# fissures command
@tree.command(
    name=ts.get(f"cmd.fissures.cmd"), description=ts.get(f"cmd.fissures.desc")
)
async def cmd_fissures(interact: discord.Interaction):
    API_Request("cmd.fissures")
    set_obj(json_load()["fissures"], "fissures")
    save_log(
        cmd="cmd.fissures",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
    )
    await interact.response.send_message(W_Fissures(cmd_obj_check("fissures")))


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
        W_DeepArchimedea(cmd_obj_check("deepArchimedea"), language)
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
        W_TemporalArchimedia(cmd_obj_check("temporalArchimedea"), language)
    )


# main function
# if __name__ == "__main__":

# run bot
bot_client.run(BOT_TOKEN)
