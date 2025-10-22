import discord
import datetime as dt

from src.translator import ts
from src.constants.keys import SETTING_FILE_LOC
from src.constants.times import convert_remain
from src.utils.file_io import json_load
from src.utils.emoji import get_emoji
from src.utils.formatter import txt_length_check
from src.utils.data_manager import getFissure, getSolNode, getMissionType, getNodeEnemy

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


def is_expired_fiss(arg_time) -> bool:
    t_now: dt.datetime = dt.datetime.now()
    t_expired: dt.datetime = dt.datetime.fromtimestamp(arg_time / 1000)

    return True if t_now > t_expired else False


# todo-delay: 검색 기능 추가
def w_fissures(fissures, args) -> str:
    setting = json_load(SETTING_FILE_LOC)
    prefix = setting["fissures"]
    fav_mission = prefix["favMission"]  # var
    tier_exclude = prefix["tierExcept"]  # var
    include_railjack_node: bool = prefix["IncludeRailjack"]

    choice: str = ""
    if isinstance(args, tuple):
        choice, include_railjack_node = args
    else:
        choice = args

    output_msg: str = ""
    normal = []  # normal fissures
    steel_path = []  # steel path fissures

    pf: str = "cmd.fissures."

    # process fissures
    for item in fissures:
        if is_expired_fiss(int(item["Expiry"]["$date"]["$numberLong"])):
            continue

        node = getSolNode(item["Node"])
        tier = getFissure(item["Modifier"])
        miss_type = getMissionType(item["MissionType"])

        # choice: fast available
        if choice == ts.get(f"{pf}choice-fast"):
            if tier in tier_exclude:
                continue

            if not miss_type in fav_mission:
                continue

        # other choices...

        if not include_railjack_node:
            if node.lower() in railjack:
                continue

        if item.get("Hard"):  # steel path
            steel_path.append(item)
        else:  # normal
            normal.append(item)

    integrated_fiss: list = normal + steel_path

    # create output msg
    output_msg += f"# {choice}: {len(integrated_fiss)}{ts.get(f'{pf}cnt')}\n\n"

    for item in integrated_fiss:
        """
        Extermination - Neo Fissure **[Steel Path]**
        53m left / Neso (Neptune) - Corpus
        """
        o_tier = getFissure(item["Modifier"])
        o_type = getMissionType(item["MissionType"])
        o_node = getSolNode(item["Node"])
        o_enemy = getNodeEnemy(item["Node"])
        o_emoji = get_emoji(o_tier)
        o_isSteel = ts.get(f"{pf}steel") if item.get("Hard") else ""
        exp_time = convert_remain(int(item["Expiry"]["$date"]["$numberLong"]))

        output_msg += f"""**{ts.trs(o_type)}** - {o_emoji} {ts.trs(o_tier)} {ts.get(f'{pf}fiss')} {o_isSteel}
{exp_time} {ts.get(f'{pf}remain')} / {o_node} - {o_enemy}\n\n"""

    return txt_length_check(output_msg)
