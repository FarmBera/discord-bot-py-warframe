import discord

from config.config import LOG_TYPE
from src.translator import ts
from src.constants.color import C
from src.constants.keys import FOOTER_FILE_LOC
from src.utils.permission import is_admin_user
from src.utils.logging_utils import save_log
from src.utils.file_io import open_file_async
from src.utils.return_err import err_embed
from src.views.help_view import SupportView


async def cmd_helper_txt(
    interact: discord.Interaction, file_name: str, isPrivateMsg: bool = True
) -> None:
    if not isPrivateMsg:
        is_admin = await is_admin_user(interact=interact, cmd=f"{file_name}")
        if not is_admin:
            isPrivateMsg = True

    # open & read file
    try:
        txt1 = await open_file_async(file_name)
        txt2 = await open_file_async(FOOTER_FILE_LOC)
        txt = txt1 + txt2
    except Exception as e:  # send err msg
        msg: str = "[err] open_file err in cmd_helper_txt"  # VAR
        await interact.response.send_message(embed=err_embed(), ephemeral=True)
        print(C.red, msg, C.default, sep="")
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.err,
            cmd="cmd_helper_txt",
            interact=interact,
            msg=msg,
            obj=e,
        )
        return

    # send message
    await interact.response.send_message(
        embed=discord.Embed(description=txt, color=0xCEFF00),  # VAR: color
        view=SupportView(),
        ephemeral=isPrivateMsg,
    )

    await save_log(
        pool=interact.client.db,
        type=LOG_TYPE.cmd,
        cmd=f"{LOG_TYPE.cmd}.{ts.get(f'cmd.help.cmd')}",
        interact=interact,
        msg="[info] cmd used",  # VAR
        obj=f"{isPrivateMsg}\n{txt}",
    )
