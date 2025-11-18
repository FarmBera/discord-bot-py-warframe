import discord

from src.utils.logging_utils import save_log
from src.utils.discord_file import img_file
from src.utils.data_manager import cmd_obj_check


async def cmd_helper(
    interact: discord.Interaction,
    key: str,
    parser_func,
    isFollowUp: bool = False,
    need_api_call: bool = False,
    parser_args=None,
    isUserViewOnly: bool = True,
    isMarketQuery: bool = False,
    marketQuery: tuple = (None, None),
) -> None:
    if isFollowUp:  # delay response if needed
        await interact.response.defer(ephemeral=isUserViewOnly)

    # if need_api_call:  # API request if needed
    #     # await API_Request(lock=,f"cmd.{key}")
    #     set_obj(json_load()[key], key)

    # load objects
    if parser_args:
        obj = parser_func(cmd_obj_check(key), parser_args)
    elif isMarketQuery:
        obj = await parser_func(interact.client.log_lock, marketQuery)
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
        file = img_file(file)
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

    await save_log(
        lock=interact.client.log_lock,
        type="cmd",
        cmd=f"cmd.{key}{f'-{parser_args}' if parser_args else ''}",
        time=interact.created_at,
        user=interact.user.display_name,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used",  # VAR
        obj=log_obj,
    )
