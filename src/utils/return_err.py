import traceback
from src.constants.color import C
import discord
from src.translator import ts


def print_test_err(msg: str = "") -> str:
    tberr: str = traceback.format_exc()
    print(C.magenta, msg, "\n", C.red, traceback.format_exc(), C.default, sep="")
    return tberr


def return_test_err() -> str:
    return traceback.format_exc()


def err_text(err_code: str) -> str:
    return ts.get("general.error-cmd") + err_code


def err_embed(err_code: str) -> discord.Embed:
    return discord.Embed(
        description=f"{ts.get('general.error-cmd')} {err_code}",
        color=0xFF0000,
    )
