import discord
import asyncio
import datetime as dt
from typing import Optional

from src.utils.times import KST
from src.utils.db_helper import transaction
from src.utils.return_err import return_traceback
from src.constants.color import C

TIMEOUT_SECONDS: float = 30.0
MSG_TRUNCATE_LEN: int = 500

background_log_tasks = set()


async def save_log(
    pool,  # aiomysql.Pool
    type: str = "info",
    cmd: str = None,
    time: Optional[dt.datetime] = None,
    user: str = None,
    guild: str = None,
    channel: str = None,
    msg: str = None,
    obj: str = None,
    interact: discord.Interaction = None,
):
    """
    [Non-blocking Wrapper]
    create background task (fire-and-forget)
    """
    task = asyncio.create_task(
        _process_log_background(
            pool, type, cmd, time, user, guild, channel, msg, obj, interact
        )
    )
    background_log_tasks.add(task)
    task.add_done_callback(background_log_tasks.discard)
    return


async def _process_log_background(
    pool,
    type: str,
    cmd: str,
    time: Optional[dt.datetime],
    user: str,
    guild: str,
    channel: str,
    msg: str,
    obj: str,
    interact: discord.Interaction,
):
    try:
        await asyncio.wait_for(
            _execute_db_logging(
                pool, type, cmd, time, user, guild, channel, msg, obj, interact
            ),
            timeout=TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        print(f"{C.red}[warn] Log Dropped (DB Timeout): {type}/{cmd}{C.default}")
    except Exception as e:
        print(f"{C.red}[err] Async Log Task Error: {e}{C.default}")


async def _execute_db_logging(
    pool,
    type: str,
    cmd: str,
    time: Optional[dt.datetime],
    user: str,
    guild: str,
    channel: str,
    msg: str,
    obj: str,
    interact: discord.Interaction,
):
    # data pre-processing
    user_id = None
    display_name = user
    global_name = None
    user_name = None

    guild_id = None
    guild_name = guild

    channel_id = None
    channel_name = channel

    if interact:
        if interact.user:
            user_id = interact.user.id
            display_name = interact.user.display_name
            global_name = interact.user.global_name
            user_name = interact.user.name

        if interact.guild:
            guild_id = interact.guild.id
            guild_name = interact.guild.name

        if interact.channel:
            channel_id = interact.channel.id
            channel_name = interact.channel.name

        if time is None:
            time = interact.created_at

            # correct timezone
            if time.tzinfo is None:
                time = time.replace(tzinfo=dt.timezone.utc)
            time = time.astimezone(KST)

    if time is None:
        time = dt.datetime.now(KST)

    full_msg = msg if msg else ""
    summary_msg = full_msg[:MSG_TRUNCATE_LEN] if full_msg else None

    detail_content = None
    has_detail = False

    if obj:
        detail_content = str(obj)
        has_detail = True

    # if len(full_msg) > MSG_TRUNCATE_LEN:
    #     if detail_content:
    #         detail_content = f"Original Msg: {full_msg}\n\nInfo: {detail_content}"
    #     else:
    #         detail_content = full_msg
    #     has_detail = True

    # run db query
    async with transaction(pool) as cur:
        # insert main log
        sql_logs = "INSERT INTO logs ( `type`, display_name, global_name, user_name, user_id, guild_name, guild_id, channel_name, channel_id, created_at, cmd, msg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        await cur.execute(
            sql_logs,
            (
                type,
                display_name,
                global_name,
                user_name,
                user_id,
                guild_name,
                guild_id,
                channel_name,
                channel_id,
                time,
                cmd,
                summary_msg,
            ),
        )

        # get inserted id
        log_id = cur.lastrowid

        # insert detailed object
        if has_detail and log_id:
            sql_detail = "INSERT INTO log_detail (log_id, content) VALUES (%s, %s)"
            await cur.execute(sql_detail, (log_id, detail_content))
