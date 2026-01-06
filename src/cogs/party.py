import discord
from discord import app_commands
from discord.ext import commands

from config.config import LOG_TYPE
from src.translator import ts
from src.constants.keys import LFG_WEBHOOK_NAME, COOLDOWN_DEFAULT
from src.utils.data_manager import CHANNELS
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.permission import is_valid_guild, is_banned_user
from src.services.party_service import PartyService
from src.views.party_view import PartyView, build_party_embed, pf, MIN_SIZE, MAX_SIZE


class PartyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="party", description="cmd.party.desc")
    @app_commands.checks.cooldown(
        1, COOLDOWN_DEFAULT, key=lambda i: (i.guild_id, i.user.id)
    )
    @app_commands.describe(
        title="cmd.party.desc-title",
        game_name="cmd.party.desc-game-name",
        departure="cmd.party.desc-departure",
        descriptions="cmd.party.desc-descriptions",
        number_of_user="cmd.party.desc-number-of-user",
   )
    async def cmd_create_party(
        self,
        interact: discord.Interaction,
        title: str,
        game_name: str,
        departure: str = None,
        descriptions: str = ts.get(f"{pf}c-no-desc"),
        number_of_user: int = 4,
    ):
        await interact.response.defer(ephemeral=True)
        await save_log(
            pool=interact.client.db,
            type="cmd",
            cmd=f"cmd.party",
            interact=interact,
            msg="cmd used",  # VAR
            obj=f"T:{title}\nTYPE:{game_name}\nDEPT:{departure}\nDESC:{descriptions}\n{number_of_user}",
        )

        if not await is_valid_guild(interact, isFollowUp=True):
            return

        if await is_banned_user(interact, isFollowUp=True):
            return

        target_channel = self.bot.get_channel(CHANNELS["party"])
        if not target_channel:
            await interact.followup.send(ts.get(f"{pf}not-found-ch"), ephemeral=True)
            return

        if number_of_user < MIN_SIZE:
            await interact.followup.send(
                ts.get(f"{pf}pt-low").format(num=MIN_SIZE),
                ephemeral=True,
            )
            number_of_user = 4

        elif number_of_user > MAX_SIZE:
            await interact.followup.send(
                ts.get(f"{pf}pt-high").format(num=MAX_SIZE),
                ephemeral=True,
            )
            number_of_user = MAX_SIZE

        # create party & insert into db
        try:
            party_id = await PartyService.create_party(
                self.bot.db,
                interact.user.id,
                interact.user.display_name,
                interact.user.mention,
                title,
                game_name,
                departure,
                number_of_user,
                descriptions,
            )
        except Exception as e:
            await interact.followup.send(ts.get("cmd.err-db"), ephemeral=True)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.err,
                cmd=f"cmd.party",
                interact=interact,
                msg="cmd used",  # VAR
                obj=f"T:{title}\nTYPE:{game_name}\nDEPT:{departure}\nDESC:{descriptions}\n{number_of_user}",
            )
            return

        # create webhook & threads
        try:
            webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(webhooks, name=LFG_WEBHOOK_NAME)
            if not webhook:
                webhook = await target_channel.create_webhook(name=LFG_WEBHOOK_NAME)

            thread_starter_msg = await webhook.send(
                content=ts.get(f"{pf}created-party"),
                username=interact.user.display_name,
                avatar_url=interact.user.display_avatar.url,
                wait=True,
            )
            thread = await thread_starter_msg.create_thread(
                name=f"[{game_name}] {title}",
                reason=f"{interact.user.display_name} user created party",
            )

            # create embed & view
            embed = await build_party_embed(
                {
                    "id": party_id,
                    "host_id": interact.user.id,
                    "host_mention": interact.user.mention,
                    "title": title,
                    "mission": game_name,
                    "departure": departure,
                    "max_users": number_of_user,
                    "participants": [interact.user.mention],
                    "is_closed": False,
                    "description": descriptions,
                },
                self.bot.db,
            )

            msg = await thread.send(embed=embed, view=PartyView())

            # update db (thread & msg id)
            await PartyService.update_thread_info(
                self.bot.db, party_id, thread.id, msg.id
            )

            await interact.followup.send(
                f"✅ '{target_channel.name}' {ts.get(f'{pf}pt-create')} {thread.mention}",
                ephemeral=True,
            )
            await save_log(
                pool=self.bot.db,
                type="cmd",
                cmd="party",
                interact=interact,
                msg="Party Created",
            )

        except Exception as e:
            await interact.followup.send(
                f"{ts.get(f'{pf}err-unknown')}", ephemeral=True
            )
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.err,
                cmd=f"cmd.party",
                interact=interact,
                msg="cmd used, but ERR",  # VAR
                obj=f"Error setup discord thread:\nT:{title}\nTYPE:{game_name}\nDEPT:{departure}\nDESC:{descriptions}\n{number_of_user}\n{return_traceback()}",
            )
            print(f"partyCog > {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(PartyCog(bot))
