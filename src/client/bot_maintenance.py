import discord
import datetime as dt
import asyncio

# from src.main import tree
from src.translator import ts
from src.constants.times import JSON_DATE_PAT
from src.constants.color import C
from src.constants.keys import STARTED_TIME_FILE_LOC, MSG_BOT
from src.utils.logging_utils import save_log
from src.utils.file_io import save_file
from src.commands.cmd_create_thread_mt import PartyView


class MaintanceBot(discord.Client):
    def __init__(self, *, intents: discord.Intents, log_lock: asyncio.Lock, **options):
        super().__init__(intents=intents, **options)
        self.tree = None
        self.log_lock = log_lock

    async def setup_hook(self) -> None:
        self.add_view(PartyView())
        print(f"{C.magenta}Persistent Views successfully registered for maintenance mode.{C.default}")

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

        await save_log(
            lock=self.log_lock,
            cmd="bot.BOOTED",
            user=MSG_BOT,
            msg="[info] Bot booted up with maintance mode",
            obj=dt.datetime.now(),
        )  # VAR
