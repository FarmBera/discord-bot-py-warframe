# discord module
import discord
from discord.ext import tasks, commands
from discord import app_commands  # , Interaction

# essential module
import datetime as dt
import asyncio
import yaml, csv, re
from translator import Translator

# custom module & variables
from TOKEN import TOKEN as BOT_TOKEN
from translator import Translator
from text import log_file_path


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


# save log into file
def save_log(
    cmd, time=f"{dt.datetime.now()}", user="null", guild="null", channel="null"
):
    log_f = open(log_file_path, "a", encoding="UTF-8", newline="")
    time = (time + dt.timedelta(hours=9)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )  # for UTC+9 Timezone
    # time = (time + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")  # for US(UTC+0) Timezone
    wr = csv.writer(log_f)
    wr.writerow([user, time, cmd, guild, channel])
    log_f.close()


kst = dt.timezone(dt.timedelta(hours=9))
alert_times = [
    dt.time(hour=7, minute=30, tzinfo=kst),
    dt.time(hour=9, minute=0, tzinfo=kst),
]


class DiscordBot(discord.Client):
    async def on_ready(self):
        await self.wait_until_ready()
        await tree.sync()
        # Change Bot State
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("init.bot-status-msg")),
        )
        # self.auto_send_notice.start()
        print(f"Logged on as {self.user}!")

        # send dm to specific user ???
        # user = await client.fetch_user()
        # await user.send("Bot Running Start!")

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
