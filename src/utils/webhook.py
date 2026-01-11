import discord

from src.constants.keys import LFG_WEBHOOK_NAME


async def get_webhook(target_channel, avatar) -> discord.Webhook:
    webhook_list = await target_channel.webhooks()
    webhook = discord.utils.get(webhook_list, name=LFG_WEBHOOK_NAME)
    if not webhook:
        avatar_byte = await avatar.read()
        webhook = await target_channel.create_webhook(
            name=LFG_WEBHOOK_NAME, avatar=avatar_byte
        )
    return webhook
