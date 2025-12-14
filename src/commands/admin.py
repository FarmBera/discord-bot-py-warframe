import discord

from src.translator import ts
from src.utils.db_helper import query_reader
from src.utils.return_err import print_test_err


ADMIN_EMBED: discord.Embed = discord.Embed(
    description=ts.get(f"general.admin"), color=0xFF0000
)


async def is_admin_user(interact: discord.Interaction) -> bool:
    """check interaction user is admin

    Args:
        interact (discord.Interaction): interaction object

    Returns:
        bool: is admin user (if admin user returns True else False)
    """
    async with query_reader(interact.client.db) as cursor:
        await cursor.execute(
            "SELECT user_id FROM admins WHERE user_id = %s", (interact.user.id,)
        )
        result = await cursor.fetchone()
    try:
        if result is None or interact.user.id != result.get("user_id"):
            await interact.response.send_message(embed=ADMIN_EMBED, ephemeral=True)
            return False
        return True
    except Exception:
        # print_test_err()
        return False
