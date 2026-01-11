import discord
from discord.ext import commands
from discord import app_commands

from src.translator import ts
from src.constants.keys import (
    # cooldown var
    COOLDOWN_DEFAULT,
    # docs file
    HELP_FILE_LOC,
    ANNOUNCE_FILE_LOC,
    PATCHNOTE_FILE_LOC,
    POLICY_FILE_LOC,
    # cmd obj
    ALERTS,
    NEWS,
    CETUSCYCLE,
    SORTIE,
    ARCHONHUNT,
    VOIDTRADERS,
    STEELPATH,
    ARCHIMEDEA,
    # DUVIRICYCLE,
    FISSURES,
    CALENDAR,
    CAMBIONCYCLE,
    DAILYDEALS,
    INVASIONS,
    MARKET_SEARCH,
    VALLISCYCLE,
    DUVIRI_ROTATION,
    EVENTS,
    DESCENDIA,
)
from src.utils.cmd_helper import cmd_helper, cmd_helper_txt
from src.commands.noti_channel import noti_subscribe_helper, noti_unsubscribe_helper

from src.parser.alerts import w_alerts
from src.parser.news import w_news
from src.parser.cetusCycle import w_cetusCycle
from src.parser.sortie import w_sortie
from src.parser.archonHunt import w_archonHunt
from src.parser.voidTraders import w_voidTraders, w_voidTradersItem
from src.parser.steelPath import w_steelPath  # duviri
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


class GeneralCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # help command
    @app_commands.command(name="help", description="cmd.help.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_help(
        self, interact: discord.Interaction, developer_options: bool = False
    ):
        await cmd_helper_txt(
            interact, file_name=HELP_FILE_LOC, isPrivateMsg=developer_options
        )

    # announcement command
    @app_commands.command(name="announcement", description="cmd.announcement.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_announcement(
        self, interact: discord.Interaction, developer_options: bool = False
    ):
        await cmd_helper_txt(
            interact, file_name=ANNOUNCE_FILE_LOC, isPrivateMsg=developer_options
        )

    # patch-note command
    @app_commands.command(name="patch-note", description="cmd.patch-note.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_patch_note(
        self, interact: discord.Interaction, developer_options: bool = False
    ):
        await cmd_helper_txt(
            interact, file_name=PATCHNOTE_FILE_LOC, isPrivateMsg=developer_options
        )

    # privacy-policy command
    @app_commands.command(name="privacy-policy", description="cmd.privacy-policy.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_privacy_policy(
        self, interact: discord.Interaction, developer_options: bool = False
    ):
        await cmd_helper_txt(
            interact, file_name=POLICY_FILE_LOC, isPrivateMsg=developer_options
        )

    # news command
    @app_commands.command(name="news", description="cmd.news.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_news(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact, key=NEWS, parser_func=w_news, isPrivateMsg=developer_options
        )

    # alerts command
    @app_commands.command(name="alerts", description="cmd.alerts.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_alerts(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact=interact,
            key=ALERTS,
            parser_func=w_alerts,
            isPrivateMsg=developer_options,
        )

    # cetus command (cetusCycle)
    @app_commands.command(name="cetus", description="cmd.cetus.desc")
    async def cmd_cetus(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact=interact,
            key=CETUSCYCLE,
            parser_func=w_cetusCycle,
            isPrivateMsg=developer_options,
        )

    # sortie command
    @app_commands.command(name="sortie", description="cmd.sortie.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_sortie(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact, key=SORTIE, parser_func=w_sortie, isPrivateMsg=developer_options
        )

    # archon hunt command
    @app_commands.command(name="archon-hunt", description="cmd.archon-hunt.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_archon_hunt(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=ARCHONHUNT,
            parser_func=w_archonHunt,
            isPrivateMsg=developer_options,
        )

    # void traders command
    @app_commands.command(name="void-traders", description="cmd.void-traders.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_voidTraders(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            isFollowUp=True,
            key=VOIDTRADERS,
            parser_func=w_voidTraders,
            isPrivateMsg=developer_options,
        )

    # steel path reward command
    @app_commands.command(
        name="steel-path-reward", description="cmd.steel-path-reward.desc"
    )
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_steel_reward(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=STEELPATH,
            parser_func=w_steelPath,
            isPrivateMsg=developer_options,
        )

    # fissures command
    @app_commands.command(name="fissures", description="cmd.fissures.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
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
        self,
        interact: discord.Interaction,
        # types: discord.app_commands.Choice[int],
        # is_include_railjack_node: bool = False,
        developer_options: bool = True,
    ):
        await cmd_helper(
            interact,
            key=FISSURES,
            parser_func=w_fissures,
            parser_args=(ts.get("cmd.fissures.choice-fast"), False),
            # parser_args=(types.name, is_include_railjack_node),
            isPrivateMsg=developer_options,
        )

    # deep-archimedea command
    @app_commands.command(
        name="deep-archimedea", description="cmd.deep-archimedea.desc"
    )
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_deep_archimedea(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact=interact,
            key=ARCHIMEDEA,
            parser_func=w_deepArchimedea,
            isPrivateMsg=developer_options,
        )

    # temporal-archimedea command
    @app_commands.command(
        name="temporal-archimedea",
        description=ts.get(f"cmd.temporal-archimedea.desc"),
    )
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_temporal_archimedea(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact=interact,
            key=ARCHIMEDEA,
            parser_func=w_temporalArchimedia,
            isPrivateMsg=developer_options,
        )

    # duviriCycle command
    # @tree.command(
    #     name=ts.get(f"cmd.duviri-cycle.cmd"),
    #     description=ts.get(f"cmd.duviri-cycle.desc"),
    # )
    # async def cmd_duviri_cycle(self,interact: discord.Interaction):
    #     await cmd_helper(interact, key=DUVIRICYCLE, parser_func=w_duviriCycle)

    # 1999 calendar
    @app_commands.command(name="calendar", description="cmd.calendar.desc")
    @app_commands.choices(
        types=[
            app_commands.Choice(name="Prize", value=1),
            app_commands.Choice(name="To-Do", value=2),
            app_commands.Choice(name="Over", value=3),
        ]
    )
    @app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_calendar(
        self,
        interact: discord.Interaction,
        types: app_commands.Choice[int],
        developer_options: bool = True,
    ):
        await cmd_helper(
            interact,
            key=CALENDAR,
            parser_func=w_calendar,
            parser_args=ts.get(f"cmd.calendar.choice-{types.name.lower()}"),
            isPrivateMsg=developer_options,
        )

    # cambion command (cambionCycle)
    @app_commands.command(name="cambion", description=f"cmd.cambion.desc")
    async def cmd_cambion(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=CAMBIONCYCLE,
            parser_func=w_cambionCycle,
            isPrivateMsg=developer_options,
        )

    # dailyDeals command
    @app_commands.command(name="dailydeals", description="cmd.dailydeals.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_dailydeals(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=DAILYDEALS,
            parser_func=w_dailyDeals,
            isPrivateMsg=developer_options,
        )

    # invasions command
    @app_commands.command(name="invasions", description="cmd.invasions.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_invasions(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=INVASIONS,
            parser_func=w_invasions,
            isPrivateMsg=developer_options,
        )

    # voidTrader item command
    @app_commands.command(
        name="void-traders-item", description="cmd.void-traders-item.desc"
    )
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_traders_item(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=VOIDTRADERS,
            parser_func=w_voidTradersItem,
            isPrivateMsg=developer_options,
        )

    # search 'warframe.market' commnad
    @app_commands.command(name="market-search", description="cmd.market-search.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @app_commands.describe(
        item_name="cmd.market-search.desc-item-name",
        item_rank="cmd.market-search.desc-item-rank",
    )
    async def cmd_market_search(
        self,
        interact: discord.Interaction,
        item_name: str,
        item_rank: int = None,
        developer_options: bool = True,
    ):
        await cmd_helper(
            interact,
            key=MARKET_SEARCH,
            parser_func=w_market_search,
            isFollowUp=True,
            isMarketQuery=True,
            marketQuery=(item_name, item_rank),
            isPrivateMsg=developer_options,
        )

    @cmd_market_search.autocomplete("item_name")
    async def market_search_autocomplete(
        self, interact: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        """Autocompletes the item name for the market search."""
        choices = [
            discord.app_commands.Choice(name=name, value=name)
            for name in get_market_item_names()
            if current.lower() in name.lower()
        ]
        return choices[:25]

    # vallisCycle command
    @app_commands.command(name="vallis", description="cmd.vallis.desc")
    async def cmd_vallis(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=VALLISCYCLE,
            parser_func=w_vallisCycle,
            isPrivateMsg=developer_options,
        )

    # duviri-circuit-warframe
    @app_commands.command(
        name="duviri-wf",
        description="cmd.duviri-circuit.wf-desc",
        extras={"key": "cmd.duviri-circuit.wf-cmd"},
    )
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_circuit_wf(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=DUVIRI_ROTATION,
            parser_func=w_duviri_warframe,
            isFollowUp=True,
            isPrivateMsg=developer_options,
        )

    # duviri-circuit-incarnon
    @app_commands.command(
        name="duviri-incarnon",
        description="cmd.duviri-circuit.inc-desc",
        extras={"key": "cmd.duviri-circuit.inc-cmd"},
    )
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_circuit_inc(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=DUVIRI_ROTATION,
            parser_func=w_duviri_incarnon,
            isFollowUp=True,
            isPrivateMsg=developer_options,
        )

    # events (like thermina, fomorian)
    @app_commands.command(name="events", description="cmd.events.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_ingame_events(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact, key=EVENTS, parser_func=w_events, isPrivateMsg=developer_options
        )

    # setup alert
    @app_commands.command(name="alert-set", description="cmd.alert-set.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def noti_subscribe(self, interact: discord.Interaction):
        await noti_subscribe_helper(interact)

    @app_commands.command(name="alert-delete", description="cmd.alert-delete.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def noti_unsubscribe(self, interact: discord.Interaction):
        await noti_unsubscribe_helper(interact)

    @app_commands.command(name="descendia", description="cmd.descendia.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_descendia(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper(
            interact,
            key=DESCENDIA,
            parser_func=w_descendia,
            isPrivateMsg=developer_options,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCommands(bot))
