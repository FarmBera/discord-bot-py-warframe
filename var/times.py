import datetime as dt


JSON_DATE_PAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

KST = dt.timezone(dt.timedelta(hours=9))

alert_times = [
    dt.time(hour=7, minute=0, tzinfo=KST),
    # dt.time(hour=7, minute=30, tzinfo=KST),
    # dt.time(hour=9, minute=0, tzinfo=KST),
]


def time_calculate_with_curr(time_data: str) -> str:
    t = dt.datetime.strptime(time_data, JSON_DATE_PAT) - (
        dt.datetime.now() - dt.timedelta(hours=9)
    )
    h, r = divmod(t.seconds, 3600)
    m = divmod(r, 60)
    return f"{'' if h == 0 else f'{h}h '}{m[0]}m"


def time_format(t) -> str:
    """
    lang == 'ko'
    """
    h, r = divmod(t.seconds, 3600)
    m = divmod(r, 60)
    return f"{'' if h == 0 else f'{h}시간 '}{m[0]}분"
