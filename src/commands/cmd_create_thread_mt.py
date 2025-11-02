import discord
import sqlite3

from src.translator import ts
from src.constants.keys import CHANNEL_FILE_LOC
from src.utils.file_io import yaml_open
from src.utils.logging_utils import save_log
from src.commands.cmd_maintenance import cmd_helper_maintenance

pf: str = "cmd.party."
pf_edit: str = f"{pf}p-edit-modal-"
pf_size: str = f"{pf}p-size-modal-"
pf_btn: str = f"{pf}p-del-modal-"
pf_pv: str = f"{pf}pv-"


class PartyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # make the button persistent

    @discord.ui.button(
        label=ts.get(f"{pf_pv}join-btn"),
        style=discord.ButtonStyle.success,
        custom_id="party_join",
    )
    async def join_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type="event.maintenance",
            cmd="btn.main.join",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
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
        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type="event.maintenance",
            cmd="btn.main.leave",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> leave_party",
        )

    @discord.ui.button(
        label=ts.get(f"{pf_pv}mod-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_size",
    )
    async def edit_size(self, interact: discord.Interaction, button: discord.ui.Button):
        await cmd_helper_maintenance(interact)

        await save_log(
            lock=interact.client.log_lock,
            type="event.maintenance",
            cmd="btn.main.edit-size",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
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
        await cmd_helper_maintenance(interact)
        await save_log(
            lock=interact.client.log_lock,
            type="event.maintenance",
            cmd="btn.main.edit-content",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
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
        await cmd_helper_maintenance(interact)
        await save_log(
            lock=interact.client.log_lock,
            type="event.maintenance",
            cmd="btn.main.toggle_close_party",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> toggle_close_party",
        )

    @discord.ui.button(
        label=ts.get(f"{pf}pv-del-label"),
        style=discord.ButtonStyle.danger,
        custom_id="party_delete",
    )
    async def delete_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await cmd_helper_maintenance(interact)
        await save_log(
            lock=interact.client.log_lock,
            type="event.maintenance",
            cmd="btn.main.delete_party",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> delete_party",
        )
