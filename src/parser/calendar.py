import datetime as dt

from src.translator import ts
from src.utils.emoji import get_emoji
from src.utils.return_err import err_text
from src.utils.data_manager import getLanguage

cal_type: dict = {
    "CET_CHALLENGE": "To Do",
    "CET_REWARD": "Big Prize",
    "CET_UPGRADE": "Override",
}


def w_calendar(cal, typ) -> str:
    if not cal:
        return err_text("calendar")

    output_msg: str = f"# {ts.get('cmd.calendar.title')} ({typ if typ else ''})\n\n"

    type_all = ts.get("cmd.calendar.choice-all")
    type_todo = ts.get("cmd.calendar.choice-to-do")
    type_prize = ts.get("cmd.calendar.choice-prize")
    type_over = ts.get("cmd.calendar.choice-over")

    for item in cal[0]["Days"]:
        t = item["events"]

        if len(t) <= 0:  # empty objects
            continue

        output = []

        for jtem in t:
            e_type = jtem["type"]

            # to do
            if (typ in [type_all, type_todo]) and e_type == "CET_CHALLENGE":  # var
                output.append(f": {getLanguage(jtem['challenge'],'desc')}")

            # big prize
            elif (typ in [type_all, type_prize]) and e_type == "CET_REWARD":  # var
                tt = jtem["reward"]
                output.append(f"\n- {get_emoji(tt)} {getLanguage(tt)}")

            # override
            elif (typ in [type_all, type_over]) and e_type == "CET_UPGRADE":  # var
                desc = jtem["upgrade"]
                override_info = (
                    f"\n- **{getLanguage(desc)}**: {getLanguage(desc,'desc')}"
                )
                output.append(override_info)

        if output:
            o_date = item["day"]
            output_msg += f"Day {o_date}"
            output_msg += f" - {cal_type.get(t[0]['type'])}"
            output_msg += "".join(output)
            output_msg += "\n\n"

    return output_msg
