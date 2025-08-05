import discord
import datetime as dt

from translator import ts
from times import JSON_DATE_PAT, time_calculate_with_curr
from module.json_load import json_load


def W_Fissures(fissures, *lang):
    setting = json_load("setting.json")  # VAR
    fav_mission = setting["fissures"]["favMission"]  # VAR
    tier_except = setting["fissures"]["tierExcept"]  # VAR

    output_msg: str = ""
    normal = []  # normal fissures
    steel_path = []  # steel path fissures

    output_msg += "# Void Fissures\n\n"  # VAR

    for item in fissures:
        if item["tier"] in tier_except:
            continue

        if item["missionType"] in fav_mission:
            if item["isHard"]:  # steel path
                steel_path.append(item)
            else:  # normal mission
                normal.append(item)

    for item in normal + steel_path:
        item["expiry"] = time_calculate_with_curr(item["expiry"])

    for item in normal + steel_path:
        """
        Extermination - Neo Fissure **[Steel Path]**
        53m(53m 54s) left / Neso (Neptune) - Corpus
        """
        output_msg += f"""{item['missionType']} - {item['tier']} {ts.get('cmd.fissures.fiss')} {ts.get('cmd.fissures.steel') if item['isHard'] else ''}
{item['expiry']}({item['eta']}) {ts.get('cmd.fissures.remain')} / {item['node']} - {item['enemy']}\n\n"""

    return output_msg
