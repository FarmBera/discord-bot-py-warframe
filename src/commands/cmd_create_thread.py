import discord
import sqlite3

from src.translator import ts
from src.constants.keys import CHANNEL_FILE_LOC
from src.utils.file_io import yaml_open
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

        except Exception as e:
            await interact.response.send_message(
                f"{ts.get(f'{pf_edit}err')}: {e}", ephemeral=True
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
            if not new_max_size_str.isdigit() or int(new_max_size_str) <= 0:
                await interact.response.send_message(
                    ts.get(f"{pf_size}err-low"), ephemeral=True
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

        except Exception as e:
            await interact.response.send_message(
                f"{ts.get(f'{pf_edit}err')}: {e}", ephemeral=True
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

            # 1. delete party info from DB
            cursor.execute(
                "DELETE FROM party WHERE thread_id = ?", (interact.channel.id,)
            )
            db.commit()

            # 2. delete the thread
            await interact.channel.delete()

        except discord.Forbidden:
            await interact.response.send_message(
                ts.get(f"{pf_btn}err-del"), ephemeral=True
            )
        except Exception as e:
            await interact.response.send_message(f"{pf_size}err: {e}", ephemeral=True)

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
        cursor = self.db.cursor()

        try:
            if self.action == "join":
                cursor.execute(
                    "INSERT INTO participants (party_id, user_id, user_mention) VALUES (?, ?, ?)",
                    (self.party_id, self.user_id, self.user_mention),
                )
                self.db.commit()
                # reply confirm chat
                await interact.response.edit_message(
                    content=ts.get(f"{pf_pv}joined"), view=None
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


class PartyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # make the button persistent

    async def fetch_party_data(self, interact: discord.Interaction):
        """fetch party and participant data from DB"""
        db = interact.client.db
        db.row_factory = sqlite3.Row

        # search party using message id
        party_data = db.execute(
            "SELECT * FROM party WHERE message_id = ?", (interact.message.id,)
        ).fetchone()

        if not party_data:
            await interact.response.send_message(
                ts.get(f"{pf_pv}not-found"), ephemeral=True
            )
            return None, None

        # search participants
        participants_list = db.execute(
            "SELECT * FROM participants WHERE party_id = ?", (party_data["id"],)
        ).fetchall()

        return dict(party_data), [dict(p) for p in participants_list]

    @discord.ui.button(
        label=ts.get(f"{pf_pv}join-btn"),
        style=discord.ButtonStyle.success,
        custom_id="party_join",
    )
    async def join_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
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

        if is_participant:  # leave party
            action = "leave"
            prompt_msg = ts.get(f"{pf_pv}confirm-exit")
        else:  # join party
            # check party is full
            if len(participants_list) >= party_data["max_users"]:
                await interact.response.send_message(
                    ts.get(f"{pf_pv}full"), ephemeral=True
                )
                return
            action = "join"
            prompt_msg = ts.get(f"{pf_pv}confirm-join")

        # send confirm ui
        view = ConfirmJoinLeaveView(
            action=action,
            db=db,
            party_id=party_id,
            user_id=interact.user.id,
            user_mention=interact.user.mention,
            original_message=interact.message,  # deliver main embed msg
        )

        await interact.response.send_message(prompt_msg, view=view, ephemeral=True)

        timed_out = await view.wait()
        if timed_out and view.value is None:
            try:
                # modify temporary confirm windows
                await interact.edit_original_response(
                    content=ts.get(f"{pf}pv-del-cancel"), view=None
                )
            except discord.errors.NotFound:
                pass

        # refresh embed
        new_embed = await build_party_embed_from_db(interact.message.id, db)
        await interact.message.edit(embed=new_embed)

    @discord.ui.button(
        label=ts.get(f"{pf_pv}mod-label"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_size",
    )
    async def edit_size(self, interact: discord.Interaction, button: discord.ui.Button):
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

    @discord.ui.button(
        label=ts.get(f"{pf_pv}mod-article"),
        style=discord.ButtonStyle.secondary,
        custom_id="party_edit_content",
    )
    async def edit_content(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
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

    @discord.ui.button(
        label=ts.get(f"{pf_pv}done"),
        style=discord.ButtonStyle.primary,
        custom_id="party_toggle_close",
    )
    async def toggle_close_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
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

        # refresh embed
        new_embed = await build_party_embed_from_db(interact.message.id, db)

        # change button label & style
        join_btn = discord.utils.get(self.children, custom_id="party_join")
        edit_size_btn = discord.utils.get(self.children, custom_id="party_edit_size")
        if new_status == ts.get(f"{pf_pv}done"):
            button.label = ts.get(f"{pf_pv}ing")
            button.style = discord.ButtonStyle.success
            if join_btn:
                join_btn.disabled = True
            if edit_size_btn:
                edit_size_btn.disabled = True

        else:
            button.label = ts.get(f"{pf_pv}done")
            button.style = discord.ButtonStyle.primary
            if join_btn:
                join_btn.disabled = False
            if edit_size_btn:
                edit_size_btn.disabled = False

        await interact.response.edit_message(embed=new_embed, view=self)

    @discord.ui.button(
        label=ts.get(f"{pf}pv-del-label"),
        style=discord.ButtonStyle.danger,
        custom_id="party_delete",
    )
    async def delete_party(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
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
            except discord.errors.NotFound:
                pass


pf_pb: str = f"{pf}pb-"


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
        participants_str = ts.get(f"{pf_pb}no-player")

    description_field = ""
    if data.get("description"):
        description_field = f"{data['description']}"

    description = f"""
### {data['title']} {status_text}

- **{ts.get(f'{pf_pb}host')}:** {data['host_mention']}
- **{ts.get(f'{pf_pb}player-count')}:** {len(data['participants'])} / {data['max_users']}
- **{ts.get(f'{pf_pb}player-joined')}:** {participants_str}
- **{ts.get(f'{pf_pb}mission')}:** {data['mission']}
{description_field}

{ts.get(f'{pf_pb}desc')}
```
/w {data['game_nickname']}
```
"""
    embed = discord.Embed(description=description.strip(), color=color)
    embed.set_footer(text=f"{ts.get(f'{pf_pb}pid')}: {data['id']}")
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
    description: str,
    number_of_user: int = 4,
) -> None:
    db = db_conn
    db.row_factory = sqlite3.Row

    game_nickname = parseNickname(interact.user.display_name)
    ch_file = yaml_open(CHANNEL_FILE_LOC)["party"]
    target_channel = interact.client.get_channel(ch_file)

    await interact.response.defer(ephemeral=True)

    if number_of_user <= 0:
        await interact.followup.send(
            ts.get(f"{pf}pt-low"),
            ephemeral=True,
        )
        number_of_user = 4

    elif number_of_user > 4:
        await interact.followup.send(
            ts.get(f"{pf}pt-high"),
            ephemeral=True,
        )
        number_of_user = 4

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
                "INSERT INTO participants (party_id, user_id, user_mention) VALUES (?, ?, ?)",
                (PARTY_ID, interact.user.id, interact.user.mention),
            )
            db.commit()  # fisrt commit (party creation)

            thread_name = f"[{mission_type}] {title}"  # therad title
            thread = await target_channel.create_thread(
                name=thread_name,
                type=discord.ChannelType.public_thread,
                reason=f"Thread started by a {interact.user.display_name}",
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

        except discord.Forbidden:
            await interact.followup.send(
                ts.get(f"{pf}no-thread-permission"),
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interact.followup.send(
                f"{ts.get(f'{pf}err-creation')}: {e}",
                ephemeral=True,
            )
        except Exception as e:
            await interact.followup.send(
                f"{ts.get(f'{pf}err-unknown')}: {e}", ephemeral=True
            )
    else:
        await interact.followup.send(ts.get(f"{pf}not-found-ch"), ephemeral=True)

    # save_log(
    #     type="cmd",
    #     cmd=f"cmd.",
    #     time=interact.created_at,
    #     user=interact.user,
    #     guild=interact.guild,
    #     channel=interact.channel,
    #     msg="[info] cmd used",  # VAR
    #     obj=None,
    # )
