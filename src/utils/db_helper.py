import aiomysql
from contextlib import asynccontextmanager


@asynccontextmanager
async def transaction(pool):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            try:
                yield cursor
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise e


# read only query
@asynccontextmanager
async def query_reader(pool):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield cursor
