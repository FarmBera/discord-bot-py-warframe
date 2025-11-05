import discord

from src.translator import ts
from src.constants.color import C
from src.constants.keys import FOOTER_FILE_LOC
from src.utils.data_manager import ADMINS
from src.utils.logging_utils import save_log
from src.utils.file_io import open_file
from src.utils.return_err import err_embed


async def cmd_helper_txt(
    interact: discord.Interaction, file_name: str, isPublicMsg: bool = False
) -> None:
    # is custom admin user
    admins = ADMINS

    if isPublicMsg and interact.user.id not in admins:
        msg: str = ts.get("cmd.no-permission")
        embed = discord.Embed(
            title=ts.get("cmd.no-perm-title"), description=msg, color=0xFF0000
        )
        embed.set_footer(text=open_file(FOOTER_FILE_LOC))
        await interact.response.send_message(embed=embed, ephemeral=True)
        await save_log(
            lock=interact.client.log_lock,
            type="err.admin",  # VAR
            cmd="cmd_helper_txt",
            time=interact.created_at,
            user=interact.user.display_name,
            guild=interact.guild,
            channel=interact.channel,
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
            type="err",  # VAR
            cmd="cmd_helper_txt",
            time=interact.created_at,
            user=interact.user.display_name,
            guild=interact.guild,
            channel=interact.channel,
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
        type="cmd",  # VAR: cmd
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        time=interact.created_at,
        user=interact.user.display_name,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used",  # VAR
        obj=txt,
    )
