import discord
import datetime as dt
from dateutil.relativedelta import relativedelta

from src.translator import ts
from src.constants.keys import DUVIRI_ROTATION
from src.utils.emoji import get_emoji
from src.utils.data_manager import get_obj
from src.utils.discord_file import img_file
from src.utils.times import timeNowDT
from src.utils.return_err import err_embed

rotation_data = get_obj("RotationDuviri")
IDX_MAX_WAF: int = 11
IDX_MAX_INC: int = 8
ADD_ONE_WEEK: int = 604800


pf: str = "cmd.duviri-circuit."


def convert_diff(unix_timestamp: int | str) -> str:
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
    if now_dt >= input_dt:
        rdelta = relativedelta(now_dt, input_dt)
    else:
        # timestamp is future
        rdelta = relativedelta(input_dt, now_dt)

    # calculate month
    months = rdelta.years * 12 + rdelta.months
    days = rdelta.days

    output: list = []

    # month check
    if months > 0:
        if months == 1:
            output.append("한 달")
        elif months == 2:
            output.append("두 달")
        elif months >= 3:
            output.append("먼 훗날")

    elif days > 0:
        output.append(f"{days}{ts.get('time.day')}")

    return " ".join(output)


def create_embed(output_msg: str, color=None):
    f = img_file("zariman")
    embed = (
        discord.Embed(description=output_msg, color=color)
        if color
        else discord.Embed(description=output_msg)
    )
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f


def w_duviri_warframe(rotation):
    if not rotation:
        return err_embed("w_duviri_warframe")

    curr_rotation = rotation[0]["Choices"]
    tstamp: int = rotation_data["expiry"]

    # title
    output_msg: str = (
        f"# {ts.get(f'{pf}wf-lvl')} {ts.get(f'{pf}circuit')} - {ts.get(f'{pf}wf-title')}\n"
    )
    # sub-title
    output_msg += f"### __{ts.get(f'{pf}curr-rotate')}__\n"
    # items
    output_msg += ", ".join(
        [f"{ts.trs(item)} {get_emoji(item)}" for item in curr_rotation]
    )
    # ends in
    output_msg += f"\n{ts.get(f'{pf}end').format(day=convert_diff(tstamp))}\n"

    # next items
    warframe_list = rotation_data["warframe"]
    length = len(warframe_list)

    if length == 0:
        return create_embed(output_msg)

    # init index (find curr index)
    idx, idx_init = 0, 0
    for item in warframe_list:
        if set(item) == set(curr_rotation):
            idx_init = idx
            break
        idx += 1

    # create next rotation list
    output_msg += f"### __{ts.get(f'{pf}next-rotate')}__\n"
    for _ in range(length - 1):
        idx = (idx + 1) % length
        if idx == idx_init:
            break

        jtem = warframe_list[idx]
        tstamp += ADD_ONE_WEEK
        output_msg += (
            f"{ts.get(f'{pf}coming').format(day=convert_diff(tstamp))}: "
            + ", ".join([f"{ts.trs(i)} {get_emoji(i)}" for i in jtem])
            + "\n"
        )

    return create_embed(output_msg)


def w_duviri_incarnon(incarnon):
    if not incarnon:
        return err_embed("w_duviri_warframe")

    curr_rotation = incarnon[1]["Choices"]
    tstamp: int = rotation_data["expiry"]

    # title
    output_msg: str = (
        f"# {ts.get(f'{pf}inc-lvl')} {ts.get(f'{pf}circuit')} - {ts.get(f'{pf}inc-title')}\n"
    )
    # sub-title
    output_msg += f"### __{ts.get(f'{pf}curr-rotate')}__\n"
    # items
    output_msg += ", ".join([f"{ts.trs(i)} {get_emoji(i)}" for i in curr_rotation])
    # ends in
    output_msg += f"\n{ts.get(f'{pf}end').format(day=convert_diff(tstamp))}\n"

    # next items
    incarnon_list = rotation_data["incarnon"]
    length = len(incarnon_list)

    if length == 0:
        return create_embed(output_msg=output_msg, color=0x65E6E1)

    # init index (find curr index)
    idx, idx_init = 0, 0
    for item in incarnon_list:
        if set(item) == set(curr_rotation):
            idx_init = idx
            break
        idx += 1

    # create next rotation list
    output_msg += f"### __{ts.get(f'{pf}next-rotate')}__\n"
    for _ in range(length - 1):
        idx = (idx + 1) % length
        if idx == idx_init:
            break

        jtem = incarnon_list[idx]
        tstamp += ADD_ONE_WEEK
        output_msg += (
            f"{ts.get(f'{pf}coming').format(day=convert_diff(tstamp))}: "
            + ", ".join([f"{ts.trs(i)} {get_emoji(i)}" for i in jtem])
            + "\n"
        )
    return create_embed(output_msg=output_msg, color=0x65E6E1)


# print(rotation_data["warframe"][1])
# print(w_duviri_warframe(get_obj(DUVIRI_ROTATION)).description)
# print(w_duviri_incarnon(get_obj(DUVIRI_ROTATION)).description)
