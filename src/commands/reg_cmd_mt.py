import discord

from src.translator import ts
from src.constants.keys import (
    # cooldown
    COOLDOWN_DEFAULT,
    COOLDOWN_CREATE,
    # docs
    HELP_FILE_LOC,
    ANNOUNCE_FILE_LOC,
    POLICY_FILE_LOC,
)

from src.commands.cmd_helper_text import cmd_helper_txt
from src.commands.cmd_maintenance import cmd_helper_maintenance


async def register_maintenance_commands(tree: discord.app_commands.CommandTree) -> None:
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.help.cmd"), description=f"{ts.get('cmd.help.desc')}"
    )
    async def cmd_help(interact: discord.Interaction, is_public_msg: bool = False):
        await cmd_helper_txt(interact, file_name=HELP_FILE_LOC)

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
        await cmd_helper_txt(interact, file_name=ANNOUNCE_FILE_LOC)

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
        await cmd_helper_maintenance(interact, "patch-notee")

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
        await cmd_helper_txt(interact, file_name=POLICY_FILE_LOC)

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(name=ts.get(f"cmd.news.cmd"), description=ts.get(f"cmd.news.desc"))
    async def cmd_news(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "news")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.alerts.cmd"), description=ts.get(f"cmd.alerts.desc")
    )
    async def cmd_alerts(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "alerts")

    # @tree.command(name=ts.get(f"cmd.cetus.cmd"), description=ts.get(f"cmd.cetus.desc"))
    # async def cmd_cetus(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.sortie.cmd"), description=ts.get(f"cmd.sortie.desc")
    )
    async def cmd_sortie(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "sortie")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.archon-hunt.cmd"), description=ts.get(f"cmd.archon-hunt.desc")
    )
    async def cmd_archon_hunt(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "archon-hunt")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.void-traders.cmd"),
        description=ts.get(f"cmd.void-traders.desc"),
    )
    async def cmd_voidTraders(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "voidtrader")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.steel-path-reward.cmd"),
        description=ts.get(f"cmd.steel-path-reward.desc"),
    )
    async def cmd_steel_reward(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "steel-path-reward")

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
        await cmd_helper_maintenance(interact, "fissures")

    # @tree.command(
    #     name=ts.get(f"cmd.duviri-cycle.cmd"),
    #     description=ts.get(f"cmd.duviri-cycle.desc"),
    # )
    # async def cmd_duviri_cycle(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

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
        await cmd_helper_maintenance(interact, "hexcal")

    # @tree.command(
    #     name=ts.get(f"cmd.cambion.cmd"), description=ts.get(f"cmd.cambion.desc")
    # )
    # async def cmd_cambion(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.dailyDeals.cmd"), description=ts.get(f"cmd.dailyDeals.desc")
    )
    async def cmd_dailyDeals(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "dailydeals")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.invasions.cmd"), description=ts.get(f"cmd.invasions.desc")
    )
    async def cmd_invasions(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "invasions")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.void-traders-item.cmd"),
        description=ts.get(f"cmd.void-traders-item.desc"),
    )
    async def cmd_traders_item(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "voidtrader-items")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.market-search.cmd"),
        description=ts.get(f"cmd.market-search.desc"),
    )
    async def cmd_market_search(interact: discord.Interaction, item_name: str):
        await cmd_helper_maintenance(interact, f"market-search:{item_name}")

    # @tree.command(
    #     name=ts.get(f"cmd.vallis.cmd"),
    #     description=ts.get(f"cmd.vallis.desc"),
    # )
    # async def cmd_vallis(interact: discord.Interaction):
    #     await cmd_helper_maintenance(interact)

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_CREATE, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.party.cmd"),
        description=ts.get("cmd.party.desc"),
    )
    @discord.app_commands.describe(
        title=ts.get("cmd.party.title"),
        # game_nickname="인게임 닉네임",
        game_type=ts.get(f"cmd.party.miss-types"),
        descriptions=ts.get("cmd.party.descript"),
        number_of_user=ts.get("cmd.party.nou"),
    )
    async def cmd_create_party(
        interact: discord.Interaction,
        title: str,
        # game_nickname: str,
        game_type: str,
        descriptions: str = "(설명 없음)",
        number_of_user: int = 4,
    ) -> None:
        await cmd_helper_maintenance(
            interact, f"party::{title}::{game_type}::{descriptions}:{number_of_user}"
        )

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_CREATE, key=lambda i: (i.guild_id, i.user.id)
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
        await cmd_helper_maintenance(
            interact,
            f"trade::{trade_type}::{item_name}::{game_nickname}::{item_rank}::{price}::{item_rank}::{quantity}",
        )

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.duviri-circuit.wf-cmd"),
        description=ts.get(f"cmd.duviri-circuit.wf-desc"),
    )
    async def cmd_circuit_wf(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "duviri-circuit")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.duviri-circuit.inc-cmd"),
        description=ts.get(f"cmd.duviri-circuit.inc-desc"),
    )
    async def cmd_circuit_inc(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "duviri-incarnon")

    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.events.cmd"),
        description=ts.get(f"cmd.events.desc"),
    )
    async def cmd_ingame_events(interact: discord.Interaction):
        await cmd_helper_maintenance(interact, "events")

    # create receive complain
    @discord.app_commands.checks.cooldown(
        1, COOLDOWN_CREATE, key=lambda i: (i.guild_id, i.user.id)
    )
    @tree.command(
        name=ts.get(f"cmd.complain.cmd"), description=ts.get(f"cmd.complain.desc")
    )
    async def cmd_receive_complain(
        interact: discord.Interaction,
    ) -> None:
        await cmd_helper_maintenance(interact, "complain")
