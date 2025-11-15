from src.translator import ts
from src.constants.keys import (
    ALERTS,
    NEWS,
    SORTIE,
    ARCHONHUNT,
    VOIDTRADERS,
    FISSURES,
    CALENDAR,
    DAILYDEALS,
    INVASIONS,
    DUVIRI_ROTATION,
    EVENTS,
)
from src.parser.alerts import w_alerts
from src.parser.news import w_news
from src.parser.cetusCycle import w_cetusCycle
from src.parser.sortie import w_sortie
from src.parser.archonHunt import w_archonHunt
from src.parser.voidTraders import w_voidTraders
from src.parser.steelPath import w_steelPath
from src.parser.duviriCycle import w_duviriCycle
from src.parser.calendar import w_calendar
from src.parser.cambionCycle import w_cambionCycle
from src.parser.dailyDeals import w_dailyDeals
from src.parser.invasions import w_invasions, w_invasions_se
from src.parser.duviriRotation import w_duviri_warframe, w_duviri_incarnon
from src.parser.events import w_events


DATA_HANDLERS = {
    ALERTS: {
        "parser": w_alerts,
        "special_logic": "handle_missing_items",
    },
    NEWS: {
        "parser": w_news,
        "special_logic": "handle_new_news",
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
        "special_logic": "handle_voidtraders",
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
    FISSURES: {"special_logic": "handle_fissures"},
    CALENDAR: {
        "parser": lambda data: w_calendar(data, ts.get("cmd.calendar.choice-prize")),
        "update_check": lambda prev, new: prev[0]["Activation"]["$date"]["$numberLong"]
        != new[0]["Activation"]["$date"]["$numberLong"],
        "channel_key": "hex-cal",
    },
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
        "parser": w_invasions_se,
        "special_logic": "handle_missing_invasions",
        "channel_key": "invasions",
    },
    DUVIRI_ROTATION: {  # circuit-warframe
        "parser": w_duviri_warframe,
        "special_logic": "handle_duviri_rotation-1",
    },
    DUVIRI_ROTATION: {  # circuit-incarnon
        "parser": w_duviri_incarnon,
        "special_logic": "handle_duviri_rotation-2",
    },
    EVENTS: {
        "parser": w_events,
        "special_logic": "handle_missing_items",
    },
}
