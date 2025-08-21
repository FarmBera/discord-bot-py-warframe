import csv
import datetime as dt

from variables.times import KST
from variables.color import color

LOG_FILE_PATH = "log/logfile.csv"  # VAR
threshold = 2  # VAR


# save log into file
def save_log(
    type: str = "info",
    cmd: str = "NULL",  # cmd or function name
    time=None,  # current time
    user: str = "NULL",  # used user
    guild: str = "NULL",  # used server
    channel: str = "NULL",  # used channel
    msg: str = "NULL",  # msg content
    obj: str = "NULL",  # used objects
):
    # convert times
    try:
        if time is None:
            time = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        else:
            now = dt.datetime.now(KST).hour
            prop = time.hour

            hour_diff = (now - prop) % 24
            min_diff = min(hour_diff, 24 - hour_diff)

            if min_diff > threshold:
                time = (time + dt.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        time = f"Time convertion ERR > {e}"

    # write to file
    try:
        log_f = open(LOG_FILE_PATH, "a", encoding="UTF-8", newline="")
        wr = csv.writer(log_f)
        wr.writerow([type, user, time, cmd, guild, channel, msg, obj])
        log_f.close()
    except Exception as e:
        print(f"{color['red']}ERR with saving file (save_log) >> {e}{color['default']}")
