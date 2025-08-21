import discord

from translator import ts
from module.discord_file import img_file


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
    pf: str = "cmd.void-traders"

    output_msg: str = f"# {ts.get(f'{pf}.title')}\n\n"

    for item in trader:
        if length >= 2:
            output_msg += f"{idx}. {ts.get(f'{pf}.tdr-name')}: {item['character']}\n\n"
            idx += 1
        else:
            output_msg += f"- {ts.get(f'{pf}.tdr-name')}: {item['character']}\n"

        status = item["active"]

        # OO appeared
        if status:
            output_msg += (
                f"- {ts.get(f'{pf}.status')}: ✅ **{ts.get(f'{pf}.activate')}**\n"
            )
            output_msg += f"- {ts.get(f'{pf}.end')} {item['endString']}\n"
            output_msg += f"- {ts.get(f'{pf}.location')}: "
        # XX NOT appeared
        else:
            output_msg += (
                f"- {ts.get(f'{pf}.status')}: ❌ *{ts.get(f'{pf}.deactivate')}*\n"
            )
            output_msg += f"- {ts.get(f'{pf}.appear')} {item['startString']}\n"
            output_msg += f"- {ts.get(f'{pf}.place')}: "

        # appear location
        output_msg += f"{item['location']}\n\n"

    f = img_file("baro-ki-teer")  # VAR
    embed = discord.Embed(description=output_msg, color=color_decision(trader))
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f


def W_voidTradersItem(traderItem, *lang):
    return None
