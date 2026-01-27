import datetime as dt
import json
import os
import aiohttp
import discord
from discord.ext import commands, tasks

from config.config import LOG_TYPE
from src.bot_translator import BotTranslator
from src.commands.noti_channel import DB_COLUMN_MAP, PROFILE_CONFIG
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.services.party_service import PartyService
from src.services.trade_service import TradeService
from src.translator import ts
from src.utils.data_manager import SETTINGS
from src.utils.db_helper import query_reader, transaction
from src.utils.delay import delay
from src.utils.discord_file import img_file
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.times import timeNowDT
from src.views.party_view import PartyView
from src.views.trade_view import TradeView


class DiscordBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents, db, **options):
        super().__init__(command_prefix="!", intents=intents, **options)
        self.db = db
        self.webhook_cache = {}
        self.processing: bool = False

    async def setup_hook(self) -> None:
        self.add_view(PartyView())
        self.add_view(TradeView())
        print(
            f"{C.blue}[{LOG_TYPE.info}] {C.green}Persistent Views successfully registered.{C.default}"
        )
        # load translator
        await self.tree.set_translator(BotTranslator())
        # load cogs
        cog_ext = [
            # commands
            "register",
            "party",
            "trade",
            "complain",
            "user_warn",
            # tasks
            "tasks.weekly_task",
            "tasks.week_start_noti",
            "tasks.check_new_content",
            "tasks.auto_party_expire",
            "tasks.auto_trade_expire",
        ]
        for ext in cog_ext:
            try:
                await self.load_extension(f"src.cogs.{ext}")
                print(ext)
            except Exception as e:
                print(f"{C.red}Failed to load extension {ext}: {e}{C.default}")

    async def on_ready(self) -> None:
        print(
            f"{C.blue}[{LOG_TYPE.info}] {C.yellow}{ts.get('start.sync')}...{C.default}",
            end="",
        )
        await self.wait_until_ready()

        if self.tree:
            await self.tree.sync()
            print(f"{C.green}Synced Tree Commands")
        else:
            print(f"{C.blue}[{LOG_TYPE.err}] {C.red}Commands Not Synced!")

        # noinspection PyTypeChecker
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(ts.get("start.bot-status-msg")),
        )
        print(
            f"{C.blue}[{LOG_TYPE.info}] {C.cyan}{ts.get('start.final')} <<{C.white}{self.user}{C.cyan}>>"
        )
        print(f"{C.green}{ts.get(f'start.final2')}{C.default}")
        await save_log(
            pool=self.db,
            cmd="bot.BOOTED",
            user=MSG_BOT,
            msg=f"[{LOG_TYPE.info}] Bot booted up.",
        )
        # start coroutine
        if not SETTINGS["noti"]["isEnabled"]:
            return

        print(
            f"{C.blue}[{LOG_TYPE.info}] {C.green}{ts.get('start.coroutine')}{C.default}"
        )

    async def send_alert(
        self, value: discord.Embed | tuple[discord.Embed, str] | str, channel_list: list
    ) -> None:
        # send message
        for ch in channel_list:
            try:
                channel = self.get_channel(ch)
                msg: str = f"msg sent"
                if isinstance(value, discord.Embed):
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.msg,
                        cmd="auto_sent_message",
                        user=MSG_BOT,
                        guild=channel.guild.name,
                        channel=channel.name,
                        msg=msg,
                        obj=value.description,
                    )
                    await channel.send(embed=value)
                elif isinstance(value, tuple):  # embed with file
                    eb, f = value
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.msg,
                        cmd="auto_sent_message",
                        user=MSG_BOT,
                        guild=channel.guild.name,
                        channel=channel.name,
                        msg=msg,
                        obj=eb.description,
                    )
                    f = img_file(f)
                    await channel.send(embed=eb, file=f)
                else:  # string type
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.msg,
                        cmd="auto_sent_message",
                        user=MSG_BOT,
                        guild=channel.guild.name,
                        channel=channel.name,
                        msg=msg,
                        obj=value,
                    )
                    await channel.send(value)
            except Exception as e:
                error_msg = f"[Error] error on sending in {ch}: {e}"
                print(f"{C.red}{error_msg}{C.default}")
                await save_log(
                    pool=self.db,
                    type=LOG_TYPE.err,
                    cmd="send_alert",
                    user=MSG_BOT,
                    msg=error_msg,
                    obj=return_traceback(),
                )

    async def get_profile_img(self, noti_key):
        out_name = self.user.name
        out_avatar = self.user.display_avatar.url if self.user else None

        # get profile config
        profile_conf = PROFILE_CONFIG.get(noti_key)
        if not profile_conf:
            return out_name, out_avatar

        # get profile name
        fetched_name = profile_conf.get("name")
        fetched_avatar = profile_conf.get("avatar")
        if (not fetched_name) or (not fetched_avatar):
            return out_name, out_avatar

        out_name = fetched_name

        # fetch url & combine
        async with transaction(self.db) as cursor:
            await cursor.execute("SELECT value FROM vari WHERE name='img_server'")
            base_url = await cursor.fetchone()
        if base_url:
            out_avatar = f"{base_url["value"]}/?name={fetched_avatar}"

        return out_name, out_avatar

    async def broadcast_webhook(self, noti_key: str, content) -> None:
        """
        search the webhook subscribed to that notification (noti_key) in the database and sends it.
        """
        # debug
        # await save_log(pool=self.db,type=LOG_TYPE.info,cmd="broadcast_webhook",user=MSG_BOT,msg="called broadcast_webhook")
        # check db column mapping
        db_column = DB_COLUMN_MAP.get(noti_key)
        if not db_column:
            msg = f"[{LOG_TYPE.err}] Unmapped notification key: `{noti_key}` -> {db_column}"
            await save_log(
                pool=self.db,
                type=LOG_TYPE.err,
                cmd="broadcast_webhook",
                user=MSG_BOT,
                msg=msg,
            )
            print(C.yellow, msg, C.default, sep="")
            return

        # search subscribers in db
        async with query_reader(self.db) as cursor:
            await cursor.execute(
                f"SELECT webhook_url FROM webhooks WHERE {db_column} = 1"
            )
            subscribers = await cursor.fetchall()

        if not subscribers:
            # debug
            # await save_log(pool=self.db,type=LOG_TYPE.info,cmd="broadcast_webhook",user=MSG_BOT,msg="No Subscribers")
            return

        # initialize counters
        total_subscribers = len(subscribers)
        success_count = 0
        # prepare payload data
        embed_data = None
        text_content = ""
        files_to_upload = []
        content_file_name = "i.webp"

        # process embed
        if isinstance(content, discord.Embed):
            embed_data = content.to_dict()
            log_content = content.description

        # process tuple (embed, file)
        elif isinstance(content, tuple):
            eb, file_info = content
            embed_data = eb.to_dict()
            real_file_path = None

            log_content = f"IMG: {file_info}\n{eb.description}"
            # img path is string
            if isinstance(file_info, str):
                path = f"img/{file_info}.webp"
                if os.path.exists(path):
                    real_file_path = path
                    # content_file_name = "i.webp"
                # else:
                #     real_file_path = file_info
                #     content_file_name = os.path.basename(file_info)

            # read file
            if real_file_path:
                try:
                    with open(real_file_path, "rb") as f:
                        files_to_upload.append(
                            {
                                "name": "file",
                                "filename": content_file_name,
                                "data": f.read(),
                            }
                        )
                except Exception as e:
                    msg = f"Failed to read image file: {e}"
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="broadcast_webhook",
                        user=MSG_BOT,
                        msg=msg,
                        obj=return_traceback(),
                    )
                    print(C.red, msg, C.default)

        # string only
        else:
            text_content = str(content)
            log_content = text_content

        # setup profile
        final_username, final_avatar_url = await self.get_profile_img(noti_key)

        # send alert & check result
        async with aiohttp.ClientSession() as session:
            eta_start: dt.datetime = timeNowDT()
            for row in subscribers:
                url = row["webhook_url"]
                # custom_msg = row.get("custom_msg", "")

                # verify URL
                if not url or not str(url).startswith("http"):
                    continue

                # combine msg
                # final_text = (
                #     f"{custom_msg}\n{text_content}" if custom_msg else text_content
                # )
                payload = {
                    "username": final_username,
                    "avatar_url": final_avatar_url,
                    "content": text_content.strip(),  # final_text
                }
                if embed_data:
                    payload["embeds"] = [embed_data]

                try:
                    if files_to_upload:
                        # [send file] multipart/form-data
                        form = aiohttp.FormData()
                        form.add_field("payload_json", json.dumps(payload))

                        # upload all file
                        for file_obj in files_to_upload:
                            form.add_field(
                                file_obj["name"],
                                file_obj["data"],
                                filename=file_obj["filename"],
                                content_type="application/octet-stream",
                            )

                        async with session.post(url, data=form) as response:
                            if 200 <= response.status < 300:
                                success_count += 1
                            else:
                                err_text = await response.text()
                                eta_end: dt.timedelta = timeNowDT() - eta_start
                                await save_log(
                                    pool=self.db,
                                    type=LOG_TYPE.err,
                                    cmd="broadcast_webhook",
                                    user=MSG_BOT,
                                    msg=f"Failed to send {noti_key} Multipart (code: {response.status}, eta: {eta_end})",
                                    obj=err_text,
                                )
                    else:  # general send (json)
                        async with session.post(url, json=payload) as response:
                            if 200 <= response.status < 300:
                                success_count += 1
                            else:
                                err_text = await response.text()
                                eta_end: dt.timedelta = timeNowDT() - eta_start
                                await save_log(
                                    pool=self.db,
                                    type=LOG_TYPE.err,
                                    cmd="broadcast_webhook",
                                    user=MSG_BOT,
                                    msg=f"Failed to send {noti_key} general (code: {response.status}, eta: {eta_end})",
                                    obj=err_text,
                                )

                except Exception as e:
                    eta_sending: dt.timedelta = timeNowDT() - eta_start
                    await save_log(
                        pool=self.db,
                        type=LOG_TYPE.err,
                        cmd="broadcast_webhook",
                        user=MSG_BOT,
                        msg=f"ERROR on sending msg: {noti_key} (eta: {eta_sending})\n{e}",
                        obj=return_traceback(),
                    )

        # logging
        eta_sending: dt.timedelta = timeNowDT() - eta_start
        log_msg = (
            f"{noti_key} sent. {success_count}/{total_subscribers} (eta: {eta_sending})"
        )
        await save_log(
            pool=self.db,
            type=LOG_TYPE.msg,
            cmd="broadcast_webhook",
            user=MSG_BOT,
            msg=log_msg,
            obj=f"{log_content}",
        )

    @tasks.loop(count=1)
    async def process_queue(self):
        try:
            db = self.db
            print("start process queue")  # DEBUG_CODE
            await delay()
            # Party queues
            await PartyService.process_create_queue(db)
            await PartyService.process_update_queue(db)
            await PartyService.process_delete_queue(db)

            # Trade queues
            await TradeService.process_create_queue(db)
            await TradeService.process_update_queue(db)
            await TradeService.process_delete_queue(db)

            if not (
                await TradeService.is_queue_empty()
                and await PartyService.is_queue_empty()
            ):
                self.process_queue.restart()
                print("restart (queue is not empty)")  # DEBUG_CODE
        except Exception as e:
            msg = f"Failed to process queue: {C.red}{e}"
            print(C.red, msg, C.default)
            await save_log(
                pool=self.bot.db,
                type=LOG_TYPE.err,
                cmd="bot.process_queue",
                user=MSG_BOT,
                msg=msg,
                obj=return_traceback(),
            )
        finally:
            if self.process_queue.is_running():
                self.process_queue.stop()

    async def trigger_queue_processing(self):
        if self.process_queue.is_running():
            print("already running")  # DEBUG_CODE
            return

        print("start queue process")  # DEBUG_CODE
        self.process_queue.start()
