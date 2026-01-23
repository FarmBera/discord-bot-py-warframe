from config.config import language as lang

# commands cooldown time (sec)
CDN: float = 1.0
COOLDOWN_DEFAULT: float = 10.0
COOLDOWN_CREATE: float = 60.0
COOLDOWN_BTN_ACTION: float = 15.0  # btn join/leave
COOLDOWN_BTN_MANAGE: float = 15.0  # btn modify/remove
COOLDOWN_5_MIN: float = 300.0  # 5 minute cooldown
COOLDOWN_BTN_CALL: float = 900.0  # btn call members


filePfx: str = f"docs/{lang}/"
configPfx: str = "config/"
JSON: str = "api_cache"
fileExt: str = ".md"

# json file location
# DEFAULT_JSON_PATH: str = f"data/Warframe.json"
# DEFAULT_MARKET_JSON_PATH: str = f"data/market-search.json"
# other file location
LOG_FILE_PATH: str = "log/log.csv"
SETTING_FILE_LOC: str = f"{configPfx}setting.json"
CHANNEL_FILE_LOC: str = f"{configPfx}channel"
# docs file list
HELP_FILE_LOC: str = f"{filePfx}help{fileExt}"
ANNOUNCE_FILE_LOC: str = f"{filePfx}announcement{fileExt}"
PATCHNOTE_FILE_LOC: str = f"{filePfx}patch-note{fileExt}"
POLICY_FILE_LOC: str = f"{filePfx}privacy-policy{fileExt}"
FOOTER_FILE_LOC: str = f"{filePfx}footer{fileExt}"


MSG_BOT: str = "bot.self"


ALERTS: str = "Alerts"
NEWS: str = "Events"
CETUSCYCLE: str = "cetusCycle"
SORTIE: str = "Sorties"
ARCHONHUNT: str = "LiteSorties"
VOIDTRADERS: str = "VoidTraders"
STEELPATH: str = "steelPath"
DUVIRICYCLE: str = "duviriCycle"
ARCHIMEDEA: str = "Conquests"
FISSURES: str = "ActiveMissions"
CALENDAR: str = "KnownCalendarSeasons"
CAMBIONCYCLE: str = "cambionCycle"
DAILYDEALS: str = "DailyDeals"
INVASIONS: str = "Invasions"
MARKET_SEARCH: str = "market-search"
VALLISCYCLE: str = "vallisCycle"
DUVIRI_ROTATION: str = "EndlessXpChoices"
EVENTS: str = "Goals"
# CODA: str = ""  # coda weapon
EVENT_BOOSTER: str = ""
DESCENDIA: str = "Descents"
ARBITRATION: str = "arbitration"
WORLDSTATE: str = "WorldState"

DUVIRI_U_K_W: str = "Warframe"
DUVIRI_U_K_I: str = "Incarnon"
DUVIRI_CACHE: str = "RotationDuviri"

ARCHIMEDEA_DEEP: str = "Deep"
ARCHIMEDEA_TEMPORAL: str = "Temporal"

keys: list = [
    ALERTS,
    NEWS,
    # CETUSCYCLE,
    SORTIE,
    ARCHONHUNT,
    VOIDTRADERS,
    # STEELPATH,
    # DUVIRICYCLE,
    ARCHIMEDEA,
    FISSURES,
    CALENDAR,
    # CAMBIONCYCLE,
    DAILYDEALS,
    INVASIONS,
    # VALLISCYCLE,
    DUVIRI_ROTATION,
    EVENTS,
    DESCENDIA,
]

LFG_WEBHOOK_NAME: str = "cat-prime-profile"

SPECIAL_ITEM_LIST: list = [
    # en
    "exilus",
    "orokin",
    "reactor",
    "forma",
    # ko
    "오로킨",
    "포르마",
    "엑실러스",
]
