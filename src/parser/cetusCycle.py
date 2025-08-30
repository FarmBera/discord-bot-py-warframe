import discord
from src.translator import ts
from src.utils.formatter import time_cal_with_curr
from src.utils.discord_file import img_file
from src.utils.return_err import err_embed


cetus_color = {"day": 0xFFBB00, "night": 0x2B79FF}


# cetus day/night state & cycle
def w_cetusCycle(cetus) -> tuple:
    if not cetus:
        return err_embed("cetusCycle")

    STATE = cetus["state"]

    pf: str = "cmd.cetus."
    output_msg: str = f"""### {ts.get(f'{pf}title')}

# < **{ts.get(f'{pf}{STATE}')}** >

- {ts.get(f'{pf}endin')} {time_cal_with_curr(cetus['expiry'])} ({cetus['timeLeft']})
"""
    # f"- {ts.get(f'{pf}current')}: < **{STATE.capitalize()}** >"

    f = img_file(f"cetus-{STATE}")
    embed = discord.Embed(description=output_msg, color=cetus_color[STATE])
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f
