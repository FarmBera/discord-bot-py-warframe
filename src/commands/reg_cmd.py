import discord
import sqlite3

from src.translator import ts
from src.commands.cmd_helper import cmd_helper
from src.commands.cmd_helper_text import cmd_helper_txt
from src.commands.cmd_create_thread import cmd_create_thread_helper


from src.constants.keys import (
    # docs file
    HELP_FILE_LOC,
    ANNOUNCE_FILE_LOC,
    PATCHNOTE_FILE_LOC,
    POLICY_FILE_LOC,
    MARKET_HELP_FILE,
    # cmd obj
    ALERTS,
    NEWS,
    CETUSCYCLE,
    SORTIE,
    ARCHONHUNT,
    VOIDTRADERS,
    STEELPATH,
    DUVIRICYCLE,
    FISSURES,
    CALENDAR,
    CAMBIONCYCLE,
    DAILYDEALS,
    INVASIONS,
    MARKET_SEARCH,
    VALLISCYCLE,
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
from src.parser.calendar import w_calendar
from src.parser.cambionCycle import w_cambionCycle
from src.parser.dailyDeals import w_dailyDeals
from src.parser.invasions import w_invasions
from src.parser.vallisCycle import w_vallisCycle
from src.parser.marketsearch import w_market_search


async def register_main_commands(
    tree: discord.app_commands.CommandTree, db_conn: sqlite3.Connection
) -> None:

    # help command
    @tree.command(
        name=ts.get(f"cmd.help.cmd"), description=f"{ts.get('cmd.help.desc')}"
    )
    async def cmd_help(interact: discord.Interaction):
        await cmd_helper_txt(interact, file_name=HELP_FILE_LOC)

    # announcement command
    @tree.command(
        name=ts.get(f"cmd.announcement.cmd"),
        description=f"{ts.get('cmd.announcement.desc')}",
    )
    async def cmd_announcement(
        interact: discord.Interaction, is_user_view_only: bool = True
    ):
        # TODO: only I can send public messages
        await cmd_helper_txt(
            interact,
            file_name=ANNOUNCE_FILE_LOC,
            isUserViewOnly=True,
        )

    # patch-note command
    @tree.command(
        name=ts.get(f"cmd.patch-note.cmd"),
        description=f"{ts.get('cmd.patch-note.desc')}",
    )
    async def cmd_patch_note(interact: discord.Interaction):
        await cmd_helper_txt(interact, file_name=PATCHNOTE_FILE_LOC)

    # privacy-policy command
    @tree.command(
        name=ts.get(f"cmd.privacy-policy.cmd"),
        description=f"{ts.get('cmd.privacy-policy.desc')}",
    )
    async def cmd_privacy_policy(interact: discord.Interaction):
        await cmd_helper_txt(interact, file_name=POLICY_FILE_LOC)

    # news command
    @tree.command(name=ts.get(f"cmd.news.cmd"), description=ts.get(f"cmd.news.desc"))
    async def cmd_news(interact: discord.Interaction, number_of_news: int = 20):
        await cmd_helper(
            interact, key=NEWS, parser_func=w_news, parser_args=number_of_news
        )

    # alerts command
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
    @tree.command(
        name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc")
    )
    async def cmd_sortie(interact: discord.Interaction):
        await cmd_helper(interact, key=SORTIE, parser_func=w_sortie)

    # archon hunt command
    @tree.command(
        name=ts.get(f"cmd.archon-hunt.cmd"), description=ts.get(f"cmd.archon-hunt.desc")
    )
    async def cmd_archon_hunt(interact: discord.Interaction):
        await cmd_helper(interact, key=ARCHONHUNT, parser_func=w_archonHunt)

    # void traders command
    @tree.command(
        name=ts.get(f"cmd.void-traders.cmd"),
        description=ts.get(f"cmd.void-traders.desc"),
    )
    async def cmd_voidTraders(interact: discord.Interaction):
        await cmd_helper(interact, key=VOIDTRADERS, parser_func=w_voidTraders)

    # steel path reward command
    # @tree.command(
    #     name=ts.get(f"cmd.steel-path-reward.cmd"),
    #     description=ts.get(f"cmd.steel-path-reward.desc"),
    # )
    # async def cmd_steel_reward(interact: discord.Interaction):
    #     await cmd_helper(interact, key=STEELPATH, parser_func=w_steelPath)

    # fissures command
    @tree.command(
        name=ts.get(f"cmd.fissures.cmd"), description=ts.get(f"cmd.fissures.desc")
    )
    @discord.app_commands.choices(
        types=[
            discord.app_commands.Choice(
                name=ts.get("cmd.fissures.choice-fast"), value=1
            ),
            discord.app_commands.Choice(
                name=ts.get("cmd.fissures.choice-all"), value=2
            ),
        ]
    )
    async def cmd_fissures(
        interact: discord.Interaction,
        types: discord.app_commands.Choice[int],
        is_include_railjack_node: bool = False,
    ):
        await cmd_helper(
            interact,
            key=FISSURES,
            parser_func=w_fissures,
            parser_args=(types.name, is_include_railjack_node),
        )

    # duviriCycle command
    # @tree.command(
    #     name=ts.get(f"cmd.duviri-cycle.cmd"),
    #     description=ts.get(f"cmd.duviri-cycle.desc"),
    # )
    # async def cmd_duviri_cycle(interact: discord.Interaction):
    #     await cmd_helper(interact, key=DUVIRICYCLE, parser_func=w_duviriCycle)

    # hex calendar reward command
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
            discord.app_commands.Choice(
                name=ts.get("cmd.calendar.choice-all"), value=4
            ),
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
    @tree.command(
        name=ts.get(f"cmd.dailyDeals.cmd"), description=ts.get(f"cmd.dailyDeals.desc")
    )
    async def cmd_dailyDeals(interact: discord.Interaction):
        await cmd_helper(interact, key=DAILYDEALS, parser_func=w_dailyDeals)

    # invasions command
    @tree.command(
        name=ts.get(f"cmd.invasions.cmd"), description=ts.get(f"cmd.invasions.desc")
    )
    async def cmd_invasions(interact: discord.Interaction):
        await cmd_helper(interact, key=INVASIONS, parser_func=w_invasions)

    # voidTrader item command
    @tree.command(
        name=ts.get(f"cmd.void-traders-item.cmd"),
        description=ts.get(f"cmd.void-traders-item.desc"),
    )
    async def cmd_traders_item(interact: discord.Interaction):
        await cmd_helper(interact, key=VOIDTRADERS, parser_func=w_voidTradersItem)

    # search 'warframe.market' commnad
    @tree.command(
        name=ts.get(f"cmd.market-search.cmd"),
        description=ts.get(f"cmd.market-search.desc"),
    )
    async def cmd_market_search(interact: discord.Interaction, item_name: str):
        await cmd_helper(
            interact,
            key=MARKET_SEARCH,
            parser_func=w_market_search,
            isMarketQuery=True,
            marketQuery=item_name,
        )

    # 'warframe.market' search guide commnad
    @tree.command(
        name=ts.get(f"cmd.market-help.cmd"),
        description=ts.get(f"cmd.market-help.desc"),
    )
    async def cmd_market_help(interact: discord.Interaction):
        await cmd_helper_txt(interact, MARKET_HELP_FILE)

    # vallisCycle command
    # @tree.command(
    #     name=ts.get(f"cmd.vallis.cmd"),
    #     description=ts.get(f"cmd.vallis.desc"),
    # )
    # async def cmd_vallis(interact: discord.Interaction):
    #     await cmd_helper(interact, key=VALLISCYCLE, parser_func=w_vallisCycle)

    @tree.command(
        name=ts.get(f"cmd.party.cmd"),
        description=ts.get("cmd.party.desc"),
    )
    @discord.app_commands.describe(
        title=ts.get("cmd.party.title"),
        # game_nickname="인게임 닉네임",
        mission_type=ts.get(f"cmd.party.miss-types"),
        descriptions=ts.get("cmd.party.descript"),
        number_of_user=ts.get("cmd.party.nou"),
    )
    async def cmd_create_thread(
        interact: discord.Interaction,
        title: str,
        # game_nickname: str,
        mission_type: str,
        descriptions: str = None,
        number_of_user: int = 4,
    ) -> None:
        await cmd_create_thread_helper(
            interact=interact,
            db_conn=db_conn,
            title=title,
            number_of_user=number_of_user,
            mission_type=mission_type,
            description=descriptions,
        )
