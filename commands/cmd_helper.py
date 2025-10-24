import discord
from discord.ext import tasks

from src.utils.api_request import API_Request
from src.utils.file_io import json_load
from src.utils.logging_utils import save_log
from src.utils.data_manager import set_obj, cmd_obj_check


async def cmd_helper(
    interact: discord.Interaction,
    key: str,
    parser_func,
    isFollowUp: bool = False,
    need_api_call: bool = False,
    parser_args=None,
    isUserViewOnly: bool = True,
    isMarketQuery: bool = False,
    marketQuery: str = "",
) -> None:
    if isFollowUp:  # delay response if needed
        await interact.response.defer(ephemeral=isUserViewOnly)

    if need_api_call:  # API request if needed
        API_Request(f"cmd.{key}")
        set_obj(json_load()[key], key)

    # load objects
    if parser_args:
        obj = parser_func(cmd_obj_check(key), parser_args)
    elif isMarketQuery:
        obj = parser_func(marketQuery)
    else:
        obj = parser_func(cmd_obj_check(key))

    # send message
    resp_head = interact.followup if isFollowUp else interact.response

    if isinstance(obj, discord.Embed):  # embed only
        if isFollowUp:
            await resp_head.send(embed=obj, ephemeral=isUserViewOnly)
        else:
            await resp_head.send_message(embed=obj, ephemeral=isUserViewOnly)
        log_obj = obj.description
    elif isinstance(obj, tuple):  # embed with file
        eb, file = obj
        if isFollowUp:
            await resp_head.send(embed=eb, file=file, ephemeral=isUserViewOnly)
        else:
            await resp_head.send_message(embed=eb, file=file, ephemeral=isUserViewOnly)
        log_obj = eb.description
    else:  # text only
        if isFollowUp:
            await resp_head.send(obj, ephemeral=isUserViewOnly)
        else:
            await resp_head.send_message(obj, ephemeral=isUserViewOnly)
        log_obj = obj

    save_log(
        type="cmd",
        cmd=f"cmd.{key}{f'-{parser_args}' if parser_args else ''}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used",  # VAR
        obj=log_obj,
    )
