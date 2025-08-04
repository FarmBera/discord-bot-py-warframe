import discord

from translator import ts


def color_decision(t):
    for item in t:
        if item["active"]:
            return 0x4DD2FF
    return 0xFFA826


def W_VoidTraders(trader, *lang):
    if trader == False:
        return discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000)

    if trader is None:
        return None

    idx = 1
    length = len(trader)
    prefix: str = "cmd.void-traders"

    output_msg: str = f"# {ts.get(f'{prefix}.title')}\n\n"

    for item in trader:
        if length >= 2:
            output_msg += (
                f"{idx}. {ts.get(f'{prefix}.tdr-name')}: {item['character']}\n\n"
            )
            idx += 1
        else:
            output_msg += f"- {ts.get(f'{prefix}.tdr-name')}: {item['character']}\n"

        status = item["active"]

        # OO appeared
        if status:
            output_msg += (
                f"- {ts.get(f'{prefix}.status')}: **{ts.get(f'{prefix}.activate')}**\n"
            )
            output_msg += f"- {ts.get(f'{prefix}.end')} {item['endString']}\n"
            output_msg += f"- {ts.get(f'{prefix}.location')}: "
        # XX NOT appeared
        else:
            output_msg += f"- {ts.get(f'{prefix}.status')}: *Deactivated*\n"
            output_msg += f"- {ts.get(f'{prefix}.appear')} {item['startString']}\n"
            output_msg += f"- {ts.get(f'{prefix}.place')}: "

        # appear location
        output_msg += f"{item['location']}\n\n"

    embed = discord.Embed(description=output_msg, color=color_decision(trader))

    return embed


def W_voidTradersItem(traderItem, *lang):
    return None
