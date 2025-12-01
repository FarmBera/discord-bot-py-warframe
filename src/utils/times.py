import datetime as dt
from zoneinfo import ZoneInfo


JSON_DATE_PAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

KST = ZoneInfo("Asia/Seoul")

alert_times = [
    dt.time(hour=7, minute=0, tzinfo=KST),
    # dt.time(hour=7, minute=30, tzinfo=KST),
    # dt.time(hour=9, minute=0, tzinfo=KST),
]


def timeNow() -> int:
    return int(dt.datetime.now(tz=KST).timestamp())


def timeNowDT() -> dt.datetime:
    return dt.datetime.now(tz=KST)


def unixToDatetime(timestamp: int) -> dt.datetime:
    if timestamp > 10**12:  # ms unit
        return dt.datetime.fromtimestamp(timestamp / 1000)
    else:  # sec unit
        return dt.datetime.fromtimestamp(timestamp)


def convert_remain(unix_timestamp: int | str):
    """
    Calculates the time difference between the current time and a given Unix timestamp, and returns it as a string in the specified format.

    Args:
        unix_timestamp: Unix Timestamp to compare (int or str type)

    Returns:
        string that shows remain time with discord timestamp
        <t:1234567890:R>
    """
    from src.translator import ts

    try:
        ts_str = str(unix_timestamp)

        # convert milliseconds into seconds
        if len(ts_str) == 13:
            ts_int = int(ts_str) // 1000
        else:
            ts_int = int(ts_str)
    except (ValueError, TypeError):
        return "Wrong Timestamp Format"

    return f"<t:{ts_int}:R>"

    # convert into datetime obj
    now_dt = timeNowDT()
    input_dt = dt.datetime.fromtimestamp(ts_int)

    # calculate time diff
    diff = now_dt - input_dt
    if diff.total_seconds() > 0:
        return "`Event End!`"
    time_difference = abs(diff)

    # extract day, hour, minute
    days = time_difference.days
    remaining_seconds = time_difference.seconds
    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60

    output: list = []
    if days > 0:
        output.append(f"{days}{ts.get('time.day')}")
    if hours > 0:
        output.append(f"{hours}{ts.get('time.hour')}")
    if minutes > 0:
        output.append(f"{minutes}{ts.get('time.min')}")

    return " ".join(output)
