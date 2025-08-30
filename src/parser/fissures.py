import discord
import datetime as dt

from src.translator import ts
from src.constants.keys import SETTING_FILE_LOC
from src.utils.formatter import time_cal_with_curr
from src.utils.file_io import json_load
from src.utils.get_emoji import get_emoji

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


# TODO: fissures 전체/빠른클 나눠서 하기 & 레일잭 포함 여부도
def w_fissures(fissures) -> str:
    setting = json_load(SETTING_FILE_LOC)
    prefix = setting["fissures"]
    fav_mission = prefix["favMission"]  # var
    tier_except = prefix["tierExcept"]  # var
    include_railjack_node: bool = prefix["IncludeRailjack"]

    output_msg: str = ""
    normal = []  # normal fissures
    steel_path = []  # steel path fissures

    pf: str = "cmd.fissures."
    output_msg += f"# {ts.get(f'{pf}title')}\n\n"

    for item in fissures:
        if item["expired"]:
            continue

        if item["tier"] in tier_except:
            continue

        # except railjack node
        if not include_railjack_node:
            if item["node"].split(" (")[0].lower() in railjack:
                continue

        if item["missionKey"] in fav_mission:
            if item["isHard"]:  # steel path
                steel_path.append(item)
            else:  # normal
                normal.append(item)

    for item in normal + steel_path:
        """
        Extermination - Neo Fissure **[Steel Path]**
        53m left / Neso (Neptune) - Corpus
        """
        o_tier = item["tier"]
        o_emoji = get_emoji(o_tier)
        o_isSteel = ts.get(f"{pf}steel") if item["isHard"] else ""
        exp_time = time_cal_with_curr(item["expiry"])

        output_msg += f"""{ts.trs(f'trs.{item["missionKey"]}')} - {o_emoji} {ts.trs(f'trs.{o_tier}')} {ts.get(f'{pf}fiss')} {o_isSteel}
{exp_time} {ts.get(f'{pf}remain')} / {item['node']} - {item['enemy']}\n\n"""

    return output_msg
