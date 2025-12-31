import discord
import asyncio

from config.config import Lang
from config.TOKEN import base_url_market_image
from src.translator import ts, language as lang
from src.constants.keys import MSG_BOT
from src.utils.api_request import API_MarketSearch
from src.utils.file_io import json_load
from src.utils.logging_utils import save_log

THRESHOLD: int = 7
SLUGS: list = json_load("data/market-item-list.json")["data"]

_market_item_names = sorted([item["i18n"][lang]["name"] for item in SLUGS])

pf: str = "cmd.market-search."


def get_market_item_names() -> list[str]:
    return _market_item_names


def get_slug_data(name) -> tuple[bool, str, str, str]:
    if name not in _market_item_names:
        # rename input name
        iname: list = []
        for item in name.split(" "):
            # en pattern
            if item in ["p", "pr", "pri", "prim"]:
                iname.append("prime")
            elif item in ["c", "ch", "cha", "chas", "chass", "chassi"]:
                iname.append("chassis")
            elif item in ["s", "sy", "sys", "syst"]:
                iname.append("systems")
            elif item in ["n", "ne", "neu", "neur", "neuro", "neurop"]:
                iname.append("neuroptics")
            elif item in ["b", "bl", "bp", "blue", "bluep"]:
                iname.append("blueprint")

            # pattern not found
            else:
                iname.append(item)

        item_slug: str = " ".join(iname)
    else:
        item_slug = name

    # find slug data
    flag: bool = False
    for i in SLUGS:
        if item_slug == i["i18n"][lang]["name"]:
            item_slug = i["slug"]
            item_name = i["i18n"][lang]["name"]
            item_img_url = i["i18n"][lang]["icon"]
            flag = True
            break

    return flag, item_slug, item_name, item_img_url


def categorize(result, rank: int) -> list:
    # categorize only 'ingame' stocks (ignores online, offline)
    ingame_orders: list = []

    # if rank exists: categorize only selected rank
    if rank and (0 <= rank <= 5) and result["data"][0].get("rank"):
        # print(f"rank {rank} search")
        for item in result["data"]:
            if item["user"]["status"] != "ingame":
                continue
            if item["type"] != "sell":
                continue
            if item["rank"] != rank:
                continue
            # print(item["rank"], rank, item["platinum"])
            ingame_orders.append(item)

    else:
        # print("default search")
        for item in result["data"]:
            if item["user"]["status"] != "ingame":
                continue
            if item["type"] != "sell":
                continue
            ingame_orders.append(item)

    return sorted(ingame_orders, key=lambda x: x["platinum"])


def create_market_url(name, slug=None):
    msg = f"[{name}](https://warframe.market"
    msg += f"/{lang}" if lang != Lang.EN else ""

    if not slug:
        slug = get_slug_data(name)[1]

    msg += f"/items/{slug}?type=sell)"
    return msg


async def w_market_search(
    log_lock: asyncio.Lock, arg_obj: tuple[str, int]
) -> discord.Embed:
    name, rank = arg_obj
    flag: bool = False
    flag, item_slug, item_name, item_img_url = get_slug_data(name)

    if not flag:  # data not found
        return discord.Embed(
            description=f"## {ts.get(f'{pf}no-result')}\n- {ts.get(f'{pf}data')}: `{name}`",
            color=0xE67E22,  # discord.Color.orange
        )

    # api request
    result = await API_MarketSearch(log_lock, item_name=item_slug)

    # check response code
    try:
        if result.status_code == 404:  # item not found
            await save_log(
                lock=log_lock,
                type="api",
                cmd="w_market_search()",
                user=MSG_BOT,
                msg=f"{name},{item_slug} > 404 Not Found",
                obj=result.res_code,
            )
            return discord.Embed(
                description=ts.get(f"{pf}no-result"),
                color=0xE67E22,
            )
        elif result.status_code == 500:  # internal server err
            await save_log(
                lock=log_lock,
                type="api",
                cmd="w_market_search()",
                user=MSG_BOT,
                msg=f"{name},{item_slug} > 500 Internal Server Error",
                obj=result.res_code,
            )
            return discord.Embed(
                description=ts.get(f"{pf}server-err"),
                color=0xE67E22,
            )
        elif result.status_code != 200:  # another code err
            await save_log(
                lock=log_lock,
                type="api",
                cmd="w_market_search()",
                user=MSG_BOT,
                msg=f"{name},{item_slug} > {result.status_code}",
                obj=result.res_code,
            )
            return discord.Embed(
                description=ts.get(f"{pf}err"),
                color=0xE67E22,
            )
    except Exception as e:
        await save_log(
            lock=log_lock,
            type="api",
            cmd="w_market_search()",
            user=MSG_BOT,
            msg=f"response ERROR",
            obj=e,
        )
        return discord.Embed(
            description=ts.get(f"{pf}err"),
            color=0xE67E22,
        )

    # init categorize
    ingame_orders = categorize(result.json(), rank=rank)

    output_msg = ""

    # create output msg
    idx: int = 0
    # title
    output_msg += f"## {ts.get(f'{pf}result')}: {create_market_url(name=item_name,slug=item_slug)}"
    # item rank if exists
    output_msg += (
        ts.get(f"{pf}rank").format(rank=rank) if ingame_orders[0].get("rank") else ""
    )
    # sub desc
    output_msg += f"\n> {ts.get(f'{pf}link-to-market')}\n"
    # item list
    for item in ingame_orders:
        idx += 1
        if idx > THRESHOLD:
            break

        output_msg += f"- **{item['platinum']} {ts.get(f'{pf}platinum')}** : {item['quantity']} {ts.get(f'{pf}qty')} (`{item['user']['ingameName']}`)\n"

    embed = discord.Embed(
        description=output_msg,
        color=0x3498DB,  # discord.Color.blue,
    )
    embed.set_thumbnail(url=f"{base_url_market_image}{item_img_url}")
    return embed
