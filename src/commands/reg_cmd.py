import discord

from src.translator import ts
from config.config import LOG_TYPE
from src.utils.logging_utils import save_log
from src.commands.cmd_helper import cmd_helper
from src.commands.cmd_helper_text import cmd_helper_txt
from src.commands.party import cmd_create_party_helper
from src.commands.trade import cmd_create_trade_helper
from src.commands.complain import cmd_create_complain_helper
from src.commands.unavailable import cmd_unavailable
from src.commands.user_warn import cmd_user_warn_helper
from src.commands.admin import is_admin_user
from src.commands.noti_channel import noti_subscribe_helper, noti_unsubscribe_helper

from src.constants.keys import (
    # cooldown var
    COOLDOWN_DEFAULT,
    COOLDOWN_CREATE,
    COOLDOWN_5_MIN,
    # docs file
    HELP_FILE_LOC,
    ANNOUNCE_FILE_LOC,
    PATCHNOTE_FILE_LOC,
    POLICY_FILE_LOC,
    MARKET_HELP_FILE,
    # cmd obj
    ALERTS,
    NEWS,
    # CETUSCYCLE,
    SORTIE,
    ARCHONHUNT,
    VOIDTRADERS,
    STEELPATH,
    ARCHIMEDEA,
    # DUVIRICYCLE,
    FISSURES,
    CALENDAR,
    # CAMBIONCYCLE,
    DAILYDEALS,
    INVASIONS,
    MARKET_SEARCH,
    # VALLISCYCLE,
    DUVIRI_ROTATION,
    EVENTS,
    DESCENDIA,
)

from src.parser.alerts import w_alerts
from src.parser.news import w_news
from src.parser.cetusCycle import w_cetusCycle
from src.parser.sortie import w_sortie
from src.parser.archonHunt import w_archonHunt
from src.parser.voidTraders import w_voidTraders, w_voidTradersItem
from src.parser.steelPath import w_steelPath
from src.parser.duviriCycle import w_duviriCycle
from src.parser.fissures import w_fissures
from src.parser.archimedea import w_deepArchimedea
from src.parser.archimedea import w_temporalArchimedia
from src.parser.calendar import w_calendar
from src.parser.cambionCycle import w_cambionCycle
from src.parser.dailyDeals import w_dailyDeals
from src.parser.invasions import w_invasions
from src.parser.vallisCycle import w_vallisCycle
from src.parser.marketsearch import w_market_search, get_market_item_names
from src.parser.duviriRotation import w_duviri_warframe, w_duviri_incarnon
from src.parser.events import w_events
from src.parser.descendia import w_descendia


async def register_main_cmds(tree: discord.app_commands.CommandTree, db_pool) -> None:
    # help command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.help.cmd"), description=f"{ts.get('cmd.help.desc')}"
    )
    async def cmd_help(interact: discord.Interaction, is_public_msg: bool = False):
        await cmd_helper_txt(
            interact, file_name=HELP_FILE_LOC, isPublicMsg=is_public_msg
        )

    # announcement command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.announcement.cmd"),
        description=f"{ts.get('cmd.announcement.desc')}",
    )
    async def cmd_announcement(
        interact: discord.Interaction, is_public_msg: bool = False
    ):
        await cmd_helper_txt(
            interact,
            file_name=ANNOUNCE_FILE_LOC,
            isPublicMsg=is_public_msg,
        )

    # patch-note command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.patch-note.cmd"),
        description=f"{ts.get('cmd.patch-note.desc')}",
    )
    async def cmd_patch_note(
        interact: discord.Interaction, is_public_msg: bool = False
    ):
        await cmd_helper_txt(
            interact, file_name=PATCHNOTE_FILE_LOC, isPublicMsg=is_public_msg
        )

    # privacy-policy command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.privacy-policy.cmd"),
        description=f"{ts.get('cmd.privacy-policy.desc')}",
    )
    async def cmd_privacy_policy(
        interact: discord.Interaction, is_public_msg: bool = False
    ):
        await cmd_helper_txt(
            interact, file_name=POLICY_FILE_LOC, isPublicMsg=is_public_msg
        )

    # news command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(name=ts.get(f"cmd.news.cmd"), description=ts.get(f"cmd.news.desc"))
    async def cmd_news(interact: discord.Interaction):
        await cmd_helper(interact, key=NEWS, parser_func=w_news)

    # alerts command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.alerts.cmd"), description=ts.get(f"cmd.alerts.desc")
    )
    async def cmd_alerts(interact: discord.Interaction):
        await cmd_helper(interact=interact, key=ALERTS, parser_func=w_alerts)

    # cetus command (cetusCycle)
    # @tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
    # async def cmd_cetus(interact: discord.Interaction):
    #     await cmd_helper(interact=interact, key=CETUSCYCLE, parser_func=w_cetusCycle)

    # sortie command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc")
    )
    async def cmd_sortie(interact: discord.Interaction):
        await cmd_helper(interact, key=SORTIE, parser_func=w_sortie)

    # archon hunt command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.archon-hunt.cmd"), description=ts.get(f"cmd.archon-hunt.desc")
    )
    async def cmd_archon_hunt(interact: discord.Interaction):
        await cmd_helper(interact, key=ARCHONHUNT, parser_func=w_archonHunt)

    # void traders command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.void-traders.cmd"),
        description=ts.get(f"cmd.void-traders.desc"),
    )
    async def cmd_voidTraders(interact: discord.Interaction):
        await cmd_helper(
            interact, isFollowUp=True, key=VOIDTRADERS, parser_func=w_voidTraders
        )

    # steel path reward command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.steel-path-reward.cmd"),
        description=ts.get(f"cmd.steel-path-reward.desc"),
    )
    async def cmd_steel_reward(interact: discord.Interaction):
        await cmd_helper(interact, key=STEELPATH, parser_func=w_steelPath)

    # fissures command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.fissures.cmd"), description=ts.get(f"cmd.fissures.desc")
    )
    # @discord.app_commands.choices(
    #     types=[
    #         discord.app_commands.Choice(
    #             name=ts.get("cmd.fissures.choice-fast"), value=1
    #         ),
    #         # discord.app_commands.Choice(
    #         #     name=ts.get("cmd.fissures.choice-all"), value=2
    #         # ),
    #     ]
    # )
    async def cmd_fissures(
        interact: discord.Interaction,
        # types: discord.app_commands.Choice[int],
        # is_include_railjack_node: bool = False,
    ):
        await cmd_helper(
            interact,
            key=FISSURES,
            parser_func=w_fissures,
            parser_args=(ts.get("cmd.fissures.choice-fast"), False),
            # parser_args=(types.name, is_include_railjack_node),
        )

    # deep-archimedea command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.deep-archimedea.cmd"),
        description=ts.get(f"cmd.deep-archimedea.desc"),
    )
    async def cmd_alerts(interact: discord.Interaction):
        await cmd_helper(
            interact=interact, key=ARCHIMEDEA, parser_func=w_deepArchimedea
        )

    # temporal-archimedea command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.temporal-archimedea.cmd"),
        description=ts.get(f"cmd.temporal-archimedea.desc"),
    )
    async def cmd_alerts(interact: discord.Interaction):
        await cmd_helper(
            interact=interact, key=ARCHIMEDEA, parser_func=w_temporalArchimedia
        )

    # duviriCycle command
    # @tree.command(
    #     name=ts.get(f"cmd.duviri-cycle.cmd"),
    #     description=ts.get(f"cmd.duviri-cycle.desc"),
    # )
    # async def cmd_duviri_cycle(interact: discord.Interaction):
    #     await cmd_helper(interact, key=DUVIRICYCLE, parser_func=w_duviriCycle)

    # hex calendar reward command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.calendar.cmd"),
        description=ts.get(f"cmd.calendar.desc"),
    )
    @discord.app_commands.choices(
        types=[
            discord.app_commands.Choice(
                name=ts.get("cmd.calendar.choice-prize"), value=1
            ),
            discord.app_commands.Choice(
                name=ts.get("cmd.calendar.choice-to-do"), value=2
            ),
            discord.app_commands.Choice(
                name=ts.get("cmd.calendar.choice-over"), value=3
            ),
            # discord.app_commands.Choice(
            #     name=ts.get("cmd.calendar.choice-all"), value=4
            # ),
        ]
    )
    async def cmd_calendar(
        interact: discord.Interaction, types: discord.app_commands.Choice[int]
    ):
        await cmd_helper(
            interact, key=CALENDAR, parser_func=w_calendar, parser_args=types.name
        )

    # cambion command (cambionCycle)
    # @tree.command(
    #     name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc")
    # )
    # async def cmd_cambion(interact: discord.Interaction):
    #     await cmd_helper(interact, key=CAMBIONCYCLE, parser_func=w_cambionCycle)

    # dailyDeals command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.dailyDeals.cmd"), description=ts.get(f"cmd.dailyDeals.desc")
    )
    async def cmd_dailyDeals(interact: discord.Interaction):
        await cmd_helper(interact, key=DAILYDEALS, parser_func=w_dailyDeals)

    # invasions command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.invasions.cmd"), description=ts.get(f"cmd.invasions.desc")
    )
    async def cmd_invasions(interact: discord.Interaction):
        await cmd_helper(interact, key=INVASIONS, parser_func=w_invasions)

    # voidTrader item command
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.void-traders-item.cmd"),
        description=ts.get(f"cmd.void-traders-item.desc"),
    )
    async def cmd_traders_item(interact: discord.Interaction):
        await cmd_helper(interact, key=VOIDTRADERS, parser_func=w_voidTradersItem)

    # vallisCycle command
    # @tree.command(
    #     name=ts.get(f"cmd.vallis.cmd"),
    #     description=ts.get(f"cmd.vallis.desc"),
    # )
    # async def cmd_vallis(interact: discord.Interaction):
    #     await cmd_helper(interact, key=VALLISCYCLE, parser_func=w_vallisCycle)

    # duviri-circuit-warframe
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.duviri-circuit.wf-cmd"),
        description=ts.get(f"cmd.duviri-circuit.wf-desc"),
    )
    async def cmd_circuit_wf(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=DUVIRI_ROTATION,
            parser_func=w_duviri_warframe,
            isFollowUp=True,
        )

    # duviri-circuit-incarnon
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.duviri-circuit.inc-cmd"),
        description=ts.get(f"cmd.duviri-circuit.inc-desc"),
    )
    async def cmd_circuit_inc(interact: discord.Interaction):
        await cmd_helper(
            interact,
            key=DUVIRI_ROTATION,
            parser_func=w_duviri_incarnon,
            isFollowUp=True,
        )

    # events (like thermina, fomorian)
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.events.cmd"),
        description=ts.get(f"cmd.events.desc"),
    )
    async def cmd_ingame_events(interact: discord.Interaction):
        await cmd_helper(interact, key=EVENTS, parser_func=w_events)

    # create receive complain
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_5_MIN, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.complain.cmd"), description=ts.get(f"cmd.complain.desc")
    )
    async def cmd_receive_complain(interact: discord.Interaction) -> None:
        if not await is_admin_user(interact):
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.cmd,
                cmd=f"{LOG_TYPE.cmd}.complain",
                interact=interact,
                msg="[info] cmd used, but not authorized",  # VAR
            )
            return
        # await cmd_unavailable(interact)
        await cmd_create_complain_helper(interact=interact)

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.alert-set.cmd"),
        description=ts.get(f"cmd.alert-set.desc"),
    )
    async def noti_subscribe(interact: discord.Interaction):
        await noti_subscribe_helper(interact)

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.alert-delete.cmd"),
        description=ts.get(f"cmd.alert-delete.desc"),
    )
    async def noti_unsubscribe(interact: discord.Interaction):
        await noti_unsubscribe_helper(interact)

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.descendia.cmd"),
        description=ts.get(f"cmd.descendia.desc"),
    )
    async def cmd_descendia(interact: discord.Interaction):
        await cmd_helper(interact, key=DESCENDIA, parser_func=w_descendia)


async def register_sub_cmds(tree: discord.app_commands.CommandTree, db_pool) -> None:
    # search 'warframe.market' commnad
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.market-search.cmd"),
        description=ts.get(f"cmd.market-search.desc"),
    )
    async def cmd_market_search(
        interact: discord.Interaction, item_name: str, item_rank: int = None
    ):
        """Search for an item on warframe.market."""
        await cmd_helper(
            interact,
            key=MARKET_SEARCH,
            parser_func=w_market_search,
            isFollowUp=True,
            isMarketQuery=True,
            marketQuery=(item_name, item_rank),
        )

    @cmd_market_search.autocomplete("item_name")
    async def market_search_autocomplete(
        interact: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        """Autocompletes the item name for the market search."""
        choices = [
            discord.app_commands.Choice(name=name, value=name)
            for name in get_market_item_names()
            if current.lower() in name.lower()
        ]
        return choices[:25]

    # create party
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_5_MIN, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.party.cmd"),
        description=ts.get("cmd.party.desc"),
    )
    @discord.app_commands.describe(
        title=ts.get("cmd.party.title"),
        # game_nickname="인게임 닉네임",
        game_name=ts.get(f"cmd.party.miss-types"),
        descriptions=ts.get("cmd.party.descript"),
        number_of_user=ts.get("cmd.party.nou"),
    )
    async def cmd_create_party(
        interact: discord.Interaction,
        title: str,
        # game_nickname: str,
        game_name: str,
        departure: str = "",
        descriptions: str = "(설명 없음)",
        number_of_user: int = 4,
    ) -> None:
        if not await is_admin_user(interact):
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.cmd,
                cmd=f"{LOG_TYPE.cmd}.party",
                interact=interact,
                msg="[info] cmd used, but not authorized",  # VAR
            )
            return
        await cmd_create_party_helper(
            interact=interact,
            db_pool=db_pool,
            title=title,
            number_of_user=number_of_user,
            departure=departure,
            game_name=game_name,
            description=descriptions,
        )

    # create trade article
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_5_MIN, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.trade.cmd"),
        description=ts.get("cmd.trade.desc"),
    )
    @discord.app_commands.choices(
        trade_type=[
            discord.app_commands.Choice(name=ts.get(f"cmd.trade.type-sell"), value=1),
            discord.app_commands.Choice(name=ts.get("cmd.trade.type-buy"), value=2),
        ]
    )
    @discord.app_commands.describe(
        trade_type=ts.get(f"cmd.trade.desc-trade-type"),
        item_name=ts.get(f"cmd.trade.desc-item-name"),
        item_rank=ts.get(f"cmd.trade.desc-item-rank"),
        game_nickname=ts.get(f"cmd.trade.desc-nickname"),
        price=ts.get("cmd.trade.desc-price"),
        quantity=ts.get("cmd.trade.desc-qty"),
    )
    async def cmd_create_trade(
        interact: discord.Interaction,
        trade_type: discord.app_commands.Choice[int],
        item_name: str,
        game_nickname: str = "",
        item_rank: int = 0,
        price: int = 0,
        quantity: int = 1,
    ) -> None:
        if not await is_admin_user(interact):
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.cmd,
                cmd=f"{LOG_TYPE.cmd}.trade",
                interact=interact,
                msg="[info] cmd used, but not authorized",  # VAR
            )
            return
        await cmd_create_trade_helper(
            interact=interact,
            db_pool=db_pool,
            trade_type=trade_type.name,
            game_nickname=game_nickname,
            item_name=item_name,
            item_rank=item_rank,
            price=price,
            quantity=quantity,
            # description=descriptions,
        )

    @cmd_create_trade.autocomplete("item_name")
    async def trade_item_name_autocomplete(
        interact: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        """Autocompletes the item name for the market search."""
        choices = [
            discord.app_commands.Choice(name=name, value=name)
            for name in get_market_item_names()
            if current.lower() in name.lower()
        ]
        return choices[:25]

    # warn or ban user
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.user-ban.cmd"),
        description=ts.get("cmd.user-ban.desc"),
    )
    async def cmd_user_warn(
        interact: discord.Interaction,
        member: discord.Member,
    ) -> None:
        if not await is_admin_user(interact):
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.cmd,
                cmd=f"{LOG_TYPE.cmd}.user-ban",
                interact=interact,
                msg="[info] cmd used, but not authorized",  # VAR
            )
            return

        if member.id == interact.client.user.id:
            await interact.response.send_message(
                ts.get("cmd.user-ban.self-unable"), ephemeral=True
            )
            return

        await cmd_user_warn_helper(interact=interact, user=member)


async def register_ko_cmds(tree: discord.app_commands.CommandTree, db_pool) -> None:
    # search 'warframe.market' commnad
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.market-search.cmd"),
        description=ts.get(f"cmd.market-search.desc"),
    )
    async def cmd_market_search(
        interact: discord.Interaction, 아이템_이름: str, 아이템_랭크: int = None
    ):
        """Search for an item on warframe.market."""
        await cmd_helper(
            interact,
            key=MARKET_SEARCH,
            parser_func=w_market_search,
            isFollowUp=True,
            isMarketQuery=True,
            marketQuery=(아이템_이름, 아이템_랭크),
        )

    @cmd_market_search.autocomplete("아이템_이름")
    async def market_search_autocomplete(
        interact: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        """Autocompletes the item name for the market search."""
        choices = [
            discord.app_commands.Choice(name=name, value=name)
            for name in get_market_item_names()
            if current.lower() in name.lower()
        ]
        return choices[:25]

    # create party
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_5_MIN, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.party.cmd"),
        description=ts.get("cmd.party.desc"),
    )
    @discord.app_commands.describe(
        파티_제목=ts.get("cmd.party.desc-title"),
        # game_nickname="인게임 닉네임",
        같이_할_게임이름=ts.get(f"cmd.party.desc-miss-types"),
        파티_설명=ts.get("cmd.party.desc-descript"),
        모집_인원수=ts.get("cmd.party.desc-nou"),
    )
    async def cmd_create_party(
        interact: discord.Interaction,
        파티_제목: str,
        # game_nickname: str,
        같이_할_게임이름: str,
        출발_일자: str = "",
        파티_설명: str = "(설명 없음)",
        모집_인원수: int = 4,
    ) -> None:
        if not await is_admin_user(interact):
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.cmd,
                cmd=f"{LOG_TYPE.cmd}.party",
                interact=interact,
                msg="[info] cmd used, but not authorized",  # VAR
            )
            return
        await cmd_create_party_helper(
            interact=interact,
            db_pool=db_pool,
            title=파티_제목,
            number_of_user=모집_인원수,
            game_name=같이_할_게임이름,
            departure=출발_일자,
            description=파티_설명,
        )

    # create trade article
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_5_MIN, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.trade.cmd"),
        description=ts.get("cmd.trade.desc"),
    )
    @discord.app_commands.choices(
        거래_종류=[
            discord.app_commands.Choice(name=ts.get(f"cmd.trade.type-sell"), value=1),
            discord.app_commands.Choice(name=ts.get("cmd.trade.type-buy"), value=2),
        ]
    )
    @discord.app_commands.describe(
        거래_종류=ts.get(f"cmd.trade.desc-trade-type"),
        아이템_이름=ts.get(f"cmd.trade.desc-item-name"),
        아이템_랭크=ts.get(f"cmd.trade.desc-item-rank"),
        워프레임_닉네임=ts.get(f"cmd.trade.desc-nickname"),
        개당_가격=ts.get("cmd.trade.desc-price"),
        수량=ts.get("cmd.trade.desc-qty"),
    )
    async def cmd_create_trade(
        interact: discord.Interaction,
        거래_종류: discord.app_commands.Choice[int],
        아이템_이름: str,
        워프레임_닉네임: str = "",
        아이템_랭크: int = 0,
        개당_가격: int = 0,
        수량: int = 1,
    ) -> None:
        if not await is_admin_user(interact):
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.cmd,
                cmd=f"{LOG_TYPE.cmd}.trade",
                interact=interact,
                msg="[info] cmd used, but not authorized",  # VAR
            )
            return
        await cmd_create_trade_helper(
            interact=interact,
            db_pool=db_pool,
            trade_type=거래_종류.name,
            game_nickname=워프레임_닉네임,
            item_name=아이템_이름,
            item_rank=아이템_랭크,
            price=개당_가격,
            quantity=수량,
            # description=descriptions,
        )

    @cmd_create_trade.autocomplete("아이템_이름")
    async def trade_item_name_autocomplete(
        interact: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        """Autocompletes the item name for the market search."""
        choices = [
            discord.app_commands.Choice(name=name, value=name)
            for name in get_market_item_names()
            if current.lower() in name.lower()
        ]
        return choices[:25]

    # warn or ban user
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.user-ban.cmd"),
        description=ts.get("cmd.user-ban.desc"),
    )
    @discord.app_commands.describe(
        사용자_아이디=ts.get(f"cmd.user-ban.desc-uid"),
    )
    async def cmd_user_warn(
        interact: discord.Interaction,
        사용자_아이디: discord.Member,
    ) -> None:
        if not await is_admin_user(interact):
            return

        if 사용자_아이디.id == interact.client.user.id:
            await interact.response.send_message(
                ts.get("cmd.user-ban.self-unable"), ephemeral=True
            )
            return

        await cmd_user_warn_helper(interact=interact, user=사용자_아이디)
