import csv
import datetime as dt

from text import log_file_path
from module.color import color


# save log into file
def save_log(
    cmd: str,  # cmd or function name
    time=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))),  # current time
    user: str = "NULL",  # used user
    guild: str = "NULL",  # used server
    channel: str = "NULL",  # used channel
    msg: str = "NULL",  # msg content
    obj: str = "NULL",  # used objects
):
    try:
        log_f = open(log_file_path, "a", encoding="UTF-8", newline="")
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        wr = csv.writer(log_f)
        wr.writerow([user, time, cmd, guild, channel, msg, obj])
        log_f.close()
    except Exception as e:
        print(f"{color['red']}ERR >> {e}{color['default']}")
