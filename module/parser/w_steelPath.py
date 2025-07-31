from translator import ts


# 태신 강철의 길 아이템 현황
def W_SteelPathReward(steel, *lang):
    if steel == False:
        return ts.get("general.error-cmd")

    if steel is None:
        return None

    current = steel["currentReward"]
    output_msg: str = f"# Steel Path Reward\n\n"

    output_msg += f"- Current Reward: **{current['name']}** ({current['cost']} cost)\n"

    # calculate next week item
    idx = 0
    for item in steel["rotation"]:
        # next week item
        if item["name"] == current["name"]:
            idx += 1
            if idx >= len(steel["rotation"]):  # index overflow fix
                idx = 0

            # output
            item = steel["rotation"][idx]
            output_msg += f"- Next Week: *{item['name']}* ({item['cost']} cost)"
            break
        else:
            idx += 1

    return output_msg
