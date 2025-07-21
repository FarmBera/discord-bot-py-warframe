# discord module
import discord
from discord.ext import tasks, commands
from discord import app_commands  # , Interaction

# essential module
import datetime as dt
import asyncio
import yaml, csv, json, re
from translator import Translator

# custom module & variables
from TOKEN import TOKEN as BOT_TOKEN
from TOKEN import channel_list  # notice channel list

from translator import Translator
from text import log_file_path
from module.color import color
from module.api_request import API_Request
from module.save_log import save_log

from module.parser.w_alerts import W_Alerts
from module.parser.w_news import W_news

# terminal text color dict
color: dict = {
    "black": "\033[30m",
    "white": "\033[37m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
}


def json_load(file_path):
    """
    read json file at provided path and return

    Args:
        file_path (str): JSON file path

    Returns:
        dict or list: JSON file object.
        None: file not found || parse error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"{color['yellow']}File Not Found > {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"{color['yellow']}ERR: JSON Decode Exception > {file_path}")
        return None
    except Exception as e:
        print(f"{color['red']}ERR: {e}")
        return None


def json_save(data, file_path) -> bool:
    """
    convert object(dict or list) and save as JSON file

    Args:
        data (dict or list): to save data
        file_path (str): JSON file path

    Returns:
        bool: save success True, failed to save
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except TypeError as e:
        print(f"{color['yellow']}ERR: Convertion Exception > {e}")
        return False
    except Exception as e:
        print(f"{color['red']}ERR > {e}")
        return False


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
        print(f"Logged on as {self.user}!")

        # send dm to specific user ???
        # user = await client.fetch_user()
        # await user.send("Bot Running Start!")

    # auto api request & check new contents
    @tasks.loop(minutes=5.0)
    async def api_request(self):
        try:  # send API request
            est, response = API_Request()
        except Exception as e:
            print(f"{color['red']}ERR: {e}")

        # open setting file
        setting = json_load("setting.json")

        def analyze_obj(name: str):
            FILE_PATH = f"json/{name}.json"

            if setting["noti"]["list"][name]:
                # load json objects
                obj_prev = json_load(FILE_PATH)
                obj_new = json_load("Warframe_pc.json")[name]

            # print(len(obj_prev), len(obj_new))

            # check loaded obj
            if obj_prev is None or obj_new is None:
                print(
                    f"{color['red']}ERR: obj is NOT Loaded! (from analyze_obj {name}){color['white']}"
                )
                return False

            missing = [
                item
                for item in [item["id"] for item in obj_new]
                if item not in [item["id"] for item in obj_prev]
            ]
            if missing:  # if exist new contents
                obj_result = []
                for id in missing:  # open id
                    for i in range(len(obj_new)):  # check each objects
                        if id == obj_new[i]["id"]:
                            obj_result.append(obj_new[i])  # append new objects
                json_save(obj_new, FILE_PATH)
                return obj_result  # only missing items
            else:  # not exist
                return False

        # analyze response data if flag is true
        key = "alerts"
        if setting["noti"]["list"][key]:
            value = W_Alerts(analyze_obj(key))
            if value != False:
                print(value)
                # send message

        key = "news"
        if setting["noti"]["list"][key]:
            value = W_news(analyze_obj(key))
            if value != False:
                print(value)
                # send message

        # key = "cetus"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "sortie"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "archonHunt"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "voidTraders"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "voidTraderItem"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "steelPathReward"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "fissures"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "invasions"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "duviriCycle"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "deepArchimedia"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        # key = "temporalArchimedia"
        # if setting["noti"]["list"][key]:
        #     value = W_news(analyze_obj(key))
        #     if value != False:
        #         print(value)
        #         # send message

        return

    # TODO
    # send daily reset message
    @tasks.loop(time=dt.time(hour=7, minute=0, tzinfo=kst))
    async def send_atime_alert(self):
        for ch in channel_list:
            channel = await self.fetch_channel(ch)
            # await channel.send()

    # TODO: send weekly reset message
    @tasks.loop(time=dt.time(hour=9, minute=0, tzinfo=kst))
    async def send_weekly_noti(self):
        return

    # TODO: 특정 시간에 메시지 보내기 (공지)
    # alert specific time
    @tasks.loop(time=alert_times)
    async def auto_notification(self):
        for ch in channel_list:
            channel = await self.fetch_channel(ch)
            # await channel.send()

    async def on_message(self, message):
        if message.author == self.user:
            return

        trim_text = message.content.replace(" ", "")

        usrname = message.author.display_name

        await message.delete()
        await message.channel.send(f"response: {trim_text}")
        save_log(
            cmd=trim_text,
            user=usrname,
            time=message.created_at,
            guild=message.guild,
            channel=message.channel,
        )


# init discord bot
intents = discord.Intents.default()
intents.message_content = True
bot_client = DiscordBot(intents=intents)
tree = app_commands.CommandTree(bot_client)

# commands
# to be continue


# main function
if __name__ == "__main__":
    language = input("Select Language (en/ko) >> ")
    if language not in ["en", "ko"]:
        print(
            f"{color['red']}Selection ERR:{color['yellow']}'{language}'. {color['red']}abort."
        )
        exit(1)
    ts = Translator(lang=language)
    print(ts.get("init.init"), end="")
    print(ts.get("init.components"), end="")
    print(ts.get("init.done"))
    print(ts.get("init.start"))

    # run bot
    bot_client.run(BOT_TOKEN)
