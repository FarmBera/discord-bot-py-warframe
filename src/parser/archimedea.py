import discord

from src.constants.keys import ARCHIMEDEA, ARCHIMEDEA_DEEP, ARCHIMEDEA_TEMPORAL
from src.translator import ts as _ts, language as _default_lang
from src.utils.data_manager import (
    get_obj,
    set_obj_async,
    getMissionType,
    getLanguageOrigin,
)
from src.utils.return_err import err_embed
from src.utils.times import convert_remain

archimedea_deep = get_obj(f"{ARCHIMEDEA}{ARCHIMEDEA_DEEP}")
archimedea_temporal = get_obj(f"{ARCHIMEDEA}{ARCHIMEDEA_TEMPORAL}")

CT_LAB = "CT_LAB"
CT_HEX = "CT_HEX"

pf: str = "cmd.archimedea."


def getDeepArchimedea():
    global archimedea_deep
    return archimedea_deep


def getTemporalArchimedea():
    global archimedea_temporal
    return archimedea_temporal


async def setDeepArchimedea(obj):
    global archimedea_deep
    archimedea_deep = obj
    await set_obj_async(obj, f"{ARCHIMEDEA}{ARCHIMEDEA_DEEP}")


async def setTemporalArchimedea(obj):
    global archimedea_temporal
    archimedea_temporal = obj
    await set_obj_async(obj, f"{ARCHIMEDEA}{ARCHIMEDEA_TEMPORAL}")


def generateMissions(obj, ts=_ts, lang=_default_lang) -> str:
    text = ""
    idx = 1
    for item in obj["Missions"]:
        # mission only
        # text += f"{idx}. **{getMissionType(item['missionType'])}**"

        # faction
        # ({getFactions(item['faction'])})\n"

        # mission with h2 header
        text += f"## {idx}. {getMissionType(item['missionType'],lang)}"

        # deviation
        for jtem in item["difficulties"]:
            if jtem.get("type") != "CD_HARD":
                continue

            key = getLanguageOrigin(jtem["deviation"], lang)
            if not key:
                text += f"\n- {jtem['deviation']}"
                continue

            value = key["value"]
            desc = key["simple"] if key.get("simple") else key["desc"]
            text += f"\n- **{ts.get(f'{pf}deviation')}**: {value} - {desc}"
            break

        # risks
        risks: dict = {}
        for jtem in item["difficulties"]:
            if jtem.get("type") == "CD_HARD":
                risks = jtem.get("risks")
                break
        for rsk in risks:
            key = getLanguageOrigin(rsk, lang)
            if not key:
                text += f"\n- {rsk}"
                continue

            value = key["value"]
            desc = key["simple"] if key.get("simple") else key["desc"]
            text += f"\n- **{ts.get(f'{pf}risks')}**: {value} - {desc}"

        text += "\n"
        idx += 1

    return text


def generateVariables(obj, ts=_ts, lang=_default_lang) -> str:
    text = ts.get(f"{pf}var")
    for var in obj["Variables"]:
        translate = getLanguageOrigin(var, lang)
        if not translate:
            text += f"\n- **{var}**"
            continue

        key = translate["value"]
        desc = translate["simple"] if translate.get("simple") else translate["desc"]
        text += f"\n- **{key}**: {desc}"
    return text


pfd: str = "cmd.deep-archimedea."


def w_deepArchimedea(
    archimedea, ts=_ts, lang=_default_lang
) -> tuple[discord.Embed, str]:
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
        return err_embed("deep-archimedea"), ""

    # generate output msg
    output_msg: str = ts.get(f"{pfd}content").format(
        time=convert_remain(deep["Expiry"]["$date"]["$numberLong"])
    )
    # missions
    output_msg += generateMissions(deep, ts, lang)
    # risks & global variables
    output_msg += generateVariables(deep, ts, lang)

    embed = discord.Embed(description=output_msg, color=discord.Color.dark_gold())
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "deep"


pft: str = "cmd.temporal-archimedea."


def w_temporalArchimedia(
    archimedea, ts=_ts, lang=_default_lang
) -> tuple[discord.Embed, str]:
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
        return ts.get("general.error-cmd"), ""

    # generate output msg
    output_msg = ts.get(f"{pft}content").format(
        time=convert_remain(temporal["Expiry"]["$date"]["$numberLong"]),
    )
    # missions
    output_msg += generateMissions(temporal, ts, lang)
    # global variables
    output_msg += generateVariables(temporal, ts, lang)

    embed = discord.Embed(description=output_msg, color=discord.Color.teal())
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "temporal"


# from src.constants.keys import ARCHIMEDEA
# from src.utils.data_manager import get_obj
# print(w_deepArchimedea(get_obj(ARCHIMEDEA))[0].description)
# print()
# print(w_temporalArchimedia(get_obj(ARCHIMEDEA))[0].description)
