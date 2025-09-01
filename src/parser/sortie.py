from src.translator import ts
from src.utils.formatter import time_cal_with_curr


def w_sortie(sortie):
    if not sortie:
        return ts.get("general.error-cmd")

    prefix: str = "cmd.sortie"
    mis_list = sortie["variants"]

    output_msg = f"# {ts.get(f'{prefix}.title')}\n\n"

    output_msg += f"- {ts.get(f'{prefix}.eta')}: "
    output_msg += f"{time_cal_with_curr(sortie['expiry'])}\n\n"

    idx = 1
    for item in mis_list:
        output_msg += f"{idx}. **{ts.trs(item['missionType'])}** "
        output_msg += f"at {item['node']} - {item['modifier']}\n"
        idx += 1

    return output_msg
