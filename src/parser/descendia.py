import discord
import datetime as dt

from src.translator import ts, language as lang
from src.utils.times import convert_remain, timeNow, KST
from src.utils.data_manager import get_obj
from src.utils.file_io import json_load

descendiaLanguage = json_load(f"data/{lang}/descendiaLanguages.json")


def getDescendiaChallenge(challenge: str) -> str:
    return descendiaLanguage.get("challenge", {}).get(challenge, {})


def getDescendiaMiss(mission: str) -> str:
    return descendiaLanguage.get("missionType", {}).get(mission, {})


pf: str = "cmd.descendia."
format_string = "%Y-%m-%d %H:%M:%S"


def parseDate(timestamp: int) -> str:
    return dt.datetime.strftime(
        dt.datetime.fromtimestamp(int(timestamp), KST), format_string
    )


def check_date(start: str, end: str) -> bool:
    start = int(start)
    end = int(end)
    if start < timeNow() < end:
        return True
    return False


def w_descendia(descendia) -> tuple:
    if not descendia:
        return ts.get("general.error-cmd")

    this_week_content = None
    this_week_index: int = 0
    output_msg: str = ""

    # find this week's descendia challenges
    for item in descendia:
        activation_time: int = int(item["Activation"]["$date"]["$numberLong"][:10])
        expiry_time: int = int(item["Expiry"]["$date"]["$numberLong"][:10])
        if activation_time <= timeNow() <= expiry_time:
            this_week_content = item
            break

        this_week_index += 1

    output_msg += ts.get(f"{pf}title")

    if not this_week_content:
        output_msg = "ERROR: Descendia Content Not Found"

    for challenge in descendia[this_week_index]["Challenges"]:
        output_msg += f"{challenge['Index']:2d}. {getDescendiaMiss(challenge['Type'])} - {getDescendiaChallenge(challenge['Challenge'])}\n"

    f = "descendia"
    embed = discord.Embed(description=output_msg, color=0x883F0A)
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, f


# from src.constants.keys import DESCENDIA

# TEST_OBJECT = get_obj(DESCENDIA)
# print(w_descendia(TEST_OBJECT)[0].description)
