from config.config import Lang
from src.constants.color import C
from src.constants.keys import JSON, SETTING_FILE_LOC
from src.translator import language as _default_lang
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


# convert object to human-readable — load both language datasets
_all_sol_nodes = {
    Lang.EN: json_load(f"data/{Lang.EN}/solNodes.json"),
    Lang.KO: json_load(f"data/{Lang.KO}/solNodes.json"),
}
_all_mission_types = {
    Lang.EN: json_load(f"data/{Lang.EN}/missionTypes.json"),
    Lang.KO: json_load(f"data/{Lang.KO}/missionTypes.json"),
}
_all_sortie_data = {
    Lang.EN: json_load(f"data/{Lang.EN}/sortieData.json"),
    Lang.KO: json_load(f"data/{Lang.KO}/sortieData.json"),
}
_all_languages = {
    Lang.EN: json_load(f"data/{Lang.EN}/languages.json"),
    Lang.KO: json_load(f"data/{Lang.KO}/languages.json"),
}
_all_factions = {
    Lang.EN: json_load(f"data/{Lang.EN}/factionsData.json"),
    Lang.KO: json_load(f"data/{Lang.KO}/factionsData.json"),
}
_all_fissure_modifiers = {
    Lang.EN: json_load(f"data/{Lang.EN}/fissureModifiers.json"),
    Lang.KO: json_load(f"data/{Lang.KO}/fissureModifiers.json"),
}

# backward-compat globals (used by legacy direct-access code)
solNodes = _all_sol_nodes[_default_lang]
missionTypes = _all_mission_types[_default_lang]
sortieData = _all_sortie_data[_default_lang]
languages = _all_languages[_default_lang]
factionsData = _all_factions[_default_lang]
fissureModifiers = _all_fissure_modifiers[_default_lang]


def getSolNodeData(node: str, lang: str = _default_lang) -> dict:
    """return full solNode dict (type, value, enemy)"""
    return _all_sol_nodes.get(lang, _all_sol_nodes[_default_lang]).get(node, {})


def getSolNode(node: str, lang: str = _default_lang) -> str:
    """return node name & planet

    :param node: solNodes like 'SolNode22'
    :param lang: language to parse
    :return: solNode's name and planet like 'Tessera (Venus)'
    """
    return getSolNodeData(node, lang).get("value", node)


def getNodeEnemy(node: str, lang: str = _default_lang) -> str:
    """return node's enemy factions

    :param node: solNodes like 'SolNode22'
    :param lang: language to parse
    :return: solNode's enemy faction like 'Corpus'
    """
    return getSolNodeData(node, lang).get("enemy", f"unknown: {node}")


def getMissionType(miss: str, lang: str = _default_lang) -> str:
    """return mission type

    :param miss: mission code like 'MT_CAPTURE'
    :param lang: language to parse
    :return: ingame mission name like 'Capture'
    """
    return (
        _all_mission_types.get(lang, _all_mission_types[_default_lang])
        .get(miss, {})
        .get("value", miss)
    )


def getSortieMod(modifier: str, lang: str = _default_lang) -> str:
    """return sortie modifier title

    :param modifier: modifier code like 'SORTIE_MODIFIER_LOW_ENERGY'
    :param lang: language to parse
    :return: simple sortie modifier description like 'Energy Reduction'
    """
    return (
        _all_sortie_data.get(lang, _all_sortie_data[_default_lang])
        .get("modifierTypes", {})
        .get(modifier, modifier)
    )


def getSortieModDesc(modifier: str, lang: str = _default_lang) -> str:
    """return sortie modifier descriptions

    :param modifier: modifier code like 'SORTIE_MODIFIER_LOW_ENERGY'
    :param lang: language to parse
    :return: full sortie modifier description like 'Maximum Warframe Energy capacity is quartered.'
    """
    return (
        _all_sortie_data.get(lang, _all_sortie_data[_default_lang])
        .get("modifierDescriptions", {})
        .get(modifier, modifier)
    )


def getLanguageOrigin(key_data: str, lang: str = _default_lang):
    return _all_languages.get(lang, _all_languages[_default_lang]).get(key_data)


def getLanguage(data: str, query1: str = "value", lang: str = _default_lang) -> str:
    """convert /Lotus path into item name etc

    :param data: item name with game path like '/lotus/storeitems/types/items/miscitems/formaumbra'
    :param query1: special key in query
    :param lang: language to parse
    :return: parsed name like 'Umbra Forma'
    """
    if not data:
        return ""

    _languages = _all_languages.get(lang, _all_languages[_default_lang])
    mapping = _languages.get(data) or _languages.get(data.lower())
    if mapping:
        result = mapping.get(query1)
        if result:
            return result

    splitted = data.split("/")
    if len(splitted) > 1 and splitted[1].lower() == "lotus":
        return add_space(splitted[-1])

    return data


def getFactions(factions: str, lang: str = _default_lang) -> str:
    """return enemy factions data

    :param factions: enemy faction code like 'FC_SENTIENT'
    :param lang: language to parse
    :return: ingame name like 'Sentient'
    """
    return (
        _all_factions.get(lang, _all_factions[_default_lang])
        .get(factions, {})
        .get("value", factions)
    )


def getFissure(fiss: str, lang: str = _default_lang) -> str:
    """returns fissure name

    :param fiss: fissure code like 'VoidT2'
    :param lang: language to parse
    :return: fissure name like 'Meso'
    """
    return (
        _all_fissure_modifiers.get(lang, _all_fissure_modifiers[_default_lang])
        .get(fiss, {})
        .get("value", fiss)
    )
