import datetime as dt
from src.translator import language as lang, ts
from src.constants.times import JSON_DATE_PAT

D: str = ts.get(f"time.day")
H: str = ts.get(f"time.hour")
M: str = ts.get(f"time.min")


def time_cal_with_curr(time_data: str) -> str:
    t = dt.datetime.strptime(time_data, JSON_DATE_PAT) - (
        dt.datetime.now() - dt.timedelta(hours=9)
    )
    if t.total_seconds() < 0:
        return "Event End!"

    d = t.days
    h, r = divmod(t.seconds, 3600)
    m = divmod(r, 60)

    output = []
    if d > 0:
        output.append(f"{d}{D}")
    if h > 0:
        output.append(f"{h}{H}")
    output.append(f"{m[0]}{M}")

    return " ".join(output)


def time_format(t) -> str:
    h, r = divmod(t.seconds, 3600)
    m = divmod(r, 60)
    return f"{'' if h == 0 else f'{h}{H} '}{m[0]}{M}"


def txt_length_check(txt):
    threshold: int = 2000

    return txt[0:threshold] if len(txt) > threshold else txt
