import discord
import datetime as dt
import asyncio

# from src.main import tree
from src.translator import ts
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.utils.times import timeNowDT
from src.utils.logging_utils import save_log
from src.utils.db_helper import transaction
from src.commands.cmd_maintenance import PartyView, TradeView


class MaintanceBot(discord.Client):
    def __init__(self, *, intents: discord.Intents, db, **options):
        super().__init__(intents=intents, **options)
        self.db = db

    async def setup_hook(self) -> None:
        self.add_view(PartyView())
        self.add_view(TradeView())
        await self.load_extension(f"src.cogs.maintenance")
        print(
            f"{C.magenta}Persistent Views successfully registered for maintenance mode.{C.default}"
        )

    async def on_ready(self):
        print(f"{C.blue}[info] {C.yellow}{ts.get('start.sync')}...{C.default}", end="")
        await self.wait_until_ready()
        if self.tree:
            await self.tree.sync()
        await self.change_presence(
            status=discord.Status.do_not_disturb,
            activity=discord.Game(ts.get("maintenance.bot-status-msg")),
        )
        print(
            f"{C.cyan}{ts.get('start.final')} <<{C.white}{self.user}{C.cyan}>>{C.default}"
        )
        async with transaction(self.db) as cursor:
            await cursor.execute(
                "UPDATE vari SET value = CURRENT_TIMESTAMP() WHERE name = 'start_time'"
            )

        print(f"{C.magenta}[info] Bot is on Maintance Mode!{C.default}")

        await save_log(
            pool=self.db,
            cmd="bot.BOOTED",
            user=MSG_BOT,
            msg="[info] Bot booted up with maintance mode",
            obj=timeNowDT(),
        )  # VAR
