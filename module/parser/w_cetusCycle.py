import discord
from translator import ts
from module.discord_file import img_file


cetus_color = {"day": 0xFFBB00, "night": 0x2B79FF}


# cetus day/night state & cycle
def W_CetusCycle(cetus, *lang):
    if cetus == False:
        return (
            discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000),
            None,
        )

    if cetus is None:
        return None, None

    STATE = cetus["state"]

    prefix: str = "cmd.cetus"
    output_msg: str = f"### {ts.get(f'{prefix}.title')}\n\n"
    # output_msg += f"- {ts.get(f'{prefix}.current')}: < **{STATE.capitalize()}** >\n"
    output_msg += f"# < **{STATE.capitalize()}** >\n\n"
    output_msg += f"- {cetus['timeLeft']} to "
    output_msg += (
        ts.get(f"{prefix}.night") if cetus["isDay"] else ts.get(f"{prefix}.day")
    )

    f = img_file(f"cetus-{STATE}")
    embed = discord.Embed(description=output_msg, color=cetus_color[STATE])
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f
