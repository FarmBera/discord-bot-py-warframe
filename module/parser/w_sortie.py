def W_Sortie(sortie):
    mis_list = sortie["variants"]
    # mis_list = json.dumps(mis_list, ensure_ascii=False)
    # print(mis_list)
    output_msg = f"# Today's Sortie\n\n"
    output_msg += f"- ETA: {sortie['eta']}\n\n"

    idx = 1
    for item in mis_list:
        output_msg += f"{idx}. {item['missionType']} - {item['node']}\n"
        output_msg += f"{item['modifier']}\n\n"
        idx += 1

    # print(output_msg)
    return output_msg
