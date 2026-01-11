import discord

from src.translator import ts, language as lang
from src.constants.keys import ARCHIMEDEA, ARCHIMEDEA_DEEP, ARCHIMEDEA_TEMPORAL
from src.utils.file_io import json_load
from src.utils.data_manager import get_obj, set_obj_async, getMissionType  # getFactions
from src.utils.times import convert_remain
from src.utils.return_err import err_embed

archimedea_deep = get_obj(f"{ARCHIMEDEA}{ARCHIMEDEA_DEEP}")
archimedea_temporal = get_obj(f"{ARCHIMEDEA}{ARCHIMEDEA_TEMPORAL}")
conquest_var: dict = json_load(f"data/{lang}/archimedeaData.json")


CT_LAB = "CT_LAB"
CT_HEX = "CT_HEX"


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


pf: str = "cmd.archimedea."


def generateVariables(obj) -> str:
    try:
        text = ts.get(f"{pf}var")
        for var in obj["Variables"]:
            archi_data = conquest_var["var"]
            if not archi_data:
                return ""
            text += f"\n- **{archi_data[var]['key']}**: {archi_data[var]['simple']}"
        return text
    except KeyError as e:
        print(f"KeyError in archimedea: {e}")
        return ""


def generateMissions(obj) -> str:
    text = ""
    idx = 1
    for item in obj["Missions"]:
        # mission only
        text += f"{idx}. **{getMissionType(item['missionType'])}**"

        # faction
        # ({getFactions(item['faction'])})\n"

        # mission with deviation & risks
        # text += f"## {idx}. **{getMissionType(item['missionType'])}**"
        # # deviation
        # try:
        #     for jtem in item["difficulties"]:
        #         if jtem.get("type") == "CD_HARD":
        #             path: dict = conquest_var["deviation"][jtem["deviation"]]
        #             text += f"\n- {ts.get(f'{pf}deviation')}: {path['key']} - {path['value']}"
        #             break
        # except Exception as e:
        #     print(e)
        #     pass
        #
        # # risks
        # try:
        #     risks: dict = {}
        #     for jtem in item["difficulties"]:
        #         if jtem.get("type") == "CD_HARD":
        #             risks = jtem.get("risks")
        #             # text += ", ".join(jtem.get("risks"))
        #             break
        #     for rsk in risks:
        #         path: dict = conquest_var["risks"][rsk]
        #         text += f"\n- {ts.get(f'{pf}risks')}: {path['key']} - {path['value']}"
        # except Exception as e:
        #     print(e)
        #     pass

        text += "\n"
        idx += 1

    return text


pfd: str = "cmd.deep-archimedea."


def w_deepArchimedea(archimedea) -> tuple[discord.Embed, str]:
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
    output_msg = ts.get(f"{pfd}content").format(
        time=convert_remain(deep["Expiry"]["$date"]["$numberLong"])
    )
    # missions
    output_msg += generateMissions(deep)
    # risks & global variables
    output_msg += generateVariables(deep)

    embed = discord.Embed(description=output_msg, color=discord.Color.dark_gold())
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "deep"


pft: str = "cmd.temporal-archimedea."


def w_temporalArchimedia(archimedea) -> tuple[discord.Embed, str]:
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
    output_msg += generateMissions(temporal)
    # global variables
    output_msg += generateVariables(temporal)

    embed = discord.Embed(description=output_msg, color=discord.Color.teal())
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "temporal"


# from src.constants.keys import ARCHIMEDEA
# from src.utils.data_manager import get_obj
# print(w_deepArchimedea(get_obj(ARCHIMEDEA))[0].description)
# print()
# print(w_temporalArchimedia(get_obj(ARCHIMEDEA))[0].description)
