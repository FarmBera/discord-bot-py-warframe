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
        return "**Event End!**"

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


def time_format(t: dt.timedelta) -> str:
    h, r = divmod(t.seconds, 3600)
    m = divmod(r, 60)
    return f"{'' if h == 0 else f'{h}{H} '}{m[0]}{M}"


def txt_length_check(txt):
    threshold: int = 2000

    return txt[0:threshold] if len(txt) > threshold else txt


def add_space(text: str) -> str:
    """
    Add spaces only at the beginning of consecutive uppercase letters or numbers in the given text.
    Do not add a space before the first letter.

    Args:
        text: string to convert.

    Returns:
        converted new string

    Examples:
        >>> add_space("Plushy2021QTCC")
        'Plushy 2021 QTCC'
        >>> add_space("iPhone17ProMax")
        'i Phone 17 Pro Max'
        >>> add_space("ABC")
        'ABC'
        >>> add_space("")
        ''
    """
    if not text:
        return ""

    result_list = [text[0]]

    # process
    for i in range(1, len(text)):
        current_char = text[i]
        prev_char = text[i - 1]

        is_new_upper_group = current_char.isupper() and not prev_char.isupper()
        is_new_digit_group = current_char.isdigit() and not prev_char.isdigit()
        is_case_change = prev_char.islower() and current_char.isupper()

        if is_new_upper_group or is_new_digit_group or is_case_change:
            result_list.append(" ")

        result_list.append(current_char)

    return "".join(result_list)
