import traceback
from src.constants.color import C
import discord
from src.translator import ts


def print_test_err(msg: str = "") -> None:
    print(C.magenta, msg, "\n", C.red, traceback.format_exc(), C.default, sep="")


def err_text(err_code: str) -> str:
    return ts.get("general.error-cmd") + err_code


def err_embed(err_code: str) -> discord.Embed:
    return discord.Embed(
        description=f"{ts.get('general.error-cmd')} {err_code}",
        color=0xFF0000,
    )
