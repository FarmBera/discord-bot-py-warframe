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
    cmd: str = "NULL",  # cmd or function name
    time: Optional[dt.datetime] = None,  # current time
    user: str = "NULL",  # used user
    guild: str = "NULL",  # used server
    channel: str = "NULL",  # used channel
    msg: str = "NULL",  # msg content
    obj: str = "NULL",  # used objects
):
    """
    New async function to be called by all logs

    Safely executes _save_log_sync (the existing function) in a separate thread using a Lock.
    """
    try:
        loop = asyncio.get_running_loop()

        # 1. wait until acquire Lock
        async with lock:
            # acquired lock
            await loop.run_in_executor(
                None,
                _save_log_sync,
                # args to be passed to _save_log_sync
                type,
                cmd,
                time,
                user,
                guild,
                channel,
                msg,
                str(obj),
            )
    except Exception as e:
        print(
            f"{C.red}[err] Failed to run _save_log_sync in executor: {cmd}{e}{C.default}"
        )


def _save_log_sync(
    type: str = "info",
    cmd: str = "NULL",
    time: Optional[dt.datetime] = None,
    user: str = "NULL",
    guild: str = "NULL",
    channel: str = "NULL",
    msg: str = "NULL",
    obj: str = "NULL",
):
    """The original save_log function"""

    try:  # time conversion
        if time is None:
            time_str = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        else:
            if time.tzinfo is None:
                time = KST.localize(time)
            else:  # convert to KST
                time = time.astimezone(KST)

            # final time conversion
            now_kst_hour = dt.datetime.now(KST).hour
            prop_kst_hour = time.hour

            hour_diff = (now_kst_hour - prop_kst_hour) % 24
            min_diff = min(hour_diff, 24 - hour_diff)

            if min_diff > threshold:
                time_str = (time + dt.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = time.strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        time_str = f"Time convertion ERR > {e}"

    try:
        log_f = open(LOG_FILE_PATH, "a", encoding="UTF-8", newline="")
        wr = csv.writer(log_f)
        wr.writerow([type, user, time_str, cmd, guild, channel, msg, obj])
        log_f.close()
    except Exception as e:
        print(
            f"{C.red}[err] Something wrong with saving file (_save_log_sync) Failed to write to CSV log >> {e}{C.default}"
        )
