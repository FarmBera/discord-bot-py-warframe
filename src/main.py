import discord
import asyncio
import sys
import logging
import sqlite3

from config.TOKEN import TOKEN as BOT_TOKEN
from src.constants.color import C
from src.client.bot_main import DiscordBot
from src.client.bot_maintenance import MaintanceBot

from src.commands.reg_cmd import register_main_commands
from src.commands.reg_cmd_mt import register_maintenance_commands


discord.utils.setup_logging(level=logging.INFO, root=False)

tree = None


# main thread

ERR_COUNT: int = 0

CMD_MAIN: str = "main"
CMD_MAINTENANCE: str = "maintenance"
CMD_EXIT: str = "exit"

EXIT_CMD: list = [CMD_EXIT, "ㄷ턋"]


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

    log_lock = asyncio.Lock()

    # bot_mode = CMD_MAIN  # init mode
    bot_mode = input("Starting Bot Mode > ").lower()
    if not bot_mode:
        print(f"\033[A\rUnknown Mode > '{bot_mode}'\033[A\r")
        bot_mode = CMD_MAIN

    while bot_mode not in EXIT_CMD:
        intents = discord.Intents.default()
        intents.message_content = True
        if bot_mode == CMD_MAIN:
            print(f"{C.cyan}[info] Starting Main Bot...{C.default}", end=" ")  # VAR
            current_bot = DiscordBot(intents=intents, log_lock=log_lock)
            tree = discord.app_commands.CommandTree(current_bot)
            current_bot.tree = tree

            db_conn = sqlite3.connect("db/party.db")
            # db_conn.execute("PRAGMA foreign_keys = ON;")
            db_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS party (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id INTEGER UNIQUE,
                    message_id INTEGER UNIQUE,
                    host_id INTEGER,
                    title TEXT,
                    mission_type TEXT,
                    max_users INTEGER,
                    description TEXT,
                    game_nickname TEXT,
                    status TEXT DEFAULT '모집중',
                    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                    updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
                );
            """
            )
            db_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS participants (
                    party_id INTEGER,
                    user_id INTEGER,
                    user_mention TEXT,
                    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                    updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                    PRIMARY KEY (party_id, user_id),
                    FOREIGN KEY (party_id) REFERENCES party (id) ON DELETE CASCADE
                );
            """
            )
            db_conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_party_updated_at
                AFTER UPDATE ON party
                FOR EACH ROW
                BEGIN
                    UPDATE party SET updated_at = (datetime('now', 'localtime')) WHERE id = OLD.id;
                END;
            """
            )
            db_conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_participants_updated_at
                AFTER UPDATE ON participants
                FOR EACH ROW
                BEGIN
                    UPDATE participants SET updated_at = (datetime('now', 'localtime')) WHERE party_id = OLD.party_id AND user_id = OLD.user_id;
                END;
            """
            )
            db_conn.commit()
            current_bot.db = db_conn

            await register_main_commands(tree, db_conn)

        elif bot_mode == CMD_MAINTENANCE:
            print(f"{C.magenta}Starting Maintenance Bot...{C.default}", end=" ")  # VAR
            current_bot = MaintanceBot(intents=intents, log_lock=log_lock)
            tree = discord.app_commands.CommandTree(current_bot)
            current_bot.tree = tree
            await register_maintenance_commands(tree)

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
            if new_mode not in EXIT_CMD:  # VAR
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

        if bot_mode not in EXIT_CMD:  # VAR
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
        ERR_COUNT += 1
        print(f"Continuously Error #{ERR_COUNT} >> {e}")
        if ERR_COUNT > 20:
            exit()
