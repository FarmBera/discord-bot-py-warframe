import discord
from discord.ext import commands
from discord import app_commands

from src.translator import ts
from config.config import LOG_TYPE
from src.constants.keys import (
    # cooldown var
    COOLDOWN_DEFAULT,
    COOLDOWN_CREATE,
    COOLDOWN_5_MIN,
    # docs
    HELP_FILE_LOC,
    ANNOUNCE_FILE_LOC,
    POLICY_FILE_LOC,
)
from src.commands.cmd_helper_text import cmd_helper_txt
from src.commands.cmd_maintenance import cmd_helper_maintenance
from src.parser.marketsearch import get_market_item_names


class MaintenanceCommands(commands.Cog):
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
        await cmd_helper_txt(interact, file_name=HELP_FILE_LOC)

    # announcement command
    @app_commands.command(name="announcement", description="cmd.announcement.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_announcement(
        self, interact: discord.Interaction, developer_options: bool = False
    ):
        await cmd_helper_txt(interact, file_name=ANNOUNCE_FILE_LOC)

    # patch-note command
    @app_commands.command(name="patch-note", description="cmd.patch-note.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_patch_note(
        self, interact: discord.Interaction, developer_options: bool = False
    ):
        await cmd_helper_maintenance(interact, "patch-note")

    # privacy-policy command
    @app_commands.command(name="privacy-policy", description="cmd.privacy-policy.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_privacy_policy(
        self, interact: discord.Interaction, developer_options: bool = False
    ):
        await cmd_helper_txt(interact, file_name=POLICY_FILE_LOC)

    # news command
    @app_commands.command(name="news", description="cmd.news.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_news(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "news")

    # alerts command
    @app_commands.command(name="alerts", description="cmd.alerts.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_alerts(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "alerts")

    # cetus command (cetusCycle)
    # @app_commands.command(name="cetus", description="cmd.cetus.desc")
    # async def cmd_cetus(self,interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact,'cetusCycle')

    # sortie command
    @app_commands.command(name="sortie", description="cmd.sortie.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_sortie(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "sortie")

    # archon hunt command
    @app_commands.command(name="archon-hunt", description="cmd.archon-hunt.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_archon_hunt(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "archon-hunt")

    # void traders command
    @app_commands.command(name="void-traders", description="cmd.void-traders.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_voidTraders(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "voidTraders")

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
        await cmd_helper_maintenance(interact, "steelPath-reward")

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
        await cmd_helper_maintenance(interact, "fissures")

    # deep-archimedea command
    @app_commands.command(
        name="deep-archimedea", description="cmd.deep-archimedea.desc"
    )
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_alerts(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "deep-archimedea")

    # temporal-archimedea command
    @app_commands.command(
        name="temporal-archimedea",
        description=ts.get(f"cmd.temporal-archimedea.desc"),
    )
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_alerts(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "temporal-archimedea")

    # duviriCycle command
    # @tree.command(
    #     name=ts.get(f"cmd.duviri-cycle.cmd"),
    #     description=ts.get(f"cmd.duviri-cycle.desc"),
    # )
    # async def cmd_duviri_cycle(self,interact: discord.Interaction):
    #     await cmd_helper(interact, key=DUVIRICYCLE, parser_func=w_duviriCycle)

    # 1999 달력
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
        await cmd_helper_maintenance(interact, "calendar")

    # cambion command (cambionCycle)
    # @tree.command(
    #     name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc")
    # )
    # async def cmd_cambion(self,interact: discord.Interaction):
    #     await cmd_helper(interact, key=CAMBIONCYCLE, parser_func=w_cambionCycle)

    # dailyDeals command
    @app_commands.command(name="dailydeals", description="cmd.dailydeals.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_dailydeals(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "dailydeals")

    # invasions command
    @app_commands.command(name="invasions", description="cmd.invasions.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_invasions(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "invasions")

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
        await cmd_helper_maintenance(interact, "voidTraders-item")

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
        await cmd_helper_maintenance(interact, "market-search")

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
    # @tree.command(
    #     name=ts.get(f"cmd.vallis.cmd"),
    #     description=ts.get(f"cmd.vallis.desc"),
    # )
    # async def cmd_vallis(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact, "vallisCycle")

    # create party
    @app_commands.command(name="party", description="cmd.party.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_5_MIN, key=lambda i: (i.guild_id, i.user.id)
    )
    @discord.app_commands.describe(
        title="cmd.party.title",
        departure="cmd.party.date-placeholder",
        game_name="cmd.party.miss-types",
        descriptions="cmd.party.descript",
        number_of_user="cmd.party.nou",
    )
    async def cmd_create_party(
        self,
        interact: discord.Interaction,
        title: str,
        game_name: str,
        departure: str = None,
        descriptions: str = "(설명 없음)",
        number_of_user: int = 4,
    ) -> None:
        await cmd_helper_maintenance(interact, "party")

    # create trade article
    @app_commands.command(name="trade", description="cmd.trade.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_5_MIN, key=lambda i: (i.guild_id, i.user.id)
    )
    @discord.app_commands.choices(
        trade_type=[
            discord.app_commands.Choice(name=ts.get("cmd.trade.type-sell"), value=1),
            discord.app_commands.Choice(name=ts.get("cmd.trade.type-buy"), value=2),
        ]
    )
    @discord.app_commands.describe(
        trade_type="cmd.trade.desc-trade-type",
        item_name="cmd.trade.desc-item-name",
        item_rank="cmd.trade.desc-item-rank",
        game_nickname="cmd.trade.desc-nickname",
        price="cmd.trade.desc-price",
        quantity="cmd.trade.desc-qty",
    )
    async def cmd_create_trade(
        self,
        interact: discord.Interaction,
        trade_type: discord.app_commands.Choice[int],
        item_name: str,
        game_nickname: str = "",
        item_rank: int = 0,
        price: int = 0,
        quantity: int = 1,
    ) -> None:
        await cmd_helper_maintenance(interact, "trade")

    @cmd_create_trade.autocomplete("item_name")
    async def trade_item_name_autocomplete(
        self,
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
        await cmd_helper_maintenance(interact, "duviri-warframe")

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
        await cmd_helper_maintenance(interact, "duviri-incarnon")

    # events (like thermina, fomorian)
    @app_commands.command(name="events", description="cmd.events.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_ingame_events(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "events")

    # receive complain
    @app_commands.command(name="complain", description="cmd.complain.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_5_MIN, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_receive_complain(self, interact: discord.Interaction) -> None:
        await cmd_helper_maintenance(interact, "complain")

    # setup alert
    @app_commands.command(name="alert-set", description="cmd.alert-set.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def noti_subscribe(self, interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "noti-set")

    @app_commands.command(name="alert-delete", description="cmd.alert-delete.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def noti_unsubscribe(self, interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "noti-delete")

    @app_commands.command(name="descendia", description="cmd.descendia.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_descendia(
        self, interact: discord.Interaction, developer_options: bool = True
    ):
        await cmd_helper_maintenance(interact, "descendia")

    # warn or ban user
    @app_commands.command(name="user-ban", description="cmd.user-ban.desc")
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    async def cmd_user_warn(
        interact: discord.Interaction,
        member: discord.Member,
    ) -> None:
        await cmd_helper_maintenance(interact, "user-ban")


async def setup(bot: commands.Bot):
    await bot.add_cog(MaintenanceCommands(bot))
