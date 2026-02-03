import datetime as dt

from discord.ext import tasks, commands

from config.config import LOG_TYPE, language as lang, Lang
from src.constants.color import C
from src.constants.keys import MSG_BOT, STEELPATH
from src.translator import ts
from src.utils.data_manager import get_obj_async, set_obj_async
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.times import KST


class TASKSWeeklyTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # weekly task (auto refresh)
        if lang == Lang.EN and not self.weekly_task.is_running():
            self.weekly_task.start()
            print(
                f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.crt-each')}",
                "weekly_task",
            )

    async def cog_unload(self):
        self.weekly_task.cancel()

    # weekly reset task
    @tasks.loop(time=dt.time(hour=8, minute=55, tzinfo=KST))
    async def weekly_task(self) -> None:
        await save_log(
            pool=self.bot.db,
            type=LOG_TYPE.info,
            cmd="weekly_task()",
            user=MSG_BOT,
            msg="Executing weekly_task()",
        )
        # weekday() -> int // 0: Mon, 1: Tue, ..., 6: Sun
        if dt.datetime.now(tz=KST).weekday() != 0:
            return

        # update steelPath reward index
        try:
            steel_data: dict = await get_obj_async(STEELPATH)
            rotation_list: list = steel_data["rotation"]
            curr_idx: int = steel_data["currentReward"]

            # increment & save index
            new_idx: int = (curr_idx + 1) % len(rotation_list)
            steel_data["currentReward"] = new_idx

            # save index
            await set_obj_async(steel_data, STEELPATH)

            msg = f"Steel Path reward index updated {curr_idx} -> {new_idx}"
            await save_log(
                pool=self.bot.db,
                type=LOG_TYPE.info,
                cmd="bot.WEEKLY_TASK.steelpath",
                user=MSG_BOT,
                msg=msg,
            )
        except Exception as e:
            msg = f"Failed to update Steel Path reward index: {C.red}{e}"
            print(C.red, msg, C.default)
            await save_log(
                pool=self.bot.db,
                type=LOG_TYPE.err,
                cmd="bot.WEEKLY_TASK.steelpath",
                user=MSG_BOT,
                msg=msg,
                obj=return_traceback(),
            )


async def setup(bot):
    await bot.add_cog(TASKSWeeklyTask(bot))
