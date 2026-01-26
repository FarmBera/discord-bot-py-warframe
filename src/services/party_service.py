import discord

from config.config import LOG_TYPE
from src.translator import ts
from src.utils.db_helper import transaction, query_reader
from src.utils.delay import delay
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.times import parseKoreanDatetime
from src.utils.webhook import get_webhook

PARTY_CREATE_QUEUE = []
PARTY_UPDATE_QUEUE = []
PARTY_DELETE_QUEUE = []

pf = "cmd.party."


class PartyService:
    @staticmethod
    async def get_party_by_message_id(pool, message_id: int):
        async with query_reader(pool) as cursor:
            await cursor.execute(
                "SELECT * FROM party WHERE message_id = %s", (message_id,)
            )
            party = await cursor.fetchone()
            if not party:
                return None, None

            # searc participants
            await cursor.execute(
                "SELECT * FROM participants WHERE party_id = %s", (party["id"],)
            )
            participants = await cursor.fetchall()
            return party, participants

    @staticmethod
    async def create_party(
        pool,
        host_id,
        host_name,
        host_mention,
        title,
        game_name,
        departure_str,
        max_users,
        desc,
    ):
        departure_dt = parseKoreanDatetime(departure_str) if departure_str else None

        async with transaction(pool) as cursor:
            # 1. insert party info
            await cursor.execute(
                "INSERT INTO party (host_id, title, game_name, departure, max_users, status, description) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    host_id,
                    title,
                    game_name,
                    departure_dt,
                    max_users,
                    ts.get(f"{pf}pv-ing"),
                    desc,
                ),
            )
            party_id = cursor.lastrowid

            # register host for first attend
            await cursor.execute(
                "INSERT INTO participants (party_id, user_id, user_mention, display_name) VALUES (%s, %s, %s, %s)",
                (party_id, host_id, host_mention, host_name),
            )
            return party_id

    @staticmethod
    async def update_thread_info(pool, party_id, thread_id, message_id):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE party SET thread_id = %s, message_id = %s WHERE id = %s",
                (thread_id, message_id, party_id),
            )

    @staticmethod
    async def update_party_content(pool, message_id, title, mission, desc):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE party SET title = %s, game_name = %s, description = %s WHERE message_id = %s",
                (title, mission, desc, message_id),
            )

    @staticmethod
    async def update_party_size(pool, message_id, new_size: int):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE party SET max_users = %s WHERE message_id = %s",
                (new_size, message_id),
            )

    @staticmethod
    async def update_party_departure(pool, message_id, date_str):
        conv_date = parseKoreanDatetime(date_str)
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE party SET departure = %s WHERE message_id = %s",
                (conv_date, message_id),
            )
        return conv_date

    @staticmethod
    async def toggle_status(pool, party_id, current_status):
        new_status = (
            ts.get(f"{pf}pv-done")
            if current_status == ts.get(f"{pf}pv-ing")
            else ts.get(f"{pf}pv-ing")
        )
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE party SET status = %s WHERE id = %s",
                (new_status, party_id),
            )
        return new_status

    @staticmethod
    async def delete_party(pool, thread_id):
        async with transaction(pool) as cursor:
            await cursor.execute("DELETE FROM party WHERE thread_id = %s", (thread_id,))

    @staticmethod
    async def join_participant(pool, party_id, user_id, user_mention, display_name):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "INSERT INTO participants (party_id, user_id, user_mention, display_name) VALUES (%s, %s, %s, %s)",
                (party_id, user_id, user_mention, display_name),
            )

    @staticmethod
    async def leave_participant(pool, party_id, user_id):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "DELETE FROM participants WHERE party_id = %s AND user_id = %s",
                (party_id, user_id),
            )

    ############################
    ############################
    @staticmethod
    async def is_queue_empty() -> bool:
        global PARTY_CREATE_QUEUE, PARTY_UPDATE_QUEUE, PARTY_DELETE_QUEUE

        return (
            len(PARTY_CREATE_QUEUE) == 0
            and len(PARTY_UPDATE_QUEUE) == 0
            and len(PARTY_DELETE_QUEUE) == 0
        )

    @staticmethod
    async def get_queue_count() -> str:
        global PARTY_CREATE_QUEUE, PARTY_UPDATE_QUEUE, PARTY_DELETE_QUEUE
        return f"""## Party Queue
- CREATE: {len(PARTY_CREATE_QUEUE)}
- UPDATE: {len(PARTY_UPDATE_QUEUE)}
- DELETE: {len(PARTY_DELETE_QUEUE)}
"""

    @staticmethod
    async def add_create_queue(obj):
        global PARTY_CREATE_QUEUE
        PARTY_CREATE_QUEUE.append(obj)

    @staticmethod
    async def add_update_queue(obj):
        global PARTY_UPDATE_QUEUE

        # Remove existing entry with same message_id if present
        try:
            message_id = obj.get("interact").message.id
            PARTY_UPDATE_QUEUE[:] = [
                item
                for item in PARTY_UPDATE_QUEUE
                if item.get("interact").message.id != message_id
            ]
        except:
            message_id = obj.get("origin_msg").id
            PARTY_UPDATE_QUEUE[:] = [
                item
                for item in PARTY_UPDATE_QUEUE
                if item.get("origin_msg").id != message_id
            ]

        PARTY_UPDATE_QUEUE.append(obj)
        # print(len(PARTY_UPDATE_QUEUE))  # DEBUG_CODE

    @staticmethod
    async def add_delete_queue(obj):
        global PARTY_DELETE_QUEUE

        message_id = obj.get("origin_msg").id
        PARTY_DELETE_QUEUE[:] = [
            item
            for item in PARTY_DELETE_QUEUE
            if item.get("origin_msg").id != message_id
        ]
        PARTY_DELETE_QUEUE.append(obj)
        # print(len(PARTY_DELETE_QUEUE))  # DEBUG_CODE

    @staticmethod
    async def process_create_queue(emergency_db):
        from src.views.party_view import PartyView, build_party_embed

        global PARTY_CREATE_QUEUE
        # print("create", len(PARTY_CREATE_QUEUE))  # DEBUG_CODEv
        processed_index = []

        for idx, party in enumerate(PARTY_CREATE_QUEUE):
            interact = party["interact"]
            data = party["data"]
            try:
                webhook = await get_webhook(
                    party["target_channel"], interact.client.user.avatar
                )

                await delay()

                thread_starter_msg = await webhook.send(
                    content=data["title"],  # ts.get(f"{pf}created-party"),
                    username=interact.user.display_name,
                    avatar_url=interact.user.display_avatar.url,
                    wait=True,
                )
                thread = await thread_starter_msg.create_thread(
                    name=f"[{data['mission']}] {data['title']}",
                    reason=f"{interact.user.display_name} user created party",
                )

                # create embed & view
                embed = await build_party_embed(data, emergency_db)
                msg = await thread.send(embed=embed, view=PartyView())

                # update db (thread & msg id)
                await PartyService.update_thread_info(
                    emergency_db, data["id"], thread.id, msg.id
                )
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.cmd,
                    cmd="party",
                    interact=interact,
                    msg="Party Created",
                    obj=embed.description,
                )
            except Exception as e:
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.err,
                    cmd=f"cmd.party",
                    interact=interact,
                    msg="cmd used, but ERR",  # VAR
                    obj=f"Error setup discord thread:\nT:{data['title']}\nTYPE:{data['mission']}\nDEPT:{data['departure']}\nDESC:{data['description']}\n{data['max_users']}\n{return_traceback()}",
                )
                print(f"partyCog > {e}")

            processed_index.append(idx)
            await delay()

        # print("create", processed_index)  # DEBUG_CODE

        for idx in reversed(processed_index):
            PARTY_CREATE_QUEUE.pop(idx)

    @staticmethod
    async def process_update_queue(emergency_db):
        from src.views.party_view import build_party_embed_from_db

        global PARTY_UPDATE_QUEUE
        # print("update:", len(PARTY_UPDATE_QUEUE))  # DEBUG_CODE
        processed_index = []

        for idx, queue_party in enumerate(PARTY_UPDATE_QUEUE):
            try:
                interact = queue_party.get("interact")
                if interact:
                    interact = queue_party["interact"]
                    selfp = queue_party.get("self")

                    new_embed = await build_party_embed_from_db(
                        interact.message.id, emergency_db
                    )
                    await interact.message.edit(embed=new_embed)

                    await delay()

                    if selfp:
                        ch_name = (
                            f"[{selfp.mission_input.value}] {selfp.title_input.value}"
                        )
                        if (
                            isinstance(interact.channel, discord.Thread)
                            and interact.channel.name != ch_name
                        ):
                            await interact.channel.edit(name=ch_name)
                            await delay()
                    await save_log(
                        pool=emergency_db,
                        type=LOG_TYPE.event,
                        cmd="btn.edit.article",
                        interact=interact,
                        msg=f"PartyEditModal -> Clicked Submit",
                        obj=f"{selfp.title_input.value}\n{selfp.mission_input.value}\n{selfp.desc_input.value}",
                    )
                else:
                    msg = queue_party["origin_msg"]
                    new_embed = await build_party_embed_from_db(msg.id, emergency_db)
                    await msg.edit(embed=new_embed)
                    await delay()
            except Exception as e:
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.err,
                    cmd="process.update_queue",
                    msg=f"Failed to process update queue item",
                    obj=f"{e}\n{return_traceback()}",
                )
            processed_index.append(idx)

        # print("update", processed_index)  # DEBUG_CODE

        for idx in reversed(processed_index):
            PARTY_UPDATE_QUEUE.pop(idx)

    @staticmethod
    async def process_delete_queue(emergency_db):
        from src.views.party_view import build_party_embed_from_db

        global PARTY_DELETE_QUEUE
        # print("delete:", len(PARTY_DELETE_QUEUE))  # DEBUG_CODE
        processed_index = []

        for idx, party in enumerate(PARTY_DELETE_QUEUE):
            try:
                msg = party["origin_msg"]
                interact = party["interact"]

                # build new embed & edit msg
                new_embed = await build_party_embed_from_db(
                    msg.id, emergency_db, isDelete=True
                )
                await msg.edit(embed=new_embed, view=None)

                await delay()

                # edit thread starter msg
                try:
                    webhook = await get_webhook(
                        interact.channel.parent, interact.client.user.avatar
                    )
                    if webhook:
                        await webhook.edit_message(
                            message_id=interact.channel.id,
                            content=ts.get(f"{pf}del-deleted"),
                        )
                except:
                    pass  # starter msg not found (maybe deleted manually)

                await delay()

                # lock thread
                if isinstance(interact.channel, discord.Thread):
                    await interact.channel.edit(locked=True)

                await PartyService.delete_party(emergency_db, interact.channel.id)
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.info,
                    cmd="btn.confirm.delete",
                    interact=interact,
                    msg=f"Party Deleted",
                    obj=new_embed.description,
                )

                await delay()
            except Exception as e:
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.err,
                    cmd="PartyService.process_delete_queue",
                    msg=f"Failed to process update queue item{e}",
                    obj=return_traceback(),
                )
            processed_index.append(idx)

        # print("delete", processed_index)  # DEBUG_CODE

        for idx in reversed(processed_index):
            PARTY_DELETE_QUEUE.pop(idx)
