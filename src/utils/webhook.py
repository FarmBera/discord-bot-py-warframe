import discord

from src.constants.keys import LFG_WEBHOOK_NAME


async def get_webhook(target_channel, avatar) -> discord.Webhook:
    webhook = discord.utils.get(await target_channel.webhooks(), name=LFG_WEBHOOK_NAME)
    if not webhook:
        avatar_byte = await avatar.read()
        webhook = await target_channel.create_webhook(
            name=LFG_WEBHOOK_NAME, avatar=avatar_byte
        )
    return webhook
