filePfx: str = "docs/"
configPfx: str = "config/"
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

ALERTS = "alerts"
NEWS = "news"
CETUSCYCLE = "cetusCycle"
SORTIE = "sortie"
ARCHONHUNT = "archonHunt"
VOIDTRADERS = "voidTraders"
STEELPATH = "steelPath"
DUVIRICYCLE = "duviriCycle"
DEEPARCHIMEDEA = "deepArchimedea"
TEMPORALARCHIMEDEA = "temporalArchimedea"
FISSURES = "fissures"
CALENDAR = "calendar"
CAMBIONCYCLE = "cambionCycle"
DAILYDEALS = "dailyDeals"
INVASIONS = "invasions"
MARKET_SEARCH = "market-search"
VALLISCYCLE = "vallisCycle"

keys: list = [
    ALERTS,  # 0
    NEWS,  # 1
    CETUSCYCLE,  # 2
    SORTIE,  # 3
    ARCHONHUNT,  # 4
    VOIDTRADERS,  # 5
    STEELPATH,  # 6
    DUVIRICYCLE,  # 7
    # DEEPARCHIMEDEA,  # 8
    # TEMPORALARCHIMEDEA,  # 9
    FISSURES,  # 10
    CALENDAR,  # 11
    CAMBIONCYCLE,  # 12
    DAILYDEALS,  # 13
    INVASIONS,  # 14
    VALLISCYCLE,
]

cal_item: dict = {
    "Riven": "Riven Mod",
    "Forma": "Forma Blueprint",
    "Exilus Adapter": "Exilus Warframe Adapter",
    # "[PH] Calendar Kill Enemies With Melee Medium Desc": "kill Enemies With Melee Weapons",
}
