from translator import ts

from module.parser.alerts import w_alerts
from module.parser.news import w_news
from module.parser.cetusCycle import w_cetusCycle
from module.parser.sortie import w_sortie
from module.parser.archonHunt import w_archonHunt
from module.parser.voidTraders import w_voidTraders, w_voidTradersItem
from module.parser.steelPath import w_steelPath
from module.parser.duviriCycle import w_duviriCycle
from module.parser.deepArchimedea import w_deepArchimedea
from module.parser.temporalArchimedea import w_temporalArchimedia
from module.parser.fissures import w_fissures
from module.parser.calendar import w_calendar
from module.parser.cambionCycle import w_cambionCycle
from module.parser.dailyDeals import w_dailyDeals
from module.parser.invasions import w_invasions


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
    # TODO: improve
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
    "deepArchimedea": {
        "parser": w_deepArchimedea,
        "update_check": lambda prev, new: prev["activation"] != new["activation"],
    },
    "temporalArchimedea": {
        "parser": w_temporalArchimedia,
        "update_check": lambda prev, new: prev["activation"] != new["activation"],
    },
    "calendar": {
        "parser": lambda data: w_calendar(data, ts.get("cmd.alendar.choice-prize")),
        "update_check": lambda prev, new: prev
        and new
        and prev[0]["activation"] != new[0]["activation"],
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
