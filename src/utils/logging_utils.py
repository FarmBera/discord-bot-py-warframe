import discord
import csv
import datetime as dt
import asyncio
import logging
from typing import Optional

from src.utils.times import KST
from src.constants.color import C
from src.constants.keys import LOG_FILE_PATH

# csv file header
CSV_HEADER = ["type", "user", "time", "cmd", "guild", "channel", "msg", "obj"]

threshold = 2  # VAR
TIMEOUT_SECONDS: float = 30.0  # max stanby time (Lock + file I/O)

# A storage mechanism that prevents running log operations from being lost due to garbage collection (GC)
background_log_tasks = set()


async def init_csv_log_async(lock: asyncio.Lock):
    """initialize csv file"""
    async with lock:
        try:
            with open(LOG_FILE_PATH, "x", encoding="UTF-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADER)
        except FileExistsError:
            pass
        except Exception as e:
            print(f"{C.red}[err] Failed to initialize CSV file: {e}{C.default}")


async def save_log(
    lock: asyncio.Lock,
    type: str = "info",
    cmd: str = "NULL",
    time: Optional[dt.datetime] = None,
    user: str = "NULL",
    guild: str = "NULL",
    channel: str = "NULL",
    msg: str = "NULL",
    obj: str = "NULL",
    interact: discord.Interaction = None,
):
    """
    [Non-blocking Wrapper]
    Externally, it is called as await save_log(...), but internally, it creates a background task and
    returns immediately to prevent the bot's main thread from blocking.
    """

    # Creating a coroutine to perform the actual work (Fire-and-Forget)
    task = asyncio.create_task(
        _process_log_background(
            lock, type, cmd, time, user, guild, channel, msg, obj, interact
        )
    )

    # [GC Prevention Pattern] Maintain Reference to Task
    background_log_tasks.add(task)

    # When a task completes (whether successful or not), remove it from the set to free up memory.
    task.add_done_callback(background_log_tasks.discard)

    return  # return immediately


async def _process_log_background(
    lock: asyncio.Lock,
    type: str,
    cmd: str,
    time: Optional[dt.datetime],
    user: str,
    guild: str,
    channel: str,
    msg: str,
    obj: str,
    interact: discord.Interaction,
):
    """
    [Internal Logic]
    Asynchronous functions handling actual log storage
    Intermediate manager function responsible for timeout & error handling
    """
    try:
        loop = asyncio.get_running_loop()
        # if task delayed, force terminate
        await asyncio.wait_for(
            _execute_logging(
                loop, lock, type, cmd, time, user, guild, channel, msg, obj, interact
            ),
            timeout=TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        print(  # print warning msg
            f"{C.red}[warn] Log Dropped (Timeout {TIMEOUT_SECONDS}s): {type}{cmd}{C.default}"
        )
    except Exception as e:  # other unexpect error
        print(f"{C.red}[err] Async Log Task Error: {e}{C.default}")
        # traceback.print_exc()  # for debug


async def _execute_logging(loop, lock, *args):
    """
    Acquire the lock and execute the synchronous function (_save_log_sync) in the thread pool
    """
    async with lock:
        await loop.run_in_executor(None, _save_log_sync, *args)


def _save_log_sync(
    type: str,
    cmd: str,
    time: Optional[dt.datetime],
    user: str,
    guild: str,
    channel: str,
    msg: str,
    obj: str,
    interact: discord.Interaction,
):
    """
    [Existing Function]
    File Writing Logic (No changes, remains unchanged)
    Synchronous functions that perform actual file I/O
    """
    try:
        if interact is not None:
            time = interact.created_at
            user = f"{interact.user.display_name}//{interact.user.global_name}//{interact.user.name}//{interact.user.id}"
            guild = f"{interact.guild.name}//{interact.guild_id}"
            channel = f"{interact.channel.name}//{interact.channel_id}"

        # time convertion logic
        if time is None:
            time_str = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        else:
            if time.tzinfo is None:
                time = KST.localize(time)
            else:
                time = time.astimezone(KST)

            now_kst_hour = dt.datetime.now(KST).hour
            prop_kst_hour = time.hour

            hour_diff = (now_kst_hour - prop_kst_hour) % 24
            min_diff = min(hour_diff, 24 - hour_diff)

            if min_diff > threshold:
                time_str = (time + dt.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = time.strftime("%Y-%m-%d %H:%M:%S")

        with open(LOG_FILE_PATH, "a", encoding="UTF-8", newline="") as log_f:
            wr = csv.writer(log_f)
            wr.writerow([type, user, time_str, cmd, guild, channel, msg, obj])
    except Exception as e:
        # want to raise an error to a higher level, use raise e.
        print(f"{C.red}[err] _save_log_sync Failed >> {e}{C.default}")
