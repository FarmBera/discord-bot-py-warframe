import discord
import datetime as dt

from src.translator import ts
from src.constants.times import JSON_DATE_PAT
from src.constants.keys import STARTED_TIME_FILE_LOC, DELTA_TIME_LOC
from src.utils.logging_utils import save_log
from src.utils.file_io import open_file
from src.utils.formatter import time_format


async def cmd_helper_maintenance(interact: discord.Interaction) -> None:
    time_target = dt.datetime.strptime(
        open_file(STARTED_TIME_FILE_LOC), JSON_DATE_PAT
    ) + dt.timedelta(minutes=int(open_file(DELTA_TIME_LOC)))
    time_left = time_target - dt.datetime.now()

    txt = f"""# 서버 점검 중

지금은 **서버 점검 및 패치 작업**으로 인하여 **봇을 사용할 수 없습니다.**
이용에 불편을 드려 죄송합니다.

> 종료까지 약 **{time_format(time_left)}** 남았습니다.
> 예상 완료 시간: {dt.datetime.strftime(time_target,"%Y-%m-%d %H:%M")}

패치 작업은 조기 종료 될 수 있으며, 또한 지연될 수 있음을 알립니다.
"""

    # send message
    await interact.response.send_message(
        embed=discord.Embed(description=txt, color=0xFF0000),  # VAR: color
        ephemeral=True,
    )

    await save_log(
        lock=interact.client.log_lock,
        type="cmd/maintenance",
        cmd=f"cmd.{ts.get(f'cmd.help.cmd')}",
        time=interact.created_at,
        user=interact.user,
        guild=interact.guild,
        channel=interact.channel,
        msg="[info] cmd used in maintenance mode",  # VAR
    )
