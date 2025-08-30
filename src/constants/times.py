import datetime as dt


JSON_DATE_PAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

KST = dt.timezone(dt.timedelta(hours=9))

alert_times = [
    dt.time(hour=7, minute=0, tzinfo=KST),
    # dt.time(hour=7, minute=30, tzinfo=KST),
    # dt.time(hour=9, minute=0, tzinfo=KST),
]
