from src.utils.db_helper import transaction, query_reader
from src.utils.api_request import API_MarketSearch
from src.parser.marketsearch import categorize
from src.translator import ts

pf = "cmd.trade."


class TradeService:
    @staticmethod
    async def get_trade_by_message_id(pool, message_id: int):
        async with query_reader(pool) as cursor:
            await cursor.execute(
                "SELECT * FROM trade WHERE message_id = %s", (message_id,)
            )
            return await cursor.fetchone()

    @staticmethod
    async def get_trade_by_id(pool, trade_id: int):
        async with query_reader(pool) as cursor:
            await cursor.execute("SELECT * FROM trade WHERE id = %s", (trade_id,))
            return await cursor.fetchone()

    @staticmethod
    async def create_trade(
        pool, host_id, game_nickname, trade_type, item_name, item_rank, quantity, price
    ):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "INSERT INTO trade (host_id, game_nickname, trade_type, item_name, item_rank, quantity, price) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    host_id,
                    game_nickname,
                    trade_type,
                    item_name,
                    item_rank,
                    quantity,
                    price,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    async def update_thread_info(pool, trade_id, thread_id, message_id):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE trade SET thread_id = %s, message_id = %s WHERE id = %s",
                (thread_id, message_id, trade_id),
            )

    @staticmethod
    async def update_nickname(pool, message_id, new_nickname):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE trade SET game_nickname = %s WHERE message_id = %s",
                (new_nickname, message_id),
            )

    @staticmethod
    async def update_quantity(pool, message_id, new_quantity):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE trade SET quantity = %s WHERE message_id = %s",
                (new_quantity, message_id),
            )

    @staticmethod
    async def update_price(pool, message_id, new_price):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE trade SET price = %s WHERE message_id = %s",
                (new_price, message_id),
            )

    @staticmethod
    async def update_item_rank(pool, message_id, new_rank):
        async with transaction(pool) as cursor:
            await cursor.execute(
                "UPDATE trade SET item_rank = %s WHERE message_id = %s",
                (new_rank, message_id),
            )

    @staticmethod
    async def delete_trade(pool, thread_id):
        async with transaction(pool) as cursor:
            await cursor.execute("DELETE FROM trade WHERE thread_id = %s", (thread_id,))

    @staticmethod
    async def estimate_price(
        pool, trade_type, item_slug, item_rank, input_price
    ) -> tuple[int, list, str]:
        output_msg = ""
        # get market price
        market_api_result = await API_MarketSearch(pool, item_slug)
        market = categorize(market_api_result.json(), rank=item_rank)

        if market_api_result.status_code == 404:
            output_msg += f"{ts.get(f'{pf}err-no-market')}\n\n"
            return (input_price if input_price else 0), market, output_msg
        elif market_api_result.status_code != 200:
            raise ValueError("Market API resp-code is not 200")

        if input_price:
            return input_price, market, output_msg

        # automatic price decision
        price_list = []
        length = len(market)
        for i in range(min(length, 6)):
            price_list.append(market[i]["platinum"])

        estimated_price = sum(price_list) // len(price_list) if price_list else 0
        output_msg += f"{ts.get(f'{pf}auto-price').format(price=estimated_price)}\n\n"

        return estimated_price, market, output_msg
