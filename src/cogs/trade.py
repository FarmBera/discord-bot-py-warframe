import discord
from discord import app_commands
from discord.ext import commands

from src.translator import ts
from src.constants.keys import LFG_WEBHOOK_NAME, COOLDOWN_DEFAULT
from src.utils.data_manager import CHANNELS
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.permission import is_valid_guild, is_admin_user
from src.commands.user_warn import is_banned_user
from src.parser.marketsearch import get_slug_data, get_market_item_names
from src.services.trade_service import TradeService
from src.views.trade_view import TradeView, build_trade_embed, parseNickname

pf = "cmd.trade."


class TradeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="trade", description="cmd.trade.desc")
    @app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @app_commands.choices(
        trade_type=[
            app_commands.Choice(name=ts.get("cmd.trade.type-sell"), value=1),
            app_commands.Choice(name=ts.get("cmd.trade.type-buy"), value=2),
        ]
    )
    @app_commands.describe(
        trade_type="cmd.trade.desc-trade-type",
        item_name="cmd.trade.desc-item-name",
        item_rank="cmd.trade.desc-item-rank",
        # game_nickname="cmd.trade.desc-nickname",
        price="cmd.trade.desc-price",
        quantity="cmd.trade.desc-qty",
    )
    async def cmd_create_trade(
        self,
        interact: discord.Interaction,
        trade_type: app_commands.Choice[int],
        item_name: str,
        # game_nickname: str = "",
        item_rank: int = 0,
        price: int = 0,
        quantity: int = 1,
    ):
        if not await is_valid_guild(interact, isFollowUp=False):
            return

        if await is_banned_user(interact, isFollowUp=False):
            return

        await interact.response.defer(ephemeral=True)

        target_channel = self.bot.get_channel(CHANNELS["trade"])
        if not target_channel:
            await interact.followup.send(
                ts.get("cmd.party.not-found-ch"), ephemeral=True
            )
            return

        # search item & verify
        flag, item_slug, real_item_name, _ = get_slug_data(item_name)
        if not flag:
            await interact.followup.send(
                ts.get("cmd.market-search.no-result")
                + f"\n- `{item_name}`에 대한 마켓 검색 결과가 없습니다.\n- 아이템 이름을 확인해주세요.",
                ephemeral=True,
            )
            return

        # setup price
        try:
            estimated_price, market_data, output_msg = (
                await TradeService.estimate_price(
                    self.bot.db, trade_type.name, item_slug, item_rank, price
                )
            )
        except Exception as e:
            await interact.followup.send(f"{ts.get(f'{pf}err-api')}", ephemeral=True)
            return

        # setup automatic nickname
        final_nickname = parseNickname(interact.user.display_name)
        # game_nickname if game_nickname else parseNickname(interact.user.display_name)

        isRankItem = True if market_data[0].get("rank") is not None else False

        if not isRankItem:
            item_rank = -1

        # save to db
        try:
            trade_id = await TradeService.create_trade(
                self.bot.db,
                interact.user.id,
                final_nickname,
                trade_type.name,
                real_item_name,
                item_rank,
                quantity,
                estimated_price,
            )
        except Exception as e:
            await interact.followup.send(ts.get("cmd.err-db"), ephemeral=True)
            return

        # create embed & thread
        try:
            webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(webhooks, name=LFG_WEBHOOK_NAME)
            if not webhook:
                webhook = await target_channel.create_webhook(name=LFG_WEBHOOK_NAME)

            thread_name = f"[{trade_type.name}] {real_item_name}"
            if isRankItem:
                thread_name += f" ({ts.get(f'{pf}rank-simple').format(rank=item_rank)})"

            starter_msg = await webhook.send(
                content=f"**{trade_type.name}** 합니다.",
                username=interact.user.display_name,
                avatar_url=interact.user.display_avatar.url,
                wait=True,
            )
            thread = await starter_msg.create_thread(name=thread_name)

            embed = await build_trade_embed(
                {
                    "id": trade_id,
                    "host_id": interact.user.id,
                    "host_mention": interact.user.mention,
                    "game_nickname": final_nickname,
                    "trade_type": trade_type.name,
                    "item_name": real_item_name,
                    "item_rank": item_rank,
                    "quantity": quantity,
                    "price": estimated_price,
                },
                self.bot.db,
                isRank=isRankItem,
            )
            msg = await thread.send(embed=embed, view=TradeView())

            await TradeService.update_thread_info(
                self.bot.db, trade_id, thread.id, msg.id
            )

            await interact.followup.send(
                f"{output_msg}{ts.get(f'{pf}created-trade').format(ch=target_channel.name, mention=thread.mention)}",
                ephemeral=True,
            )

            await save_log(
                pool=interact.client.db,
                type="cmd",
                cmd=f"cmd.trade",
                interact=interact,
                msg="[info] cmd used",
                obj=f"Type:{trade_type}, Item:{item_name}, Qty:{quantity}, Price:{price}",
            )

        except Exception as e:
            await interact.followup.send(f"Error setup thread", ephemeral=True)

    # auto complete item
    @cmd_create_trade.autocomplete("item_name")
    async def trade_item_name_autocomplete(
        self, interact: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        choices = [
            app_commands.Choice(name=name, value=name)
            for name in get_market_item_names()
            if current.lower() in name.lower()
        ]
        return choices[:25]


async def setup(bot: commands.Bot):
    await bot.add_cog(TradeCog(bot))
