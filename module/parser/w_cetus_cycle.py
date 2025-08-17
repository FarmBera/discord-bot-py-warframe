import discord
from translator import ts


cetus_color = {"day": 0xFFBB00, "night": 0x2B79FF}


# cetus day/night state & cycle
def W_CetusCycle(cetus, *lang) -> str:
    if cetus == False:
        return ts.get("general.error-cmd")

    if cetus is None:
        return None

    STATE = cetus["state"]

    prefix: str = "cmd.cetus"
    output_msg: str = f"# {ts.get(f'{prefix}.title')}\n\n"
    output_msg += f"- {ts.get(f'{prefix}.current')}: < {STATE.capitalize()} >\n"
    output_msg += f"- {cetus['timeLeft']} to "
    output_msg += (
        ts.get(f"{prefix}.night") if cetus["isDay"] else ts.get(f"{prefix}.day")
    )

    return discord.Embed(description=output_msg, color=cetus_color[STATE])
