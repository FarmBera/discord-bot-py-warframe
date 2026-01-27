from src.translator import ts
from src.utils.db_helper import query_reader, transaction

WARN_THRESHOLD: int = 3


class WarnService:
    @staticmethod
    async def getCount(pool, host_id) -> int:
        async with query_reader(pool) as cursor:
            await cursor.execute(
                "SELECT COUNT(*) AS cnt FROM warnings WHERE user_id=%s",
                (host_id,),
            )
            res = await cursor.fetchone()
            return res["cnt"]

    @staticmethod
    async def getCriticalCount(pool, host_id: int) -> int:
        async with query_reader(pool) as cursor:
            await cursor.execute(
                "SELECT COUNT(critical) AS count FROM warnings WHERE user_id=%s AND critical=TRUE",
                (host_id,),
            )
            res = await cursor.fetchone()
            return res["count"]

    @staticmethod
    async def generateWarnMsg(pool, host_id) -> str:
        host_warn_count = await WarnService.getCriticalCount(pool, host_id)
        return (
            ts.get(f"cmd.warning-count").format(count=host_warn_count)
            if host_warn_count >= 1
            else ""
        )

    @staticmethod
    async def insertWarn(
        pool, user_id, display_name, game_nickname, warn_type, warn_reason, given_name
    ) -> bool:
        is_executed_ban = False

        async with transaction(pool) as cursor:
            # cumulative warning count
            # count_sql = "SELECT COUNT(*) as cnt FROM warnings WHERE user_id = %s"
            count_sql = "SELECT COUNT(*) as cnt FROM warnings WHERE user_id = %s AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)"
            await cursor.execute(count_sql, (user_id,))
            result = await cursor.fetchone()
            current_warn_count = result["cnt"] if result else 0

            # decision ban
            if current_warn_count + 1 >= WARN_THRESHOLD:
                is_executed_ban = True

            await cursor.execute(
                "INSERT INTO warnings (user_id, display_name, game_nickname, category, note, given_name, critical) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    user_id,
                    display_name,
                    game_nickname,
                    warn_type,
                    warn_reason,
                    given_name,
                    is_executed_ban,
                ),
            )
            return is_executed_ban
