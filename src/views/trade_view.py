import discord
from discord import ui
from discord.ext import commands

from src.translator import ts
from src.utils.return_err import return_traceback
from src.utils.logging_utils import save_log
from config.config import LOG_TYPE
from config.TOKEN import base_url_market_image
from src.constants.keys import (
    LFG_WEBHOOK_NAME,
    COOLDOWN_BTN_ACTION,
    COOLDOWN_BTN_MANAGE,
    COOLDOWN_BTN_CALL,
)
from src.utils.permission import is_admin_user
from src.parser.marketsearch import get_slug_data, create_market_url
from src.services.trade_service import TradeService
from src.services.warn_service import WarnService
from src.utils.webhook import get_webhook

pf = "cmd.trade."


# ----------------- Helpers -----------------
def parseNickname(nickname: str) -> str:
    return nickname.split("]")[-1].strip()


def revTradeType(trade_type: str) -> str:
    return (
        ts.get("cmd.trade.type-buy")
        if trade_type == ts.get(f"cmd.trade.type-sell")
        else ts.get(f"cmd.trade.type-sell")
    )


async def isTradeExists(interact: discord.Interaction, trade, cmd: str = "") -> bool:
    if trade:
        return True

    await interact.response.send_message(
        embed=discord.Embed(
            description=ts.get(f"{pf}err-not-found"), color=discord.Color.red()
        ),
        ephemeral=True,
    )
    await save_log(
        pool=interact.client.db,
        type=LOG_TYPE.err,
        cmd="btn",
        msg="trade not found from db",
        interact=interact,
    )
    return False


async def build_trade_embed(
    data: dict, db_pool, isDelete: bool = False, isRank: bool = False
) -> discord.Embed:
    flag, _, __, img_url = get_slug_data(data["item_name"])
    description: str = ""

    host_warn_count = await WarnService.getCriticalCount(db_pool, data["host_id"])
    if host_warn_count >= 1:
        description += ts.get(f"cmd.warning-count").format(count=host_warn_count)

    description += f"### [{data['trade_type']}] {data['item_name']}"

    if isRank and data.get("item_rank") != -1:
        description += f" ({ts.get(f'{pf}rank-simple').format(rank=data['item_rank'])})"

    color = 0x00FF00 if not isDelete else 0xFF0000

    description += f"""
- **{ts.get(f'{pf}creator')}:** {data['host_mention']}
- **{ts.get(f'{pf}item-name')}:** {create_market_url(data['item_name'])}
- **{ts.get(f'{pf}price-per')}:** `{data['price']:,} {ts.get(f'{pf}platinum')}` (총합 {data['price'] * data['quantity']:,} 플레)
- **{ts.get(f'{pf}quantity')}:** `{data['quantity']:,}` 개
"""
    rank_val = int(data.get("item_rank", -1))
    rank_str = f" ({rank_val} {ts.get(f'{pf}rank-label')})" if rank_val > -1 else ""

    if not isDelete:
        description += f"""
> 귓속말 명령어 복사 (드래그 또는 우측 복사버튼 이용)
```
/w {data['game_nickname']} 안녕하세요. 클랜디코 거래글 보고 귓말 드렸습니다. '{data['item_name']}{rank_str}' (을)를 {data['price']} 플레로 {revTradeType(data["trade_type"])}하고 싶어요.
```
"""
    if isDelete:
        description = f"~~{description.strip().replace('~~', '')}~~"
    else:
        description = description.strip()

    embed = discord.Embed(description=description, color=color)
    embed.set_footer(text=f"ID: {data['id']}")
    if flag and img_url:
        embed.set_thumbnail(url=f"{base_url_market_image}{img_url}")
    return embed


async def build_trade_embed_from_db(
    message_id: int, db_pool, isDelete: bool = False
) -> discord.Embed:
    trade_data = await TradeService.get_trade_by_message_id(db_pool, message_id)
    if not trade_data:
        return discord.Embed(
            title=ts.get(f"{pf}err"),
            description=ts.get(f"{pf}err-not-found"),
            color=discord.Color.dark_red(),
        )

    return await build_trade_embed(
        {
            "id": trade_data["id"],
            "host_id": trade_data["host_id"],
            "host_mention": f"<@{trade_data['host_id']}>",
            "game_nickname": trade_data["game_nickname"],
            "trade_type": trade_data["trade_type"],
            "item_name": trade_data["item_name"],
            "item_rank": trade_data["item_rank"],
            "quantity": trade_data["quantity"],
            "price": trade_data["price"],
        },
        db_pool,
        isDelete=isDelete,
        isRank=(trade_data["item_rank"] > -1),
        # isRank=(trade_data["item_rank"] is not None),
    )


# ----------------- Modals -----------------
class EditNicknameModal(ui.Modal, title=ts.get(f"{pf}edit-nick-title")):
    def __init__(self, curr_nickname: str, db_pool):
        super().__init__(timeout=None)
        self.db_pool = db_pool
        self.input_nickname = ui.TextInput(
            label=ts.get(f"{pf}edit-nick-label"), default=curr_nickname, required=True
        )
        self.add_item(self.input_nickname)

    async def on_submit(self, interact: discord.Interaction):
        try:
            await TradeService.update_nickname(
                self.db_pool, interact.message.id, self.input_nickname.value
            )
            new_embed = await build_trade_embed_from_db(
                interact.message.id, self.db_pool
            )
            await interact.response.edit_message(embed=new_embed)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="btn.edit.nickname",
                interact=interact,
                msg="EditNicknameModal -> Submit",
            )
        except Exception:
            await interact.response.send_message(
                ts.get(f"{pf}err-edit"), ephemeral=True
            )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.e_event,
                cmd="btn.edit.nickname",
                interact=interact,
                msg=f"EditNicknameModal -> Submit, but ERR",
                obj=f"T:{self.input_nickname.value}\n{return_traceback()}",
            )


class EditQuantityModal(ui.Modal, title=ts.get(f"{pf}edit-qty-title")):
    def __init__(self, current_quantity: int, db_pool):
        super().__init__(timeout=None)
        self.db_pool = db_pool
        self.quantity_input = ui.TextInput(
            label=ts.get(f"{pf}edit-qty-label"),
            default=str(current_quantity),
            required=True,
        )
        self.add_item(self.quantity_input)

    async def on_submit(self, interact: discord.Interaction):
        if not self.quantity_input.value.isdigit():
            await interact.response.send_message(
                ts.get(f"{pf}err-invalid-value"), ephemeral=True
            )
            return

        if int(self.quantity_input.value) < 1:
            await interact.response.send_message(
                ts.get(f"{pf}err-size-low"), ephemeral=True
            )
            return

        try:
            await TradeService.update_quantity(
                self.db_pool, interact.message.id, self.quantity_input.value
            )
            new_embed = await build_trade_embed_from_db(
                interact.message.id, self.db_pool
            )
            await interact.response.edit_message(embed=new_embed)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="btn.edit.quantity",
                interact=interact,
                msg=f"EditQuantityModal -> Submit '{self.quantity_input.value}'",
            )
        except Exception:
            await interact.response.send_message(
                ts.get(f"{pf}err-edit"), ephemeral=True
            )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.e_event,
                cmd="btn.edit.quantity",
                interact=interact,
                msg=f"EditQuantityModal -> Submit, but ERR",
                obj=f"{self.quantity_input.value}\n{return_traceback()}",
            )


class EditPriceModal(ui.Modal, title=ts.get(f"{pf}edit-price-title")):
    def __init__(self, current_price: int, db_pool):
        super().__init__(timeout=None)
        self.db_pool = db_pool
        self.price_input = ui.TextInput(
            label=ts.get(f"{pf}edit-price-label"),
            default=str(current_price),
            required=True,
        )
        self.add_item(self.price_input)

    async def on_submit(self, interact: discord.Interaction):
        if not self.price_input.value.isdigit() or int(self.price_input.value) < 0:
            await interact.response.send_message(
                ts.get(f"{pf}err-invalid-value"), ephemeral=True
            )
            return

        try:
            await TradeService.update_price(
                self.db_pool, interact.message.id, int(self.price_input.value)
            )
            new_embed = await build_trade_embed_from_db(
                interact.message.id, self.db_pool
            )
            await interact.response.edit_message(embed=new_embed)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="btn.edit.price",
                interact=interact,
                msg=f"EditPriceModal -> Submit",
                obj=self.price_input.value,
            )
        except Exception:
            await interact.response.send_message(
                ts.get(f"{pf}err-edit"), ephemeral=True
            )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.e_event,
                cmd="btn.edit.price",
                interact=interact,
                msg=f"EditPriceModal -> Submit, but ERR",
                obj=f"{self.price_input.value}\n{return_traceback()}",
            )


class EditRankModal(ui.Modal, title=ts.get(f"{pf}edit-rank-title")):
    def __init__(self, current_rank: int, db_pool):
        super().__init__(timeout=None)
        self.db_pool = db_pool
        default_val = str(current_rank) if current_rank is not None else "0"

        self.rank_input = ui.TextInput(
            label=ts.get(f"{pf}edit-rank-label"),
            default=default_val,
            required=True,
            max_length=2,
            placeholder="0",
        )
        self.add_item(self.rank_input)

    async def on_submit(self, interact: discord.Interaction):
        if not self.rank_input.value.isdigit() or int(self.rank_input.value) < 0:
            await interact.response.send_message(
                ts.get(f"{pf}err-invalid-value"), ephemeral=True
            )
            return

        try:
            await TradeService.update_item_rank(
                self.db_pool, interact.message.id, int(self.rank_input.value)
            )
            new_embed = await build_trade_embed_from_db(
                interact.message.id, self.db_pool
            )
            await interact.response.edit_message(embed=new_embed)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="btn.edit.rank",
                interact=interact,
                msg=f"EditRankModal -> Submit",
                obj=self.rank_input.value,
            )
        except Exception:
            await interact.response.send_message(
                ts.get(f"{pf}err-edit"), ephemeral=True
            )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.e_event,
                cmd="btn.edit.rank",
                interact=interact,
                msg=f"EditRankModal -> Submit, but ERR",
                obj=f"{self.rank_input.value}\n{return_traceback()}",
            )


# ----------------- Views -----------------
class ConfirmDeleteView(ui.View):
    def __init__(
        self,
        interact: discord.Interaction,
        origin_message: discord.Message,
        trade_data,
        trade_view,
    ):
        super().__init__(timeout=20)
        self.interact = interact
        self.origin_message = origin_message
        self.data = trade_data
        self.party_view = trade_view
        self.value = None

    async def on_timeout(self):
        cmd = "btn.confirm.delete"
        try:
            await self.interact.edit_original_response(
                content=ts.get(f"cmd.err-timeout"), view=None
            )
            await save_log(
                pool=self.interact.client.db,
                type=LOG_TYPE.event,
                cmd=cmd,
                interact=self.interact,
                msg=f"TradeView.ConfirmDeleteView -> timeout",
            )
        except discord.NotFound:
            await save_log(
                pool=self.interact.client.db,
                type=LOG_TYPE.event,
                cmd=cmd,
                interact=self.interact,
                msg=f"TradeView.ConfirmDeleteView -> timeout, but Not Found",
            )
        except Exception:
            await save_log(
                pool=self.interact.client.db,
                type=LOG_TYPE.err,
                cmd=cmd,
                interact=self.interact,
                msg=f"TradeView.ConfirmDeleteView -> timeout, but ERR",
                obj=return_traceback(),
            )

    @ui.button(label=ts.get(f"{pf}del-btny"), style=discord.ButtonStyle.danger)
    async def yes_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.defer()
        await interact.delete_original_response()
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.confirm.delete",
            interact=interact,
            msg=f"ConfirmDeleteView -> clicked yes",
        )
        try:
            await TradeService.delete_trade(interact.client.db, interact.channel.id)

            new_embed = await build_trade_embed(
                self.data, interact.client.db, isDelete=True
            )
            # for item in self.party_view.children:
            #     item.disabled = True
            await self.origin_message.edit(embed=new_embed, view=None)

            # update webhook
            try:
                webhook = await get_webhook(
                    interact.channel.parent, interact.client.user.avatar
                )
                if webhook:
                    await webhook.edit_message(
                        message_id=interact.channel.id, content=ts.get(f"{pf}deleted")
                    )
            except:
                pass

            if isinstance(interact.channel, discord.Thread):
                await interact.channel.edit(locked=True)
        except Exception:
            await interact.followup.send(ts.get(f"{pf}err-general"), ephemeral=True)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.e_event,
                cmd="btn.confirm.delete",
                interact=interact,
                msg=f"ConfirmDeleteView -> clicked yes, but ERR",
                obj=return_traceback(),
            )
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.confirm.delete",
            interact=interact,
            msg=f"ConfirmDeleteView -> yes",
        )
        self.value = True
        self.stop()

    @ui.button(label=ts.get(f"{pf}del-btnn"), style=discord.ButtonStyle.secondary)
    async def no_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.edit_message(content=ts.get(f"{pf}canceled"), view=None)
        self.value = False
        self.stop()
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.confirm.delete.cancel",
            interact=interact,
            msg=f"ConfirmDeleteView -> clicked no",
        )


class ConfirmTradeView(ui.View):
    def __init__(self, db_pool, trade_id, original_message):
        super().__init__(timeout=20)
        self.db_pool = db_pool
        self.trade_id = trade_id
        self.original_message = original_message
        self.value = None

    @ui.button(label=ts.get(f"{pf}btn-confirm"), style=discord.ButtonStyle.success)
    async def yes_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.defer()
        await interact.delete_original_response()
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.confirm.trade",
            interact=interact,
            msg=f"ConfirmTradeView -> YES",
        )
        try:
            host_warn_count = await WarnService.getCriticalCount(
                interact.client.db, interact.user.id
            )
            trade_info = await TradeService.get_trade_by_id(self.db_pool, self.trade_id)

            req_text = ""
            if host_warn_count >= 1:
                req_text += ts.get(f"cmd.warning-count").format(count=host_warn_count)

            req_text += ts.get(f"{pf}trade-request").format(
                host_mention=f"<@{trade_info['host_id']}>",
                user_mention=interact.user.mention,
                user=parseNickname(interact.user.display_name),
                price=trade_info["price"],
                type=revTradeType(trade_info["trade_type"]),
            )
            await self.original_message.channel.send(req_text)
            self.value = True
            self.stop()
        except Exception:
            await interact.followup.send(ts.get(f"{pf}err-general"), ephemeral=True)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="btn.confirm.trade",
                interact=interact,
                msg=f"ConfirmTradeView -> ERR",
                obj=return_traceback(),
            )

    @ui.button(label=ts.get(f"{pf}btn-cancel"), style=discord.ButtonStyle.secondary)
    async def no_button(self, interact: discord.Interaction, button: ui.Button):
        await interact.response.edit_message(content=ts.get(f"{pf}canceled"), view=None)
        self.value = False
        self.stop()
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="btn.confirm.trade.cancel",
            interact=interact,
            msg=f"ConfirmTradeView -> clicked no",
        )


class TradeView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown_action = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_ACTION, commands.BucketType.user
        )
        self.cooldown_manage = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_MANAGE, commands.BucketType.user
        )
        self.cooldown_call = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_BTN_CALL, commands.BucketType.user
        )

    async def is_cooldown(self, interact, mapping):
        bucket = mapping.get_bucket(interact.message)
        retry = bucket.update_rate_limit()
        if retry:
            await interact.response.send_message(
                embed=discord.Embed(
                    title=ts.get(f"cmd.err-cooldown.title"),
                    description=ts.get("cmd.err-cooldown.btn").format(
                        time=f"{int(retry)}"
                    ),
                    color=0xFF0000,
                ),
                ephemeral=True,
            )
            return True
        return False

    async def check_permissions(self, interact, trade_data, cmd: str = ""):
        is_host = interact.user.id == trade_data["host_id"]
        is_admin = await is_admin_user(interact, notify=False, cmd=cmd)
        if not is_host:
            if not is_admin:
                await interact.response.send_message(
                    ts.get(f"{pf}err-only-host"), ephemeral=True
                )
                return False
        return True

    # btn trade request
    @ui.button(
        label=ts.get(f"{pf}btn-trade"),
        style=discord.ButtonStyle.primary,
        custom_id="trade_btn_trade",
    )
    async def trade_action(self, interact: discord.Interaction, button: ui.Button):
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=f"btn.trade",
            interact=interact,
            msg=f"TradeView -> trade_action",
        )
        if await self.is_cooldown(interact, self.cooldown_call):
            return

        trade_data = await TradeService.get_trade_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isTradeExists(interact, trade_data):
            return

        if interact.user.id == trade_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf}err-self-trade"), ephemeral=True
            )
            return

        view = ConfirmTradeView(interact.client.db, trade_data["id"], interact.message)
        await interact.response.send_message(
            ts.get(f"{pf}confirm-trade"), view=view, ephemeral=True
        )

    # btn edit qty
    @ui.button(
        label=ts.get(f"{pf}btn-edit-qty"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_qty",
    )
    async def edit_quantity(self, interact: discord.Interaction, button: ui.Button):
        cmd = "TradeView.btn.edit-quantity"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"TradeView -> edit_quantity",
        )
        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        trade_data = await TradeService.get_trade_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isTradeExists(interact, trade_data):
            return

        if not await self.check_permissions(interact, trade_data, cmd):
            return

        await interact.response.send_modal(
            EditQuantityModal(trade_data["quantity"], interact.client.db)
        )

    # btn edit price
    @ui.button(
        label=ts.get(f"{pf}btn-edit-price"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_price",
    )
    async def edit_price(self, interact: discord.Interaction, button: ui.Button):
        cmd = "TradeView.btn.edit-price"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f" -> edit_price",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        trade_data = await TradeService.get_trade_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isTradeExists(interact, trade_data, cmd):
            return

        if not await self.check_permissions(interact, trade_data, cmd):
            return

        await interact.response.send_modal(
            EditPriceModal(trade_data["price"], interact.client.db)
        )

    # btn edit rank
    @ui.button(
        label=ts.get(f"{pf}btn-edit-rank"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_rank",
        # row=1,
    )
    async def edit_rank(self, interact: discord.Interaction, button: ui.Button):
        cmd = "TradeView.btn.edit-rank"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f" -> edit_rank",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        trade_data = await TradeService.get_trade_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isTradeExists(interact, trade_data, cmd):
            return

        if not await self.check_permissions(interact, trade_data, cmd):
            return

        # check rank
        if trade_data.get("item_rank") <= -1:
            await interact.response.send_message(
                ts.get(f"{pf}err-no-rank-item"), ephemeral=True
            )
            return

        await interact.response.send_modal(
            EditRankModal(trade_data["item_rank"], interact.client.db)
        )

    # edit nickname
    @ui.button(
        label=ts.get(f"{pf}btn-edit-nickname"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_nick",
    )
    async def edit_nickname(self, interact: discord.Interaction, button: ui.Button):
        cmd = "TradeView.btn.edit-nickname"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f" -> edit_price",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        trade_data = await TradeService.get_trade_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isTradeExists(interact, trade_data):
            return

        if not await is_admin_user(interact, notify=False, cmd=cmd):
            await interact.response.send_message(
                ts.get(f"general.unable"), ephemeral=True
            )
            return

        await interact.response.send_modal(
            EditNicknameModal(trade_data["game_nickname"], interact.client.db)
        )

    # btn close trade
    @ui.button(
        label=ts.get(f"{pf}btn-close"),
        style=discord.ButtonStyle.danger,
        custom_id="trade_btn_edit_close",
    )
    async def close_trade(self, interact: discord.Interaction, button: ui.Button):
        cmd = "TradeView.btn.trade.toggle_close_party"
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd=cmd,
            interact=interact,
            msg=f"TradeView -> close_trade",
            # obj=new_status,
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        trade_data = await TradeService.get_trade_by_message_id(
            interact.client.db, interact.message.id
        )
        if not await isTradeExists(interact, trade_data):
            return

        trade_data["host_mention"] = f"<@{trade_data['host_id']}>"

        if not await self.check_permissions(interact, trade_data, cmd):
            return

        view = ConfirmDeleteView(interact, interact.message, trade_data, self)
        await interact.response.send_message(
            ts.get(f"{pf}confirm-delete"), view=view, ephemeral=True
        )
