import discord
from discord import ui

from config.config import LOG_TYPE
from src.services.queue_manager import add_job
from src.translator import ts
from src.utils.logging_utils import log_event
from src.utils.return_err import return_traceback
from src.views.help_view import SupportView


class TimeoutEditView(ui.View):
    """Base view that edits its original response into a timeout notice.

    Subclasses must be created with an `interact` whose original response
    is the ephemeral message hosting this view. Set `log_name` per subclass
    for readable logs.
    """

    log_name: str = "View"

    def __init__(self, interact: discord.Interaction, *, timeout: float):
        super().__init__(timeout=timeout)
        self.interact = interact

    async def on_timeout(self):
        cmd = f"{self.log_name}.timeout"
        try:
            await self.interact.edit_original_response(
                content=ts.get("cmd.err-timeout"), view=None
            )
            await log_event(self.interact, cmd, f"{self.log_name} -> timeout")
        except discord.NotFound:
            await log_event(
                self.interact,
                cmd,
                f"{self.log_name} -> timeout, but Not Found",
                type=LOG_TYPE.info,
            )
        except Exception:
            await log_event(
                self.interact,
                cmd,
                f"{self.log_name} -> timeout, but ERR",
                type=LOG_TYPE.err,
                obj=return_traceback(),
            )


class ConfirmDeleteView(TimeoutEditView):
    """Shared yes/no confirmation for deleting a party or trade post.

    Behavioral differences between the two are passed in:
    - `disable_origin=True`  -> strip buttons off the original public post
      (party). `False` -> delete the ephemeral confirm prompt (trade).
    - `success_key`          -> optional follow-up shown on the ephemeral
      response after the delete job is queued.
    """

    log_name = "ConfirmDeleteView"

    def __init__(
        self,
        interact: discord.Interaction,
        origin_message: discord.Message,
        *,
        job_type,
        yes_label_key: str,
        no_label_key: str,
        cancel_key: str,
        error_key: str,
        success_key: str | None = None,
        disable_origin: bool = False,
    ):
        super().__init__(interact, timeout=20)
        self.origin_message = origin_message
        self.job_type = job_type
        self.cancel_key = cancel_key
        self.error_key = error_key
        self.success_key = success_key
        self.disable_origin = disable_origin
        self.value = None

        self.yes_button.label = ts.get(yes_label_key)
        self.no_button.label = ts.get(no_label_key)

    @ui.button(style=discord.ButtonStyle.danger)
    async def yes_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.defer(ephemeral=True)
        if self.disable_origin:
            await self.origin_message.edit(view=None)
        else:
            await interact.delete_original_response()
        await log_event(interact, "btn.confirm.delete", "ConfirmDeleteView -> yes")

        try:
            await add_job(
                self.job_type,
                {"origin_msg": self.origin_message, "interact": interact},
            )
            await interact.client.trigger_queue_processing()
            if self.success_key:
                await interact.edit_original_response(
                    content=ts.get(self.success_key), view=None
                )
        except Exception:
            await interact.followup.send(
                ts.get(self.error_key), view=SupportView(), ephemeral=True
            )
            await log_event(
                interact,
                "btn.confirm.delete",
                "ConfirmDeleteView -> yes, but ERR",
                type=LOG_TYPE.err,
                obj=return_traceback(),
            )
        self.value = True
        self.stop()

    @ui.button(style=discord.ButtonStyle.secondary)
    async def no_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.edit_message(
            content=ts.get(self.cancel_key), view=None
        )
        self.value = False
        self.stop()
        await log_event(
            interact, "btn.confirm.delete.cancel", "ConfirmDeleteView -> no"
        )
