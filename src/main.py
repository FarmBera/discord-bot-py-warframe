import discord
import asyncio
import sys
import logging
import sqlite3
import traceback

log_lock = asyncio.Lock()

from config.config import language as lang, Lang
from config.TOKEN import TOKEN as BOT_TOKEN
from db.query import *
from src.constants.color import C
from src.constants.keys import DB_NAME
from src.translator import ts
from src.client.bot_main import DiscordBot
from src.client.bot_maintenance import MaintanceBot

from src.commands.reg_cmd import (
    register_main_cmds,
    register_sub_cmds,
    register_ko_cmds,
)
from src.commands.reg_cmd_mt import (
    register_maintenance_cmds,
    register_mt_sub_cmds,
    register_mt_ko_cmds,
)


discord.utils.setup_logging(level=logging.INFO, root=False)

tree = None

# main thread

ERR_COUNT: int = 0

CMD_MAIN: str = "main"
CMD_MAINTENANCE: str = "maintenance"
CMD_EXIT: str = "exit"

EXIT_CMD: list = [CMD_EXIT, "ㄷ턋", "멱ㅓ"]


async def console_input_listener() -> None:
    """
    wait for console input and returns the specified keyword when it is entered.
    """
    while True:
        cmd = await asyncio.to_thread(sys.stdin.readline)
        cmd = cmd.strip().lower()

        if cmd in [CMD_MAIN, CMD_MAINTENANCE] + EXIT_CMD:
            print(f"[info] Console input detected! '{cmd}'")  # VAR
            return cmd
        else:
            print(f"\033[A\rUnknown Command > '{cmd}'")


async def main_manager() -> None:
    """
    manage bot state, and switch bot status depends on console input
    """
    global tree

    # bot_mode = CMD_MAIN  # init mode
    bot_mode = input("Starting Bot Mode > ").lower()
    if not bot_mode:
        print(
            f"\033[A\r{C.yellow}Unknown Mode > '{C.red}{bot_mode}{C.yellow}' / setup default mode: {C.cyan}`main`{C.default}"
        )
        bot_mode = CMD_MAIN

    while bot_mode not in EXIT_CMD:
        intents = discord.Intents.default()
        intents.message_content = True
        if bot_mode == CMD_MAIN:
            print(f"{C.cyan}[info] Starting Main Bot...{C.default}", end=" ")  # VAR
            current_bot = DiscordBot(intents=intents, log_lock=log_lock)
            tree = discord.app_commands.CommandTree(current_bot)
            current_bot.tree = tree

            @tree.error
            async def on_app_command_error(
                interact: discord.Interaction,
                error: discord.app_commands.AppCommandError,
            ):
                if isinstance(error, discord.app_commands.CommandOnCooldown):
                    pf = "cmd.err-cooldown."
                    embed = discord.Embed(
                        title=ts.get(f"{pf}title"),
                        description=ts.get(f"{pf}desc").format(
                            time=f"{error.retry_after:.0f}"
                        ),
                        color=0xFF0000,
                    )
                    await interact.response.send_message(embed=embed, ephemeral=True)
                else:  # other type of error
                    print(f"Unhandled app command error: {error}")

            db_conn = sqlite3.connect(f"db/{DB_NAME}.db")
            # db_conn.execute("PRAGMA foreign_keys = ON;")
            db_conn.execute("PRAGMA journal_mode=WAL;")
            db_conn.execute(CREATE_TABLE_PARTY)
            db_conn.execute(CREATE_TABLE_PARTICIPANTS)
            db_conn.execute(CREATE_TABLE_TRADES)
            db_conn.execute(CREATE_TRIGGER_PARTY)
            db_conn.execute(CREATE_TRIGGER_PARTICIPANTS)
            db_conn.execute(CREATE_TRIGGER_TRADES)
            db_conn.commit()
            current_bot.db = db_conn

            await register_main_cmds(tree, db_conn)
            if lang == Lang.KO:
                await register_ko_cmds(tree, db_conn)
            else:
                await register_sub_cmds(tree, db_conn)

        elif bot_mode == CMD_MAINTENANCE:
            print(f"{C.magenta}Starting Maintenance Bot...{C.default}", end=" ")  # VAR
            current_bot = MaintanceBot(intents=intents, log_lock=log_lock)
            tree = discord.app_commands.CommandTree(current_bot)
            current_bot.tree = tree

            await register_maintenance_cmds(tree)
            if lang == Lang.KO:
                await register_mt_ko_cmds(tree)
            else:
                await register_mt_sub_cmds(tree)

        else:
            break

        print("Creating Task...")
        # create execution task: bot run / console input handler
        bot_task = asyncio.create_task(current_bot.start(BOT_TOKEN))
        console_task = asyncio.create_task(console_input_listener())

        # wait until at least one of the two tasks is completed.
        done, pending = await asyncio.wait(
            [bot_task, console_task], return_when=asyncio.FIRST_COMPLETED
        )

        # verify the completed task is a console input task
        if console_task in done:
            # get input command
            new_mode = console_task.result()
            if new_mode not in EXIT_CMD:
                print(f"Switching Bot... '{bot_mode}' into '{new_mode}'")  # VAR
            bot_mode = new_mode
        else:
            print(
                f"{C.red}[err] The Bot has unexpectedly terminated!{C.default}"
            )  # VAR

            for i in range(5, 0, -1):
                print(
                    f"{C.red}[err] Unexpect Error. Retry in {i}s ",
                    end="\r",
                    flush=True,
                )  # VAR
                await asyncio.sleep(1.0)
            print(f"{C.yellow}Retrying #{ERR_COUNT}{C.default}")
            # bot_mode = "exit"  # exit loop

        # quit currently running bot & skip to next loop
        print(f"{C.default}[info] Terminating current bot...")  # VAR
        await current_bot.close()
        for task in pending:  # cancel remaining task
            task.cancel()

        if bot_mode not in EXIT_CMD:
            for i in range(4, 0, -1):
                print(
                    f"{C.yellow}[info] Executes in {i}s  ",
                    end="\r",
                    flush=True,
                )  # VAR
                await asyncio.sleep(0.98)

    print("[info] Exiting Program...")  # VAR


if __name__ == "__main__":
    try:
        asyncio.run(main_manager())
    except KeyboardInterrupt:
        print(f"\n{C.yellow}Force Quitted!")  # VAR
    except Exception as e:
        print(C.red, traceback.format_exc(), sep="")
        ERR_COUNT += 1
        print(f"Continuously Error #{ERR_COUNT} >> {e}")
        if ERR_COUNT > 20:
            exit()
