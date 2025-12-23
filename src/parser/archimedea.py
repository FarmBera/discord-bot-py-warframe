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


def generateVariables(object) -> str:
    text = "## Global Variables"
    for var in object["Variables"]:
        text += f"\n- {var}"

    return text


def generateMissions(object) -> str:
    text = ""
    idx = 1
    for item in object["Missions"]:
        text += f"{idx}. **{getMissionType(item['missionType'])}**: "
        # ({getFactions(item['faction'])})\n"
        for jtem in item["difficulties"]:
            if jtem.get("type") == "CD_HARD":
                text += ", ".join(jtem.get("risks"))
                break
        text += "\n"
        idx += 1

    return text


pfd: str = "cmd.deep-archimedea."


def w_deepArchimedea(archimedea) -> str:
    # find deep archimedea
    deep = None
    try:
        for item in archimedea:
            if item.get("Type") == CT_LAB:
                deep = item
                break
    except:
        deep = archimedea

    if deep is None or not deep:
        return ts.get("general.error-cmd")

    # generate output msg
    output_msg = ts.get(f"{pfd}content").format(
        time=convert_remain(deep["Expiry"]["$date"]["$numberLong"])
    )
    # missions
    output_msg += generateMissions(deep)
    # global variables
    output_msg += generateVariables(deep)

    return output_msg


pft: str = "cmd.temporal-archimedea."


def w_temporalArchimedia(archimedea) -> str:
    # find temporal archimedea
    temporal = None
    try:
        for item in archimedea:
            if item.get("Type") == CT_HEX:
                temporal = item
                break
    except:
        temporal = archimedea

    if temporal is None or not temporal:
        return ts.get("general.error-cmd")

    # generate output msg
    output_msg = ts.get(f"{pft}content").format(
        time=convert_remain(temporal["Expiry"]["$date"]["$numberLong"]),
    )
    # missions
    output_msg += generateMissions(temporal)
    # global variables
    output_msg += generateVariables(temporal)

    return output_msg


# from src.constants.keys import ARCHIMEDEA
# from src.utils.data_manager import get_obj

# print(w_deepArchimedea(get_obj(ARCHIMEDEA)))
# print(w_temporalArchimedia(get_obj(ARCHIMEDEA)))
