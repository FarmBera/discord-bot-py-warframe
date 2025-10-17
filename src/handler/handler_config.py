from src.translator import ts

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

    return (prev_data.get("activation"), prev_data.get("active")) != (
        new_data.get("activation"),
        new_data.get("active"),
    )


DATA_HANDLERS = {
    "alerts": {
        "parser": w_alerts,
        "special_logic": "handle_missing_items",
    },
    "news": {
        "parser": w_news,
        "special_logic": "handle_missing_items",
        "channel_key": "news",
    },
    "cetusCycle": {
        "parser": w_cetusCycle,
        "update_check": lambda prev, new: prev["state"] != new["state"]
        or prev["activation"] != new["activation"],
    },
    "sortie": {
        "parser": w_sortie,
        "update_check": lambda prev, new: prev["id"] != new["id"]
        or prev["activation"] != new["activation"],
        "channel_key": "sortie",
    },
    "archonHunt": {
        "parser": w_archonHunt,
        "update_check": lambda prev, new: prev["activation"] != new["activation"],
        "channel_key": "sortie",
    },
    "voidTraders": {
        "parser": w_voidTraders,
        "update_check": _check_void_trader_update,
    },
    "steelPath": {
        "parser": w_steelPath,
        "update_check": lambda prev, new: prev["currentReward"] != new["currentReward"],
    },
    "duviriCycle": {
        "parser": w_duviriCycle,
        "update_check": lambda prev, new: prev["state"] != new["state"]
        or prev["activation"] != new["activation"],
    },
    "calendar": {
        "parser": lambda data: w_calendar(data, ts.get("cmd.calendar.choice-prize")),
        "update_check": lambda prev, new: prev["activation"] != new["activation"],
        "channel_key": "hex-cal",
    },
    "cambionCycle": {
        "parser": w_cambionCycle,
        "update_check": lambda prev, new: prev["state"] != new["state"]
        or prev["activation"] != new["activation"],
    },
    "dailyDeals": {
        "parser": w_dailyDeals,
        "update_check": lambda prev, new: prev[0]["item"] != new[0]["item"],
    },
    "invasions": {
        "parser": w_invasions,
        "special_logic": "handle_missing_invasions",
        "channel_key": "invasions",
    },
}
