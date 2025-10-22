from src.translator import ts

from src.constants.keys import (
    ALERTS,
    NEWS,
    SORTIE,
    ARCHONHUNT,
    VOIDTRADERS,
    CALENDAR,
    DAILYDEALS,
    INVASIONS,
)

from src.parser.alerts import w_alerts
from src.parser.news import w_news
from src.parser.cetusCycle import w_cetusCycle
from src.parser.sortie import w_sortie
from src.parser.archonHunt import w_archonHunt
from src.parser.voidTraders import w_voidTraders
from src.parser.steelPath import w_steelPath
from src.parser.duviriCycle import w_duviriCycle
from src.parser.deepArchimedea import w_deepArchimedea
from src.parser.temporalArchimedea import w_temporalArchimedia
from src.parser.fissures import w_fissures
from src.parser.calendar import w_calendar
from src.parser.cambionCycle import w_cambionCycle
from src.parser.dailyDeals import w_dailyDeals
from src.parser.invasions import w_invasions


def _check_void_trader_update(prev, new):
    """
    Checks for updates regardless of the data structure (dict or list) of voidTraders
    """

    prev_data = prev[-1] if isinstance(prev, list) and prev else prev
    new_data = new[-1] if isinstance(new, list) and new else new

    if not isinstance(prev_data, dict) or not isinstance(new_data, dict):
        return prev != new
        # perform a simple comparison. data structure is diff than normal

    return prev_data.get("Activation") != new_data.get("Activation")


DATA_HANDLERS = {
    ALERTS: {
        "parser": w_alerts,
        "special_logic": "handle_missing_items",
    },
    NEWS: {
        "parser": w_news,
        "special_logic": "handle_missing_items",
        "channel_key": "news",
    },
    # "cetusCycle": {
    #     "parser": w_cetusCycle,
    #     "update_check": lambda prev, new: prev["state"] != new["state"]
    #     or prev["activation"] != new["activation"],
    # },
    SORTIE: {
        "parser": w_sortie,
        "update_check": lambda prev, new: prev[0]["_id"]["$oid"]
        != new[0]["_id"]["$oid"]
        or prev[0]["Activation"]["$date"] != new[0]["Activation"]["$date"],
        "channel_key": "sortie",
    },
    ARCHONHUNT: {
        "parser": w_archonHunt,
        "update_check": lambda prev, new: prev[0]["Activation"] != new[0]["Activation"],
        "channel_key": "sortie",
    },
    VOIDTRADERS: {
        "parser": w_voidTraders,
        "update_check": _check_void_trader_update,
    },
    # "steelPath": {
    #     "parser": w_steelPath,
    #     "update_check": lambda prev, new: prev["currentReward"] != new["currentReward"],
    # },
    # "duviriCycle": {
    #     "parser": w_duviriCycle,
    #     "update_check": lambda prev, new: prev["state"] != new["state"]
    #     or prev["activation"] != new["activation"],
    # },
    # CALENDAR: {
    #     "parser": lambda data: w_calendar(data, ts.get("cmd.calendar.choice-prize")),
    #     "update_check": lambda prev, new: prev["activation"] != new["activation"],
    #     "channel_key": "hex-cal",
    # },
    # "cambionCycle": {
    #     "parser": w_cambionCycle,
    #     "update_check": lambda prev, new: prev["state"] != new["state"]
    #     or prev["activation"] != new["activation"],
    # },
    DAILYDEALS: {
        "parser": w_dailyDeals,
        "update_check": lambda prev, new: prev[0]["StoreItem"] != new[0]["StoreItem"],
    },
    INVASIONS: {
        "parser": w_invasions,
        "special_logic": "handle_missing_invasions",
        "channel_key": "invasions",
    },
}
