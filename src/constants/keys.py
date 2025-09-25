filePfx: str = "docs/"
configPfx: str = "config/"

LOG_FILE_PATH: str = "log/log.csv"
SETTING_FILE_LOC: str = f"{configPfx}setting.json"
CHANNEL_FILE_LOC: str = f"{configPfx}channel"

HELP_FILE_LOC: str = f"{filePfx}help.md"
ANNOUNCE_FILE_LOC: str = f"{filePfx}announcement.md"
PATCHNOTE_FILE_LOC: str = f"{filePfx}patch-note.md"
POLICY_FILE_LOC: str = f"{filePfx}privacy-policy.md"
FOOTER_FILE_LOC: str = f"{filePfx}footer.md"
STARTED_TIME_FILE_LOC: str = f"{filePfx}m-started_time.md"
DELTA_TIME_LOC: str = f"{filePfx}m-delta.md"


MSG_BOT: str = "bot.self"

keys: list = [
    "alerts",  # 0
    "news",  # 1
    "cetusCycle",  # 2
    "sortie",  # 3
    "archonHunt",  # 4
    "voidTraders",  # 5
    "steelPath",  # 6
    "duviriCycle",  # 7
    # "deepArchimedea",  # 8
    # "temporalArchimedea",  # 9
    "fissures",  # 10
    "calendar",  # 11
    "cambionCycle",  # 12
    "dailyDeals",  # 13
    "invasions",  # 14
]

cal_item: dict = {
    "Riven": "Riven Mod",
    "Forma": "Forma Blueprint",
    "Exilus Adapter": "Exilus Warframe Adapter",
    # "[PH] Calendar Kill Enemies With Melee Medium Desc": "kill Enemies With Melee Weapons",
}
