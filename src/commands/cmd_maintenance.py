import discord
from discord.ext import commands
import datetime as dt

from config.config import LOG_TYPE
from src.translator import ts
from src.utils.times import convert_remain
from src.constants.keys import (
    COOLDOWN_BTN_ACTION,
    COOLDOWN_BTN_MANAGE,
    COOLDOWN_BTN_CALL,
)
from src.utils.logging_utils import save_log
from src.utils.db_helper import query_reader


async def cmd_helper_maintenance(interact: discord.Interaction, arg: str = "") -> None:
    async with query_reader(interact.client.db) as cursor:
        # delta time
        await cursor.execute("SELECT value FROM vari WHERE name='delta_time'")
        delta_time = await cursor.fetchone()
        delta_time = int(delta_time["value"])

        # get started time
        await cursor.execute("SELECT updated_at FROM vari WHERE name='start_time'")
        start_time = await cursor.fetchone()
        start_time = start_time["updated_at"]

    # calculate time
    time_target = start_time + dt.timedelta(minutes=delta_time)

    txt = ts.get("maintenance.content").format(
        remain=convert_remain(time_target.timestamp())
    )

    # send message
    await interact.response.send_message(
        embed=discord.Embed(description=txt, color=0xFF0000),  # VAR: color
        ephemeral=True,
    )
    await save_log(
        pool=interact.client.db,
        type=f"{LOG_TYPE.cmd}.{LOG_TYPE.maintenance}",
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        interact=interact,
        msg=f"cmd used in maintenance mode: {arg}",
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
            1, COOLDOWN_BTN_ACTION, commands.BucketType.user
        )
        self.cooldown_manage = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_MANAGE, commands.BucketType.user
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
            pool=interact.client.db,
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
            pool=interact.client.db,
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
            pool=interact.client.db,
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
            pool=interact.client.db,
            type=etype,
            cmd="btn.main.edit-content",
            interact=interact,
            msg=f"PartyView -> edit_content",
        )

    @discord.ui.button(  # 날짜 수정
        label=ts.get(f"{pf}date-btn"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_departure",
    )
    async def edit_departure(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_manage):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            pool=interact.client.db,
            type=etype,
            cmd="btn.main.edit_departure",
            interact=interact,
            msg=f"PartyView -> edit_departure",
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
            pool=interact.client.db,
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
            pool=interact.client.db,
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
            pool=interact.client.db,
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
            pool=interact.client.db,
            type=etype,
            cmd="btn.main.delete_party",
            interact=interact,
            msg=f"PartyView -> delete_party",
        )


pf: str = "cmd.trade."


class TradeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown_action = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_ACTION, commands.BucketType.user
        )
        self.cooldown_manage = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_MANAGE, commands.BucketType.user
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

    @discord.ui.button(  # 거래하기
        label=ts.get(f"{pf}btn-trade"),
        style=discord.ButtonStyle.primary,
        custom_id="trade_btn_trade",
    )
    async def trade_action(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_action):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)

        await save_log(
            pool=interact.client.db,
            type=etype,
            cmd=f"btn.trade",
            interact=interact,
            msg=f"TradeView -> trade_action",
        )

    @discord.ui.button(  # 수량 변경
        label=ts.get(f"{pf}btn-edit-qty"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_qty",
    )
    async def edit_quantity(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_action):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)
        await save_log(
            pool=interact.client.db,
            type=etype,
            cmd="btn.main.edit-quantity",
            interact=interact,
            msg=f"TradeView -> edit_quantity",
        )

    @discord.ui.button(  # 가격 수정
        label=ts.get(f"{pf}btn-edit-price"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_price",
    )
    async def edit_price(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_action):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)
        await save_log(
            pool=interact.client.db,
            type=etype,
            cmd="btn.main.edit-price",
            interact=interact,
            msg=f"TradeView -> edit_price",
        )

    @discord.ui.button(  # 닉네임 변경
        label=ts.get(f"{pf}btn-edit-nickname"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_nick",
    )
    async def edit_nickname(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_action):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)
        await save_log(
            pool=interact.client.db,
            type=etype,
            cmd="btn.main.edit-price",
            interact=interact,
            msg=f"TradeView -> edit_price",
        )

    @discord.ui.button(  # 거래 글 닫기
        label=ts.get(f"{pf}btn-close"),
        style=discord.ButtonStyle.danger,
        custom_id="trade_btn_edit_close",
    )
    async def close_trade(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        etype: str = EVENT_TYPE

        if await self.is_cooldown(interact, self.cooldown_action):
            etype += EVENT_COOLDOWN
            return

        await cmd_helper_maintenance(interact)
        await save_log(
            pool=interact.client.db,
            type=etype,
            cmd="btn.trade.toggle_close_party",
            interact=interact,
            msg=f"TradeView -> close_trade",
            # obj=new_status,
        )
