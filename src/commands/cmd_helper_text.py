import discord

from config.config import LOG_TYPE
from src.translator import ts
from src.constants.color import C
from src.constants.keys import FOOTER_FILE_LOC
from src.commands.admin import is_admin_user
from src.utils.logging_utils import save_log
from src.utils.file_io import open_file
from src.utils.return_err import err_embed


async def cmd_helper_txt(
    interact: discord.Interaction, file_name: str, isPublicMsg: bool = False
) -> None:
    if isPublicMsg and not is_admin_user(interact):
        msg: str = ts.get("cmd.no-permission")
        embed = discord.Embed(
            title=ts.get("cmd.no-perm-title"), description=msg, color=0xFF0000
        )
        embed.set_footer(text=open_file(FOOTER_FILE_LOC))
        await interact.response.send_message(embed=embed, ephemeral=True)
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.e_admin,
            cmd="cmd_helper_txt",
            interact=interact,
            msg=msg,
        )
        return

    # open & read file
    try:
        txt1 = open_file(file_name)
        txt2 = open_file(FOOTER_FILE_LOC)
        txt = txt1 + txt2
    except Exception as e:  # send err msg
        msg: str = "[err] open_file err in cmd_helper_txt"  # VAR
        await interact.response.send_message(embed=err_embed(msg), ephemeral=True)
        print(C.red, msg, C.default, sep="")
        await save_log(
            lock=interact.client.log_lock,
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
        ephemeral=not isPublicMsg,
    )

    await save_log(
        lock=interact.client.log_lock,
        type=LOG_TYPE.cmd,
        cmd=f"{LOG_TYPE.cmd}.{ts.get(f'cmd.help.cmd')}",
        interact=interact,
        msg="[info] cmd used",  # VAR
        obj=txt,
    )
