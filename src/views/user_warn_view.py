import discord
from discord import ui

from src.translator import ts
from config.config import LOG_TYPE
from src.utils.logging_utils import save_log
from src.utils.db_helper import transaction
from src.utils.return_err import return_traceback
from src.services.warn_service import WarnService, BAN_THRESHOLD
from src.views.help_view import SupportView

pf: str = "cmd.user-ban."


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
        global_name = self.target_member.global_name
        display_name = self.target_member.display_name

        try:
            is_executed_ban = await WarnService.insertWarn(
                self.pool, user_id, display_name, game_nickname, warn_type, warn_reason
            )
        except Exception:
            await interact.followup.send(
                content=ts.get(f"cmd.err-db"), view=SupportView(), ephemeral=True
            )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.err,
                cmd=pf,
                interact=interact,
                msg="cmd used",  # VAR
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
            pool=interact.client.db,
            type=LOG_TYPE.cmd,
            cmd=pf,
            interact=interact,
            msg="warning user",  # VAR
            obj=f"{user_id}//{original_name}//{global_name}//{display_name}//{game_nickname}\nisBanned: {is_executed_ban}\n{warn_type}\n{warn_reason}",
        )
