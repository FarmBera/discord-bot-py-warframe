import discord
import datetime as dt

# from src.main import tree
from src.translator import ts
from src.constants.times import JSON_DATE_PAT
from src.constants.color import C
from src.constants.keys import STARTED_TIME_FILE_LOC, MSG_BOT
from src.utils.logging_utils import save_log
from src.utils.file_io import save_file


class MaintanceBot(discord.Client):
    def __init__(self, *, intents, **options):
        super().__init__(intents=intents, **options)
        self.tree = None

    async def on_ready(self):
        print(
            f"{C.blue}[info] {C.yellow}{ts.get('start.sync')}...{C.default}",
            end="",
        )
        await self.wait_until_ready()
        if self.tree:
            await self.tree.sync()
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
            obj=dt.datetime.now(),
        )  # VAR
