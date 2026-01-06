from src.utils.file_io import (
    json_load,
    json_save,
    yaml_open,
    json_load_async,
    json_save_async,
)
from src.constants.color import C
from src.translator import language as lang
from src.constants.keys import JSON, CHANNEL_FILE_LOC, SETTING_FILE_LOC


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


CHANNELS = yaml_open(CHANNEL_FILE_LOC)
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

    Args:
        node (str): solNodes like 'SolNode22'

    Returns:
        str: return solNode's name and planet like 'Tessera (Venus)'
    """
    return solNodes.get(node, {}).get("value", node)


def getNodeEnemy(node: str) -> str:
    """return node's enemy factions

    Args:
        node (str): solNodes like 'SolNode22'

    Returns:
        str: return solNode's enemy faction like 'Corpus'
    """
    return solNodes.get(node, {}).get("enemy", f"unknown: {node}")


def getMissionType(miss: str) -> str:
    """return mission type

    Args:
        miss (str): mission code like 'MT_CAPTURE'

    Returns:
        str: Capture
    """
    return missionTypes.get(miss, {}).get("value", miss)


def getSortieMod(modifier: str) -> str:
    """return sortie modifier title

    Args:
        modifier (str): modifier code like 'SORTIE_MODIFIER_LOW_ENERGY'

    Returns:
        str: return simple sortie modifier description like 'Energy Reduction'
    """
    return sortieData.get("modifierTypes", {}).get(modifier, modifier)


def getSortieModDesc(modifier: str) -> str:
    """return sortie modifier descriptions

    Args:
        modifier (str): modifier code like 'SORTIE_MODIFIER_LOW_ENERGY'

    Returns:
        str: return detailed sortie modifier description like 'Maximum Warframe Energy capacity is quartered. Energy Siphon is less effective.'
    """
    return sortieData.get("modifierDescriptions", {}).get(modifier, modifier)


def getLanguage(data: str, query1: str = "value") -> str:
    """convert /Lotus path into item name etc

    :param data: item name with game path like '/lotus/storeitems/types/items/miscitems/formaumbra'
    :param query1: special key in query
    :return: parsed /lotus path
    """
    result = languages.get(data, {}).get(query1)
    return result if result else languages.get(data.lower(), {}).get(query1, data)


def getFactions(factions: str) -> str:
    """return enemy factions data

    Args:
        factions (str): enemy faction code like 'FC_SENTIENT'

    Returns:
        str: return ingame name like 'Sentient'
    """
    return factionsData.get(factions, {}).get("value", factions)


def getFissure(fiss: str) -> str:
    """return fissure name

    Args:
        fiss (str): fissure code like 'VoidT2'

    Returns:
        str: return fissure name like 'Meso'
    """
    return fissureModifiers.get(fiss, {}).get("value", fiss)
