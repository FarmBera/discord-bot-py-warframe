import discord

from src.translator import Translator, ts as _ts, language as _default_lang
from src.utils.data_manager import SETTINGS
from src.utils.data_manager import getFissure, getSolNode, getMissionType, getNodeEnemy
from src.utils.emoji import get_emoji
from src.utils.formatter import check_str_length
from src.utils.times import convert_remain, timeNow

pf: str = "cmd.fissures."
FISSURE_CHOICE_FAST = f"{pf}choice-fast"

RAILJACK_NODES: list = [
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
    t_now: int = timeNow()
    t_expired: int = arg_time // 1000

    return True if t_now > t_expired else False


# todo-delay: 검색 기능 추가
def w_fissures(
    fissures, args, ts: Translator = _ts, lang: str = _default_lang
) -> tuple[discord.Embed, str]:
    setting = SETTINGS
    prefix = setting["fissures"]
    fav_mission = prefix["favMission"]
    tier_exclude = prefix["tierExcept"]
    include_railjack_node: bool = prefix["IncludeRailjack"]

    if isinstance(args, tuple):
        choice, include_railjack_node = args
    else:
        choice = args

    output_msg: str = ""
    normal: list = []  # normal fissures
    steel_path: list = []  # steel path fissures
    railjack: list = []  # railjack node

    # process fissures
    for item in fissures:
        if is_expired_fiss(int(item["Expiry"]["$date"]["$numberLong"])):
            continue

        node = getSolNode(item["Node"], lang)
        tier = getFissure(item["Modifier"], lang)
        miss_type = getMissionType(item["MissionType"], lang)

        # choice: fast available
        if choice == FISSURE_CHOICE_FAST:
            if tier in tier_exclude:
                continue

            if not miss_type in fav_mission:
                continue

        # other choices...

        if not include_railjack_node:
            if node.lower() in RAILJACK_NODES:
                continue

        if item.get("Hard"):  # steel path
            steel_path.append(item)
        # elif item in RAILJACK_NODES:
        #     railjack.append(item)
        else:  # normal
            normal.append(item)

    integrated_fiss: list = normal + steel_path + railjack

    # create output msg
    output_msg += f"# {ts.get(choice)}: {len(integrated_fiss)}{ts.get(f'{pf}cnt')}\n"

    for item in integrated_fiss:
        """
        Extermination - Neo Fissure **[Steel Path]**
        53m left / Neso (Neptune) - Corpus
        """
        o_node = getSolNode(item["Node"], lang)
        o_railjack = ts.get(f"{pf}railjack") if o_node in RAILJACK_NODES else ""
        o_tier = getFissure(item["Modifier"], lang)
        o_type = getMissionType(item["MissionType"], lang)
        o_enemy = getNodeEnemy(item["Node"], lang)
        o_emoji = get_emoji(o_tier)
        o_isSteel = ts.get(f"{pf}steel") if item.get("Hard") else ""
        exp_time = convert_remain(int(item["Expiry"]["$date"]["$numberLong"]))

        output_msg += ts.get(f"{pf}output").format(
            railjack=o_railjack,
            type=o_type,
            emoji=o_emoji,
            tier=o_tier,
            steel=o_isSteel,
            time=exp_time,
            node=o_node,
            enemy=o_enemy,
        )
        output_msg += "\n"
    output_msg = check_str_length(output_msg)

    embed = discord.Embed(description=output_msg, color=0x11806A)
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "fissures"


# from src.utils.data_manager import get_obj
# from src.constants.keys import FISSURES
# print(w_fissures(get_obj(FISSURES), ts.get(f"{pf}choice-fast"))[0].description)
