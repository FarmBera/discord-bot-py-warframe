import discord
import asyncio
import sys
import logging

from config.TOKEN import TOKEN as BOT_TOKEN
from src.constants.color import C
from src.client.bot_main import DiscordBot
from src.client.bot_maintenance import MaintanceBot

from commands.reg_cmd import register_main_commands
from commands.reg_cmd_mt import register_maintenance_commands


discord.utils.setup_logging(level=logging.INFO, root=False)

tree = None


# main thread

ERR_COUNT: int = 0


async def console_input_listener() -> None:
    """
    wait for console input and returns the specified keyword when it is entered.
    """
    while True:
        cmd = await asyncio.to_thread(sys.stdin.readline)
        cmd = cmd.strip().lower()

        if cmd in ["maintenance", "main", "exit"]:
            print(f"[info] Console input detected! '{cmd}'")  # VAR
            return cmd


async def main_manager() -> None:
    """
    manage bot state, and switch bot status depends on console input
    """
    global tree

    bot_mode = "main"  # init mode

    while bot_mode != "exit":
        intents = discord.Intents.default()
        intents.message_content = True
        if bot_mode == "main":
            print(f"{C.cyan}[info] Starting Main Bot...{C.default}", end=" ")  # VAR
            current_bot = DiscordBot(intents=intents)
            current_bot.tree = discord.app_commands.CommandTree(current_bot)
            await register_main_commands(tree)

        elif bot_mode == "maintenance":
            print(f"{C.magenta}Starting Maintenance Bot...{C.default}", end=" ")  # VAR
            current_bot = MaintanceBot(intents=intents)
            tree = discord.app_commands.CommandTree(current_bot)
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
            if new_mode != "exit":  # VAR
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

        if bot_mode != "exit":  # VAR
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
