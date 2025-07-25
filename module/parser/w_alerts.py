from translator import ts


# Event Mission
def W_Alerts(alerts, lang):
    # error check
    if alerts == False:
        return ts.get("general.error-cmd") + ": alert error"

    # skip if data is empty
    if alerts is None:
        return None

    # activated mission count
    activated_count = len(alerts)
    output_msg = f"# {ts.get('cmd.alerts.title')}: {activated_count}\n\n"

    # process missions
    idx = 1
    for item in alerts:
        dd = item["mission"]  # tmp var
        node = dd["node"]  # node name
        type = dd["type"]  # mission type

        # write output text
        output_msg += f"{idx}. {dd['reward']['asString']}\n".replace(
            "cr", ts.get("cmd.alerts.credit")
        )
        output_msg += f"{type} at {node}\n\n"
        # output_msg += f"{idx}. {type} - {node}\n"
        # output_msg += f"- reward: **{dd['reward']['asString']}**\n\n".replace("cr", " Credit")
        idx += 1

    return output_msg
