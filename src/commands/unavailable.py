import discord

from config.config import LOG_TYPE
from src.translator import ts
from src.utils.logging_utils import save_log


async def cmd_unavailable(interact: discord.Interaction) -> None:
    txt = ts.get("general.unable")

    # send message
    await interact.response.send_message(
        embed=discord.Embed(description=txt, color=0xFF0000),  # VAR: color
        ephemeral=True,
    )
    await save_log(
        pool=interact.client.db,
        type=LOG_TYPE.unable,
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        interact=interact,
        msg="[info] cmd used",  # VAR
    )
