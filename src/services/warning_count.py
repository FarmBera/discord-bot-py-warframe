from src.utils.db_helper import query_reader


class UserService:
    @staticmethod
    async def get_host_warning_count(pool, host_id: int) -> int:
        async with query_reader(pool) as cursor:
            await cursor.execute(
                "SELECT COUNT(critical) AS count FROM warnings WHERE user_id=%s AND critical=TRUE",
                (host_id,),
            )
            res = await cursor.fetchone()
            return res["count"]
