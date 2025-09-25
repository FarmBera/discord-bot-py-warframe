import discord
from src.translator import ts
from src.utils.return_err import err_embed


def color_decision(t):
    return 0x4DD2FF if t else 0xFFA826


def w_alerts(alerts) -> discord.Embed:
    if alerts == []:  # empty list
        return discord.Embed(
            description=ts.get("cmd.alerts.desc-none"), color=color_decision(alerts)
        )

    if not alerts:
        return err_embed("alert obj error")

    activated_count = len(alerts)
    output_msg = f"# {ts.get('cmd.alerts.title')}: {activated_count}\n\n"

    idx = 1
    for item in alerts:
        dd = item["mission"]  # tmp var
        node = dd["node"]  # node name
        type = dd["type"]  # mission type

        # TODO: format
        output_msg += f"{idx}. {dd['reward']['items']} + {dd['reward']['credits']} {ts.get('cmd.alerts.credit')}\n"
        output_msg += f"{type} at {node}\n\n"
        idx += 1

    return discord.Embed(description=output_msg, color=color_decision(alerts))
