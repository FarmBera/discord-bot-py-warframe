import discord

from config.config import LOG_TYPE
from src.commands.admin import is_admin_user
from src.utils.logging_utils import save_log
from src.utils.discord_file import img_file
from src.utils.data_manager import get_obj_async


async def cmd_helper(
    interact: discord.Interaction,
    key: str,
    parser_func,
    isFollowUp: bool = False,
    parser_args=None,
    isPrivateMsg: bool = True,
    isMarketQuery: bool = False,
    marketQuery: tuple = (None, None),
) -> None:
    # check admin if user want to send public msg
    if not isPrivateMsg:
        is_admin = await is_admin_user(
            interact=interact, cmd=f"{parser_func}//{parser_args}//MARKET:{marketQuery}"
        )
        if not is_admin:
            isPrivateMsg = True

    if isFollowUp:
        await interact.response.defer(ephemeral=isPrivateMsg)

    # parse objects
    if parser_args:
        obj = parser_func(await get_obj_async(key), parser_args)
    elif isMarketQuery:
        obj = await parser_func(interact.client.log_lock, marketQuery)
    else:
        obj = parser_func(await get_obj_async(key))

    # send message
    resp_head = interact.followup if isFollowUp else interact.response

    # check object type
    if isinstance(obj, discord.Embed):  # embed only
        if isFollowUp:
            await resp_head.send(embed=obj, ephemeral=isPrivateMsg)
        else:
            await resp_head.send_message(embed=obj, ephemeral=isPrivateMsg)
        log_obj = obj.description
    elif isinstance(obj, tuple):  # embed with file
        eb, file = obj
        file = img_file(file)
        if isFollowUp:
            await resp_head.send(embed=eb, file=file, ephemeral=isPrivateMsg)
        else:
            await resp_head.send_message(embed=eb, file=file, ephemeral=isPrivateMsg)
        log_obj = eb.description
    else:  # text only
        if isFollowUp:
            await resp_head.send(obj, ephemeral=isPrivateMsg)
        else:
            await resp_head.send_message(obj, ephemeral=isPrivateMsg)
        log_obj = obj

    await save_log(
        lock=interact.client.log_lock,
        type=LOG_TYPE.cmd,
        cmd=f"{LOG_TYPE.cmd}.{key}{f'-{parser_args}' if parser_args else ''}",
        interact=interact,
        msg="[info] cmd used",  # VAR
        obj=log_obj,
    )
