import discord

from src.utils.db_helper import query_reader


class ChannelService:
    @staticmethod
    async def getChannels(interact: discord.Interaction) -> dict | None:
        pool = interact.client.db
        guild_id = interact.guild_id

        async with query_reader(pool) as cursor:
            await cursor.execute(
                "SELECT guild_id,party_ch,trade_ch,complain_ch,is_allowed FROM channels WHERE guild_id = %s LIMIT 1",
                (guild_id,),
            )
            channels = await cursor.fetchone()
            if not channels:
                return None

            if not channels.get("is_allowed"):
                return None

            return channels
