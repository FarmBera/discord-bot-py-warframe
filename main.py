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

        # API_Request("auto_send_msg_request()")
        if not setting["noti"]["isEnabled"]:
            return

        def analyze_obj(name: str):
            # if setting["noti"]["list"][name]:
            # load json objects
            obj_prev = get_obj(name)
            obj_new = json_load(DEFAULT_JSON_PATH)[name]

            # check loaded obj
            if obj_prev is None or obj_new is None:
                print(
                    f"{color['red']}ERR: obj is NOT Loaded! (from analyze_obj {name}){color['white']}"
                )
                return False

            # [fix bug]
            if f"{type(obj_new)}" != "<class 'list'>":
                obj_new = list(obj_new)

            # check new contents
            try:  # [fix bug]
                missing = [
                    item
                    for item in [item["id"] for item in obj_new]
                    if item not in [item["id"] for item in obj_prev]
                ]
            except:
                missing = [item for item in obj_new if item not in obj_prev]
            if missing:  # if exist new contents
                save_log(
                    cmd="auto_send_msg_request()",
                    user="bot.self",
                    msg=f"New contents found. from {name}",
                    obj=missing,
                )
                obj_result = []
                for id in missing:  # open id
                    for i in range(len(obj_new)):  # check each objects
                        if id == obj_new[i]["id"]:
                            obj_result.append(obj_new[i])  # append new objects
                set_obj(obj_new, name)
                return obj_result  # only missing items

            # update expired content
            try:  # [fix bug]
                new_content = [
                    item
                    for item in [item["id"] for item in obj_prev]
                    if item not in [item["id"] for item in obj_new]
                ]
            except:
                new_content = [item for item in obj_prev if item not in obj_new]
            if new_content:
                save_log(
                    cmd="auto_send_msg_request()",
                    user="bot.self",
                    msg=f"Removed previous content. from {name}",
                    obj=new_content,
                )
                set_obj(obj_new, name)

            # else: nothing exist
            return None

        # send alert if notification flag (settings.json) is true
        keys = [
            ["alerts", W_Alerts],
            ["news", W_news],
            ["cetusCycle", W_CetusCycle],
            ["sortie", W_Sortie],
            ["archonHunt", W_archonHunt],
            ["voidTraders", W_VoidTraders],
            ## ['voidTraderItem',],
            ["steelPath", W_SteelPathReward],
            # ["fissures", W_Fissures],# TODO: fix error
            ## ['invasions',],
            ## ['duviriCycle'],
            ["deepArchimedea", W_DeepArchimedea],
            ["temporalArchimedea", W_TemporalArchimedia],
        ]
        for item in keys:
            # fetch object & check object
            value = item[1](analyze_obj(item[0]), language)
            if value is None:
                continue

            # force save latest data
            if not set_obj(json_load(DEFAULT_JSON_PATH)[item[0]], item[0]):
                print(
                    f"{color['red']}ERR with saving object (from 'auto_send_msg_request'){color['default']}"
                )
            # else:
            #     save_log(
            #         cmd="auto_send_msg_request()",
            #         user="bot.self",
            #         msg=f"Updated obj > {item}",
            #     )

            # checks alert is enabled in setting file
            if not setting["noti"]["list"][item[0]]:
                continue

            # send message
            channel_list = yaml_open("channel")["channel"]
            for ch in channel_list:
                print(ch, value)
                # channel = await self.fetch_channel(ch)
                # save_log(
                #     cmd="auto_sent_message",
                #     user="bot.self",
                #     guild=channel.guild,
                #     channel=channel.name,
                #     msg=item,
                #     obj=value,
                # )
                # await channel.send(value)

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
    await interact.response.send_message(W_Alerts(cmd_obj_check("alerts"), language))


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
    API_Request("cmd.cetus")
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
# language = input("Select Language (en/ko) >> ")
# if language not in ["en", "ko"]:
#     print(f"{color['red']}Selection ERR:{color['yellow']}'{language}'. {color['red']}abort.")
#     exit(1)
# ts = Translator(lang=language)


# run bot
bot_client.run(BOT_TOKEN)
