import csv
import datetime as dt

from text import log_file_path


# save log into file
def save_log(
    cmd, time=f"{dt.datetime.now()}", user="null", guild="null", channel="null"
):
    log_f = open(log_file_path, "a", encoding="UTF-8", newline="")
    time = (time + dt.timedelta(hours=9)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )  # for UTC+9 Timezone
    # time = (time + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")  # for US(UTC+0) Timezone
    wr = csv.writer(log_f)
    wr.writerow([user, time, cmd, guild, channel])
    log_f.close()
