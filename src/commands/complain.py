import discord
from discord.ext import commands
import asyncio

from config.config import LOG_TYPE
from config.TOKEN import HOMEPAGE, SERVER_NAME
from src.translator import ts
from src.constants.color import C
from src.constants.keys import COOLDOWN_DEFAULT
from src.utils.return_err import return_test_err, print_test_err
from src.utils.data_manager import CHANNELS
from src.utils.logging_utils import save_log
from src.utils.times import timeNowDT
from src.utils.db_helper import query_reader

pf: str = "cmd.complain."

complain_guide: discord.Embed = discord.Embed(
    description=ts.get(f"{pf}info").format(SERVER_NAME=SERVER_NAME, HOMEPAGE=HOMEPAGE),
    color=discord.Color.yellow(),
)


def parseNickname(nickname: str) -> str:
    return nickname.split("]")[-1].strip()


# article editor modal
class Complain(discord.ui.Modal, title=ts.get(f"{pf}")):
    def __init__(self, btn_interact: discord.Interaction):
        super().__init__(timeout=None)
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

            # Send DM to User
            async with query_reader(interact.client.db) as cursor:
                await cursor.execute(
                    "SELECT user_id, is_dm_target FROM admins WHERE is_dm_target = TRUE"
                )
                result = await cursor.fetchall()

            if result is None or not result:  # or bool(result.get("is_dm_target")):
                raise NameError("DM Target Not Found!")

            for user in result:
                target_user = await interact.client.fetch_user(user["user_id"])
                await target_user.send(
                    embed=discord.Embed(title=title, description=desc)
                )
                await asyncio.sleep(1)

            # Post New Article in Forum Channel
            forum_channel = interact.client.get_channel(CHANNELS["complain"])
            if isinstance(forum_channel, discord.ForumChannel):
                await forum_channel.create_thread(name=title, content=desc)

            try:
                await self.button_interact.edit_original_response(
                    content=ts.get(f"{pf}done"), embed=None, view=None
                )
            except Exception:
                print(
                    timeNowDT(),
                    C.yellow,
                    "[warn] Failed to edit origin msg (from Complain -> edit msg logic)",
                )
                # print_test_err("Failed to edit origin msg")

            # await interact.followup.send(ts.get(f"{pf}done"), ephemeral=True)

            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.event,
                cmd="btn.complain.submit",
                interact=interact,
                msg="Complain successfully submitted",
                obj=f"TITLE: {self.input_title}\nCATEGORY: {self.input_category}\nDESC: {self.input_desc}",
            )

        except Exception as e:
            await interact.followup.send(ts.get(f"{pf}err"), ephemeral=True)
            print(e)
            await save_log(
                lock=interact.client.log_lock,
                type=LOG_TYPE.e_event,
                cmd="btn.complain.submit",
                interact=interact,
                msg=f"Complain submitted, but error",
                obj=f"TITLE: {self.input_title}\nCATEGORY: {self.input_category}\nDESC: {self.input_desc}\n{return_test_err()}",
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

        await interact.response.send_modal(Complain(btn_interact=interact))


async def cmd_create_complain_helper(interact: discord.Interaction) -> None:
    await interact.response.defer(ephemeral=True)

    if interact.guild_id != CHANNELS["guild"]:
        msg_obj = ts.get(f"cmd.err-limit-server")
        await interact.followup.send(msg_obj, ephemeral=True)
        await save_log(
            lock=interact.client.log_lock,
            type="cmd",
            cmd=f"cmd.complain",
            interact=interact,
            msg="[warn] cmd used, but unauthorized server",
            obj=msg_obj,
        )
        return

    target_channel = interact.client.get_channel(CHANNELS["complain"])

    # channel not exists or not a Forum
    if not target_channel:
        await interact.followup.send(ts.get(f"{pf}err-channel"), ephemeral=True)
        await save_log(
            lock=interact.client.log_lock,
            type="cmd",
            cmd=f"cmd.complain",
            interact=interact,
            msg="[warn] cmd used, but complain channel not found",
        )
        return

    await interact.followup.send(
        embed=complain_guide,
        view=ApplyButtonView(interact=interact),
        ephemeral=True,
    )
    await save_log(
        lock=interact.client.log_lock,
        type="cmd",
        cmd=f"cmd.complain",
        interact=interact,
        msg="[info] cmd used",
    )
