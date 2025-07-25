from translator import ts


# 태신 강철의 길 아이템 현황
def W_SteelPathReward(steel, lang):
    if not steel or steel is None:
        return ts.get("general.error-cmd")

    current = steel["currentReward"]
    output_msg: str = f"# Steel Path Reward\n\n"

    output_msg += f"- Current Reward: **{current['name']}** ({current['cost']} cost)\n"

    idx = 0  # 다음주 아이템 계산을 위한 인덱스
    for item in steel["rotation"]:
        # print(item["name"])
        # 현재 아이템과 리스트에 있는 아이템이 같다면
        if item["name"] == current["name"]:
            idx += 1  # 다음 인덱스의 아이템을 가리킴
            if idx >= len(steel["rotation"]):  # index overflow fix
                idx = 0  # reset index

            # 출력
            item = steel["rotation"][idx]
            output_msg += f"- Next Week: *{item['name']}* ({item['cost']} cost)"
            break
        else:
            idx += 1

    # for item in steel:
    #     # item = item["syndicate"]
    #     print(item["syndicate"], item["jobs"])
    # print(output_msg)
    return output_msg
