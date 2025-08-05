import discord
import datetime as dt

from translator import ts
from times import JSON_DATE_PAT, time_calculate_with_curr


state_color = {
    "joy": 0x377C82,
    "anger": 0xED983C,
    "envy": 0x8CC847,
    "sorrow": 0x8CA6DF,
    "fear": 0xA67BC1,
}


def W_duviriCycle(duviri, *lang):
    if duviri == False:
        return discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000)

    if duviri is None:
        return None

    output_msg: str = ""

    output_msg += f"# {ts.get('cmd.duviri-cycle.title')}\n\n"
    output_msg += (
        f"- State: < " + ts.get(f"cmd.duviri-cycle.{duviri['state']}") + " >\n"
    )
    output_msg += f"- Expires in {time_calculate_with_curr(duviri["expiry"])}"  # VAR

    embed = discord.Embed(description=output_msg, color=state_color[duviri["state"]])

    return embed
