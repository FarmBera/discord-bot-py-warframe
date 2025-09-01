import discord
import datetime as dt

from src.translator import ts
from src.utils.formatter import time_cal_with_curr
from src.utils.return_err import err_embed

duviri_color = {
    "joy": 0x377C82,
    "anger": 0xED983C,
    "envy": 0x8CC847,
    "sorrow": 0x8CA6DF,
    "fear": 0xA67BC1,
}


def w_duviriCycle(duviri):
    if not duviri:
        return err_embed("duviriCycle")

    pf: str = "cmd.duviri-cycle."

    output_msg: str = ""

    output_msg += f"""### {ts.get(f'{pf}title')}\n\n

# < {ts.get(f"{pf}{duviri['state']}")} >

- {ts.get(f'{pf}expire')} {time_cal_with_curr(duviri['expiry'])}
"""
    # - {ts.get(f'{pf}state')}: < **" + ts.get(f"{pf}{duviri['state']}") + "** >

    embed = discord.Embed(description=output_msg, color=duviri_color[duviri["state"]])

    return embed
