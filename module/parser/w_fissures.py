def W_Fissures(fissures):
    def PrintingLayout(item):
        # return f"{item['missionType']} - {item['enemy']} {'[Steel Path]' if item['isHard'] else ''}\n{item['tier']} Fissure\n{item['node']}\n{item['eta']} remain\n"
        return f"{item['missionType']} - {item['tier']} Fissure {'[Steel Path]' if item['isHard'] else ''}\n{item['node']} - {item['enemy']}\n{item['eta']} remain\n"

    normal = []  # 일반 성유물 노드
    steel_path = []  # 강길 성유물 노드
    fav_fissure = []  # 즐겨찾는 성유물 노드 저장
    # 즐겨찾는 성유물 미션 목록
    fav = ["Extermination", "Rescue", "Capture"]  # , "Excavation"]
    # 제외 할 성유물 티어 종류
    # exception_tier = ["Requiem"]  # "Axi"]  #

    for item in fissures:
        # 강철의 길 구분
        if item["isHard"] == True:
            steel_path.append(item)
        else:  # 일반 미션 (강길 아닌)
            normal.append(item)

        # 즐격찾는 미션 타입 있으면 별도 알림
        if (
            item["missionType"]
            in fav
            # or (item["node"] == "Circulus (Lua)")
            # or (item["tier"] == "Omnia")
        ):
            fav_fissure.append(item)

    # # 일반 미션에 있는 모든 미션 출력
    # for item in normal:
    #     print(PrintingLayout(item))

    # # 강길 미션 모두 출력
    # for item in steel_path:
    #     print(PrintingLayout(item))

    # 즐겨찾기 미션 처리 & 출력
    # idx = 0
    # for item in fav_fissure:
    #     for_flag = True
    #     for jtem in exception_tier:
    #         if item["tier"] in jtem:
    #             for_flag = False
    #             fav_fissure.pop(idx)
    #     if not (for_flag):
    #         continue
    #     idx += 1

    # def ExceptItems(item_list: list, except_list: list, key: str):
    #     idx = 0
    #     for item in item_list:
    #         for_flag = True
    #         for jtem in except_list:
    #             if item[key] in jtem:
    #                 for_flag = False
    #                 item_list.pop(idx)
    #         if not (for_flag):
    #             continue
    #         idx += 1
    #     return item_list

    # fav_fissure = ExceptItems(fav_fissure, exception_tier, "tier")
    for item in fav_fissure:
        print(PrintingLayout(item))
