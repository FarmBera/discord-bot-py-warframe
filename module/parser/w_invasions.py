import discord
import datetime as dt

from translator import ts
from variables.times import JSON_DATE_PAT

# def check(inv):


def singleInvasion(inv) -> str:
    if inv["completed"]:
        return ""

    atk = inv["attackingFaction"]
    dfd = inv["defender"]

    pf = "cmd.invasions."
    output_msg = f"""### {ts.get(f'{pf}title')} {ts.get(f'{pf}at')} *{inv['node']}*

{ts.get(f'{pf}atk-from')} **{atk}** \\ {int(inv['completion'])}%
{ts.get(f'{pf}eta')} {inv['eta']}

- **{atk}** - {'X' if inv["vsInfestation"] else inv['attacker']['reward']['itemString']}
- **{dfd['faction']}** - {dfd['reward']['itemString']}

"""
    return output_msg


def w_invasions(invasions, *lang):
    if invasions == False:
        return discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000)

    if invasions is None:
        return None

    output_msg: str = ""
    for inv in invasions:
        output_msg += singleInvasion(inv)

    return discord.Embed(description=output_msg)  # color=0x00FFFF,
