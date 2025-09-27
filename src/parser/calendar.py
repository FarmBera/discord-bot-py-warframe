import datetime as dt

from src.translator import ts
from src.constants.keys import cal_item
from src.constants.times import JSON_DATE_PAT
from src.utils.emoji import get_emoji
from src.utils.return_err import err_text


def redef(prop):
    try:
        return cal_item[prop]
    except:
        return prop


def convert_365d(date) -> str:
    return str(dt.datetime.strptime(date, JSON_DATE_PAT).timetuple().tm_yday)


def convert_simple_date(date) -> str:
    return dt.datetime.strftime(dt.datetime.strptime(date, JSON_DATE_PAT), "%Y-%m-%d")


def w_calendar(cal, typ) -> str:
    if not cal:
        return err_text("calendar")

    output_msg: str = f"# {ts.get('cmd.calendar.title')} ({typ if typ else ''})\n\n"

    type_all = ts.get("cmd.calendar.choice-all")
    type_todo = ts.get("cmd.calendar.choice-to-do")
    type_prize = ts.get("cmd.calendar.choice-prize")
    type_over = ts.get("cmd.calendar.choice-over")

    for item in cal["days"]:
        t = item["events"]

        if len(t) <= 0:  # empty objects
            continue

        output = []

        for jtem in t:
            e_type = jtem["type"]

            # to do
            if (typ in [type_all, type_todo]) and e_type == "To Do":
                output.append(f": {redef(jtem['challenge']['description'])}")

            # big prize
            elif (typ in [type_all, type_prize]) and e_type == "Big Prize!":
                tt = jtem["reward"]
                output.append(f"\n- {get_emoji(tt)} {redef(tt)}")

            # override
            elif (typ in [type_all, type_over]) and e_type == "Override":
                title = jtem["upgrade"]["title"]
                description = jtem["upgrade"]["description"]
                override_info = f"\n- {title}: {description}"
                output.append(override_info)

        if output:
            o_date = item["date"]
            output_msg += f"Day {convert_365d(o_date)}"
            output_msg += f" - {t[0]['type']} ({convert_simple_date(o_date)})"
            output_msg += "".join(output)
            output_msg += "\n\n"

    return output_msg
