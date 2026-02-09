import discord
from discord.ext import commands

from config.config import LOG_TYPE
from src.services.channel_service import ChannelService
from src.translator import ts
from src.utils.db_helper import query_reader
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback

GUILD_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"cmd.err-limit-server"), color=0xFF0000
)
ADMIN_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"general.admin"), color=0xFF0000
)
TEMP_BANNED_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"general.banned").format(time="1시간"), color=0xFF0000
)
BANNED_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"general.banned").format(time="영구"), color=0xFF0000
)


async def is_cooldown(
    interact: discord.Interaction, cooldown_mapping: commands.CooldownMapping
):
    bucket = cooldown_mapping.get_bucket(interact.message)
    retry = bucket.update_rate_limit()
    if retry:
        await interact.response.send_message(
            embed=discord.Embed(
                title=ts.get(f"cmd.err-cooldown.title"),
                description=ts.get("cmd.err-cooldown.btn").format(time=f"{int(retry)}"),
                color=0xFF0000,
            ),
            ephemeral=True,
        )
        return True
    return False


async def is_admin_user(
    interact: discord.Interaction,
    cmd="",
    isFollowUp: bool = False,
    notify: bool = False,
) -> bool:
    """check interaction user is admin

        Args:
            interact (discord.Interaction): interaction object

    :param interact: interaction object to response back
    :param cmd: used function
    :param isFollowUp: is ephemeral msg
    :param notify: is sending response
    :return: bool: is admin user (if admin user returns True else False)
    """
    try:
        async with query_reader(interact.client.db) as cursor:
            await cursor.execute(
                "SELECT user_id FROM admins WHERE user_id = %s LIMIT 1",
                (interact.user.id,),
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
            msg=f"admin verification error (from '{cmd}'>is_admin_user): {e}",
            obj=return_traceback(),
        )
        return False


async def is_super_user(
    interact: discord.Interaction,
    cmd="",
    isFollowUp: bool = False,
    notify: bool = False,
) -> bool:
    """check interaction user is super admin

        Args:
            interact (discord.Interaction): interaction object

    :param interact: interaction object to response back
    :param cmd: used function
    :param isFollowUp: is ephemeral msg
    :param notify: is sending response
    :return: bool: is admin user (if admin user returns True else False)
    """
    try:
        # INLINE_SQL
        async with query_reader(interact.client.db) as cursor:
            await cursor.execute(
                "SELECT user_id FROM admins WHERE user_id = %s AND super_user = 1 LIMIT 1",
                (interact.user.id,),
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
            msg=f"cmd '{cmd}' used, but no super permission",
        )
        return False
    except Exception as e:
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.err,
            interact=interact,
            msg=f"admin verification error (from '{cmd}'>is_super_user): {e}",
            obj=return_traceback(),
        )
        return False


async def is_valid_guild(
    interact: discord.Interaction, isFollowUp: bool = False, cmd: str = ""
) -> bool:
    """
    :param interact: discord Interactino object
    :param isFollowUp: is defer()
    :param cmd: used place
    :return: TRUE if valid_guild else FALSE
    """
    try:
        # fetch & check guild
        channel_list = await ChannelService.getChannels(interact)
        if channel_list.get("guild") == interact.guild_id:
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
    pool = interact.client.db
    user_id = interact.user.id

    sql = """SELECT COALESCE(MAX(banned), 0) AS is_perm_banned,
COALESCE(MAX(CASE WHEN critical = 1 AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR) THEN 1 ELSE 0 END), 0) AS is_temp_banned
FROM warnings WHERE user_id  = %s"""

    async with query_reader(pool) as cursor:
        await cursor.execute(sql, (user_id,))
        status = await cursor.fetchone()

    if not status:
        return False

    if status["is_perm_banned"]:
        if isFollowUp:
            await interact.followup.send(embed=BANNED_EMBED, ephemeral=True)
        else:
            await interact.response.send_message(embed=BANNED_EMBED, ephemeral=True)
        await save_log(
            pool=pool,
            type=LOG_TYPE.warn,
            interact=interact,
            msg="cmd used, but permanently banned user",
        )
        return True

    if status["is_temp_banned"]:
        if isFollowUp:
            await interact.followup.send(embed=TEMP_BANNED_EMBED, ephemeral=True)
        else:
            await interact.response.send_message(
                embed=TEMP_BANNED_EMBED, ephemeral=True
            )
        await save_log(
            pool=pool,
            type=LOG_TYPE.warn,
            interact=interact,
            msg="cmd used, but temporary banned user",
        )
        return True

    return False
