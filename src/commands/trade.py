import discord
from discord.ext import commands
import sqlite3
import asyncio

from config.config import LOG_TYPE
from config.TOKEN import base_url_market_image
from src.translator import ts
from src.constants.keys import (
    LFG_WEBHOOK_NAME,
    COOLDOWN_BTN_ACTION,
    COOLDOWN_BTN_MANAGE,
    COOLDOWN_BTN_CALL,
)
from src.parser.marketsearch import get_slug_data, categorize, create_market_url
from src.utils.data_manager import CHANNELS, ADMINS
from src.utils.logging_utils import save_log
from src.utils.api_request import API_MarketSearch

pf: str = "cmd.trade."


def parseNickname(nickname: str) -> str:
    return nickname.split("]")[-1].strip()


class EditNicknameModal(discord.ui.Modal, title=ts.get(f"{pf}edit-nick-title")):
    def __init__(self, curr_nickname: str, db: sqlite3.Connection):
        super().__init__(timeout=None)
        self.db = db

        self.input_nickname = discord.ui.TextInput(
            label=ts.get(f"{pf}edit-nick-label"),
            style=discord.TextStyle.short,
            default=curr_nickname,
            required=True,
        )
        self.add_item(self.input_nickname)

    async def on_submit(self, interact: discord.Interaction):
        try:
            cursor = self.db.cursor()

            # update DB
            cursor.execute(
                "UPDATE trades SET game_nickname = ? WHERE message_id = ?",
                (self.input_nickname.value, interact.message.id),
            )
            self.db.commit()

            # refresh Embed
            new_embed = await build_trade_embed_from_db(interact.message.id, self.db)
            await interact.response.edit_message(embed=new_embed)

            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.event,
                cmd="btn.edit.article",
                interact=interact,
                msg=f"EditTradeModal -> Clicked Submit",
                obj=f"{self.input_nickname.value}",
            )
        except Exception as e:
            await interact.response.send_message(
                ts.get(f"{pf}err-edit"), ephemeral=True
            )
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.e_event,
                cmd="btn.edit.article",
                interact=interact,
                msg=f"EditTradeModal -> Clicked Submit",
                obj=f"{e}\nT:{self.input_nickname.value}",
            )


class EditQuantityModal(discord.ui.Modal, title=ts.get(f"{pf}edit-qty-title")):
    def __init__(self, current_quantity: int, db: sqlite3.Connection):
        super().__init__(timeout=None)
        self.db = db

        self.quantity_input = discord.ui.TextInput(
            label=ts.get(f"{pf}edit-qty-label"),
            style=discord.TextStyle.short,
            default=str(current_quantity),
            required=True,
        )
        self.add_item(self.quantity_input)

    async def on_submit(self, interact: discord.Interaction):
        try:
            new_quantity_str = self.quantity_input.value

            if not new_quantity_str.isdigit() or int(new_quantity_str) < 1:
                await interact.response.send_message(
                    ts.get(f"{pf}err-size-low"), ephemeral=True
                )
                return

            if not new_quantity_str.isdigit() or int(new_quantity_str) >= 12:
                await interact.response.send_message(
                    ts.get(f"{pf}err-size-high"), ephemeral=True
                )
                return

            new_quantity = int(new_quantity_str)
            cursor = self.db.cursor()

            cursor.execute(
                "UPDATE trades SET quantity = ? WHERE message_id = ?",
                (new_quantity, interact.message.id),
            )
            self.db.commit()

            # refresh Embed
            new_embed = await build_trade_embed_from_db(interact.message.id, self.db)
            await interact.response.edit_message(embed=new_embed)

            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.event,
                cmd="btn.edit.quantity",
                interact=interact,
                msg=f"EditQuantityModal -> Clicked Submit",
                obj=new_quantity_str,
            )
        except Exception as e:
            await interact.response.send_message(
                ts.get(f"{pf}err-edit"), ephemeral=True
            )
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.e_event,
                cmd="btn.edit.quantity",
                interact=interact,
                msg=f"EditQuantityModal -> Clicked Submit '{new_quantity_str}'",
                obj=e,
            )


class EditPriceModal(discord.ui.Modal, title=ts.get(f"{pf}edit-price-title")):
    def __init__(self, current_price: int, db: sqlite3.Connection):
        super().__init__(timeout=None)
        self.db = db

        self.price_input = discord.ui.TextInput(
            label=ts.get(f"{pf}edit-price-label"),
            style=discord.TextStyle.short,
            default=str(current_price),
            required=True,
        )
        self.add_item(self.price_input)

    async def on_submit(self, interact: discord.Interaction):
        try:
            new_price_str = self.price_input.value

            if not new_price_str.isdigit() or int(new_price_str) < 0:
                await interact.response.send_message(
                    ts.get(f"{pf}err-invalid-value"), ephemeral=True
                )
                return

            new_price = int(new_price_str)
            cursor = self.db.cursor()

            cursor.execute(
                "UPDATE trades SET price = ? WHERE message_id = ?",
                (new_price, interact.message.id),
            )
            self.db.commit()

            new_embed = await build_trade_embed_from_db(interact.message.id, self.db)
            await interact.response.edit_message(embed=new_embed)

            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.event,
                cmd="btn.edit.price",
                interact=interact,
                msg=f"EditPriceModal -> Clicked Submit",
                obj=new_price_str,
            )
        except Exception as e:
            await interact.response.send_message(
                ts.get(f"{pf}err-edit"), ephemeral=True
            )
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.e_event,
                cmd="btn.edit.price",
                interact=interact,
                msg=f"EditPriceModal -> Clicked Submit '{new_price_str}' but ERR",
                obj=e,
            )


class ConfirmDeleteView(discord.ui.View):
    def __init__(self, origin_msg_id, trade_data, trade_view):
        super().__init__(timeout=60)
        self.value = None
        self.msgid = origin_msg_id
        self.data = trade_data
        self.party_view = trade_view

    # delete confirm btn
    @discord.ui.button(
        label=ts.get(f"{pf}del-btny"),
        style=discord.ButtonStyle.danger,
        custom_id="confirm_delete_yes",
    )
    async def yes_button(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await interact.response.defer()

        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd="btn.confirm.delete",
            interact=interact,
            msg=f"ConfirmDeleteView -> clicked yes",
        )
        # remove this view
        await interact.delete_original_response()

        try:
            db = interact.client.db
            cursor = db.cursor()

            # refresh Embed
            message = await interact.channel.fetch_message(self.msgid)
            new_embed = build_trade_embed(self.data, isDelete=True)

            # disable all buttons on the original PartyView
            for item in self.party_view.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True
            await message.edit(embed=new_embed, view=self.party_view)

            try:  # edit web hook msg
                webhook_name = LFG_WEBHOOK_NAME
                webhooks = await interact.channel.parent.webhooks()
                webhook = discord.utils.get(webhooks, name=webhook_name)

                if webhook:
                    starter_message = await interact.channel.parent.fetch_message(
                        interact.channel.id
                    )
                    if starter_message:
                        await webhook.edit_message(
                            message_id=interact.channel.id,
                            content=ts.get(f"{pf}deleted"),
                        )
                else:  #  if webhook is not found
                    starter_message = await interact.channel.parent.fetch_message(
                        interact.channel.id
                    )
                    await starter_message.edit(content=ts.get(f"{pf}deleted"))
            except discord.NotFound:
                # print("스레드의 첫 메시지를 찾을 수 없습니다.")
                pass  # starter msg not found, maybe deleted manually

            # delete trade info from DB
            cursor.execute(
                "DELETE FROM trades WHERE thread_id = ?", (interact.channel.id,)
            )
            db.commit()

            # lock the thread
            if isinstance(interact.channel, discord.Thread):
                await interact.channel.edit(locked=True)
        except discord.Forbidden as e:
            await interact.followup.send(ts.get(f"{pf}del-btny"), ephemeral=True)
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.event,
                cmd="btn.confirm.delete",
                interact=interact,
                msg=f"ConfirmDeleteView -> clicked yes | but Forbidden\n{e}",
            )
        except Exception as e:
            await interact.followup.send(ts.get(f"{pf}err-general"), ephemeral=True)
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.event,
                cmd="btn.confirm.delete",
                interact=interact,
                msg=f"ConfirmDeleteView -> clicked yes | but ERR\n{e}",
                obj=e,
            )

        self.value = True
        self.stop()

    # delete cancel btn
    @discord.ui.button(
        label=ts.get(f"{pf}del-btnn"),
        style=discord.ButtonStyle.secondary,
        custom_id="confirm_delete_no",
    )
    async def no_button(self, interact: discord.Interaction, button: discord.ui.Button):
        await interact.response.edit_message(content=ts.get(f"{pf}canceled"), view=None)
        self.value = False
        self.stop()

        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd="btn.confirm.delete.cancel",
            interact=interact,
            msg=f"ConfirmDeleteView -> clicked no",
        )


class ConfirmTradeView(discord.ui.View):
    def __init__(
        self,
        db: sqlite3.Connection,
        trade_id: int,
        original_message: discord.Message,
    ):
        super().__init__(timeout=60)
        self.value = None
        self.db = db
        self.trade_id = trade_id
        self.original_message = original_message

    @discord.ui.button(
        label=ts.get(f"{pf}btn-confirm"),
        style=discord.ButtonStyle.success,
        custom_id="confirm_trade_yes",
    )
    async def yes_button(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await interact.response.defer()

        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd="btn.confirm.trade",
            interact=interact,
            msg=f"ConfirmTradeView -> YES",
        )

        try:
            trade_info = self.db.execute(
                "SELECT host_id FROM trades WHERE id = ?", (self.trade_id,)
            ).fetchone()
            host_mention = f"<@{trade_info['host_id']}>" if trade_info else ""

            await self.original_message.channel.send(
                ts.get(f"{pf}trade-request").format(
                    host_mention=host_mention, user_mention=interact.user.mention
                )
            )
            await interact.delete_original_response()
            self.value = True
            self.stop()
        except Exception as e:
            if not interact.response.is_done():
                await interact.response.edit_message(
                    content=ts.get(f"{pf}err-general"), view=None
                )
            else:
                await interact.followup.send(ts.get(f"{pf}err-general"), ephemeral=True)

            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.event,
                cmd="btn.confirm.trade",
                interact=interact,
                msg=f"ConfirmTradeView -> ERR",
                obj=e,
            )

    @discord.ui.button(
        label=ts.get(f"{pf}btn-cancel"),
        style=discord.ButtonStyle.secondary,
        custom_id="confirm_trade_no",
    )
    async def no_button(self, interact: discord.Interaction, button: discord.ui.Button):
        await interact.response.edit_message(content=ts.get(f"{pf}canceled"), view=None)
        self.value = False
        self.stop()

        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd="btn.confirm.trade.cancel",
            interact=interact,
            msg=f"ConfirmTradeView -> clicked no",
        )


class TradeView(discord.ui.View):
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

    async def is_cooldown(
        self, interact: discord.Interaction, cooldown_mapping: commands.CooldownMapping
    ) -> bool:
        bucket = cooldown_mapping.get_bucket(interact.message)
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

    async def fetch_trade_data(self, interact: discord.Interaction):
        """fetch trade data from DB"""
        db = interact.client.db
        db.row_factory = sqlite3.Row

        trade_data = db.execute(
            "SELECT * FROM trades WHERE message_id = ?", (interact.message.id,)
        ).fetchone()

        if not trade_data:
            if not interact.response.is_done():
                await interact.response.send_message(
                    ts.get(f"{pf}err-not-found"), ephemeral=True
                )
            else:
                await interact.followup.send(
                    ts.get(f"{pf}err-not-found"), ephemeral=True
                )
            return None

        return dict(trade_data)

    @discord.ui.button(  # 거래하기
        label=ts.get(f"{pf}btn-trade"),
        style=discord.ButtonStyle.primary,
        custom_id="trade_btn_trade",
    )
    async def trade_action(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd=f"btn.trade",
            interact=interact,
            msg=f"TradeView -> trade_action",
        )

        if await self.is_cooldown(interact, self.cooldown_call):
            return

        db = interact.client.db
        trade_data = await self.fetch_trade_data(interact)
        if not trade_data:
            await interact.response.send_message(
                ts.get(f"{pf}err-not-found"), ephemeral=True
            )
            return

        if interact.user.id == trade_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf}err-self-trade"), ephemeral=True
            )
            return

        view = ConfirmTradeView(
            db=db,
            trade_id=trade_data["id"],
            original_message=interact.message,
        )
        await interact.response.send_message(
            ts.get(f"{pf}confirm-trade"), view=view, ephemeral=True
        )

        timed_out = await view.wait()
        if timed_out and view.value is None:
            await interact.edit_original_response(
                content=ts.get(f"{pf}err-timeout"), view=None
            )

    @discord.ui.button(  # 수량 변경
        label=ts.get(f"{pf}btn-edit-qty"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_qty",
    )
    async def edit_quantity(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd="btn.main.edit-quantity",
            interact=interact,
            msg=f"TradeView -> edit_quantity",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        trade_data = await self.fetch_trade_data(interact)
        if not trade_data:
            await interact.response.send_message(
                ts.get(f"{pf}err-not-found"), ephemeral=True
            )
            return

        if interact.user.id != trade_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf}err-only-host"), ephemeral=True
            )
            return

        modal = EditQuantityModal(
            db=interact.client.db, current_quantity=trade_data["quantity"]
        )
        await interact.response.send_modal(modal)

    @discord.ui.button(  # 가격 수정
        label=ts.get(f"{pf}btn-edit-price"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_price",
    )
    async def edit_price(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd="btn.main.edit-price",
            interact=interact,
            msg=f"TradeView -> edit_price",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        trade_data = await self.fetch_trade_data(interact)
        if not trade_data:
            await interact.response.send_message(
                ts.get(f"{pf}err-not-found"), ephemeral=True
            )
            return

        if interact.user.id != trade_data["host_id"]:
            await interact.response.send_message(
                ts.get(f"{pf}err-only-host"), ephemeral=True
            )
            return

        modal = EditPriceModal(db=interact.client.db, current_price=trade_data["price"])
        await interact.response.send_modal(modal)

    @discord.ui.button(  # 닉네임 변경
        label=ts.get(f"{pf}btn-edit-nickname"),
        style=discord.ButtonStyle.secondary,
        custom_id="trade_btn_edit_nick",
    )
    async def edit_nickname(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd="btn.main.edit-price",
            interact=interact,
            msg=f"TradeView -> edit_price",
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        trade_data = await self.fetch_trade_data(interact)
        if not trade_data:
            await interact.response.send_message(
                ts.get(f"{pf}err-not-found"), ephemeral=True
            )
            return

        # on manual estup nickname
        # if interact.user.id != trade_data["host_id"] and interact.user.id not in ADMINS:
        #     await interact.response.send_message(
        #         ts.get(f"{pf}err-only-host"), ephemeral=True
        #     )
        #     return

        if interact.user.id not in ADMINS:
            await interact.response.send_message(
                "기능을 사용할 권한이 없어요.", ephemeral=True
            )
            return

        modal = EditNicknameModal(
            db=interact.client.db, curr_nickname=trade_data["game_nickname"]
        )
        await interact.response.send_modal(modal)

    @discord.ui.button(  # 거래 글 닫기
        label=ts.get(f"{pf}btn-close"),
        style=discord.ButtonStyle.danger,
        custom_id="trade_btn_edit_close",
    )
    async def close_trade(
        self, interact: discord.Interaction, button: discord.ui.Button
    ):
        await save_log(
            lock=interact.client.log_lock,
            type=LOG_TYPE.event,
            cmd="btn.trade.toggle_close_party",
            interact=interact,
            msg=f"TradeView -> close_trade",
            # obj=new_status,
        )

        if await self.is_cooldown(interact, self.cooldown_manage):
            return

        # db = interact.client.db
        # cursor = db.cursor()

        trade_data = await self.fetch_trade_data(interact)
        if not trade_data:
            await interact.response.send_message(
                ts.get(f"{pf}err-not-found"), ephemeral=True
            )
            return

        if interact.user.id != trade_data["host_id"] and interact.user.id not in ADMINS:
            await interact.response.send_message(
                ts.get(f"{pf}err-only-host"), ephemeral=True
            )
            return

        view = ConfirmDeleteView(
            origin_msg_id=interact.message.id,
            trade_view=self,
            trade_data={
                "id": trade_data["id"],
                "host_id": trade_data["host_id"],
                "host_mention": interact.user.mention,
                "game_nickname": trade_data["game_nickname"],
                "trade_type": trade_data["trade_type"],
                "item_name": trade_data["item_name"],
                "quantity": trade_data["quantity"],
                "price": trade_data["price"],
            },
        )
        await interact.response.send_message(
            ts.get(f"{pf}confirm-delete"), view=view, ephemeral=True
        )


# embed creation helper function
def build_trade_embed(
    data: dict, isDelete: bool = False, isRank: bool = False
) -> discord.Embed:
    """Creates a trade embed from a dictionary."""

    flag, _, __, img_url = get_slug_data(data["item_name"])

    # title
    title: str = "~~" if isDelete else ""
    title += f"[{data['trade_type']}] {data['item_name']}"
    if isRank:
        title += f" ({ts.get(f'{pf}rank-simple').format(rank=data['item_rank'])})"

    if isDelete:
        title += "~~"

    # color
    color = 0x00FF00 if not isDelete else 0xFF0000

    description: str = "~~" if isDelete else ""
    description += f"""
- **{ts.get(f'{pf}creator')}:** {data['host_mention']}
- **{ts.get(f'{pf}item-name')}:** {create_market_url(data['item_name'])}
- **{ts.get(f'{pf}price-per')}:** `{data['price']:,} {ts.get(f'{pf}platinum')}` (총 {data['price'] * data['quantity']:,} 플레)
- **{ts.get(f'{pf}quantity')}:** `{data['quantity']:,}` 개
"""
    if not isDelete:
        description += f"""
> 귓속말 명령어 복사
```
/w {data['game_nickname']}
```
> 파티 초대 명령어 복사
```
/inv {data['game_nickname']}
```
"""
    if isDelete:
        description += "~~"

    embed = discord.Embed(title=title, description=description.strip(), color=color)
    embed.set_footer(text=f"ID: {data['id']}")
    if flag and img_url:
        embed.set_thumbnail(url=f"{base_url_market_image}{img_url}")
    return embed


async def build_trade_embed_from_db(
    message_id: int, db: sqlite3.Connection
) -> discord.Embed:
    """[for external use] creates an embed using a message_id & db connection"""
    db.row_factory = sqlite3.Row

    trade_data = db.execute(
        "SELECT * FROM trades WHERE message_id = ?", (message_id,)
    ).fetchone()
    if not trade_data:
        return discord.Embed(
            title=ts.get(f"{pf}err"),
            description=ts.get(f"{pf}err-not-found"),
            color=discord.Color.dark_red(),
        )

    return build_trade_embed(
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
        }
    )


async def cmd_create_trade_helper(
    interact: discord.Interaction,
    db_conn: sqlite3.Connection,
    trade_type: str,
    item_name: str,
    item_rank: int,
    price: int,
    quantity: int,
    game_nickname: str = "",
) -> None:
    db = db_conn
    db.row_factory = sqlite3.Row
    log_lock: asyncio.Lock = interact.client.log_lock

    isRankItem: bool = False
    RESULT: str = ""
    target_channel = interact.client.get_channel(CHANNELS["trade"])

    await interact.response.defer(ephemeral=True)

    # check trade_type
    types = [ts.get(f"cmd.trade.type-sell"), ts.get("cmd.trade.type-buy")]
    if trade_type not in types:
        interact.followup.send(
            ts.get(f"{pf}err-type").format(
                type=trade_type, list=", ".join(f"**{i}**" for i in types)
            )
        )
        return

    # channel not exists
    if not target_channel and not isinstance(target_channel, discord.TextChannel):
        await interact.followup.send(ts.get(f"cmd.party.not-found-ch"), ephemeral=True)
        return

    # setup nickname
    game_nickname = parseNickname(interact.user.display_name)

    # search market
    try:
        flag: bool = False
        flag, item_slug, item_name, img_url = get_slug_data(item_name)

        # item not found
        if not flag:
            await interact.followup.send(
                ts.get("cmd.market-search.no-result")
                + f"\n- `{item_name}`에 대한 마켓 검색 결과가 없습니다.\n- 아이템 이름을 확인해주세요.",
                ephemeral=True,
            )
            return

        market = await API_MarketSearch(log_lock, item_slug)

        # automatic price setup
        async def set_price(market, price) -> int:
            if market.status_code == 404:  # api not found
                await interact.followup.send(
                    ts.get(f"{pf}err-no-market"), ephemeral=True
                )
                return price if price else 0, market.json()
            elif market.status_code != 200:
                raise ValueError("resp-code is not 200 or resp err")

            market = categorize(market.json(), rank=item_rank)
            price_list: list = []
            for i in range(6):
                price_list.append(market[i]["platinum"])

            price = sum(price_list) // len(price_list)
            await interact.followup.send(
                ts.get(f"{pf}auto-price").format(price=price), ephemeral=True
            )
            return price, market

        try:
            price, market = await set_price(market, price)
        except Exception as e:
            await interact.followup.send(ts.get(f"{pf}err-api"), ephemeral=True)
            await save_log(
                lock=interact.client.log_lock,
                type="cmd.api",
                cmd=f"cmd.trade",
                interact=interact,
                msg="[err] Market API Failed",
                obj=f"{RESULT}Type:{trade_type}, Item:{item_name}, Qty:{quantity}, Price:{price}",
            )
            price = price if price else 0

        ########### db ############
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO trades (host_id, game_nickname, trade_type, item_name, item_rank, quantity, price) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                interact.user.id,
                game_nickname,
                trade_type,
                item_name,
                item_rank,
                quantity,
                price,
            ),
        )
        TRADE_ID = cursor.lastrowid
        db.commit()

        # check item have rank
        isRankItem = True if market[0].get("rank", None) is not None else False

        # create a webhook
        webhook_name = LFG_WEBHOOK_NAME
        webhooks = await target_channel.webhooks()
        webhook = discord.utils.get(webhooks, name=webhook_name)
        if webhook is None:
            webhook = await target_channel.create_webhook(name=webhook_name)

        trade_type_str = f"**{trade_type}** 합니다"
        thread_name = f"[{trade_type}] {item_name}"
        # print(market[0].get("rank", "NOT EXISTS"))
        thread_name += (
            f" ({ts.get(f'{pf}rank-simple').format(rank=item_rank)})"
            if isRankItem
            else ""
        )

        # thread start message
        thread_starter_msg = await webhook.send(
            content=trade_type_str,
            username=interact.user.display_name,
            avatar_url=interact.user.display_avatar.url,
            wait=True,
        )

        # create thread from starter msg (webhook)
        thread = await thread_starter_msg.create_thread(name=thread_name)

        # send created msg
        await interact.followup.send(
            ts.get(f"{pf}created-trade").format(
                ch=target_channel.name, mention=thread.mention
            ),
            ephemeral=True,
        )

        ############################
        initial_data = {
            "id": TRADE_ID,
            "host_id": interact.user.id,
            "host_mention": interact.user.mention,
            "game_nickname": game_nickname,
            "trade_type": trade_type,
            "item_name": item_name,
            "item_rank": item_rank,
            "quantity": quantity,
            "price": price,
        }

        embed = build_trade_embed(initial_data, isRank=isRankItem)
        view = TradeView()

        msg = await thread.send(embed=embed, view=view)

        cursor.execute(
            "UPDATE trades SET thread_id = ?, message_id = ? WHERE id = ?",
            (thread.id, msg.id, TRADE_ID),
        )
        db.commit()

        RESULT += "DONE!\n"

    except discord.Forbidden as e:
        await interact.followup.send(
            ts.get(f"cmd.party.no-thread-permission"),
            ephemeral=True,
        )
        RESULT += f"Forbidden {e}\n"
    except discord.HTTPException as e:
        await interact.followup.send(
            f"{ts.get(f'cmd.party.err-creation')}",
            ephemeral=True,
        )
        RESULT += f"HTTPException {e}\n"
    except Exception as e:
        await interact.followup.send(ts.get(f"{pf}err-general"), ephemeral=True)
        RESULT += f"ERROR {e}"

    await save_log(
        lock=interact.client.log_lock,
        type="cmd",
        cmd=f"cmd.trade",
        interact=interact,
        msg="[info] cmd used",
        obj=f"{RESULT}Type:{trade_type}, Item:{item_name}, Qty:{quantity}, Price:{price}",
    )
