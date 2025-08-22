import datetime as dt

from translator import ts
from variables.keys import cal_item
from module.get_emoji import get_emoji


def redef(prop):
    try:
        return cal_item[prop]
    except:
        return prop


def w_calendar(cal, typ, *lang) -> str:
    if cal == False:
        ts.get("general.error-cmd")

    if cal is None:
        return None

    output_msg: str = f"# {ts.get('cmd.calendar.title')} ({typ if typ else ''})\n\n"

    type_all = ts.get("cmd.calendar.choice-all")
    type_todo = ts.get("cmd.calendar.choice-to-do")
    type_prize = ts.get("cmd.calendar.choice-prize")
    type_over = ts.get("cmd.calendar.choice-over")

    for item in cal[0]["days"]:
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
            output_msg += (
                f"{dt.date(1999, 1, 1) + dt.timedelta(days=item['day'] - 1)} "  # VAR
            )
            # output_msg += f"Day {item['day']} "
            output_msg += t[0]["type"]
            output_msg += "".join(output)
            output_msg += "\n\n"

    return output_msg
