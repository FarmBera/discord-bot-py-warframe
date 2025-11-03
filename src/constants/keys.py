from config.config import language as lang

# commands cooldown time (sec)
COOLDOWN_DEFAULT: float = 10.0
COOLDOWN_PARTY: float = 60.0
COOLDOWN_BTN_ACTION: float = 20.0  # join/leave
COOLDOWN_BTN_MANAGE: float = 60.0  # modify/remove


filePfx: str = f"docs/{lang}/"
configPfx: str = "config/"
JSON: str = "api_cache"
fileExt: str = ".md"

# json file location
DEFAULT_JSON_PATH: str = f"data/Warframe.json"
DEFAULT_MARKET_JSON_PATH: str = f"data/market-search.json"
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
STARTED_TIME_FILE_LOC: str = f"docs/m-started_time{fileExt}"
DELTA_TIME_LOC: str = f"docs/m-delta{fileExt}"
MARKET_HELP_FILE: str = f"{filePfx}market-help{fileExt}"


MSG_BOT: str = "bot.self"


ALERTS: str = "Alerts"
NEWS: str = "Events"
CETUSCYCLE: str = "cetusCycle"
SORTIE: str = "Sorties"
ARCHONHUNT: str = "LiteSorties"
VOIDTRADERS: str = "VoidTraders"
STEELPATH: str = "steelPath"
DUVIRICYCLE: str = "duviriCycle"
DEEPARCHIMEDEA: str = "deepArchimedea"
TEMPORALARCHIMEDEA: str = "temporalArchimedea"
FISSURES: str = "ActiveMissions"
CALENDAR: str = "KnownCalendarSeasons"
CAMBIONCYCLE: str = "cambionCycle"
DAILYDEALS: str = "DailyDeals"
INVASIONS: str = "Invasions"
MARKET_SEARCH: str = "market-search"
VALLISCYCLE: str = "vallisCycle"

keys: list = [
    ALERTS,  # 0
    NEWS,  # 1
    # CETUSCYCLE,  # 2
    SORTIE,  # 3
    ARCHONHUNT,  # 4
    VOIDTRADERS,  # 5
    # STEELPATH,  # 6
    # DUVIRICYCLE,  # 7
    # DEEPARCHIMEDEA,  # 8
    # TEMPORALARCHIMEDEA,  # 9
    FISSURES,  # 10
    CALENDAR,  # 11
    # CAMBIONCYCLE,  # 12
    DAILYDEALS,  # 13
    INVASIONS,  # 14
    # VALLISCYCLE,
]


SPECIAL_ITEM_LIST: list = ["exilus", "orokin", "reactor", "forma"]

LFG_WEBHOOK_NAME: str = "warframe-lfg-bot"
