import discord

from translator import ts


def color_decision(t):
    if t:
        return 0x4DD2FF
    return 0xFFA826


# Event Mission
def W_Alerts(alerts, *lang):
    if alerts == False:
        return discord.Embed(
            description=ts.get("general.error-cmd") + ": alert error",
            color=0xFF0000,
        )
    ts.get("general.error-cmd") + ": alert error"

    if alerts is None or alerts == []:
        return discord.Embed(
            description=ts.get("cmd.alerts.desc-none"), color=color_decision(alerts)
        )

    activated_count = len(alerts)
    output_msg = f"# {ts.get('cmd.alerts.title')}: {activated_count}\n\n"

    idx = 1
    for item in alerts:
        dd = item["mission"]  # tmp var
        node = dd["node"]  # node name
        type = dd["type"]  # mission type

        output_msg += f"{idx}. {dd['reward']['asString']}\n".replace(
            "cr", f" {ts.get('cmd.alerts.credit')}"
        )
        output_msg += f"{type} at {node}\n\n"
        idx += 1

    return discord.Embed(description=output_msg, color=color_decision(alerts))
