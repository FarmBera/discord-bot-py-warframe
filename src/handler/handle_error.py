from config.config import LOG_TYPE
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.times import timeNowDT


async def _save_error_log(db, msg: str, cmd: str) -> None:
    await save_log(
        pool=db,
        type=LOG_TYPE.err,
        cmd=cmd,
        user=MSG_BOT,
        msg=msg,
        obj=return_traceback(),
    )


async def handleGeneralError(db, msg: str, cmd: str = "") -> None:
    print(timeNowDT(), C.red, msg, C.default)
    await _save_error_log(db, msg, cmd)


async def handleParseError(db, msg, key) -> None:
    print(timeNowDT(), C.red, key, msg, C.default, sep="")
    await _save_error_log(db, msg, "check_new_content()")
