import discord
from discord import ui
from discord.ext import commands
import datetime as dt
import random

from src.translator import ts
from src.utils.times import convert_remain, parseKoreanDatetime
from src.utils.return_err import return_traceback
from src.utils.logging_utils import save_log
from config.config import LOG_TYPE
from src.constants.keys import (
    LFG_WEBHOOK_NAME,
    COOLDOWN_BTN_ACTION,
    COOLDOWN_BTN_MANAGE,
    COOLDOWN_BTN_CALL,
)
from src.utils.permission import is_admin_user
from src.services.party_service import PartyService
from src.services.warning_count import UserService

pf = "cmd.party."
MIN_SIZE = 2
MAX_SIZE = 20


async def isPartyExist(interact: discord.Interaction, party):
    if party:
        return True

    embed = discord.Embed(
        title=ts.get(f"{pf}err"),
        description=ts.get(f"{pf}pv-not-found"),
        color=discord.Color.red(),
    )
    await interact.response.send_message(embed=embed, ephemeral=True)
    await save_log(
        pool=interact.client.db,
        type="err",
        cmd="btn",
        msg="party not found from db",
        interact=interact,
    )
    return False


# ----------------- Helper: Embed Builder -----------------
async def build_party_embed(
    data: dict, db_pool, isDelete: bool = False
) -> discord.Embed:
    color = discord.Color.orange() if data.get("is_closed") else discord.Color.blue()
    status_text = (
        f"({ts.get(f'{pf}pv-done')})"
        if data.get("is_closed")
        else f"({ts.get(f'{pf}pv-ing2')})"
    )

    # host warning check
    host_warn_count = await UserService.get_host_warning_count(db_pool, data["host_id"])

    participants_str = ", ".join(data["participants"]) or ts.get(f"{pf}pb-no-player")

    desc_field = data.get("description", "")
    warn_desc = (
        ts.get(f"cmd.warning-count").format(count=host_warn_count)
        if host_warn_count >= 1
        else ""
    )

    departure_data = data["departure"]
    if isinstance(departure_data, dt.datetime):
        time_output = convert_remain(departure_data.timestamp())
    else:
        time_output = (
            convert_remain(parseKoreanDatetime(departure_data).timestamp())
            if departure_data
            else ts.get(f"{pf}pb-departure-none")
        )

    description = f"""{warn_desc}### {data['title']} {status_text}
- **{ts.get(f'{pf}pb-departure')}:** {time_output}
- **{ts.get(f'{pf}pb-host')}:** {data['host_mention']}
- **{ts.get(f'{pf}pb-player-count')}:** {len(data['participants'])} / {data['max_users']}
- **{ts.get(f'{pf}pb-player-joined')}:** {participants_str}
- **{ts.get(f'{pf}pb-mission')}:** {data['mission']}

{desc_field}"""

    if isDelete:
        description = "~~" + description.replace("~~", "") + "~~"

    embed = discord.Embed(
        description=description.strip(), color=color if not isDelete else 0xFF0000
    )
    embed.set_footer(text=f"{ts.get(f'{pf}pb-pid')}: {data['id']}")
    return embed


async def build_party_embed_from_db(message_id: int, pool, isDelete: bool = False):
    party, participants = await PartyService.get_party_by_message_id(pool, message_id)
    if not party:
        return discord.Embed(
            title=ts.get(f"{pf}err"),
            description=ts.get(f"{pf}pv-not-found"),
            color=discord.Color.dark_red(),
        )

    host_mention = f"<@{party['host_id']}>"
    # find specific host mention if available in participants
    for p in participants:
        if p["user_id"] == party["host_id"]:
            host_mention = p["user_mention"]
            break

    return await build_party_embed(
        {
            "id": party["id"],
            "host_id": party["host_id"],
            "is_closed": party["status"] == ts.get(f"{pf}pv-done"),
            "title": party["title"],
            "host_mention": host_mention,
            "max_users": party["max_users"],
            "participants": [p["user_mention"] for p in participants],
            "mission": party["game_name"],
            "departure": party["departure"],
            "description": party["description"] or "",
        },
        pool,
        isDelete,
    )


# ----------------- Modals -----------------
class PartyEditModal(ui.Modal, title=ts.get(f"{pf}edit-title")):
    def __init__(self, current_title, current_mission, current_desc):
        super().__init__(timeout=None)
        self.title_input = ui.TextInput(
            label=ts.get(f"{pf}edit-title-input"), default=current_title, required=True
        )
        self.mission_input = ui.TextInput(
            label=ts.get(f"{pf}edit-mission-input"),
            default=current_mission,
            required=True,
        )
        self.desc_input = ui.TextInput(
            label=ts.get(f"{pf}edit-desc-input"),
            style=discord.TextStyle.long,
            default=current_desc,
            required=False,
        )
        self.add_item(self.title_input)
        self.add_item(self.mission_input)
        self.add_item(self.desc_input)

    async def on_submit(self, interact: discord.Interaction):
        try:
            await PartyService.update_party_content(
                interact.client.db,
                interact.message.id,
                self.title_input.value,
                self.mission_input.value,
                self.desc_input.value,
            )
            new_embed = await build_party_embed_from_db(
                interact.message.id, interact.client.db
            )
            await interact.response.edit_message(embed=new_embed)

            if isinstance(interact.channel, discord.Thread):
                await interact.channel.edit(
                    name=f"[{self.mission_input.value}] {self.title_input.value}"
                )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="btn.edit.article",
                interact=interact,
                msg=f"PartyEditModal -> Clicked Submit",
                obj=f"{self.title_input.value}\n{self.mission_input.value}\n{self.desc_input.value}",
            )
        except Exception:
            await interact.response.send_message(
                ts.get(f"{pf}edit-err"), ephemeral=True
            )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.e_event,
                cmd="btn.edit.article",
                interact=interact,
                msg=f"PartyEditModal -> Clicked Submit",
                obj=f"T:{self.title_input.value}\nTYP:{self.mission_input.value}\nDESC:{self.desc_input.value}\n{return_traceback()}",
            )


class PartySizeModal(ui.Modal, title=ts.get(f"{pf}size-ui-title")):
    def __init__(self, current_max):
        super().__init__(timeout=None)
        self.size_input = ui.TextInput(
            label=ts.get(f"{pf}size-label"), default=str(current_max), required=True
        )
        self.add_item(self.size_input)

    async def on_submit(self, interact: discord.Interaction):
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.edit.partysize",
            interact=interact,
            msg=f"PartySizeModal -> Clicked Submit",
            obj=self.size_input.value,
        )

        if not self.size_input.value.isdigit():
            await interact.response.send_message(
                ts.get(f"{pf}size-err-low").format(min=MIN_SIZE, max=MAX_SIZE),
                ephemeral=True,
            )
            return
        new_size = int(self.size_input.value)

        # Validation Logic (Host logic should ideally be in service, but View can handle validation for speed)
        if new_size < MIN_SIZE or new_size > MAX_SIZE:
            await interact.response.send_message(
                ts.get(f"{pf}size-err-high").format(max=MAX_SIZE), ephemeral=True
            )
            return

        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if len(participants) > new_size:
            await interact.response.send_message(
                ts.get(f"{pf}size-err-high-1").format(size=len(participants)),
                ephemeral=True,
            )
            return

        await PartyService.update_party_size(
            interact.client.db, interact.message.id, new_size
        )
        new_embed = await build_party_embed_from_db(
            interact.message.id, interact.client.db
        )
        await interact.response.edit_message(embed=new_embed)


class PartyDateEditModal(ui.Modal, title=ts.get(f"{pf}date-title")):
    def __init__(self):
        super().__init__(timeout=None)
        self.date_input = ui.TextInput(
            label=ts.get(f"{pf}date-input"), placeholder=ts.get(f"{pf}date-placeholder")
        )
        self.add_item(self.date_input)

    async def on_submit(self, interact: discord.Interaction):
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.edit.date",
            interact=interact,
            msg=f"PartyDateEditModal -> Clicked Submit",
            obj=f"{self.date_input.value}",
        )
        try:
            await PartyService.update_party_departure(
                interact.client.db, interact.message.id, self.date_input.value
            )
            new_embed = await build_party_embed_from_db(
                interact.message.id, interact.client.db
            )
            await interact.response.edit_message(embed=new_embed)
        except Exception:
            if not interact.response.is_done():
                await interact.response.send_message(
                    ts.get(f"{pf}edit-err"), ephemeral=True
                )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.e_event,
                cmd="btn.edit-date",
                interact=interact,
                msg=f"PartyDateEditModal -> Clicked Submit, but ERR",
                obj=f"{self.date_input.value}\n{return_traceback()}",
            )


# ----------------- Views -----------------
class ConfirmJoinLeaveView(ui.View):
    def __init__(self, action, party_id, interact: discord.Interaction):
        super().__init__(timeout=20)
        self.action = action
        self.db_pool = interact.client.db
        self.party_id = party_id
        self.user_id = interact.user.id
        self.user_mention = interact.user.mention
        self.original_message = interact.message
        self.interact = interact

    async def on_timeout(self):
        cmd = "PartyView.btn.confirm.join/leave"
        try:
            await self.interact.edit_original_response(
                content=ts.get(f"cmd.err-timeout"), view=None
            )
            await save_log(
                pool=self.db_pool,
                type=LOG_TYPE.event,
                cmd=cmd,
                interact=self.interact,
                msg=f"PartyView.ConfirmJoinLeaveView -> timeout",
            )
        except discord.NotFound:
            await save_log(
                pool=self.interact.client.db,
                type=LOG_TYPE.warn,
                cmd=cmd,
                interact=self.interact,
                msg=f"PartyView.ConfirmJoinLeaveView -> timeout, but Not Found",
                obj=return_traceback(),
            )
        except Exception:
            await save_log(
                pool=self.db_pool,
                type=LOG_TYPE.err,
                cmd=cmd,
                interact=self.interact,
                msg=f"PartyView.ConfirmJoinLeaveView -> timeout, but ERR",
                obj=return_traceback(),
            )

    @ui.button(label=ts.get(f"{pf}del-btny"), style=discord.ButtonStyle.success)
    async def yes_button(self, interact: discord.Interaction, button: ui.Button):
        try:
            host_warn_count = await UserService.get_host_warning_count(
                interact.client.db, interact.user.id
            )
            if self.action == "join":
                await save_log(
                    pool=interact.client.db,
                    type=LOG_TYPE.event,
                    cmd="btn.confirm.join",
                    interact=interact,
                    msg=f"ConfirmJoinLeaveView -> action join",
                )
                await PartyService.join_participant(
                    self.db_pool,
                    self.party_id,
                    self.user_id,
                    self.user_mention,
                    interact.user.display_name,
                )
                await interact.response.edit_message(
                    content=ts.get(f"{pf}pv-joined"), view=None
                )
                # TODO: random join message
                rint = 1
                await self.original_message.channel.send(
                    ts.get(f"{pf}pc-joined{rint}").format(
                        host=self.user_mention, user=interact.user.mention
                    )
                    # user warn msg
                    + ts.get(f"cmd.warning-count").format(count=host_warn_count)
                    if host_warn_count >= 1
                    else ""
                )
            elif self.action == "leave":
                await save_log(
                    pool=interact.client.db,
                    type=LOG_TYPE.event,
                    cmd="btn.confirm.leave",
                    interact=interact,
                    msg=f"ConfirmJoinLeaveView -> action leave",
                )
                await PartyService.leave_participant(
                    self.db_pool, self.party_id, self.user_id
                )
                await interact.response.edit_message(
                    content=ts.get(f"{pf}pv-exited"), view=None
                )
                # Send a public message to the thread channel
                await self.original_message.channel.send(
                    ts.get(f"{pf}pc-lefted").format(
                        host=self.user_mention, user=interact.user.mention
                    )
                    # user warn msg
                    + ts.get(f"cmd.warning-count").format(count=host_warn_count)
                    if host_warn_count >= 1
                    else ""
                )
            new_embed = await build_party_embed_from_db(
                self.original_message.id, self.db_pool
            )
            await self.original_message.edit(embed=new_embed)
        except Exception as e:
            if not interact.response.is_done():
                await interact.response.edit_message(
                    content=ts.get("general.error-cmd"), view=None
                )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="btn.confirm.err",
                interact=interact,
                msg=f"ConfirmJoinLeaveView -> action join or levae but ERR",
                obj=f"{e}\n{return_traceback()}",
            )
        self.value = True
        self.stop()

    @ui.button(label=ts.get(f"{pf}del-btnn"), style=discord.ButtonStyle.secondary)
    async def no_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.edit_message(
            content=ts.get(f"{pf}del-cancel"), view=None
        )
        self.value = False
        self.stop()
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.confirm.delete.cancel",
            interact=interact,
            msg=f"ConfirmJoinLeaveView -> clicked no",
        )


class ConfirmDeleteView(ui.View):
    def __init__(self, interact: discord.Interaction, origin_msg_id, party_view):
        super().__init__(timeout=20)
        self.interact = interact
        self.msgid = origin_msg_id
        self.party_view = party_view
        self.value = None

    async def on_timeout(self):
        cmd = "PartyView.btn.confirm.delete"
        try:
            await self.interact.edit_original_response(
                content=ts.get(f"cmd.err-timeout"), view=None
            )
            await save_log(
                pool=self.interact.client.db,
                type=LOG_TYPE.event,
                cmd=cmd,
                interact=self.interact,
                msg=f"PartyView.ConfirmDeleteView -> timeout",
            )
        except discord.NotFound:
            await save_log(
                pool=self.interact.client.db,
                type=LOG_TYPE.event,
                cmd=cmd,
                interact=self.interact,
                msg=f"PartyView.ConfirmDeleteView -> timeout, but Not Found",
            )
        except Exception:
            await save_log(
                pool=self.interact.client.db,
                type=LOG_TYPE.err,
                cmd=cmd,
                interact=self.interact,
                msg=f"PartyView.ConfirmDeleteView -> timeout, but ERR",
                obj=return_traceback(),
            )

    @ui.button(label=ts.get(f"{pf}del-btny"), style=discord.ButtonStyle.danger)
    async def yes_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.defer()
        await interact.delete_original_response()
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.confirm.delete",
            interact=interact,
            msg=f"ConfirmDeleteView -> clicked yes",
        )
        try:
            new_embed = await build_party_embed_from_db(
                self.msgid, interact.client.db, isDelete=True
            )
            for item in self.party_view.children:
                item.disabled = True

            msg = await interact.channel.fetch_message(self.msgid)
            await msg.edit(embed=new_embed, view=self.party_view)

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
                            content=ts.get(f"{pf}del-deleted"),
                        )
                else:  #  if webhook is not found
                    starter_message = await interact.channel.parent.fetch_message(
                        interact.channel.id
                    )
                    await starter_message.edit(content=ts.get(f"{pf}del-deleted"))
            except discord.NotFound:
                pass  # starter msg not found (maybe deleted manually)

            # lock thread
            if isinstance(interact.channel, discord.Thread):
                await interact.channel.edit(locked=True)

            await PartyService.delete_party(interact.client.db, interact.channel.id)

            await interact.followup.send(ts.get(f"{pf}del-deleted"), ephemeral=True)

        except Exception:
            await interact.followup.send(ts.get(f"{pf}del-err"), ephemeral=True)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="btn.confirm.delete",
                interact=interact,
                msg=f"ConfirmDeleteView -> clicked yes | but ERR\n{return_traceback()}",
                obj=return_traceback(),
            )
        self.value = True
        self.stop()

    @ui.button(label=ts.get(f"{pf}del-btnn"), style=discord.ButtonStyle.secondary)
    async def no_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.edit_message(
            content=ts.get(f"{pf}del-cancel"), view=None
        )
        self.value = False
        self.stop()

        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.confirm.delete.cancel",
            interact=interact,
            msg=f"ConfirmDeleteView -> clicked no",
        )


class KickMemberSelect(ui.Select):
    def __init__(self, members, original_message_id):
        self.original_message_id = original_message_id
        options = [
            discord.SelectOption(label=m["display_name"], value=str(m["user_id"]))
            for m in members
        ]
        super().__init__(
            placeholder=ts.get(f"{pf}pv-kick-modal-select-placeholder"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interact: discord.Interaction):
        target_id = int(self.values[0])
        party, _ = await PartyService.get_party_by_message_id(
            interact.client.db, self.original_message_id
        )

        await PartyService.leave_participant(interact.client.db, party["id"], target_id)

        new_embed = await build_party_embed_from_db(
            self.original_message_id, interact.client.db
        )
        msg = await interact.channel.fetch_message(self.original_message_id)
        await msg.edit(embed=new_embed)

        await interact.response.send_message(
            ts.get(f"{pf}pv-kick-success").format(name=f"<@{target_id}>"),
            ephemeral=False,
        )

        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="select.kick.member",
            interact=interact,
            msg=f"Kicked user {target_id} from party {party['id']}",  # TODO:verify
        )


class KickMemberView(ui.View):
    def __init__(self, members, msg_id):
        super().__init__(timeout=60)
        self.add_item(KickMemberSelect(members, msg_id))


# ----------------- Main View -----------------
class PartyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown_action = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_ACTION, commands.BucketType.user
        )
        self.cooldown_manage = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_MANAGE, commands.BucketType.user
        )
        self.cooldown_call = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_CALL, commands.BucketType.user
        )

    @staticmethod
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

    @staticmethod
    async def check_permissions(
        interact: discord.Interaction,
        party_data,
        participants,
        check_host=False,
        check_joined=False,
        check_not_joined=False,
        cmd: str = "",
    ):
        user_id = interact.user.id
        is_host: bool = user_id == party_data["host_id"]
        is_admin: bool = await is_admin_user(interact, notify=False, cmd=cmd)
        is_participant = any(p["user_id"] == user_id for p in participants)

        if check_host and not is_host:
            if not is_admin:
                await interact.response.send_message(
                    ts.get(f"{pf}pv-err-only-host"), ephemeral=True
                )
                return False

        if check_joined and not is_participant:
            await interact.response.send_message(
                ts.get(f"{pf}pv-already-left"), ephemeral=True
            )
            return False
        if check_not_joined and is_participant:
            await interact.response.send_message(
                ts.get(f"{pf}pv-already-joined"), ephemeral=True
            )
            return False
        return True

    @ui.button(
        label=ts.get(f"{pf}pv-join-btn"),
        style=discord.ButtonStyle.success,
        custom_id="party_join",
    )
    async def join_party(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.join"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> join_party",
        )

        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isPartyExist(interact, party):
            return

        if not await self.check_permissions(
            interact, party, participants, check_not_joined=True, cmd=cmd
        ):
            return

        if len(participants) >= party["max_users"]:
            await interact.response.send_message(ts.get(f"{pf}pv-full"), ephemeral=True)
            return

        view = ConfirmJoinLeaveView(
            action="join", party_id=party["id"], interact=interact
        )
        await interact.response.send_message(
            ts.get(f"{pf}pv-confirm-join"), view=view, ephemeral=True
        )

        timed_out = await view.wait()
        if timed_out and view.value is None:
            try:
                await interact.edit_original_response(
                    content=ts.get(f"{pf}pv-del-cancel"), view=None
                )
            except discord.errors.NotFound:
                pass

    @ui.button(
        label=ts.get(f"{pf}pv-leave-btn"),
        style=discord.ButtonStyle.danger,
        custom_id="party_leave",
    )
    async def leave_party(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.leave"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> leave_party",
        )

        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isPartyExist(interact, party):
            return

        if interact.user.id == party["host_id"]:  # Host cannot leave
            await interact.response.send_message(
                ts.get(f"{pf}pv-host-exit-err"), ephemeral=True
            )
            return

        if not await self.check_permissions(
            interact, party, participants, check_joined=True, cmd=cmd
        ):
            return

        view = ConfirmJoinLeaveView(
            action="leave", party_id=party["id"], interact=interact
        )
        await interact.response.send_message(
            ts.get(f"{pf}pv-confirm-exit"), view=view, ephemeral=True
        )

    @ui.button(
        label=ts.get(f"{pf}pv-mod-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_size",
    )
    async def edit_size(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.edit-size"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> edit_size",
        )
        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await self.check_permissions(
            interact, party, participants, check_host=True, cmd=cmd
        ):
            return
        await interact.response.send_modal(PartySizeModal(party["max_users"]))

    @ui.button(
        label=ts.get(f"{pf}pv-mod-article"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_content",
    )
    async def edit_content(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.edit-content"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> edit_content",
        )
        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isPartyExist(interact, party):
            return

        if not await self.check_permissions(
            interact, party, participants, check_host=True, cmd=cmd
        ):
            return
        await interact.response.send_modal(
            PartyEditModal(party["title"], party["game_name"], party["description"])
        )

    @ui.button(
        label=ts.get(f"{pf}date-btn"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_departure",
    )
    async def edit_departure(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.edit-departure"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> edit_departure",
        )
        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isPartyExist(interact, party):
            return

        if not await self.check_permissions(
            interact, party, participants, check_host=True, cmd=cmd
        ):
            return
        await interact.response.send_modal(PartyDateEditModal())

    @ui.button(
        label=ts.get(f"{pf}pv-done"),
        style=discord.ButtonStyle.primary,
        custom_id="party_toggle_close",
    )
    async def toggle_close(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.togle-close"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> toggle_close",
        )
        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isPartyExist(interact, party):
            return

        if not await self.check_permissions(
            interact, party, participants, check_host=True, cmd=cmd
        ):
            return

        new_status = await PartyService.toggle_status(
            interact.client.db, party["id"], party["status"]
        )

        # UI Button Update
        is_done = new_status == ts.get(f"{pf}pv-done")
        button.label = ts.get(f"{pf}pv-ing") if is_done else ts.get(f"{pf}pv-done")
        button.style = (
            discord.ButtonStyle.success if is_done else discord.ButtonStyle.primary
        )

        # Disable/Enable other buttons
        for child in self.children:
            if child.custom_id in ["party_join", "party_edit_size"]:
                child.disabled = is_done

        new_embed = await build_party_embed_from_db(
            interact.message.id, interact.client.db
        )
        await interact.response.edit_message(embed=new_embed, view=self)

    @ui.button(
        label=ts.get(f"{pf}pv-call-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_call_members",
    )
    async def call_members(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.member-call"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> call_members",
        )

        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isPartyExist(interact, party):
            return

        if not await self.check_permissions(
            interact, party, participants, check_host=True, cmd=cmd
        ):
            return

        mentions = [
            p["user_mention"] for p in participants if p["user_id"] != party["host_id"]
        ]
        if not mentions:
            await interact.response.send_message(
                ts.get(f"{pf}pv-call-no-members"), ephemeral=True
            )
            return

        await interact.response.send_message(
            f"{' '.join(mentions)} {ts.get(f'{pf}pv-call-msg')}"
        )

    @ui.button(
        label=ts.get(f"{pf}pv-kick-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_kick_member",
    )
    async def kick_member(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.member-kick"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> kick_member",
        )
        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isPartyExist(interact, party):
            return

        if not await self.check_permissions(
            interact, party, participants, check_host=True, cmd=cmd
        ):
            return

        members_to_kick = [p for p in participants if p["user_id"] != party["host_id"]]
        if not members_to_kick:
            await interact.response.send_message(
                ts.get(f"{pf}pv-kick-no-members"), ephemeral=True
            )
            return

        await interact.response.send_message(
            ts.get(f"{pf}pv-kick-modal-title"),
            view=KickMemberView(members_to_kick, interact.message.id),
            ephemeral=True,
        )

    @ui.button(
        label=ts.get(f"{pf}pv-del-label"),
        style=discord.ButtonStyle.danger,
        custom_id="party_delete",
    )
    async def delete_party(self, interact: discord.Interaction, button: ui.Button):
        cmd = "PartyView.btn.delete-party"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"PartyView -> delete_party",
        )

        party, participants = await PartyService.get_party_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isPartyExist(interact, party):
            return

        if not await self.check_permissions(
            interact, party, participants, check_host=True, cmd=cmd
        ):
            return

        view = ConfirmDeleteView(interact, interact.message.id, self)
        await interact.response.send_message(
            ts.get(f"{pf}pv-del-confirm"),
            view=view,
            ephemeral=True,
        )
