from translator import ts


# 태신 강철의 길 아이템 현황
def W_SteelPathReward(steel, *lang):
    if steel == False:
        return ts.get("general.error-cmd")

    if steel is None:
        return None

    pf: str = "cmd.steel-path-reward"

    current = steel["currentReward"]
    output_msg: str = f"# {ts.get(f'{pf}.title')}\n\n"

    output_msg += f"- {ts.get(f'{pf}.curr-reward')}: **{current['name']}** ({current['cost']} {ts.get(f'{pf}.cost')})\n"

    # calculate next week item
    idx = 0
    for item in steel["rotation"]:
        # next week item
        if item["name"] == current["name"]:
            idx += 1
            if idx >= len(steel["rotation"]):  # fix index overflow
                idx = 0

            # output
            item = steel["rotation"][idx]
            output_msg += (
                f"- {ts.get(f'{pf}.next')}: *{item['name']}* ({item['cost']} cost)"
            )
            break
        else:
            idx += 1

    return output_msg
