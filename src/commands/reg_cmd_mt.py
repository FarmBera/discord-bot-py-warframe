import discord

from src.translator import ts
from src.commands.cmd_maintenance import cmd_helper_maintenance


async def register_maintenance_commands(tree: discord.app_commands.CommandTree) -> None:
    @tree.command(
        name=ts.get(f"cmd.help.cmd"), description=f"{ts.get('cmd.help.desc')}"
    )
    async def cmd_help(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.announcement.cmd"),
        description=f"{ts.get('cmd.announcement.desc')}",
    )
    async def cmd_announcement(
        interact: discord.Interaction, is_user_view_only: bool = True
    ):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.patch-note.cmd"),
        description=f"{ts.get('cmd.patch-note.desc')}",
    )
    async def cmd_patch_note(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.privacy-policy.cmd"),
        description=f"{ts.get('cmd.privacy-policy.desc')}",
    )
    async def cmd_privacy_policy(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(name=ts.get(f"cmd.news.cmd"), description=ts.get(f"cmd.news.desc"))
    async def cmd_news(interact: discord.Interaction, number_of_news: int = 20):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.alerts.cmd"), description=ts.get(f"cmd.alerts.desc")
    )
    async def cmd_alerts(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    # @tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
    # async def cmd_cetus(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc")
    )
    async def cmd_sortie(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.archon-hunt.cmd"), description=ts.get(f"cmd.archon-hunt.desc")
    )
    async def cmd_archon_hunt(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.void-traders.cmd"),
        description=ts.get(f"cmd.void-traders.desc"),
    )
    async def cmd_voidTraders(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    # @tree.command(
    #     name=ts.get(f"cmd.steel-path-reward.cmd"),
    #     description=ts.get(f"cmd.steel-path-reward.desc"),
    # )
    # async def cmd_steel_reward(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

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
        await cmd_helper_maintenance(interact)

    # @tree.command(
    #     name=ts.get(f"cmd.duviri-cycle.cmd"),
    #     description=ts.get(f"cmd.duviri-cycle.desc"),
    # )
    # async def cmd_duviri_cycle(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

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
        await cmd_helper_maintenance(interact)

    # @tree.command(
    #     name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc")
    # )
    # async def cmd_cambion(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.dailyDeals.cmd"), description=ts.get(f"cmd.dailyDeals.desc")
    )
    async def cmd_dailyDeals(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.invasions.cmd"), description=ts.get(f"cmd.invasions.desc")
    )
    async def cmd_invasions(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.void-traders-item.cmd"),
        description=ts.get(f"cmd.void-traders-item.desc"),
    )
    async def cmd_traders_item(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.market-search.cmd"),
        description=ts.get(f"cmd.market-search.desc"),
    )
    async def search_market(interact: discord.Interaction, item_name: str):
        await cmd_helper_maintenance(interact)

    @tree.command(
        name=ts.get(f"cmd.market-help.cmd"),
        description=ts.get(f"cmd.market-help.desc"),
    )
    async def cmd_market_help(interact: discord.Interaction):
        await cmd_helper_maintenance(interact)

    # @tree.command(
    #     name=ts.get(f"cmd.vallis.cmd"),
    #     description=ts.get(f"cmd.vallis.desc"),
    # )
    # async def cmd_vallis(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

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
        await cmd_helper_maintenance(interact)
