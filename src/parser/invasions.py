import discord
import datetime as dt
from collections import defaultdict

from translator import ts
from var.times import JSON_DATE_PAT
from module.return_err import err_embed


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
    atk = inv["attackingFaction"]
    dfd = inv["defender"]

    pf = "cmd.invasions."
    output_msg = f"""### {ts.get(f'{pf}title')} {ts.get(f'{pf}at')} *{inv['node']}*

{ts.get(f'{pf}completion')}: **{(inv['completion']):.1f}%** ({ts.get(f'{pf}atk-from')} {atk})
"""

    date = formatDate(inv["activation"])
    if date[0:1] == "S":
        output_msg += f"{date}\n\n"
    else:
        output_msg += f"{ts.get(f'{pf}eta')} {date}\n\n"

    if not inv["vsInfestation"]:
        output_msg += f"- {atk} - **{inv['attacker']['reward']['itemString']}**\n"

    output_msg += f"- {dfd['faction']} - **{dfd['reward']['itemString']}**\n\n"

    return output_msg


def w_invasions(invasions) -> discord.Embed:
    if not invasions:
        return err_embed("invasions")

    def getPlanet(inv) -> str:
        return inv["node"].split(" (")[-1].replace(")", "")

    mission_per_planets = defaultdict(list)

    for inv in invasions:
        if inv.get("completed"):
            continue

        planet = getPlanet(inv)
        mission_per_planets[planet].append(dict(inv))

    # generate output msg
    output_msg: str = ""
    for planet, inv_list in mission_per_planets.items():
        if inv_list == []:  # ignore empty planet
            continue

        output_msg += f"# {planet}\n\n"  # planet title
        for inv in inv_list:  # desc
            output_msg += singleInvasion(inv)

    return discord.Embed(description=output_msg)  # color=0x00FFFF,
