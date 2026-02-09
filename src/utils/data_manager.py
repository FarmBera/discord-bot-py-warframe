from src.constants.color import C
from src.constants.keys import JSON, SETTING_FILE_LOC
from src.translator import language as lang
from src.utils.file_io import (
    json_load,
    json_save,
    json_load_async,
    json_save_async,
)
from src.utils.formatter import add_space


def get_obj(json_name: str):
    return json_load(f"{JSON}/{json_name}.json")


def set_obj(obj, filename: str) -> bool:
    return json_save(obj, f"{JSON}/{filename}.json")


async def get_obj_async(json_name: str):
    return await json_load_async(f"{JSON}/{json_name}.json")


async def set_obj_async(obj, filename: str) -> bool:
    return await json_save_async(obj, f"{JSON}/{filename}.json")


async def cmd_obj_check(name):
    obj = get_obj_async(name)
    if not obj:  # or not obj:
        print(f"{C.red}[err] Unknown '{name}' command. (from cmd_obj_check){C.default}")
        return False

    return obj


SETTINGS = json_load(SETTING_FILE_LOC)


# convert object to human-readable

solNodes = json_load(f"data/{lang}/solNodes.json")
missionTypes = json_load(f"data/{lang}/missionTypes.json")
sortieData = json_load(f"data/{lang}/sortieData.json")
languages = json_load(f"data/{lang}/languages.json")
factionsData = json_load(f"data/{lang}/factionsData.json")
fissureModifiers = json_load(f"data/{lang}/fissureModifiers.json")


def getSolNode(node: str) -> str:
    """return node name & planet

    :param node: solNodes like 'SolNode22'
    :return: solNode's name and planet like 'Tessera (Venus)'
    """
    return solNodes.get(node, {}).get("value", node)


def getNodeEnemy(node: str) -> str:
    """return node's enemy factions

    :param node: solNodes like 'SolNode22'
    :return: solNode's enemy faction like 'Corpus'
    """
    return solNodes.get(node, {}).get("enemy", f"unknown: {node}")


def getMissionType(miss: str) -> str:
    """return mission type

    :param miss: mission code like 'MT_CAPTURE'
    :return: ingame mission name like 'Capture'
    """
    return missionTypes.get(miss, {}).get("value", miss)


def getSortieMod(modifier: str) -> str:
    """return sortie modifier title

    :param modifier: modifier code like 'SORTIE_MODIFIER_LOW_ENERGY'
    :return: simple sortie modifier description like 'Energy Reduction'
    """
    return sortieData.get("modifierTypes", {}).get(modifier, modifier)


def getSortieModDesc(modifier: str) -> str:
    """return sortie modifier descriptions

    :param modifier: modifier code like 'SORTIE_MODIFIER_LOW_ENERGY'
    :return: full sortie modifier description like 'Maximum Warframe Energy capacity is quartered.'
    """
    return sortieData.get("modifierDescriptions", {}).get(modifier, modifier)


def getLanguageOrigin(key_data: str):
    return languages.get(key_data)


def getLanguage(data: str, query1: str = "value") -> str:
    """convert /Lotus path into item name etc

    :param data: item name with game path like '/lotus/storeitems/types/items/miscitems/formaumbra'
    :param query1: special key in query
    :return: parsed name like 'Umbra Forma'
    """
    if not data:
        return ""

    mapping = languages.get(data) or languages.get(data.lower())
    if mapping:
        result = mapping.get(query1)
        if result:
            return result

    splitted = data.split("/")
    if len(splitted) > 1 and splitted[1].lower() == "lotus":
        return add_space(splitted[-1])

    return data


def getFactions(factions: str) -> str:
    """return enemy factions data

    :param factions: enemy faction code like 'FC_SENTIENT'
    :return: ingame name like 'Sentient'
    """
    return factionsData.get(factions, {}).get("value", factions)


def getFissure(fiss: str) -> str:
    """returns fissure name

    :param fiss: fissure code like 'VoidT2'
    :return: fissure name like 'Meso'
    """
    return fissureModifiers.get(fiss, {}).get("value", fiss)
