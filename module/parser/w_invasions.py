import discord
import datetime as dt

from translator import ts
from variables.times import JSON_DATE_PAT


def formatDate(dd: str):
    d = dt.datetime.strptime(dd, JSON_DATE_PAT) + dt.timedelta(hours=9)
    d = dt.datetime.now() - d
    h, r = divmod(d.seconds, 3600)
    m, s = divmod(r, 60)

    if h <= 0 and m < 5:
        return "Started Now"

    out = f"{d.days}d " if d.days >= 1 else ""
    out += f"{h}h " if h >= 1 else ""
    out += f"{m}m"

    return out


def singleInvasion(inv) -> str:
    if inv["completed"] or inv["eta"][0:1] == "-":
        return ""

    atk = inv["attackingFaction"]
    dfd = inv["defender"]

    pf = "cmd.invasions."
    output_msg = f"""### {ts.get(f'{pf}title')} {ts.get(f'{pf}at')} *{inv['node']}*

{ts.get(f'{pf}completion')}: **{(inv['completion']):.1f}%** ({ts.get(f'{pf}atk-from')} {atk})
"""

    date = formatDate(inv["activation"])
    if date[0:1] == "S":
        output_msg += date
    else:
        output_msg += f"{ts.get(f'{pf}eta')} {date}"

    if not inv["vsInfestation"]:
        output_msg += f"- **{atk}** - {inv['attacker']['reward']['itemString']}\n"

    output_msg += f"- **{dfd['faction']}** - {dfd['reward']['itemString']}\n\n"

    return output_msg


def w_invasions(invasions, *lang) -> discord.Embed:
    if invasions == False:
        return discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000)

    if invasions is None:
        return None

    output_msg: str = ""
    for inv in invasions:
        output_msg += singleInvasion(inv)

    return discord.Embed(description=output_msg)  # color=0x00FFFF,
