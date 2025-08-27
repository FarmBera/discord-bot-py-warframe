import discord
import datetime as dt

from translator import ts
from variables.keys import SETTING_FILE_LOC
from variables.times import time_calculate_with_curr
from module.json_load import json_load
from module.get_emoji import get_emoji

railjack: list = [
    # veil proxima
    "numina",
    "calabash",
    "r-9 cloud",
    "flexa",
    "h-2 cloud",
    "nsu grid",
    # saturn proxima
    "lupal pass",
    "mordo cluster",
    "nodo gap",
    "kasio’s rest",
    # venus proxima
    "falling glory",
    "vesper strait",
    "luckless expanse",
    "orvin-haarc",
    "beacon shield ring",
    "bifrost echo",
    # earth proxima
    "bendar cluster",
    "sover strait",
    "iota temple",
    "ogal cluster",
    "korm’s belt",
    # neptune proxima
    "brom cluster",
    "mammon’s prospect",
    "enkidu ice drifts",
    "nu-gua mines",
    "arva vector",
    # pluto proxima
    "khufu envoy",
    "seven sirens",  # check
    "obol crossing",
    "fenton’s field",
    "profit margin",
    "peregrine axis",
]


def w_fissures(fissures, *lang):
    setting = json_load(SETTING_FILE_LOC)
    fav_mission = setting["fissures"]["favMission"]  # var
    tier_except = setting["fissures"]["tierExcept"]  # var

    output_msg: str = ""
    normal = []  # normal fissures
    steel_path = []  # steel path fissures

    pf: str = "cmd.fissures"
    output_msg += f"# {ts.get(f'{pf}.title')}\n\n"

    for item in fissures:
        if item["tier"] in tier_except:
            continue

        # except railjack node
        if item["node"].split(" (")[0].lower() in railjack:
            continue

        if item["missionType"] in fav_mission:
            if item["isHard"]:  # steel path
                steel_path.append(item)
            else:  # normal
                normal.append(item)

    for item in normal + steel_path:
        item["expiry"] = time_calculate_with_curr(item["expiry"])

    for item in normal + steel_path:
        """
        Extermination - Neo Fissure **[Steel Path]**
        53m(53m 54s) left / Neso (Neptune) - Corpus

        ({item['eta']})
        """
        o_tier = item["tier"]
        o_emoji = get_emoji(o_tier)
        o_isSteel = ts.get(f"{pf}.steel") if item["isHard"] else ""

        output_msg += f"""{item["missionType"]} - {o_emoji} {o_tier} {ts.get(f'{pf}.fiss')} {o_isSteel}
{item['expiry']} {ts.get(f'{pf}.remain')} / {item['node']} - {item['enemy']}\n\n"""

    return output_msg
