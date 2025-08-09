import discord
import datetime as dt

from translator import ts
from variables.keys import SETTING_FILE_LOC
from variables.times import time_calculate_with_curr
from module.json_load import json_load


def W_Fissures(fissures, *lang):
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
        """
        output_msg += f"""{item['missionType']} - {item['tier']} {ts.get(f'{pf}.fiss')} {ts.get(f'{pf}.steel') if item['isHard'] else ''}
{item['expiry']}({item['eta']}) {ts.get(f'{pf}.remain')} / {item['node']} - {item['enemy']}\n\n"""

    return output_msg
