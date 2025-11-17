import discord
import datetime as dt
from dateutil.relativedelta import relativedelta

from src.translator import ts, Lang, language as lang
from src.constants.keys import DUVIRI_ROTATION, DUVIRI_U_K_W, DUVIRI_U_K_I
from src.utils.emoji import get_emoji
from src.utils.data_manager import get_obj, set_obj
from src.utils.times import timeNowDT, convert_remain
from src.utils.return_err import err_embed

rotation_data = get_obj("RotationDuviri")
duv_warframe = get_obj(f"{DUVIRI_ROTATION}{DUVIRI_U_K_W}")
duv_incarnon = get_obj(f"{DUVIRI_ROTATION}{DUVIRI_U_K_I}")

IDX_MAX_WAF: int = 11
IDX_MAX_INC: int = 8
ADD_ONE_WEEK: int = 604800

pf: str = "cmd.duviri-circuit."


def setDuviriRotate():
    global rotation_data
    rotation_data = get_obj("RotationDuviri")


def setDuvWarframe(obj):
    global duv_warframe
    duv_warframe = obj
    set_obj(obj, f"{DUVIRI_ROTATION}{DUVIRI_U_K_W}")


def setDuvIncarnon(obj):
    global duv_incarnon
    duv_incarnon = obj
    set_obj(obj, f"{DUVIRI_ROTATION}{DUVIRI_U_K_I}")


def convert_diff(unix_timestamp: int | str, isNoti: bool = False) -> str:
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

    if isNoti:
        return f"<t:{ts_int}:R>"

    now_dt = timeNowDT()
    input_dt = dt.datetime.fromtimestamp(ts_int)

    if now_dt >= input_dt:  # calculate time diff
        rdelta = relativedelta(now_dt, input_dt)
    else:  # future timestamp
        rdelta = relativedelta(input_dt, now_dt)

    # calculate month, day, hour, minute
    months = rdelta.years * 12 + rdelta.months
    days = rdelta.days
    hours = rdelta.hours
    minutes = rdelta.minutes

    output: list = []

    if months > 0:
        if months == 1:
            output.append(ts.get("한 달"))
        elif months == 2:
            output.append(ts.get("두 달"))
        elif months >= 3:
            output.append(ts.get("먼 훗날"))
    elif days > 0:
        output.append(f"{days}{ts.get('time.day')}")
    elif hours > 0:
        output.append(f"{hours}{ts.get('time.hour')}")
    elif minutes > 0:
        output.append(f"{minutes}{ts.get('time.min')}")

    return ts.get(f"{pf}coming").format(day=" ".join(output))


def create_embed(output_msg: str, color=None):
    embed = (
        discord.Embed(description=output_msg, color=color)
        if color
        else discord.Embed(description=output_msg)
    )
    if lang != Lang.KO:
        f = "zariman"
        embed.set_thumbnail(url="attachment://i.png")
        return embed, f
    return embed


def w_duviri_warframe(rotation, isNoti: bool = False):
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
    output_msg += f"\n{ts.get(f'{pf}end').format(day=convert_diff(tstamp,isNoti))}\n"
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
            f"{convert_diff(tstamp,isNoti)}: "
            + ", ".join([f"{ts.trs(i)} {get_emoji(i)}" for i in jtem])
            + "\n"
        )
    return create_embed(output_msg)


def w_duviri_incarnon(incarnon, isNoti: bool = False):
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
    output_msg += f"\n{ts.get(f'{pf}end').format(day=convert_diff(tstamp,isNoti))}\n"
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
            f"{convert_diff(tstamp,isNoti)}: "
            + ", ".join([f"{ts.trs(i)} {get_emoji(i)}" for i in jtem])
            + "\n"
        )
    return create_embed(output_msg=output_msg, color=0x65E6E1)
