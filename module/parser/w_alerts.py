# Event Mission
def W_Alerts(d):
    # skip if data is empty
    if not d or d is None:
        return False

    # activated mission count
    activated_count = len(d)
    output_msg = f"## Activated Alert: {activated_count}\n\n"

    # process missions
    front_num = 1
    for item in d:
        dd = item["mission"]  # tmp var
        node = dd["node"]  # node name
        type = dd["type"]  # mission type

        # write output text
        output_msg += f"{front_num}. {type} - {node}\n"
        output_msg += f"- reward: **{dd['reward']['asString']}**\n\n".replace(
            "cr", " Credit"
        )
        front_num += 1

    return output_msg
