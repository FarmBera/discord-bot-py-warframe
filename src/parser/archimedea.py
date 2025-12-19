import discord

from src.translator import ts
from src.constants.keys import ARCHIMEDEA, ARCHIMEDEA_DEEP, ARCHIMEDEA_TEMPORAL
from src.utils.emoji import get_emoji
from src.utils.data_manager import get_obj, set_obj, getMissionType, getFactions
from src.utils.times import timeNowDT, convert_remain
from src.utils.return_err import err_embed, err_text

archimedea_deep = get_obj(f"{ARCHIMEDEA}{ARCHIMEDEA_DEEP}")
archimedea_temporal = get_obj(f"{ARCHIMEDEA}{ARCHIMEDEA_TEMPORAL}")


CT_LAB = "CT_LAB"
CT_HEX = "CT_HEX"


def setDeepArchimedea(object):
    global archimedea_deep
    archimedea_deep = object
    set_obj(object, f"{ARCHIMEDEA}{ARCHIMEDEA_DEEP}")


def setTemporalArchimedea(object):
    global archimedea_temporal
    archimedea_temporal = object
    set_obj(object, f"{ARCHIMEDEA}{ARCHIMEDEA_TEMPORAL}")


pfd: str = "cmd.deep-archimedea."


def w_deepArchimedea(archimedea) -> str:
    # find deep archimedea
    deep = None
    try:
        for item in archimedea:
            if item.get("Type") == CT_LAB:
                deep = item
    except:
        deep = archimedea

    if deep is None or not deep:
        return ts.get("general.error-cmd")

    # generate output msg
    output_msg = ts.get(f"{pfd}content").format(
        time=convert_remain(deep["Expiry"]["$date"]["$numberLong"])
    )
    idx = 1
    for item in deep["Missions"]:
        output_msg += f"{idx}. {getMissionType(item['missionType'])}\n"  # ({getFactions(item['faction'])})\n"
        # for jtem in item["difficulties"]:
        #     if jtem.get("type") == "CD_HARD":
        #         output_msg += ", ".join(jtem.get("risks")) + "\n"
        #         break
        idx += 1

    return output_msg


pft: str = "cmd.temporal-archimedea."


def w_temporalArchimedia(archimedea) -> str:
    # find temporal archimedea
    temporal = None
    try:
        for item in archimedea:
            if item.get("Type") == CT_HEX:
                temporal = item
    except:
        temporal = archimedea

    if temporal is None or not temporal:
        return ts.get("general.error-cmd")

    # generate output msg
    output_msg = ts.get(f"{pft}content").format(
        time=convert_remain(temporal["Expiry"]["$date"]["$numberLong"]),
    )
    idx = 1
    for item in temporal["Missions"]:
        output_msg += f"{idx}. {getMissionType(item['missionType'])} ({getFactions(item['faction'])})\n"
        # for jtem in item["difficulties"]:
        #     if jtem.get("type") == "CD_HARD":
        #         output_msg += ", ".join(jtem.get("risks")) + "\n"
        #         break
        idx += 1

    return output_msg


# from src.constants.keys import ARCHIMEDEA
# from src.utils.data_manager import get_obj

# print(w_temporalArchimedia(get_obj(ARCHIMEDEA)))


# print(w_deepArchimedea(get_obj(ARCHIMEDEA)))
