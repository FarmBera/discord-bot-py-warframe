import discord
from translator import ts


def err_text(err_code: str) -> str:
    return ts.get("general.error-cmd") + err_code


def err_embed(err_code: str) -> discord.Embed:
    return discord.Embed(
        description=f"{ts.get('general.error-cmd')} {err_code}",
        color=0xFF0000,
    )
