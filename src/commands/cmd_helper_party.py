import discord
from discord.ext import commands
import sqlite3

from src.translator import ts
from src.constants.keys import (
    LFG_WEBHOOK_NAME,
    COOLDOWN_BTN_ACTION,
    COOLDOWN_BTN_MANAGE,
    COOLDOWN_BTN_CALL,
)
from src.utils.data_manager import CHANNELS
from src.utils.logging_utils import save_log

pf: str = "cmd.party."
pf_edit: str = f"{pf}p-edit-modal-"
pf_size: str = f"{pf}p-size-modal-"
pf_btn: str = f"{pf}p-del-modal-"
pf_pv: str = f"{pf}pv-"


def parseNickname(nickname: str) -> str:
    return nickname.split(" ")[-1]


# define article editor modal
class PartyEditModal(discord.ui.Modal, title=ts.get(f"{pf_edit}title")):
    def __init__(self, current_title: str, current_mission: str, current_desc: str):
        super().__init__(timeout=None)

        self.title_input = discord.ui.TextInput(
            label=ts.get(f"{pf_edit}title-input"),
            style=discord.TextStyle.short,
            default=current_title,
            required=True,
        )
        self.mission_input = discord.ui.TextInput(
            label=ts.get(f"{pf_edit}mission-input"),
            style=discord.TextStyle.short,
            default=current_mission,
            required=True,
        )
        self.desc_input = discord.ui.TextInput(
            label=ts.get(f"{pf_edit}desc-input"),
            style=discord.TextStyle.long,
            default=current_desc,
            required=False,
        )
        self.add_item(self.title_input)
        self.add_item(self.mission_input)
        self.add_item(self.desc_input)

    async def on_submit(self, interact: discord.Interaction):
        try:
            db = interact.client.db
            cursor = db.cursor()

            # update DB
            cursor.execute(
                "UPDATE party SET title = ?, mission_type = ?, description = ? WHERE message_id = ?",
                (
                    self.title_input.value,
                    self.mission_input.value,
                    self.desc_input.value,
                    interact.message.id,
                ),
            )
            db.commit()

            # refresh Embed
            new_embed = await build_party_embed_from_db(interact.message.id, db)
            await interact.response.edit_message(embed=new_embed)

            # edit thread title & webhook msg
            if isinstance(interact.channel, discord.Thread):
                thread_to_edit = interact.client.get_channel(interact.channel.id)
                if thread_to_edit:
                    new_thread_name = (
                        f"[{self.mission_input.value}] {self.title_input.value}"
                    )
                    await thread_to_edit.edit(name=new_thread_name)

            #     # edit webhook msg
            #     try:  # get the webhook (used to create the thread)
            #         webhook_name = LFG_WEBHOOK_NAME
            #         webhooks = await interact.channel.parent.webhooks()
            #         webhook = discord.utils.get(webhooks, name=webhook_name)

            #         if webhook:  # edit msg using the webhook
            #             await webhook.edit_message(
            #                 message_id=interact.channel.id,
            #                 content=f"[{self.mission_input.value}] {self.title_input.value}",
            #             )
            #     except discord.NotFound:
            #         pass  # started msg not found, maybe deleted manually

            await save_log(
                lock=interact.client.log_lock,
                type="event",
                cmd="btn.edit.article",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"PartyEditModal -> Clicked Submit",
                obj=f"{self.title_input.value}\n{self.mission_input.value}\n{self.desc_input.value}",
            )

        except Exception as e:
            await interact.response.send_message(
                f"{ts.get(f'{pf_edit}err')}: {e}", ephemeral=True
            )
            await save_log(
                lock=interact.client.log_lock,
                type="event.err",
                cmd="btn.edit.article",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"PartyEditModal -> Clicked Submit",
                obj=f"{e}\nT:{self.title_input.value}\nTYP:{self.mission_input.value}\nDESC:{self.desc_input.value}",
            )


# define party size adjustment modal
class PartySizeModal(discord.ui.Modal, title=ts.get(f"{pf_size}ui-title")):
    def __init__(self, current_max: int):
        super().__init__(timeout=None)

        self.size_input = discord.ui.TextInput(
            label=ts.get(f"{pf_size}label"),
            style=discord.TextStyle.short,
            default=str(current_max),
            required=True,
        )
        self.add_item(self.size_input)

    async def on_submit(self, interact: discord.Interaction):
        try:
            new_max_size_str = self.size_input.value

            # NaN || < 0
            if not new_max_size_str.isdigit() or int(new_max_size_str) < 2:
                await interact.response.send_message(
                    ts.get(f"{pf_size}err-low"), ephemeral=True
                )
                return

            if not new_max_size_str.isdigit() or int(new_max_size_str) > 4:
                await interact.response.send_message(
                    ts.get(f"{pf_size}err-high"), ephemeral=True
                )
                return

            new_max_size = int(new_max_size_str)
            db = interact.client.db
            cursor = db.cursor()

            # check the current number of participants
            current_participants_count = cursor.execute(
                "SELECT COUNT(*) FROM participants p JOIN party pa ON p.party_id = pa.id WHERE pa.message_id = ?",
                (interact.message.id,),
            ).fetchone()[0]

            # overflow
            if new_max_size < current_participants_count:
                await interact.response.send_message(
                    f"{ts.get(f'{pf_size}err-high-1')}({current_participants_count}){ts.get(f'{pf_size}err-high-2')}",
                    ephemeral=True,
                )
                return

            # update DB
            cursor.execute(
                "UPDATE party SET max_users = ? WHERE message_id = ?",
                (new_max_size, interact.message.id),
            )
            db.commit()

            # refresh Embed
            new_embed = await build_party_embed_from_db(interact.message.id, db)
            await interact.response.edit_message(embed=new_embed)

            await save_log(
                lock=interact.client.log_lock,
                type="event",
                cmd="btn.edit.partysize",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"PartySizeModal -> Clicked Submit",
                obj=new_max_size_str,
            )

        except Exception as e:
            await interact.response.send_message(
                f"{ts.get(f'{pf_edit}err')}: {e}", ephemeral=True
            )
            await save_log(
                lock=interact.client.log_lock,
                type="event.err",
                cmd="btn.edit.partysize",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"PartySizeModal -> Clicked Submit '{new_max_size_str}'",
                obj=e,
            )


# define delete confirmation view
class ConfirmDeleteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None

    # delete confirm btn
    @discord.ui.button(
        label=ts.get(f"{pf_btn}btny"),
        style=discord.ButtonStyle.danger,
        custom_id="confirm_delete_yes",
    )
    async def yes_button(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        try:
            db = interact.client.db
            cursor = db.cursor()

            # edit webhook msg
            try:
                webhook_name = LFG_WEBHOOK_NAME
                webhooks = await interact.channel.parent.webhooks()
                webhook = discord.utils.get(webhooks, name=webhook_name)

                if webhook:
                    starter_message = await interact.channel.parent.fetch_message(
                        interact.channel.id
                    )
                    if starter_message:
                        await webhook.edit_message(
                            message_id=interact.channel.id,
                            content=ts.get(f"{pf}p-del-deleted"),
                        )
                else:  #  if webhook is not found
                    starter_message = await interact.channel.parent.fetch_message(
                        interact.channel.id
                    )
                    await starter_message.edit(content=ts.get(f"{pf}p-del-deleted"))
            except discord.NotFound:
                pass  # starter msg not found, maybe deleted manually

            # delete thread
            thread_to_delete = interact.client.get_channel(interact.channel.id)
            if thread_to_delete:
                await thread_to_delete.delete()

            # delete party info from DB
            cursor.execute(
                "DELETE FROM party WHERE thread_id = ?", (interact.channel.id,)
            )
            db.commit()

            await save_log(
                lock=interact.client.log_lock,
                type="event",
                cmd="btn.confirm.delete",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"ConfirmDeleteView -> clicked yes",
            )

        except discord.Forbidden as e:
            await interact.response.send_message(
                ts.get(f"{pf_btn}err-del"), ephemeral=True
            )
            await save_log(
                lock=interact.client.log_lock,
                type="event",
                cmd="btn.confirm.delete",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"ConfirmDeleteView -> clicked yes | but Forbidden\n{e}",
            )
        except Exception as e:
            await interact.response.send_message(f"{pf_size}err: {e}", ephemeral=True)
            await save_log(
                lock=interact.client.log_lock,
                type="event",
                cmd="btn.confirm.delete",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"ConfirmDeleteView -> clicked yes | but ERR\n{e}",
                obj=e,
            )

        self.value = True
        self.stop()

    # delete cancel btn
    @discord.ui.button(
        label=ts.get(f"{pf_btn}btnn"),
        style=discord.ButtonStyle.secondary,
        custom_id="confirm_delete_no",
    )
    async def no_button(self, interact: discord.Interaction, button: discord.ui.Button):
        await interact.response.edit_message(
            content=ts.get(f"{pf_btn}cancel"), view=None
        )
        self.value = False
        self.stop()

        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.confirm.delete.cancel",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"ConfirmDeleteView -> clicked no",
        )


# define kick member view
class KickMemberSelect(discord.ui.Select):
    def __init__(self, members: list[dict], original_message_id: int):
        self.original_message_id = original_message_id
        options = [
            discord.SelectOption(
                label=member["display_name"],
                # description=f"ID: {member['user_id']}",
                value=str(member["user_id"]),
            )
            for member in members
        ]
        super().__init__(
            placeholder=ts.get(f"{pf}pv-kick-modal-select-placeholder"),
            min_values=1,
            max_values=1,
            options=options,
            custom_id="kick_member_select",
        )

    async def callback(self, interact: discord.Interaction):
        selected_user_id = int(self.values[0])
        db = interact.client.db
        cursor = db.cursor()

        await interact.response.defer(ephemeral=True)

        try:
            party_data = db.execute(
                "SELECT id, host_id FROM party WHERE message_id = ?",
                (self.original_message_id,),
            ).fetchone()
            if not party_data:
                await interact.response.send_message(
                    content=ts.get(f"{pf_pv}not-found"), ephemeral=True
                )
                return

            party_id = party_data["id"]
            kicked_user_mention = f"<@{selected_user_id}>"

            cursor.execute(
                "DELETE FROM participants WHERE party_id = ? AND user_id = ?",
                (party_id, selected_user_id),
            )
            db.commit()

            # Fetch the original party message and edit it
            original_message = await interact.channel.fetch_message(
                self.original_message_id
            )
            new_embed = await build_party_embed_from_db(self.original_message_id, db)
            await original_message.edit(embed=new_embed)

            host_mention = f"<@{party_data['host_id']}>, "
            # Send notification to the thread and confirmation to the user
            await interact.followup.send(
                f"{kicked_user_mention} {ts.get(f'{pf}pv-kick-success')}"
            )

            await save_log(
                lock=interact.client.log_lock,
                type="event",
                cmd="select.kick.member",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"Kicked user {selected_user_id}",
            )

        except Exception as e:
            await interact.followup.send(f"오류: {e}", ephemeral=True)
            await save_log(
                lock=interact.client.log_lock,
                type="event.err",
                cmd="select.kick.member",
                user=f"{interact.user.display_name}",
                msg=f"Error in KickMemberSelect callback",
                obj=e,
            )
        finally:
            await interact.delete_original_response()


class KickMemberView(discord.ui.View):
    def __init__(self, members_to_kick: list[dict], original_message_id: int):
        super().__init__(timeout=60)
        self.add_item(KickMemberSelect(members_to_kick, original_message_id))


# define join/leave confirm view
class ConfirmJoinLeaveView(discord.ui.View):
    def __init__(
        self,
        action: str,
        db: sqlite3.Connection,
        party_id: int,
        user_id: int,
        user_mention: str,
        original_message: discord.Message,
    ):
        super().__init__(timeout=60)
        self.value = None
        self.action = action
        self.db = db
        self.party_id = party_id
        self.user_id = user_id
        self.user_mention = user_mention
        self.original_message = original_message  # The main embed message

    @discord.ui.button(
        label=ts.get(f"{pf_btn}btny"),
        style=discord.ButtonStyle.success,
        custom_id="confirm_join_yes",
    )
    async def yes_button(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        # Get host_id to mention the host
        party_info = self.db.execute(
            "SELECT host_id FROM party WHERE id = ?", (self.party_id,)
        ).fetchone()
        host_mention = f"<@{party_info[0]}>, " if party_info else ""

        cursor = self.db.cursor()

        try:
            if self.action == "join":
                cursor.execute(
                    "INSERT INTO participants (party_id, user_id, user_mention, display_name) VALUES (?, ?, ?, ?)",
                    (
                        self.party_id,
                        self.user_id,
                        self.user_mention,
                        interact.user.display_name,
                    ),
                )
                self.db.commit()
                # reply confirm chat
                await interact.response.edit_message(
                    content=ts.get(f"{pf_pv}joined"), view=None
                )
                # Send a public message to the thread channel
                await self.original_message.channel.send(
                    f"{host_mention}< {interact.user.display_name} > {ts.get(f'{pf}pc-joined')}"
                )

                await save_log(
                    lock=interact.client.log_lock,
                    type="event",
                    cmd="btn.confirm.join",
                    user=f"{interact.user.display_name}",
                    guild=f"{interact.guild.name}",
                    channel=f"{interact.channel.name}",
                    msg=f"ConfirmJoinLeaveView -> action join",
                )

            elif self.action == "leave":
                cursor.execute(
                    "DELETE FROM participants WHERE party_id = ? AND user_id = ?",
                    (self.party_id, self.user_id),
                )
                self.db.commit()
                # reply confirm chat
                await interact.response.edit_message(
                    content=ts.get(f"{pf_pv}exited"), view=None
                )
                # Send a public message to the thread channel
                await self.original_message.channel.send(
                    f"{host_mention}< {interact.user.display_name} > {ts.get(f'{pf}pc-lefted')}"
                )

                await save_log(
                    lock=interact.client.log_lock,
                    type="event",
                    cmd="btn.confirm.leave",
                    user=f"{interact.user.display_name}",
                    guild=f"{interact.guild.name}",
                    channel=f"{interact.channel.name}",
                    msg=f"ConfirmJoinLeaveView -> action leave",
                )

            # refresh party embed article
            new_embed = await build_party_embed_from_db(
                self.original_message.id, self.db
            )
            await self.original_message.edit(embed=new_embed)

        except Exception as e:
            # if response is done, use followup
            if not interact.response.is_done():
                await interact.response.edit_message(content=f"오류: {e}", view=None)
            else:
                await interact.followup.send(f"오류: {e}", ephemeral=True)

            await save_log(
                lock=interact.client.log_lock,
                type="event",
                cmd="btn.confirm.join",
                user=f"{interact.user.display_name}",
                guild=f"{interact.guild.name}",
                channel=f"{interact.channel.name}",
                msg=f"ConfirmJoinLeaveView -> action join or levae but ERR",
                obj=e,
            )

        self.value = True
        self.stop()

    @discord.ui.button(
        label=ts.get(f"{pf_btn}btnn"),
        style=discord.ButtonStyle.secondary,
        custom_id="confirm_join_no",
    )
    async def no_button(self, interact: discord.Interaction, button: discord.ui.Button):
        await interact.response.edit_message(
            content=ts.get(f"{pf_btn}cancel"), view=None
        )
        self.value = False
        self.stop()

        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.confirm.delete.cancel",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"ConfirmJoinLeaveView -> clicked no",
        )


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

    async def fetch_party_data(self, interact: discord.Interaction):
        """fetch party and participant data from DB"""
        db = interact.client.db
        db.row_factory = sqlite3.Row

        # search party using message id
        party_data = db.execute(
            "SELECT * FROM party WHERE message_id = ?", (interact.message.id,)
        ).fetchone()

        if not party_data:
            # defer()가 이미 호출된 경우 followup.send 사용
            if not interact.response.is_done():
                await interact.response.send_message(
                    ts.get(f"{pf_pv}not-found"), ephemeral=True
                )
            else:
                await interact.followup.send(
                    ts.get(f"{pf_pv}not-found"), ephemeral=True
                )
            return None, None

        # search participants
        participants_list = db.execute(
            "SELECT * FROM participants WHERE party_id = ?", (party_data["id"],)
        ).fetchall()

        return dict(party_data), [dict(p) for p in participants_list]

    @discord.ui.button(  # 참여하기
        label=ts.get(f"{pf_pv}join-btn"),
        style=discord.ButtonStyle.success,
        custom_id="party_join",
    )
    async def join_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.main.join",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> join_party",
        )

        if await self.is_cooldown(interact, self.cooldown_action):
            return

        db = interact.client.db
        party_data, participants_list = await self.fetch_party_data(interact)
        if not party_data:
            return

        user_id = interact.user.id
        is_participant = any(p["user_id"] == user_id for p in participants_list)

        if is_participant:  # already joined
            await interact.response.send_message(
                ts.get(f"{pf_pv}already-joined"), ephemeral=True
            )
            return

        # overflow: more than max_user
        if len(participants_list) >= party_data["max_users"]:
            await interact.response.send_message(ts.get(f"{pf_pv}full"), ephemeral=True)
            return

        view = ConfirmJoinLeaveView(
            action="join",
            db=db,
            party_id=party_data["id"],
            user_id=user_id,
            user_mention=interact.user.mention,
            original_message=interact.message,
        )
        await interact.response.send_message(
            ts.get(f"{pf_pv}confirm-join"), view=view, ephemeral=True
        )

        timed_out = await view.wait()
        if timed_out and view.value is None:
            try:
                await interact.edit_original_response(
                    content=ts.get(f"{pf}pv-del-cancel"), view=None
                )
            except discord.errors.NotFound:
                pass

    @discord.ui.button(  # 탈퇴하기
        label=ts.get(f"{pf_pv}leave-btn"),
        style=discord.ButtonStyle.danger,
        custom_id="party_leave",
    )
    async def leave_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.main.leave",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> leave_party",
        )

        if await self.is_cooldown(interact, self.cooldown_action):
            return

        db = interact.client.db

        party_data, participants_list = await self.fetch_party_data(interact)
        if not party_data:
            return

        party_id = party_data["id"]
        user_id = interact.user.id

        # check: is interacted user host
        if user_id == party_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf_pv}host-exit-err"), ephemeral=True
            )
            return

        # check: is interacted user already joined
        is_participant = any(p["user_id"] == user_id for p in participants_list)

        if not is_participant:
            await interact.response.send_message(
                ts.get(f"{pf_pv}already-left"), ephemeral=True
            )
            return

        view = ConfirmJoinLeaveView(
            action="leave",
            db=db,
            party_id=party_id,
            user_id=user_id,
            user_mention=interact.user.mention,
            original_message=interact.message,
        )
        await interact.response.send_message(
            ts.get(f"{pf_pv}confirm-exit"), view=view, ephemeral=True
        )

        timed_out = await view.wait()
        if timed_out and view.value is None:
            try:
                await interact.edit_original_response(
                    content=ts.get(f"{pf}pv-del-cancel"), view=None
                )
            except discord.errors.NotFound:
                pass

    @discord.ui.button(  # 인원 수정
        label=ts.get(f"{pf_pv}mod-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_size",
    )
    async def edit_size(self, interact: discord.Interaction, button: discord.ui.Button):
        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.main.edit-size",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> edit_size",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        party_data, _ = await self.fetch_party_data(interact)
        if not party_data:
            return

        if interact.user.id != party_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf_pv}err-only-host"), ephemeral=True
            )
            return

        modal = PartySizeModal(current_max=party_data["max_users"])
        await interact.response.send_modal(modal)

    @discord.ui.button(  # 글 수정
        label=ts.get(f"{pf_pv}mod-article"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_content",
    )
    async def edit_content(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.main.edit-content",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> edit_content",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        party_data, _ = await self.fetch_party_data(interact)
        if not party_data:
            return

        if interact.user.id != party_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf_pv}err-mod-article"), ephemeral=True
            )
            return

        modal = PartyEditModal(
            current_title=party_data["title"],
            current_mission=party_data["mission_type"],
            current_desc=party_data.get("description", "") or "",
        )
        await interact.response.send_modal(modal)

    @discord.ui.button(  # 모집 완료
        label=ts.get(f"{pf_pv}done"),
        style=discord.ButtonStyle.primary,
        custom_id="party_toggle_close",
    )
    async def toggle_close_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.main.toggle_close_party",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> toggle_close_party",
            # obj=new_status,
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        db = interact.client.db
        cursor = db.cursor()

        party_data, _ = await self.fetch_party_data(interact)
        if not party_data:
            return

        if interact.user.id != party_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf_pv}err-only-status"), ephemeral=True
            )
            return

        # toggle state
        new_status = (
            ts.get(f"{pf_pv}done")
            if party_data["status"] == ts.get(f"{pf_pv}ing")
            else ts.get(f"{pf_pv}ing")
        )

        cursor.execute(
            "UPDATE party SET status = ? WHERE id = ?", (new_status, party_data["id"])
        )
        db.commit()

        # edit webhook msg
        try:
            webhook_name = LFG_WEBHOOK_NAME
            webhooks = await interact.channel.parent.webhooks()
            webhook = discord.utils.get(webhooks, name=webhook_name)

            # original_content = f"[{party_data['mission_type']}] {party_data['title']}"
            if new_status == ts.get(f"{pf_pv}done"):
                new_content = ts.get(f"{pf}pv-tgl-done")
                # f"**[{ts.get(f'{pf_pv}done')}]** ~~{original_content}~~"
            else:
                new_content = ts.get(f"{pf}pv-tgl-ing")

            if webhook:
                await webhook.edit_message(
                    message_id=interact.channel.id,
                    content=new_content,
                )
            else:  # if webhook is not found
                starter_message = await interact.channel.parent.fetch_message(
                    interact.channel.id
                )
                if starter_message:
                    await starter_message.edit(content=new_content)
        except discord.NotFound:
            pass  # starter msg not found, maybe deleted manually
        except Exception as e:
            await save_log(
                lock=interact.client.log_lock,
                type="event.err",
                msg=f"Failed to edit webhook message on party close toggle: {e}",
            )

        # refresh embed
        new_embed = await build_party_embed_from_db(interact.message.id, db)

        # change button label & style
        join_btn = discord.utils.get(self.children, custom_id="party_join")
        edit_size_btn = discord.utils.get(self.children, custom_id="party_edit_size")
        # leave_btn = discord.utils.get(self.children, custom_id="party_leave")

        if new_status == ts.get(f"{pf_pv}done"):
            button.label = ts.get(f"{pf_pv}ing")
            button.style = discord.ButtonStyle.success
            if join_btn:
                join_btn.disabled = True
            if edit_size_btn:
                edit_size_btn.disabled = True
            # if leave_btn:
            #     leave_btn.disabled = True

        else:
            button.label = ts.get(f"{pf_pv}done")
            button.style = discord.ButtonStyle.primary
            if join_btn:
                join_btn.disabled = False
            if edit_size_btn:
                edit_size_btn.disabled = False
            # if leave_btn:
            #     leave_btn.disabled = False

        await interact.response.edit_message(embed=new_embed, view=self)

    @discord.ui.button(  # 파티원 호출
        label=ts.get(f"{pf}pv-call-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_call_members",
    )
    async def call_members(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.main.call_members",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> call_members",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        party_data, participants_list = await self.fetch_party_data(interact)
        if not party_data:
            interact.response.send_message(ts.get(f"{pf}pv-not-found"), ephemeral=True)
            return

        if interact.user.id != party_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf}pv-err-only-host-call"), ephemeral=True
            )
            return

        # create member list (exclude host)
        members_to_call = [
            p["user_mention"]
            for p in participants_list
            if p["user_id"] != party_data["host_id"]
        ]

        if not members_to_call:
            await interact.response.send_message(
                ts.get(f"{pf}pv-call-no-members"), ephemeral=True
            )
            return

        call_message = f"{' '.join(members_to_call)} {ts.get(f'{pf}pv-call-msg')}"
        await interact.response.send_message(call_message)

    @discord.ui.button(  # 멤버 내보내기
        label=ts.get(f"{pf}pv-kick-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_kick_member",
    )
    async def kick_member(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.main.kick_member",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> kick_member",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        party_data, participants_list = await self.fetch_party_data(interact)
        if not party_data:
            return

        if interact.user.id != party_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf}pv-err-only-host-kick"), ephemeral=True
            )
            return

        members_to_kick = [
            p for p in participants_list if p["user_id"] != party_data["host_id"]
        ]

        if not members_to_kick:
            await interact.response.send_message(
                ts.get(f"{pf}pv-kick-no-members"), ephemeral=True
            )
            return

        view = KickMemberView(members_to_kick, interact.message.id)
        await interact.response.send_message(
            ts.get(f"{pf}pv-kick-modal-title"), view=view, ephemeral=True
        )

    @discord.ui.button(  # 글 삭제
        label=ts.get(f"{pf}pv-del-label"),
        style=discord.ButtonStyle.danger,
        custom_id="party_delete",
    )
    async def delete_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type="event",
            cmd="btn.main.delete_party",
            user=f"{interact.user.display_name}",
            guild=f"{interact.guild.name}",
            channel=f"{interact.channel.name}",
            msg=f"PartyView -> delete_party",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        party_data, _ = await self.fetch_party_data(interact)
        if not party_data:
            return

        if interact.user.id != party_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf}pv-del-only-host"), ephemeral=True
            )
            return

        view = ConfirmDeleteView()
        await interact.response.send_message(
            ts.get(f"{pf}pv-del-confirm"), view=view, ephemeral=True
        )

        timed_out = await view.wait()
        if timed_out and view.value is None:
            try:
                await interact.edit_original_response(
                    content=ts.get(f"{pf}pv-del-cancel"), view=None
                )
                await save_log(
                    lock=interact.client.log_lock,
                    type="event",
                    cmd="btn.main.delete_party",
                    user=f"{interact.user.display_name}",
                    guild=f"{interact.guild.name}",
                    channel=f"{interact.channel.name}",
                    msg=f"PartyView -> delete_party -> TIME_OUT",
                )
            except discord.errors.NotFound:
                pass


# embed creation helper function
def build_party_embed(data: dict) -> discord.Embed:
    """[for internal use] creates an embed based on a formatted dictionary"""
    color = discord.Color.red() if data["is_closed"] else discord.Color.blue()
    status_text = (
        f"({ts.get(f'{pf_pv}done')})"
        if data["is_closed"]
        else f"({ts.get(f'{pf_pv}ing2')})"
    )

    participants_str = ", ".join(data["participants"])
    if not participants_str:
        participants_str = ts.get(f"{pf}pb-no-player")

    description_field = ""
    if data.get("description"):
        description_field = f"{data['description']}"

    description = f"""
### {data['title']} {status_text}

- **{ts.get(f'{pf}pb-host')}:** {data['host_mention']}
- **{ts.get(f'{pf}pb-player-count')}:** {len(data['participants'])} / {data['max_users']}
- **{ts.get(f'{pf}pb-player-joined')}:** {participants_str}
- **{ts.get(f'{pf}pb-mission')}:** {data['mission']}

{description_field}

> {ts.get(f'{pf}pb-desc')}
```
/w {data['game_nickname']}
```
"""
    embed = discord.Embed(description=description.strip(), color=color)
    embed.set_footer(text=f"{ts.get(f'{pf}pb-pid')}: {data['id']}")
    return embed


async def build_party_embed_from_db(
    message_id: int, db: sqlite3.Connection
) -> discord.Embed:
    """[for external use] creates an embed using a message_id & db connection"""
    db.row_factory = sqlite3.Row

    # 1. select party info
    party_data = db.execute(
        "SELECT * FROM party WHERE message_id = ?", (message_id,)
    ).fetchone()
    if not party_data:
        return discord.Embed(
            title=ts.get(f"{pf}err"),
            description=ts.get(f"pdb-not-found-party"),
            color=discord.Color.dark_red(),
        )

    # 2. select participant list
    participants_list = db.execute(
        "SELECT user_mention FROM participants WHERE party_id = ?", (party_data["id"],)
    ).fetchall()

    # 3. assemble into dictionary format required by build_party_embed
    data_dict = {
        "id": party_data["id"],
        "is_closed": party_data["status"] == ts.get(f"{pf_pv}done"),
        "title": party_data["title"],
        "host_mention": (
            db.execute(
                "SELECT user_mention FROM participants WHERE party_id = ? AND user_id = ?",
                (party_data["id"], party_data["host_id"]),
            ).fetchone()
            or [f"<@{party_data['host_id']}>"]
        )[0],
        "max_users": party_data["max_users"],
        "participants": [p["user_mention"] for p in participants_list],
        "mission": party_data["mission_type"],
        "game_nickname": party_data["game_nickname"],
        "description": party_data["description"] or "",
    }

    return build_party_embed(data_dict)


async def cmd_create_thread_helper(
    interact: discord.Interaction,
    db_conn: sqlite3.Connection,
    title: str,
    # game_nickname: str,
    mission_type: str,
    description: str = "(설명 없음)",
    number_of_user: int = 4,
) -> None:
    if interact.guild.id != CHANNELS["party-guild"]:
        msg_obj = "지정된 서버에서만 사용할 수 있는 명령어입니다."  # VAR
        await interact.response.send_message(msg_obj, ephemeral=True)
        await save_log(
            lock=interact.client.log_lock,
            type="cmd",
            cmd=f"cmd.party",
            time=interact.created_at,
            user=interact.user.display_name,
            guild=interact.guild,
            channel=interact.channel,
            msg="[info] cmd used, but unauthorized server",
            obj=msg_obj,
        )
        return

    db = db_conn
    db.row_factory = sqlite3.Row

    RESULT: str = ""
    game_nickname = parseNickname(interact.user.display_name)
    ch_file = CHANNELS["party"]
    target_channel = interact.client.get_channel(ch_file)

    await interact.response.defer(ephemeral=True)

    if number_of_user < 2:
        await interact.followup.send(
            ts.get(f"{pf}pt-low"),
            ephemeral=True,
        )
        number_of_user = 4
        result += "low number\n"

    elif number_of_user > 4:
        await interact.followup.send(
            ts.get(f"{pf}pt-high"),
            ephemeral=True,
        )
        number_of_user = 4
        result += "high humber\n"

    if target_channel and isinstance(target_channel, discord.TextChannel):
        try:
            cursor = db.cursor()

            # 1.1. INSERT party information into the table
            cursor.execute(
                "INSERT INTO party (host_id, title, mission_type, max_users, game_nickname, status, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    interact.user.id,
                    title,
                    mission_type,
                    number_of_user,
                    game_nickname,
                    ts.get(f"{pf_pv}ing"),
                    description,
                ),
            )
            PARTY_ID = cursor.lastrowid  # the unique ID of the newly created party

            # 1.2. INSERT the host as the first participant
            cursor.execute(
                "INSERT INTO participants (party_id, user_id, user_mention, display_name) VALUES (?, ?, ?, ?)",
                (
                    PARTY_ID,
                    interact.user.id,
                    interact.user.mention,
                    interact.user.display_name,
                ),
            )
            db.commit()  # fisrt commit (party creation)

            # create a webhook
            webhook_name = LFG_WEBHOOK_NAME
            webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(webhooks, name=webhook_name)
            if webhook is None:
                webhook = await target_channel.create_webhook(name=webhook_name)

            # send msg via webhook to impersonate the user
            # msg: starting point of the thread.
            thread_starter_msg = await webhook.send(
                content=ts.get(f"{pf}created-party"),
                username=interact.user.display_name,
                avatar_url=interact.user.display_avatar.url,
                wait=True,
            )

            # create thread from starter msg (webhook)
            thread = await thread_starter_msg.create_thread(
                name=f"[{mission_type}] {title}",
                reason=f"Thread for {interact.user.display_name}'s party",
            )

            await interact.followup.send(
                f"✅ '{target_channel.name}' {ts.get(f'{pf}pt-create')} {thread.mention}",
                ephemeral=True,
            )

            # initial data
            initial_data = {
                "id": PARTY_ID,
                # "host_id": interact.user.id,
                "host_mention": interact.user.mention,
                "game_nickname": game_nickname,
                "title": title,
                "mission": mission_type,
                "max_users": number_of_user,
                "participants": [interact.user.mention],
                # "participant_ids": [interact.user.id],
                "is_closed": False,
                "description": description or "",
            }

            embed = build_party_embed(initial_data)
            view = PartyView()

            # 4. send message & update DB
            msg = await thread.send(embed=embed, view=view)

            # 4.1. UPDATE thread_id & message_id
            cursor.execute(
                "UPDATE party SET thread_id = ?, message_id = ? WHERE id = ?",
                (thread.id, msg.id, PARTY_ID),
            )
            db.commit()  # secondary commit (update ID info)

            RESULT += "DONE!\n"

        except discord.Forbidden as e:
            await interact.followup.send(
                ts.get(f"{pf}no-thread-permission"),
                ephemeral=True,
            )
            RESULT += f"Forbidden {e}\n"
        except discord.HTTPException as e:
            await interact.followup.send(
                f"{ts.get(f'{pf}err-creation')}",
                ephemeral=True,
            )
            RESULT += f"HTTPException {e}\n"
        except Exception as e:
            await interact.followup.send(
                f"{ts.get(f'{pf}err-unknown')}", ephemeral=True
            )
            RESULT += f"ERROR {e}"
    else:
        await interact.followup.send(ts.get(f"{pf}not-found-ch"), ephemeral=True)

    await save_log(
        lock=interact.client.log_lock,
        type="cmd",
        cmd=f"cmd.party",
        time=interact.created_at,
        user=interact.user.display_name,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used",  # VAR
        obj=f"{RESULT}T:{title}\nTYPE:{mission_type}\nDESC:{description}\n{number_of_user}",
    )
