import datetime as dt


JSON_DATE_PAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

KST = dt.timezone(dt.timedelta(hours=9))

alert_times = [
    dt.time(hour=7, minute=0, tzinfo=KST),
    # dt.time(hour=7, minute=30, tzinfo=KST),
    # dt.time(hour=9, minute=0, tzinfo=KST),
]


def timeNow() -> int:
    return int(dt.datetime.now().timestamp())


def unixToDatetime(timestamp: int) -> dt.datetime:
    if timestamp > 10**12:  # 밀리초(ms) 단위로 판단
        return dt.datetime.fromtimestamp(timestamp / 1000)
    else:  # 초(s) 단위로 판단
        return dt.datetime.fromtimestamp(timestamp)


def convert_remain(unix_timestamp):
    """
    Calculates the time difference between the current time and a given Unix timestamp, and returns it as a string in the specified format.

    Args:
        unix_timestamp: Unix Timestamp to compare (int or str type)

    Returns:
        string that shows time diff
        (ex: "3d 4h 30m" or "4h 30m")
    """
    try:
        ts_str = str(unix_timestamp)

        # convert milliseconds into seconds
        if len(ts_str) == 13:
            ts = int(ts_str) / 1000
        else:
            ts = int(ts_str)

    except (ValueError, TypeError):
        return "Wrong Timestamp Format"

    # convert into datetime obj
    now_dt = dt.datetime.now()
    input_dt = dt.datetime.fromtimestamp(ts)

    # calculate time diff
    time_difference = abs(now_dt - input_dt)

    # extract day, hour, minute
    days = time_difference.days
    remaining_seconds = time_difference.seconds
    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60

    output: list = []
    if days > 0:
        output.append(f"{days}d")
    if hours > 0:
        output.append(f"{hours}h")
    if minutes > 0:
        output.append(f"{minutes}m")

    return " ".join(output) if output else "Event End!"
