import discord
from discord.ext import commands
import datetime as dt

from config.config import LOG_TYPE
from src.translator import ts
from src.utils.times import JSON_DATE_PAT, timeNowDT
from src.constants.keys import (
    STARTED_TIME_FILE_LOC,
    DELTA_TIME_LOC,
    COOLDOWN_BTN_ACTION,
    COOLDOWN_BTN_MANAGE,
    COOLDOWN_BTN_CALL,
)
from src.utils.logging_utils import save_log
from src.utils.file_io import open_file
from src.utils.formatter import time_format


async def cmd_helper_maintenance(interact: discord.Interaction) -> None:
    time_target = dt.datetime.strptime(
        open_file(STARTED_TIME_FILE_LOC), JSON_DATE_PAT
    ) + dt.timedelta(minutes=int(open_file(DELTA_TIME_LOC)))
    time_left = time_target - timeNowDT()

    txt = f"""# 서버 점검 중

지금은 **서버 점검 및 패치 작업**으로 인하여 **봇을 사용할 수 없습니다.**
이용에 불편을 드려 죄송합니다.

> 종료까지 약 **{time_format(time_left)}** 남았습니다.
> 예상 완료 시간: {dt.datetime.strftime(time_target,"%Y년 %m월 %d일, %H시 %M분")}

점검은 조기 종료 될 수 있으며, 또한 지연될 수 있음을 알립니다.
"""
    # send message
    await interact.response.send_message(
        embed=discord.Embed(description=txt, color=0xFF0000),  # VAR: color
        ephemeral=True,
    )
    await save_log(
        lock=interact.client.log_lock,
        type=f"{LOG_TYPE.cmd}.{LOG_TYPE.maintenance}",
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        interact=interact,
        msg="[info] cmd used in maintenance mode",  # VAR
    )


EVENT_TYPE: str = f"{LOG_TYPE.event}.{LOG_TYPE.maintenance}"
EVENT_COOLDOWN: str = LOG_TYPE.cooldown


pf: str = "cmd.party."
pf_edit: str = f"{pf}p-edit-modal-"
pf_size: str = f"{pf}p-size-modal-"
pf_btn: str = f"{pf}p-del-modal-"
pf_pv: str = f"{pf}pv-"


class PartyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # make the button persistent
        self.cooldown_action = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_ACTION, commands.BucketType.member
        )
        self.cooldown_manage = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_MANAGE, commands.BucketType.member
        )
        self.cooldown_call = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_CALL, commands.BucketType.user
        )

    async def is_cooldown(
        self, interact: discord.Interaction, cooldown_mapping: commands.CooldownMapping
    ) -> bool:
        bucket = cooldown_mapping.get_bucket(interact.message)
        retry = bucket.update_rate_limit()
        if retry:
            await interact.response.send_message(
                embed=discord.Embed(
                    title=ts.get(f"cmd.err-cooldown.title"),
                    description=ts.get("cmd.err-cooldown.btn").format(
                        time=f"{int(retry)}"
                    ),
                    color=0xFF0000,
                ),
                ephemeral=True,
            )
            return True
        return False

    @discord.ui.button(
        label=ts.get(f"{pf_pv}join-btn"),
        style=discord.ButtonStyle.success,
        custom_id="party_join",
    )
    async def join_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_action):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type=etype,
            cmd="btn.main.join",
            interact=interact,
            msg=f"PartyView -> join_party",
        )

    @discord.ui.button(
        label=ts.get(f"{pf_pv}leave-btn"),
        style=discord.ButtonStyle.danger,
        custom_id="party_leave",
    )
    async def leave_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_action):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type=etype,
            cmd="btn.main.leave",
            interact=interact,
            msg=f"PartyView -> leave_party",
        )

    @discord.ui.button(
        label=ts.get(f"{pf_pv}mod-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_size",
    )
    async def edit_size(self, interact: discord.Interaction, button: discord.ui.Button):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_manage):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type=etype,
            cmd="btn.main.edit-size",
            interact=interact,
            msg=f"PartyView -> edit_size",
        )

    @discord.ui.button(
        label=ts.get(f"{pf_pv}mod-article"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_content",
    )
    async def edit_content(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_manage):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type=etype,
            cmd="btn.main.edit-content",
            interact=interact,
            msg=f"PartyView -> edit_content",
        )

    @discord.ui.button(
        label=ts.get(f"{pf_pv}done"),
        style=discord.ButtonStyle.primary,
        custom_id="party_toggle_close",
    )
    async def toggle_close_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_manage):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type=etype,
            cmd="btn.main.toggle_close_party",
            interact=interact,
            msg=f"PartyView -> toggle_close_party",
        )

    @discord.ui.button(  # 파티원 호출
        label=ts.get(f"{pf}pv-call-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_call_members",
    )
    async def call_members(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_manage):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type=etype,
            cmd="btn.main.call_members",
            interact=interact,
            msg=f"PartyView -> call_members",
        )

    @discord.ui.button(  # 멤버 내보내기
        label=ts.get(f"{pf}pv-kick-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_kick_member",
    )
    async def kick_member(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_manage):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type=etype,
            cmd="btn.main.kick_member",
            interact=interact,
            msg=f"PartyView -> kick_member",
        )

    @discord.ui.button(
        label=ts.get(f"{pf}pv-del-label"),
        style=discord.ButtonStyle.danger,
        custom_id="party_delete",
    )
    async def delete_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_manage):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type=etype,
            cmd="btn.main.delete_party",
            interact=interact,
            msg=f"PartyView -> delete_party",
        )
