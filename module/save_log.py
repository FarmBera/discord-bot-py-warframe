import csv
import datetime as dt

from variables.times import KST
from variables.color import color

LOG_FILE_PATH = "log/logfile.csv"  # VAR


# save log into file
def save_log(
    cmd: str,  # cmd or function name
    time=dt.datetime.now(KST),  # current time
    user: str = "NULL",  # used user
    guild: str = "NULL",  # used server
    channel: str = "NULL",  # used channel
    msg: str = "NULL",  # msg content
    obj: str = "NULL",  # used objects
):
    diff: dt.datetime = dt.datetime.now().hour - time.hour
    threshold: int = 2  # VAR

    if diff > threshold or diff < -threshold:
        time = time + dt.timedelta(hours=9)

    try:
        log_f = open(LOG_FILE_PATH, "a", encoding="UTF-8", newline="")
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        wr = csv.writer(log_f)
        wr.writerow([user, time, cmd, guild, channel, msg, obj])
        log_f.close()
    except Exception as e:
        print(f"{color['red']}ERR >> {e}{color['default']}")
