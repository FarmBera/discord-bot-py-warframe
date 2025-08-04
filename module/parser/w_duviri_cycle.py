import discord
import datetime as dt

from translator import ts

from module.get_obj import get_obj

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
    date_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"

    output_msg += f"# {ts.get('cmd.duviri-cycle.title')}\n\n"
    output_msg += (
        f"- State: < " + ts.get(f"cmd.duviri-cycle.{duviri['state']}") + " >\n"
    )

    t = dt.datetime.strptime(duviri["expiry"], date_format) + dt.timedelta(hours=9)
    t -= dt.datetime.now()

    h, r = divmod(t.seconds, 3600)
    m = divmod(r, 60)

    output_msg += "- Expires in "
    if h <= 0:
        output_msg += f"{m[0]}m"
    else:
        output_msg += f"{h}h {m[0]}m"

    embed = discord.Embed(description=output_msg, color=state_color[duviri["state"]])

    return embed
