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
BANNED_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"general.banned"), color=0xFF0000
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
    try:
        async with query_reader(interact.client.db) as cursor:
            await cursor.execute(
                "SELECT user_id FROM admins WHERE user_id = %s", (interact.user.id,)
            )
            result = await cursor.fetchone()
        if result and interact.user.id == result.get("user_id"):
            return True

        if notify:
            if isFollowUp:
                await interact.followup.send(embed=ADMIN_EMBED, ephemeral=True)
            else:
                await interact.response.send_message(embed=ADMIN_EMBED, ephemeral=True)
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.warn,
            interact=interact,
            msg=f"cmd '{cmd}' used, but no permission",
        )
        return False
    except Exception as e:
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.err,
            interact=interact,
            msg=f"admin verification error (from is_admin_user): {e}",
            obj=return_traceback(),
        )
        return False


async def is_valid_guild(
    interact: discord.Interaction, isFollowUp: bool = False, cmd: str = ""
) -> bool:
    try:
        if interact.guild_id == CHANNELS["guild"]:
            return True

        if isFollowUp:
            await interact.followup.send(embed=GUILD_EMBED, ephemeral=True)
        else:
            await interact.response.send_message(embed=GUILD_EMBED, ephemeral=True)
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.warn,
            interact=interact,
            msg=f"cmd '{cmd}' used, but unauthorized server",
        )
        return False
    except Exception as e:
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.err,
            interact=interact,
            msg=f"guild validation err (in is_valid_guild): {e}",
            obj=return_traceback(),
        )
        return False


async def is_banned_user(interact: discord.Interaction, isFollowUp: bool = False):
    async with query_reader(interact.client.db) as cursor:
        check_ban_sql = (
            "SELECT 1 FROM warnings WHERE user_id = %s AND banned = 1 LIMIT 1"
        )
        await cursor.execute(check_ban_sql, (interact.user.id,))
        is_already_banned = await cursor.fetchone()

    if is_already_banned:
        if isFollowUp:
            await interact.followup.send(embed=BANNED_EMBED, ephemeral=True)
        else:
            await interact.response.send_message(embed=BANNED_EMBED, ephemeral=True)
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.warn,
            interact=interact,
            msg="cmd used, but banned user",  # VAR
        )
        return True
    return False
