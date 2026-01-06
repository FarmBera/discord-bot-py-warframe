import datetime as dt
from zoneinfo import ZoneInfo
import re

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


def convert_remain(unix_timestamp: int | float | str):
    """
    Calculates the time difference between the current time and a given Unix timestamp, and returns it as a string in the specified format.

    Args:
        unix_timestamp: Unix Timestamp to compare (int or str type)

    Returns:
        string that shows remain time with discord timestamp
        <t:1234567890:R>
    """
    try:
        ts_str = str(int(unix_timestamp))

        # convert milliseconds into seconds
        if len(ts_str) == 13:
            ts_int = int(ts_str) // 1000
        else:
            ts_int = int(ts_str)
    except (ValueError, TypeError):
        # print_test_err("Timestamp Format err")
        return "**Time ERR**"

    return f"<t:{ts_int}:R>"

    # # convert into datetime obj
    # now_dt = timeNowDT()
    # input_dt = dt.datetime.fromtimestamp(ts_int)
    #
    # # calculate time diff
    # diff = now_dt - input_dt
    # if diff.total_seconds() > 0:
    #     return "`Event End!`"
    # time_difference = abs(diff)
    #
    # # extract day, hour, minute
    # days = time_difference.days
    # remaining_seconds = time_difference.seconds
    # hours = remaining_seconds // 3600
    # minutes = (remaining_seconds % 3600) // 60
    #
    # output: list = []
    # if days > 0:
    #     output.append(f"{days}{ts.get('time.day')}")
    # if hours > 0:
    #     output.append(f"{hours}{ts.get('time.hour')}")
    # if minutes > 0:
    #     output.append(f"{minutes}{ts.get('time.min')}")
    #
    # return " ".join(output)


def parseKoreanDatetime(text):
    if not isinstance(text, str):
        return text

    from src.translator import ts

    if text == ts.get(f"cmd.party.pb-departure-none"):
        return None

    now = dt.datetime.now()
    target_date = now

    date_fixed = False
    time_fixed = False

    # parse date

    # yyyy-mm-dd or yyyy-m-d
    ymd_hyphen = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if ymd_hyphen:
        y, m, d = map(int, ymd_hyphen.groups())
        target_date = target_date.replace(year=y, month=m, day=d)
        date_fixed = True

    # yyyy년 m월 d일 (YYYYyear Mmonth Dday)
    if not date_fixed:
        ymd_korean = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", text)
        if ymd_korean:
            y, m, d = map(int, ymd_korean.groups())
            target_date = target_date.replace(year=y, month=m, day=d)
            date_fixed = True

    # 내일, 모레, 주 단위 (tomorrow)
    if not date_fixed:
        if "내일" in text:
            target_date += dt.timedelta(days=1)
            date_fixed = True
        elif "모레" in text or ("내일" in text and "모레" in text):
            target_date += dt.timedelta(days=2)
            date_fixed = True
        elif "글피" in text:
            target_date += dt.timedelta(days=3)
            date_fixed = True

        # 주 단위 요일 (이번주/다음주/다다음주 + 요일) (parse weekly unit)
        week_match = re.search(
            r"(이번|다음|다다음)\s*주\s*([월화수목금토일])요일", text
        )
        if week_match:
            prefix = week_match.group(1)  # 이번, 다음, 다다음 (this week, next week)
            weekday_char = week_match.group(2)  # 월, 화, 수... (Mon, Tue, Wed...)

            # n weeks later (몇 주 뒤)
            week_offset = 0
            if prefix == "다음":
                week_offset = 1
            elif prefix == "다다음":
                week_offset = 2

            # convert weekdays
            weekdays = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
            target_weekday = weekdays[weekday_char]

            # calculate start of the week (Mon)
            current_weekday = now.weekday()
            start_of_this_week = now - dt.timedelta(days=current_weekday)

            # calculate target date
            target_date = (
                start_of_this_week
                + dt.timedelta(days=target_weekday)
                + dt.timedelta(weeks=week_offset)
            )
            date_fixed = True

    # n일 뒤, n일 (in n days, n day)
    if not date_fixed:
        day_offset_match = re.search(r"(\d+)일\s*(뒤|후)", text)
        if day_offset_match:
            days = int(day_offset_match.group(1))
            target_date += dt.timedelta(days=days)
            date_fixed = True
        else:
            # n일
            specific_day_match = re.search(r"(\d+)일", text)
            if specific_day_match:
                day = int(specific_day_match.group(1))
                try:
                    target_date = target_date.replace(day=day)
                    date_fixed = True
                except ValueError:
                    pass

    # parse time

    hour = 0
    minute = 0

    # 15:00
    colon_match = re.search(r"(\d{1,2}):(\d{2})", text)
    if colon_match:
        hour = int(colon_match.group(1))
        minute = int(colon_match.group(2))
        time_fixed = True

    # 3시 30분 (N Hour M minute)
    korean_hour_match = re.search(r"(\d+)\s*시", text)
    if korean_hour_match:
        hour = int(korean_hour_match.group(1))
        time_fixed = True

        korean_min_match = re.search(r"(\d+)\s*분", text)
        if korean_min_match:
            minute = int(korean_min_match.group(1))
        elif "반" in text:
            minute = 30

    # AM/PM correction
    if time_fixed:
        if re.search(r"(오후|저녁|밤)", text) and hour < 12:
            hour += 12
        elif re.search(r"(오전|아침|새벽)", text) and hour == 12:
            hour = 0

    # final combination

    # date fixed, but time not fixed
    if date_fixed and not time_fixed:
        print("TIMEPASS > ", end="")
        target_date = target_date.replace(
            hour=now.hour, minute=now.minute, second=0, microsecond=0
        )

    # apply time (when time fixed)
    if time_fixed:
        try:
            target_date = target_date.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
        except ValueError:
            return None

    return target_date
