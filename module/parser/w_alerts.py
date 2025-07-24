# Event Mission
def W_Alerts(alerts):
    # skip if data is empty
    if not alerts or alerts is None:
        return False

    # activated mission count
    activated_count = len(alerts)
    output_msg = f"# Activated Alert: {activated_count}\n\n"

    # process missions
    idx = 1
    for item in alerts:
        dd = item["mission"]  # tmp var
        node = dd["node"]  # node name
        type = dd["type"]  # mission type

        # write output text
        output_msg += f"{idx}. {dd['reward']['asString']}\n".replace("cr", " Credit")
        output_msg += f"at {type} - {node}\n\n"
        # output_msg += f"{idx}. {type} - {node}\n"
        # output_msg += f"- reward: **{dd['reward']['asString']}**\n\n".replace("cr", " Credit")
        idx += 1

    return output_msg
