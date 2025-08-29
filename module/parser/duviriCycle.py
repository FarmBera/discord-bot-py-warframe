import discord
import datetime as dt

from translator import ts
from variables.times import time_calculate_with_curr
from module.return_err import err_embed

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

    output_msg: str = ""

    output_msg += f"# {ts.get('cmd.duviri-cycle.title')}\n\n"
    output_msg += (
        f"- State: < **" + ts.get(f"cmd.duviri-cycle.{duviri['state']}") + "** >\n"
    )
    output_msg += f"- {ts.get('cmd.duviri-cycle.expire')} {time_calculate_with_curr(duviri['expiry'])}"

    embed = discord.Embed(description=output_msg, color=duviri_color[duviri["state"]])

    return embed
