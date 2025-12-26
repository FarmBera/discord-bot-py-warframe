import discord

from src.translator import ts
from config.config import LOG_TYPE
from src.utils.db_helper import query_reader
from src.utils.return_err import return_traceback, print_test_err
from src.utils.data_manager import CHANNELS
from src.utils.logging_utils import save_log


GUILD_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"cmd.err-limit-server"), color=0xFF0000
)
ADMIN_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"general.admin"), color=0xFF0000
)


async def is_admin_user(
    interact: discord.Interaction,
    cmd="",
    isFollowUp: bool = False,
    notify: bool = False,
) -> bool:
    """check interaction user is admin

    Args:
        interact (discord.Interaction): interaction object

    Returns:
        bool: is admin user (if admin user returns True else False)
    """
    async with query_reader(interact.client.db) as cursor:
        await cursor.execute(
            "SELECT user_id FROM admins WHERE user_id = %s", (interact.user.id,)
        )
        result = await cursor.fetchone()
    try:
        if result and interact.user.id == result.get("user_id"):
            return True

        if notify:
            if isFollowUp:
                await interact.followup.send(embed=ADMIN_EMBED, ephemeral=True)
            else:
                await interact.response.send_message(embed=ADMIN_EMBED, ephemeral=True)
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.warn,
            interact=interact,
            msg=f"[info] cmd '{cmd}' used, but no permission",
            obj=return_traceback(),
        )
        return False
    except Exception:
        await save_log(
            lock=interact.client.log_lock,
            type="err",
            interact=interact,
            msg="undefined error (from is_admin_user)",
            obj=return_traceback(),
        )
        return False


async def is_valid_guild(
    interact: discord.Interaction, isFollowUp: bool = False
) -> bool:
    try:
        if interact.guild_id == CHANNELS["guild"]:
            return True

        if isFollowUp:
            await interact.followup.send(embed=GUILD_EMBED, ephemeral=True)
        else:
            await interact.response.send_message(embed=GUILD_EMBED, ephemeral=True)
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.warn,
            interact=interact,
            msg="[info] cmd used, but unauthorized server",
            obj=GUILD_EMBED.description,
        )
        return False
    except Exception:
        await save_log(
            lock=interact.client.log_lock,
            type="err",
            interact=interact,
            msg="[info] validation err (in is_valid_guild)",
            obj=return_traceback(),
        )
        return False
