import discord
from translator import ts
from variables.times import time_calculate_with_curr
from module.discord_file import img_file
from module.return_err import err_embed


cetus_color = {"day": 0xFFBB00, "night": 0x2B79FF}


# cetus day/night state & cycle
def w_cetusCycle(cetus) -> tuple:
    if not cetus:
        return err_embed("cetusCycle")

    STATE = cetus["state"]

    pf: str = "cmd.cetus."
    output_msg: str = f"### {ts.get(f'{pf}title')}\n\n"
    # output_msg += f"- {ts.get(f'{pf}current')}: < **{STATE.capitalize()}** >\n"
    output_msg += f"# < **{STATE.capitalize()}** >\n\n"
    output_msg += f"- {ts.get(f'{pf}endin')} {time_calculate_with_curr(cetus['expiry'])} ({cetus['timeLeft']})\n"

    f = img_file(f"cetus-{STATE}")
    embed = discord.Embed(description=output_msg, color=cetus_color[STATE])
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f
