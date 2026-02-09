import discord

from config.config import LOG_TYPE
from src.translator import ts
from src.utils.db_helper import transaction, query_reader
from src.utils.delay import delay
from src.utils.logging_utils import save_log
from src.utils.times import parseKoreanDatetime
from src.utils.webhook import get_webhook

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
    async def execute_toggle(emergency_db, job_data):
        from src.views.party_view import build_party_embed_from_db

        interact = job_data["interact"]
        view = job_data["view"]
        new_embed = await build_party_embed_from_db(interact.message.id, emergency_db)
        await interact.message.edit(embed=new_embed, view=view)
        await save_log(
            pool=emergency_db,
            type=LOG_TYPE.info,
            cmd="btn.toggle.state",
            interact=interact,
            msg=f"toggled party state",
        )

    @staticmethod
    async def execute_create(emergency_db, job_data):
        from src.views.party_view import PartyView, build_party_embed

        interact = job_data["interact"]
        party_data = job_data["data"]
        webhook = await get_webhook(
            job_data["target_channel"], interact.client.user.avatar
        )
        await delay()

        thread_starter_msg = await webhook.send(
            content=party_data["title"],  # ts.get(f"{pf}created-party"),
            username=interact.user.display_name,
            avatar_url=interact.user.display_avatar.url,
            wait=True,
        )
        thread = await thread_starter_msg.create_thread(
            name=f"[{party_data['mission']}] {party_data['title']}",
            reason=f"{interact.user.display_name} user created party",
        )

        # create embed & view
        embed = await build_party_embed(party_data, emergency_db)
        msg = await thread.send(embed=embed, view=PartyView())

        # update db (thread & msg id)
        await PartyService.update_thread_info(
            emergency_db, party_data["id"], thread.id, msg.id
        )
        await save_log(
            pool=emergency_db,
            type=LOG_TYPE.info,
            cmd="party create",
            interact=interact,
            msg="Party Created",
            obj=embed.description,
        )

    @staticmethod
    async def execute_update(db, job_data):
        from src.views.party_view import build_party_embed_from_db

        interact = job_data.get("interact")
        if interact:
            modal = job_data.get("self")

            new_embed = await build_party_embed_from_db(interact.message.id, db)
            await interact.message.edit(embed=new_embed)
            await delay()

            if modal:
                ch_name = f"[{modal.mission_input.value}] {modal.title_input.value}"
                if (
                    isinstance(interact.channel, discord.Thread)
                    and interact.channel.name != ch_name
                ):
                    await interact.channel.edit(name=ch_name)
            await save_log(
                pool=db,
                type=LOG_TYPE.info,
                interact=interact,
                msg=f"Edit Article",
                obj=f"{modal.title_input.value}\n{modal.mission_input.value}\n{modal.desc_input.value}",
            )
        else:
            msg = job_data["origin_msg"]
            new_embed = await build_party_embed_from_db(msg.id, db)
            await msg.edit(embed=new_embed)
            await save_log(
                pool=db,
                type=LOG_TYPE.info,
                interact=interact,
                msg=f"Edit Article",
                obj=new_embed.description,
            )

    @staticmethod
    async def execute_delete(db, job_data):
        from src.views.party_view import build_party_embed_from_db

        msg = job_data["origin_msg"]
        interact = job_data["interact"]
        new_embed = await build_party_embed_from_db(msg.id, db, isDelete=True)
        await msg.edit(embed=new_embed, view=None)
        await delay()

        # edit thread starter msg
        try:
            webhook = await get_webhook(
                interact.channel.parent, interact.client.user.avatar
            )
            if webhook:
                await webhook.edit_message(
                    message_id=interact.channel.id, content=ts.get(f"{pf}del-deleted")
                )
        except:
            pass  # starter msg not found (maybe deleted manually)
        await delay()

        # lock thread
        if isinstance(interact.channel, discord.Thread):
            await interact.channel.edit(locked=True)

        await PartyService.delete_party(db, interact.channel.id)
        await save_log(
            pool=db,
            type=LOG_TYPE.info,
            cmd="btn.confirm.delete",
            interact=interact,
            msg=f"Party Deleted",
            obj=new_embed.description,
        )
