import discord
import datetime as dt

from src.translator import ts
from src.constants.keys import DUVIRI_ROTATION
from src.utils.emoji import get_emoji
from src.utils.data_manager import get_obj
from src.utils.times import timeNowDT  # , convert_remain, convert_diff
from src.utils.return_err import err_embed

rotation_data = get_obj("RotationDuviri")
IDX_MAX_WAF: int = 11
IDX_MAX_INC: int = 8
ADD_ONE_WEEK: int = 604800


def convert_diff(unix_timestamp: int | str):
    from src.translator import ts

    try:
        ts_str = str(unix_timestamp)

        # convert milliseconds into seconds
        if len(ts_str) == 13:
            ts_int = int(ts_str) / 1000
        else:
            ts_int = int(ts_str)

    except (ValueError, TypeError):
        return "Wrong Timestamp Format"

    # convert into datetime obj
    now_dt = timeNowDT()
    input_dt = dt.datetime.fromtimestamp(ts_int)

    # calculate time diff
    diff = now_dt - input_dt
    time_difference = abs(diff)

    # extract day, hour, minute
    days = time_difference.days
    remaining_seconds = time_difference.seconds
    # hours = remaining_seconds // 3600
    # minutes = (remaining_seconds % 3600) // 60

    output: list = []
    if days > 0:
        output.append(f"{days}{ts.get('time.day')}")

    return " ".join(output)


def w_duviri_warframe(rotation) -> discord.Embed:
    if not rotation:
        return err_embed("w_duviri_warframe")

    pf: str = "cmd.duviri-circuit."

    curr_rotation = rotation[0]["Choices"]
    tstamp: int = rotation_data["expiry"]

    # title
    output_msg: str = f"# {ts.get(f'{pf}circuit')} - {ts.get(f'{pf}wf-title')}\n"
    # items
    output_msg += "- " + ", ".join(
        [f"{get_emoji(item)} {ts.trs(item)}" for item in curr_rotation]
    )

    # next items
    warframe_list = rotation_data["warframe"]
    length = len(warframe_list)

    if length == 0:
        embed = discord.Embed(description=output_msg)
        return embed

    # init index (find curr index)
    idx, idx_init = 0, 0
    for item in warframe_list:
        if set(item) == set(curr_rotation):
            idx_init = idx
            break
        idx += 1

    # create next rotation list
    output_msg += f"\n### {ts.get(f'{pf}next-rotate')}\n"
    for _ in range(length - 1):
        idx = (idx + 1) % length
        if idx == idx_init:
            break

        jtem = warframe_list[idx]
        tstamp += ADD_ONE_WEEK
        output_msg += (
            f"- {ts.get(f'{pf}coming').format(day=convert_diff(tstamp))}: "
            + ", ".join([f"{get_emoji(i)} {ts.trs(i)}" for i in jtem])
            + "\n"
        )

    embed = discord.Embed(description=output_msg)
    return embed


# TODO: 초기화 시간 명시
def w_duviri_incarnon(incarnon) -> discord.Embed:
    if not incarnon:
        return err_embed("w_duviri_warframe")

    pf: str = "cmd.duviri-circuit."
    curr_rotation = incarnon[1]["Choices"]
    tstamp: int = rotation_data["expiry"]

    # title
    output_msg: str = f"# {ts.get(f'{pf}circuit')} - {ts.get(f'{pf}inc-title')}\n"
    # items
    output_msg += "- " + ", ".join(
        [f"{get_emoji(i)} {ts.trs(i)}" for i in curr_rotation]
    )

    # next items
    incarnon_list = rotation_data["incarnon"]
    length = len(incarnon_list)

    if length == 0:
        embed = discord.Embed(description=output_msg)
        return embed

    # init index (find curr index)
    idx, idx_init = 0, 0
    for item in incarnon_list:
        if set(item) == set(curr_rotation):
            idx_init = idx
            break
        idx += 1

    # create next rotation list
    output_msg += f"\n### {ts.get(f'{pf}next-rotate')}\n"
    for _ in range(length - 1):
        idx = (idx + 1) % length
        if idx == idx_init:
            break

        jtem = incarnon_list[idx]
        tstamp += ADD_ONE_WEEK
        output_msg += (
            f"- {ts.get(f'{pf}coming').format(day=convert_diff(tstamp))}: "
            + ", ".join([f"{get_emoji(i)} {ts.trs(i)}" for i in jtem])
            + "\n"
        )
    embed = discord.Embed(description=output_msg, color=0x65E6E1)
    return embed


# print(rotation_data["warframe"][1])
# print(w_duviri_warframe(get_obj(DUVIRI_ROTATION)).description)
# print(w_duviri_incarnon(get_obj(DUVIRI_ROTATION)).description)
