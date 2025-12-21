import discord
from discord import ui

from src.translator import ts
from config.config import LOG_TYPE
from src.commands.admin import is_admin_user, is_valid_guild
from src.utils.logging_utils import save_log
from src.utils.db_helper import query_reader, transaction
from src.utils.return_err import return_traceback, print_test_err

BAN_THRESHOLD: int = 3

pf: str = "cmd.user-ban."

BANNED_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"general.banned"), color=0xFF0000
)


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
            lock=interact.client.log_lock,
            type=LOG_TYPE.warn,
            interact=interact,
            msg="[info] cmd used, but banned user",  # VAR
        )
        return True
    return False


class WarnInputModal(ui.Modal, title=ts.get(f"{pf}modal-title")):
    def __init__(self, pool, target_member: discord.Member):
        super().__init__()
        self.pool = pool
        self.target_member = target_member

    warn_type = ui.TextInput(
        label=ts.get(f"{pf}m-type-label"),
        placeholder=ts.get(f"{pf}m-type-desc"),
        style=discord.TextStyle.short,
        max_length=20,
        required=True,
    )

    game_nickname = ui.TextInput(
        label=ts.get(f"{pf}m-game-nic-label"),
        placeholder=ts.get(f"{pf}m-game-nic-desc"),
        style=discord.TextStyle.short,
        max_length=150,
        required=True,
    )
    warn_reason = ui.TextInput(
        label=ts.get(f"{pf}m-reason-label"),
        placeholder=ts.get(f"{pf}m-reason-desc"),
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True,
    )

    async def on_submit(self, interact: discord.Interaction):
        await interact.response.defer(ephemeral=True)

        # get input value
        warn_type = self.warn_type.value
        game_nickname = self.game_nickname.value
        warn_reason = self.warn_reason.value

        user_id = self.target_member.id
        original_name = self.target_member.name
        display_name = self.target_member.display_name

        is_executed_ban = False

        try:
            async with transaction(self.pool) as cursor:
                # cumulative warning count
                count_sql = "SELECT COUNT(*) as cnt FROM warnings WHERE user_id = %s"
                await cursor.execute(count_sql, (user_id,))
                result = await cursor.fetchone()
                current_warn_count = result["cnt"] if result else 0

                # decision ban
                if current_warn_count + 1 >= BAN_THRESHOLD:
                    is_executed_ban = True

                await cursor.execute(
                    "INSERT INTO warnings (user_id, display_name, game_nickname, category, note, banned) VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        user_id,
                        display_name,
                        game_nickname,
                        warn_type,
                        warn_reason,
                        is_executed_ban,
                    ),
                )
        except Exception:
            await interact.followup.send(content=ts.get(f"cmd.err-db"), ephemeral=True)
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.err,
                cmd=pf,
                interact=interact,
                msg="[info] cmd used",  # VAR
                obj=return_traceback(),
            )
            return

        message_body = ts.get(f"{pf}msg-body").format(
            original_name=original_name,
            display_name=display_name,
            game_nickname=game_nickname,
            warn_reason=warn_reason,
        )
        if is_executed_ban:
            message_body += ts.get(f"{pf}banned").format(ban_threshold=BAN_THRESHOLD)

        await interact.followup.send(message_body, ephemeral=True)
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.cmd,
            cmd=pf,
            interact=interact,
            msg="[info] warning user",  # VAR
            obj=f"isBanned: {is_executed_ban}",
        )


async def cmd_user_warn_helper(
    interact: discord.Interaction, user: discord.Member
) -> None:
    if not await is_valid_guild(interact):
        return

    if not await is_admin_user(interact):
        return

    try:
        async with query_reader(interact.client.db) as cursor:
            # check is already banned user
            check_ban_sql = (
                "SELECT 1 FROM warnings WHERE user_id = %s AND banned = 1 LIMIT 1"
            )
            await cursor.execute(check_ban_sql, (user.id,))
            is_already_banned = await cursor.fetchone()

        if is_already_banned:
            await interact.followup.send(
                ts.get(f"{pf}already-ban").format(user=user.display_name),
                ephemeral=True,
            )
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.info,
                cmd=pf,
                interact=interact,
                msg="[info] cmd used, but already banned",  # VAR
                obj=f"{user.id}\n{user.name}\n{user.display_name}",
            )
            return

        modal = WarnInputModal(pool=interact.client.db, target_member=user)
        await interact.response.send_modal(modal)

        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.cmd,
            cmd=pf,
            interact=interact,
            msg="[info] cmd used",  # VAR
        )
    except Exception as e:
        if not interact.response.is_done():
            await interact.response.send_message(
                ts.get(f"general.error-cmd"),
                ephemeral=True,
            )
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.err,
                cmd=pf,
                interact=interact,
                msg=f"[info] cmd used, but ERR: {e}",  # VAR
                obj=return_traceback(),
            )
