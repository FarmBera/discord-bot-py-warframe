import datetime as dt

import discord
from discord.ext import tasks, commands

from config.config import LOG_TYPE, language as lang, Lang
from src.constants.color import C
from src.constants.keys import MSG_BOT, LFG_WEBHOOK_NAME
from src.services.party_service import PartyService
from src.translator import ts
from src.utils.db_helper import query_reader
from src.utils.delay import delay
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.times import KST, timeNowDT
from src.views.party_view import build_party_embed_from_db


class task_auto_party_expire(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # automatic party delete
        if lang == Lang.KO and not self.auto_party_expire.is_running():
            self.auto_party_expire.start()
            print(
                f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.crt-each')}",
                "auto_party_expire",
            )

    async def cog_unload(self):
        self.auto_party_expire.cancel()

    # party auto expire
    @tasks.loop(time=dt.time(hour=3, minute=0, tzinfo=KST))
    async def auto_party_expire(self) -> None:
        await save_log(
            pool=self.bot.db,
            type=LOG_TYPE.info,
            cmd="auto_party_expire()",
            user=MSG_BOT,
            msg=f"START Party AutoDelete",
        )
        eta: dt.datetime = timeNowDT()

        async with query_reader(self.bot.db) as cursor:
            await cursor.execute("SELECT value FROM vari WHERE name='party_exp_time'")
            party_exp_time = await cursor.fetchone()
            party_exp_time = int(party_exp_time["value"])

        # delete time
        expiration_time = timeNowDT() - dt.timedelta(days=party_exp_time)

        # fetch all message from db
        async with query_reader(self.bot.db) as cursor:
            await cursor.execute(
                "SELECT id, thread_id, message_id FROM party WHERE updated_at < %s",
                (expiration_time,),
            )
            expired_parties = await cursor.fetchall()

        deleted_count: int = 0
        for party in expired_parties:
            try:
                thread = self.bot.get_channel(party["thread_id"])

                await delay()

                await thread.edit(locked=True)  # lock thread

                await delay()

                msg = await thread.fetch_message(party["message_id"])

                await delay()

                try:  # edit thread starter (webhook) msg
                    webhook = discord.utils.get(
                        await thread.parent.webhooks(), name=LFG_WEBHOOK_NAME
                    )
                    await delay()

                    if webhook and msg:
                        await webhook.edit_message(
                            message_id=party["message_id"],
                            content=ts.get(f"cmd.party.del-deleted"),
                        )
                except discord.NotFound:
                    pass  # starter msg not found, maybe deleted manually

                await delay()

                # refresh Embed
                new_embed = await build_party_embed_from_db(
                    party["message_id"], self.bot.db, isDelete=True
                )
                await msg.edit(embed=new_embed, view=None)

                # remove from db
                await PartyService.delete_party(self.bot.db, party["thread_id"])
                deleted_count += 1
                omsg = f"Expired party {party['id']} deleted."
                await save_log(
                    pool=self.bot.db,
                    type=LOG_TYPE.info,
                    cmd="auto_party_expire()",
                    user=MSG_BOT,
                    msg=omsg,
                )
            except discord.NotFound:
                await save_log(
                    pool=self.bot.db,
                    type=LOG_TYPE.warn,
                    cmd="auto_party_expire()",
                    user=MSG_BOT,
                    msg=f"Party AutoDelete, but msg not found",
                    obj=return_traceback(),
                )
                # msg deleted manually
                await PartyService.delete_party(self.bot.db, party["thread_id"])
                deleted_count += 1
            except Exception:
                await save_log(
                    pool=self.bot.db,
                    type=LOG_TYPE.err,
                    cmd="auto_party_expire()",
                    user=MSG_BOT,
                    msg=f"Party AutoDelete, but error occurred!",
                    obj=return_traceback(),
                )
            await delay()

        await save_log(
            pool=self.bot.db,
            type=LOG_TYPE.info,
            cmd="auto_party_expire()",
            user=MSG_BOT,
            msg=f"END Party AutoDelete (deleted: {deleted_count}, eta: {timeNowDT()-eta})",
        )


async def setup(bot):
    await bot.add_cog(task_auto_party_expire(bot))
