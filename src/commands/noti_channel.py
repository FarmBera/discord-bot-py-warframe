import discord
import aiohttp
import asyncio

from src.translator import ts
from src.utils.logging_utils import save_log
from src.utils.db_helper import transaction, query_reader
from src.constants.keys import (
    ALERTS,
    NEWS,
    SORTIE,
    ARCHONHUNT,
    VOIDTRADERS,
    STEELPATH,
    ARCHIMEDEA,
    FISSURES,
    CALENDAR,
    DAILYDEALS,
    INVASIONS,
    DUVIRI_ROTATION,
    EVENTS,
    #
    DUVIRI_U_K_W,
    DUVIRI_U_K_I,
    #
    ARCHIMEDEA_DEEP,
    ARCHIMEDEA_TEMPORAL,
)

DB_COLUMN_MAP = {
    ALERTS: "sub_alerts",
    NEWS: "sub_news",
    SORTIE: "sub_sortie",
    ARCHONHUNT: "sub_archonhunt",
    VOIDTRADERS: "sub_voidtraders",
    ARCHIMEDEA: "sub_archimedea",
    STEELPATH: "sub_steelpath",
    CALENDAR: "sub_calendar",
    DAILYDEALS: "sub_dailydeals",
    INVASIONS: "sub_invasions",
    f"{DUVIRI_ROTATION}{DUVIRI_U_K_W}": "sub_duviri_wf",
    f"{DUVIRI_ROTATION}{DUVIRI_U_K_I}": "sub_duviri_inc",
    EVENTS: "sub_events",
}

# set profile with alert type
PROFILE_CONFIG = {VOIDTRADERS: {"name": "바로 키 티어", "avatar": "baro-ki-teer"}}

# UI selection
NOTI_LABELS = {
    ALERTS: "얼럿 미션",
    NEWS: "워프레임 뉴스",
    SORTIE: "출격",
    ARCHONHUNT: "집정관 사냥",
    VOIDTRADERS: "바로 키 티어",
    ARCHIMEDEA: "심층 & 템포럴 아르키메디아",
    STEELPATH: "스틸에센스",
    CALENDAR: "1999달력",
    DAILYDEALS: "일일 특가",
    INVASIONS: "침공",
    f"{DUVIRI_ROTATION}{DUVIRI_U_K_W}": "두비리 순환로 - 워프레임",
    f"{DUVIRI_ROTATION}{DUVIRI_U_K_I}": "두비리 순환로 - 인카논",
    EVENTS: "이벤트",
}

pfs: str = "cmd.alert-set."  # prefix select
pfu: str = "cmd.alert-delete."  # prefix unselect


class NotificationSelect(discord.ui.Select):
    def __init__(self):
        options = []
        # creat options
        for key, label in NOTI_LABELS.items():
            options.append(discord.SelectOption(label=label, value=key))

        super().__init__(
            placeholder=ts.get(f"{pfs}select-placeholder"),
            min_values=0,
            max_values=len(NOTI_LABELS),
            options=options,
        )

    async def callback(self, interact: discord.Interaction):
        await interact.response.defer(ephemeral=True)

        # check permission
        if not interact.channel.permissions_for(interact.guild.me).manage_webhooks:
            await interact.edit_original_response(
                content=ts.get("cmd.err-perm-webhook"),
                embed=None,
                view=None,
            )
            return

        # get/create webhook
        bot_name = interact.client.user.display_name
        webhooks = await interact.channel.webhooks()
        webhook = discord.utils.get(webhooks, name=bot_name)

        if not webhook:
            try:
                # retrieve the bot's profile picture & apply
                avatar_bytes = None
                if interact.client.user.avatar:
                    avatar_bytes = await interact.client.user.avatar.read()

                webhook = await interact.channel.create_webhook(
                    name=bot_name, avatar=avatar_bytes
                )
            except Exception:

                webhook = await interact.channel.create_webhook(name=bot_name)

        sql_base = "INSERT INTO webhooks (channel_id, guild_id, webhook_url, {cols}) VALUES (%s, %s, %s, %s, {vals}) ON DUPLICATE KEY UPDATE webhook_url=%s, {updates}"

        col_names = []
        val_placeholders = []
        update_clauses = []

        insert_values = [interact.channel_id, interact.guild_id, webhook.url]
        update_values = [webhook.url]

        for key, col_name in DB_COLUMN_MAP.items():
            is_selected = 1 if str(key) in self.values else 0

            col_names.append(col_name)
            val_placeholders.append("%s")
            update_clauses.append(f"{col_name}=%s")

            insert_values.append(is_selected)
            update_values.append(is_selected)

        final_sql = sql_base.format(
            cols=", ".join(col_names),
            vals=", ".join(val_placeholders),
            updates=", ".join(update_clauses),
        )
        # print(final_sql, insert_values + update_values)

        try:
            async with transaction(interact.client.db) as cursor:
                await cursor.execute(final_sql, insert_values + update_values)
        except Exception:
            await interact.edit_original_response(
                content=ts.get(f"general-cmd"), embed=None, view=None
            )
            return
        await interact.edit_original_response(
            content=ts.get(f"{pfs}done").format(count=len(self.values)),
            embed=None,
            view=None,
        )


class NotificationUnSelect(discord.ui.Select):
    def __init__(self):
        options = []
        # create options
        for key, label in NOTI_LABELS.items():
            options.append(discord.SelectOption(label=label, value=str(key)))

        super().__init__(
            placeholder=ts.get(f"{pfu}select-placeholder"),
            min_values=1,  # select at least one
            max_values=len(NOTI_LABELS),
            options=options,
        )

    async def callback(self, interact: discord.Interaction):
        await interact.response.defer(ephemeral=True)

        # check permission
        if not interact.channel.permissions_for(interact.guild.me).manage_webhooks:
            await interact.edit_original_response(
                content=ts.get("cmd.err-perm-webhook"),
                embed=None,
                view=None,
            )
            return

        db_pool = interact.client.db
        is_fully_deleted = False

        # unsubscribe selected alert
        if self.values:
            set_clauses = []
            for val in self.values:
                target_col = None
                for k, col in DB_COLUMN_MAP.items():
                    if str(k) == val:
                        target_col = col
                        break

                if target_col:
                    set_clauses.append(f"{target_col} = 0")

            if set_clauses:
                sql_update = f"UPDATE webhooks SET {', '.join(set_clauses)} WHERE channel_id = %s"
                await cursor.execute(sql_update, (interact.channel_id,))

        # verify all notifications are turned off (DELETE)
        all_columns = list(DB_COLUMN_MAP.values())
        where_conditions = " AND ".join([f"{col}=0" for col in all_columns])
        # delete where alert flag is 0
        sql_delete = (
            f"DELETE FROM webhooks WHERE channel_id = %s AND {where_conditions}"
        )
        try:
            async with transaction(db_pool) as cursor:
                await cursor.execute(sql_delete, (interact.channel_id,))

                if cursor.rowcount > 0:
                    is_fully_deleted = True
        except Exception:
            await interact.edit_original_response(
                content=ts.get(f"general-cmd"), embed=None, view=None
            )
            return

        # send msg
        msg = ts.get(f"{pfu}done").format(count=len(self.values))

        if is_fully_deleted:
            try:
                webhooks = await interact.channel.webhooks()
                webhook = discord.utils.get(
                    webhooks, name=interact.client.user.display_name
                )
                if webhook:
                    await webhook.delete(reason=ts.get(f"{pfu}reason"))
            except:
                pass

        await interact.edit_original_response(
            content=msg,
            embed=None,
            view=None,
        )


class SettingView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(NotificationSelect())


class UnSettingView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(NotificationUnSelect())
