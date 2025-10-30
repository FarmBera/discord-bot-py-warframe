import discord

from src.translator import ts, language as lang
from src.constants.color import C
from src.constants.keys import (
    FOOTER_FILE_LOC,
    fileExt,
)
from src.utils.logging_utils import save_log
from src.utils.file_io import open_file
from src.utils.return_err import err_embed


async def cmd_helper_txt(
    interact: discord.Interaction, file_name: str, isUserViewOnly: bool = True
) -> None:
    try:
        txt1 = open_file(file_name.replace(fileExt, f"-{lang}{fileExt}"))
        txt2 = open_file(FOOTER_FILE_LOC.replace(fileExt, f"-{lang}{fileExt}"))
        txt = txt1 + txt2
    except Exception as e:
        msg: str = "[err] open_file err in cmd_helper_txt"  # VAR
        await interact.response.send_message(embed=err_embed(msg), ephemeral=True)
        print(C.red, msg, C.default, sep="")
        await save_log(
            lock=interact.client.log_lock,
            type="err",
            cmd="cmd_helper_txt",
            time=interact.created_at,
            user=interact.user,
            guild=interact.guild,
            channel=interact.channel,
            msg=msg,
            obj=e,
        )
        return

    # send message
    await interact.response.send_message(
        embed=discord.Embed(description=txt, color=0xCEFF00),  # VAR: color
        ephemeral=isUserViewOnly,
    )

    await save_log(
        lock=interact.client.log_lock,
        type="cmd",
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used",  # VAR
        obj=txt,
    )
