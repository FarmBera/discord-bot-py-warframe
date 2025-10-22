from src.utils.file_io import json_load, json_save
from src.constants.color import C
from src.translator import language as lang


def get_obj(json_name: str):
    return json_load(f"json/{json_name}.json")


def set_obj(obj, filename: str) -> bool:
    return json_save(obj, f"json/{filename}.json")


def cmd_obj_check(name):
    obj = get_obj(name)
    if not obj:  # or not obj:
        print(f"{C.red}[err] Unknown '{name}' command. (from cmd_obj_check){C.default}")
        return False

    return obj


# convert object to human readable

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


def getLanguage(data: str) -> str:
    """convert /Lotus path into item name etc

    Args:
        data (str): item name with game path like '/lotus/storeitems/types/items/miscitems/formaumbra'

    Returns:
        str: return real ingame item name like 'Umbra Forma'
    """
    return languages.get(data, {}).get("value", data)


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
