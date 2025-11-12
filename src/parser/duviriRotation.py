import discord
import datetime as dt

from src.translator import ts
from src.utils.emoji import get_emoji
from src.utils.formatter import time_cal_with_curr
from src.utils.return_err import err_embed


# TODO: 초기화 시간 명시
def w_duviri_warframe(rotation) -> discord.Embed:
    if not rotation:
        return err_embed("w_duviri_warframe")

    pf: str = "cmd.duviri-circuit."

    # title
    output_msg: str = f"## {ts.get(f'{pf}wf-title')}\n"
    # items
    for item in rotation[0]["Choices"]:
        output_msg += f"- {get_emoji(item)} {ts.trs(item)}\n"

    embed = discord.Embed(description=output_msg)
    return embed


# TODO: 초기화 시간 명시
def w_duviri_incarnon(incarnon) -> discord.Embed:
    if not incarnon:
        return err_embed("w_duviri_warframe")

    pf: str = "cmd.duviri-circuit."
    # title
    output_msg: str = f"## {ts.get(f'{pf}inc-title')}\n"
    # items
    for item in incarnon[1]["Choices"]:
        output_msg += f"- {get_emoji(item)} {ts.trs(item)}\n"

    embed = discord.Embed(description=output_msg, color=0x65E6E1)
    return embed
