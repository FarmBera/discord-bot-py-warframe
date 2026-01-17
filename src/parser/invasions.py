import discord
from collections import defaultdict
import re

from src.translator import ts
from src.constants.keys import SPECIAL_ITEM_LIST
from src.utils.emoji import get_emoji
from src.utils.times import convert_remain
from src.utils.return_err import err_embed
from src.utils.data_manager import getFactions, getLanguage, getSolNode

pf = "cmd.invasions."


def get_percent(numerator: int, denominator: int) -> str:
    # fix div into 0
    if denominator == 0:
        return "0.0%"
    return f"{(abs(numerator) / denominator) * 100:.1f}%"


def getPlanet(inv) -> str:
    return re.findall(r"\((.*?)\)", getSolNode(inv["Node"]))[0]


def singleInvasion(inv) -> str:
    i_node = getSolNode(inv["Node"])
    i_status_perc = get_percent(inv["Count"], inv["Goal"])
    i_fact = getFactions(inv["Faction"])  # (inv["AttackerMissionInfo"]["faction"])

    # title / progress
    output_msg = f"""### {ts.get(f'{pf}title')} - *{i_node}*
{ts.get(f'{pf}completion')}: **{i_status_perc}** ({ts.get(f'{pf}atk-from')} {i_fact})
"""
    # date
    time = convert_remain(int(inv["Activation"]["$date"]["$numberLong"]))
    if time[0:1] == "S":
        output_msg += f"{time}"
    else:
        output_msg += f"{ts.get(f'{pf}eta').format(time=time)}"
    output_msg += "\n"

    item_atk: str = getLanguage(
        inv["AttackerReward"]["countedItems"][0]["ItemType"].lower()
    )
    item_def: str = getLanguage(
        inv["DefenderReward"]["countedItems"][0]["ItemType"].lower()
    )

    # item
    if inv["AttackerReward"]:  # is VS Infestation
        output_msg += (
            f"- {getFactions(inv['Faction'])} - **{get_emoji(item_atk)} {item_atk}**\n"
        )

    output_msg += f"- {getFactions(inv['DefenderFaction'])} - **{get_emoji(item_def)} {item_def}**\n"

    return output_msg


def w_invasions(invasions) -> discord.Embed:
    if not invasions:
        return err_embed("invasions")

    mission_per_planets = defaultdict(list)

    for inv in invasions:
        if inv.get("Completed"):
            continue

        planet = getPlanet(inv)
        mission_per_planets[planet].append(dict(inv))

    # generate output msg
    output_msg: str = ""
    for planet, inv_list in mission_per_planets.items():
        if not inv_list:  # ignore empty planet
            continue

        output_msg += f"# {planet}\n\n"  # planet title
        for inv in inv_list:  # desc
            output_msg += singleInvasion(inv)

    return discord.Embed(description=output_msg)  # color=0x00FFFF,


def w_invasions_se(invasions) -> tuple[discord.Embed, str]:
    if not invasions:
        return err_embed("invasions"), ""

    mission_per_planets = defaultdict(list)

    for inv in invasions:
        if inv.get("Completed"):
            continue

        special_item_exist: bool = False
        item_list = [
            getLanguage(item["ItemType"]).lower()
            for reward in [
                inv.get("AttackerReward"),
                inv.get("DefenderReward"),
            ]
            if isinstance(reward, dict) and "countedItems" in reward
            for item in reward["countedItems"]
        ]

        for item in item_list:
            for se in SPECIAL_ITEM_LIST:
                if se in item:
                    special_item_exist = True
                    break
        if special_item_exist:
            planet = getPlanet(inv)
            mission_per_planets[planet].append(dict(inv))

    # generate output msg
    output_msg: str = ""
    for planet, inv_list in mission_per_planets.items():
        if not inv_list:  # ignore empty planet
            continue

        output_msg += f"# {planet}\n\n"  # planet title
        for inv in inv_list:  # desc
            output_msg += singleInvasion(inv)

    if not output_msg:
        output_msg = ts.get(f"{pf}no-special")
        color = discord.Color.orange()
    else:
        color = discord.Color.darker_grey()

    f = "invasion"
    embed = discord.Embed(description=output_msg, color=color)
    embed.set_thumbnail(url="attachment://i.webp")

    return embed, f


# from src.utils.data_manager import get_obj
# from src.constants.keys import INVASIONS
# print(w_invasions_se(get_obj(INVASIONS))[0].description)
