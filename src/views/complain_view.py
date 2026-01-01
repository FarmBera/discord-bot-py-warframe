import discord
from discord import ui
from discord.ext import commands
import asyncio

# editor modal
import discord
from discord.ext import commands
import asyncio

from config.config import LOG_TYPE
from src.translator import ts
from src.constants.color import C
from src.constants.keys import COOLDOWN_DEFAULT
from src.utils.return_err import return_traceback
from src.utils.data_manager import CHANNELS
from src.utils.logging_utils import save_log
from src.utils.db_helper import query_reader

pf: str = "cmd.complain."


def parseNickname(nickname: str) -> str:
    return nickname.split("]")[-1].strip()


# article editor modal
class ComplainModal(discord.ui.Modal):
    def __init__(self, btn_interact: discord.Interaction):
        super().__init__(title=ts.get(f"{pf}m-title"), timeout=None)
        self.button_interact = btn_interact

        self.input_title = discord.ui.TextInput(
            label=ts.get(f"{pf}m-title-label"),
            placeholder=ts.get(f"{pf}m-title-ph"),
            style=discord.TextStyle.short,
            max_length=100,
            required=True,
        )
        self.input_category = discord.ui.TextInput(
            label=ts.get(f"{pf}m-cat-label"),
            placeholder=ts.get(f"{pf}m-cat-ph"),
            style=discord.TextStyle.short,
            max_length=100,
            required=True,
        )
        self.input_desc = discord.ui.TextInput(
            label=ts.get(f"{pf}m-desc-label"),
            placeholder=ts.get(f"{pf}m-desc-ph"),
            style=discord.TextStyle.long,
            max_length=4000,
            required=True,
        )
        self.add_item(self.input_title)
        self.add_item(self.input_category)
        self.add_item(self.input_desc)

    async def on_submit(self, interact: discord.Interaction):
        try:
            await interact.response.defer(ephemeral=True)

            await self.button_interact.edit_original_response(
                content=ts.get(f"> 처리 중입니다. 잠시만 기다려주세요..."),
                embed=None,
                view=None,
            )

            title: str = f"[{self.input_category}] {self.input_title}"
            desc: str = f"""{ts.get(f'{pf}created').format(user=interact.user.display_name)}
(사용자 ID: {interact.user.name})

{self.input_desc}"""

            # load dm users
            async with query_reader(interact.client.db) as cursor:
                await cursor.execute(
                    "SELECT user_id, is_dm_target FROM admins WHERE is_dm_target=TRUE"
                )
                result = await cursor.fetchall()

            # dm target not found
            if result is None or not result:
                pass

            # send dm to user
            for user in result:
                target_user = await interact.client.fetch_user(user["user_id"])
                await target_user.send(
                    embed=discord.Embed(title=title, description=desc)
                )
                await asyncio.sleep(1)

            # post new article in forum channel
            forum_channel = interact.client.get_channel(CHANNELS["complain"])
            if isinstance(forum_channel, discord.ForumChannel):
                await forum_channel.create_thread(name=title, content=desc)

            await self.button_interact.edit_original_response(
                content=ts.get(f"{pf}done"), embed=None, view=None
            )

            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.event,
                cmd="Complain.btn.submit",
                interact=interact,
                msg="Complain successfully submitted",
                obj=f"TITLE: {self.input_title}\nCATEGORY: {self.input_category}\nDESC: {self.input_desc}",
            )
        except Exception as e:
            await interact.followup.send(ts.get(f"{pf}err"), ephemeral=True)
            print(e)
            await save_log(
                pool=interact.client.db,
                type=LOG_TYPE.e_event,
                cmd="Complain.btn.submit",
                interact=interact,
                msg=f"Complain submitted, but ERR",
                obj=f"TITLE: {self.input_title}\nCATEGORY: {self.input_category}\nDESC: {self.input_desc}\n{return_traceback()}",
            )


class ApplyButtonView(discord.ui.View):
    def __init__(self, interact):
        self.interact: discord.Interaction = interact
        super().__init__(timeout=None)
        self.cd = commands.CooldownMapping.from_cooldown(
            1, COOLDOWN_DEFAULT, commands.BucketType.user
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

    @discord.ui.button(
        label=ts.get(f"{pf}btn-name"),
        style=discord.ButtonStyle.primary,
        custom_id="apply_button",
    )
    async def apply_btn(self, interact: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interact, self.cd):
            return

        await interact.response.send_modal(ComplainModal(btn_interact=interact))
        await save_log(
            pool=interact.client.db,
            type=LOG_TYPE.event,
            cmd="ApplyButtonView.btn",
            interact=interact,
            msg="Clicked ApplyButtonView button",
        )
