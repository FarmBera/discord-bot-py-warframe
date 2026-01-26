import discord

from config.config import LOG_TYPE
from src.parser.marketsearch import categorize
from src.translator import ts
from src.utils.api_request import API_MarketSearch
from src.utils.db_helper import transaction, query_reader
from src.utils.delay import delay
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.webhook import get_webhook

TRADE_CREATE_QUEUE = []
TRADE_UPDATE_QUEUE = []
TRADE_DELETE_QUEUE = []

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
        output_msg: str = ""
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

    ############################
    ############################
    @staticmethod
    async def is_queue_empty() -> bool:
        global TRADE_CREATE_QUEUE, TRADE_UPDATE_QUEUE, TRADE_DELETE_QUEUE

        return (
            len(TRADE_CREATE_QUEUE) == 0
            and len(TRADE_UPDATE_QUEUE) == 0
            and len(TRADE_DELETE_QUEUE) == 0
        )

    @staticmethod
    async def get_queue_count() -> str:
        global TRADE_CREATE_QUEUE, TRADE_UPDATE_QUEUE, TRADE_DELETE_QUEUE
        return f"""## Trade Queue
- CREATE: {len(TRADE_CREATE_QUEUE)}
- UPDATE: {len(TRADE_UPDATE_QUEUE)}
- DELETE: {len(TRADE_DELETE_QUEUE)}
"""

    @staticmethod
    async def add_create_queue(obj):
        global TRADE_CREATE_QUEUE
        TRADE_CREATE_QUEUE.append(obj)

    @staticmethod
    async def add_update_queue(obj):
        global TRADE_UPDATE_QUEUE

        # Remove existing entry with same message_id if present
        try:
            message_id = obj.get("interact").message.id
            TRADE_UPDATE_QUEUE[:] = [
                item
                for item in TRADE_UPDATE_QUEUE
                if item.get("interact").message.id != message_id
            ]
        except:
            message_id = obj.get("origin_msg").id
            TRADE_UPDATE_QUEUE[:] = [
                item
                for item in TRADE_UPDATE_QUEUE
                if item.get("origin_msg").id != message_id
            ]

        TRADE_UPDATE_QUEUE.append(obj)
        # print(len(TRADE_UPDATE_QUEUE))  # DEBUG_CODE

    @staticmethod
    async def add_delete_queue(obj):
        global TRADE_DELETE_QUEUE

        message_id = obj.get("origin_msg").id
        TRADE_DELETE_QUEUE[:] = [
            item
            for item in TRADE_DELETE_QUEUE
            if item.get("origin_msg").id != message_id
        ]
        TRADE_DELETE_QUEUE.append(obj)
        # print(len(TRADE_DELETE_QUEUE))  # DEBUG_CODE

    @staticmethod
    async def process_create_queue(emergency_db):
        from src.views.trade_view import TradeView, build_trade_embed

        global TRADE_CREATE_QUEUE
        # print("create", len(TRADE_CREATE_QUEUE))  # DEBUG_CODE
        processed_index = []

        for idx, trade in enumerate(TRADE_CREATE_QUEUE):
            interact = trade["interact"]
            data = trade["data"]
            try:
                webhook = await get_webhook(
                    trade["target_channel"], interact.client.user.avatar
                )

                await delay()

                thread_name = f"[{data['trade_type']}] {data['item_name']}"
                if data.get("isRank") and data["item_rank"] != -1:
                    thread_name += f" ({ts.get(f'{pf}rank-simple').format(rank=data['item_rank'])})"

                thread_starter_msg = await webhook.send(
                    content=f"**{data['trade_type']}** 합니다.",
                    username=interact.user.display_name,
                    avatar_url=interact.user.display_avatar.url,
                    wait=True,
                )
                thread = await thread_starter_msg.create_thread(
                    name=thread_name,
                    reason=f"{interact.user.display_name} user created trade",
                )

                # create embed & view
                embed = await build_trade_embed(
                    data, emergency_db, isRank=data.get("isRank", False)
                )
                msg = await thread.send(embed=embed, view=TradeView())

                # update db (thread & msg id)
                await TradeService.update_thread_info(
                    emergency_db, data["id"], thread.id, msg.id
                )
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.cmd,
                    cmd="trade",
                    interact=interact,
                    msg="Trade Created",
                    obj=embed.description,
                )
            except Exception as e:
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.err,
                    cmd=f"cmd.trade",
                    interact=interact,
                    msg="cmd used, but ERR",  # VAR
                    obj=f"Error setup discord thread:\nT:{data['item_name']}\nTYPE:{data['trade_type']}\n{return_traceback()}",
                )
                print(f"tradeCog > {e}")

            processed_index.append(idx)
            await delay()

        # print("create", processed_index)  # DEBUG_CODE

        for idx in reversed(processed_index):
            TRADE_CREATE_QUEUE.pop(idx)

    @staticmethod
    async def process_update_queue(emergency_db):
        from src.views.trade_view import build_trade_embed_from_db

        global TRADE_UPDATE_QUEUE
        # print("update:", len(TRADE_UPDATE_QUEUE))  # DEBUG_CODE
        processed_index = []

        for idx, queue_trade in enumerate(TRADE_UPDATE_QUEUE):
            try:
                interact = queue_trade.get("interact")
                if interact:
                    interact = queue_trade["interact"]

                    new_embed = await build_trade_embed_from_db(
                        interact.message.id, emergency_db
                    )
                    await interact.message.edit(embed=new_embed)

                    await delay()

                    await save_log(
                        pool=emergency_db,
                        type=LOG_TYPE.event,
                        cmd="btn.edit.trade",
                        interact=interact,
                        msg=f"Trade Update -> Clicked Submit",
                    )
                else:
                    msg = queue_trade["origin_msg"]
                    new_embed = await build_trade_embed_from_db(msg.id, emergency_db)
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
            TRADE_UPDATE_QUEUE.pop(idx)

    @staticmethod
    async def process_delete_queue(emergency_db):
        from src.views.trade_view import build_trade_embed_from_db

        global TRADE_DELETE_QUEUE
        # print("delete:", len(TRADE_DELETE_QUEUE))  # DEBUG_CODE
        processed_index = []

        for idx, trade in enumerate(TRADE_DELETE_QUEUE):
            try:
                msg = trade["origin_msg"]
                interact = trade["interact"]

                # build new embed & edit msg
                new_embed = await build_trade_embed_from_db(
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
                            content=ts.get(f"{pf}deleted"),
                        )
                except:
                    pass  # starter msg not found (maybe deleted manually)

                await delay()

                # lock thread
                if isinstance(interact.channel, discord.Thread):
                    await interact.channel.edit(locked=True)

                await TradeService.delete_trade(emergency_db, interact.channel.id)
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.info,
                    cmd="btn.confirm.delete",
                    interact=interact,
                    msg=f"Trade Deleted",
                    obj=new_embed.description,
                )

                await delay()
            except Exception as e:
                await save_log(
                    pool=emergency_db,
                    type=LOG_TYPE.err,
                    cmd="TradeService.process_delete_queue",
                    msg=f"Failed to process delete queue item{e}",
                    obj=return_traceback(),
                )
            processed_index.append(idx)

        # print("delete", processed_index)  # DEBUG_CODE

        for idx in reversed(processed_index):
            TRADE_DELETE_QUEUE.pop(idx)
