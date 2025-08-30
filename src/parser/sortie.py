from translator import ts
from var.times import time_calculate_with_curr


def w_sortie(sortie):
    if not sortie:
        return ts.get("general.error-cmd")

    prefix: str = "cmd.sortie"
    mis_list = sortie["variants"]

    output_msg = f"# {ts.get(f'{prefix}.title')}\n\n"
    output_msg += (
        f"- {ts.get(f'{prefix}.eta')}: {time_calculate_with_curr(sortie['expiry'])}\n\n"
    )

    idx = 1
    for item in mis_list:
        # output_msg += f"{idx}. {item['missionType']} - {item['node']}\n"
        output_msg += f"{idx}. **{item['missionType']}**"
        output_msg += f" at {item['node']} - "
        output_msg += f"{item['modifier']}\n"
        idx += 1

    return output_msg
