from src.utils.db_helper import transaction, query_reader
from src.translator import ts
from src.utils.times import parseKoreanDatetime

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
