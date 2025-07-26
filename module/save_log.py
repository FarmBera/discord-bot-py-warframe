import csv
import datetime as dt

from text import log_file_path
from module.color import color


# save log into file
def save_log(
    cmd: str,  # 명령어 or 로그 적는 함수 이름
    time=dt.datetime.now(),  # 현재 시간
    user: str = "NULL",  # 생성한 사용자
    guild: str = "NULL",  # 사용한 서버
    channel: str = "NULL",  # 사용한 채널
    msg: str = "NULL",  # 메시지 내용
    obj: str = "NULL",  # 사용된 오브젝트
):
    try:
        log_f = open(log_file_path, "a", encoding="UTF-8", newline="")
        time = (time + dt.timedelta(hours=9)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # for UTC+9 Timezone
        # time = (time + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")  # for US(UTC+0) Timezone
        wr = csv.writer(log_f)
        wr.writerow([user, time, cmd, guild, channel, msg, obj])
        log_f.close()
    except Exception as e:
        print(f"{color['red']}ERR >> {e}{color['default']}")
