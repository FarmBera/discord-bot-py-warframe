from translator import ts


def W_Sortie(sortie, lang):
    if not sortie or sortie is None:
        return ts.get("general.error-cmd")

    prefix: str = "cmd.sortie"
    mis_list = sortie["variants"]

    output_msg = f"# {ts.get(f'{prefix}.title')}\n\n"
    output_msg += f"- {ts.get(f'{prefix}.eta')}: {sortie['eta']}\n\n"

    idx = 1
    for item in mis_list:
        output_msg += f"{idx}. {item['missionType']} - {item['node']}\n"
        output_msg += f"{item['modifier']}\n\n"
        idx += 1

    return output_msg
