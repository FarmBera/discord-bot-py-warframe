filePfx: str = "docs/"
configPfx: str = "config/"
JSON: str = "api_cache"
fileExt: str = ".md"

LOG_FILE_PATH: str = "log/log.csv"
SETTING_FILE_LOC: str = f"{configPfx}setting.json"
CHANNEL_FILE_LOC: str = f"{configPfx}channel"

HELP_FILE_LOC: str = f"{filePfx}help{fileExt}"
ANNOUNCE_FILE_LOC: str = f"{filePfx}announcement{fileExt}"
PATCHNOTE_FILE_LOC: str = f"{filePfx}patch-note{fileExt}"
POLICY_FILE_LOC: str = f"{filePfx}privacy-policy{fileExt}"
FOOTER_FILE_LOC: str = f"{filePfx}footer{fileExt}"
STARTED_TIME_FILE_LOC: str = f"{filePfx}m-started_time{fileExt}"
DELTA_TIME_LOC: str = f"{filePfx}m-delta{fileExt}"
MARKET_HELP_FILE: str = f"{filePfx}market-help{fileExt}"


MSG_BOT: str = "bot.self"

ALERTS = "Alerts"
NEWS = "Events"
CETUSCYCLE = "cetusCycle"
SORTIE = "Sorties"
ARCHONHUNT = "LiteSorties"
VOIDTRADERS = "VoidTraders"
STEELPATH = "steelPath"
DUVIRICYCLE = "duviriCycle"
DEEPARCHIMEDEA = "deepArchimedea"
TEMPORALARCHIMEDEA = "temporalArchimedea"
FISSURES = "ActiveMissions"
CALENDAR = "KnownCalendarSeasons"
CAMBIONCYCLE = "cambionCycle"
DAILYDEALS = "DailyDeals"
INVASIONS = "Invasions"
MARKET_SEARCH = "market-search"
VALLISCYCLE = "vallisCycle"

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


SPECIAL_ITEM_LIST = ["exilus", "orokin", "reactor", "forma"]
