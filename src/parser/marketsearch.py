import discord

from config.TOKEN import base_url_market_image
from src.translator import ts, language as lang
from src.utils.api_request import API_MarketSearch
from src.utils.file_io import json_load

THRESHOLD: int = 7
SLUGS: list = json_load("data/market-item-list.json")["data"]

_market_item_names = sorted([item["i18n"][lang]["name"] for item in SLUGS])


def get_market_item_names() -> list[str]:
    return _market_item_names


def w_market_search(name) -> discord.Embed:
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
        if item_slug in i["i18n"][lang]["name"]:
            item_slug = i["slug"]
            item_name = i["i18n"][lang]["name"]
            item_img_url = i["i18n"][lang]["icon"]
            flag = True
            break

    pf: str = "cmd.market-search."

    if not flag:  # data not found
        return discord.Embed(
            description=f"## {ts.get(f'{pf}no-result')}\n- {ts.get(f'{pf}data')}: `{name}`",
            color=0xE67E22,  # discord.Color.orange
        )

    # api request
    result = API_MarketSearch(item_name=item_slug)

    if not result:
        return discord.Embed(
            description=ts.get(f"{pf}api-fail"),
            color=0xE67E22,  # discord.Color.orange,
        )

    if result.status_code != 200:  # api not found
        return discord.Embed(
            description=f"## {ts.get(f'{pf}no-result')}\n- `{name}`\n- (Market API)",
            color=0xE67E22,  # discord.Color.orange,
        )

    # init categorize
    ingame_orders = []
    output_msg = ""

    # categorize only 'ingame' stocks (ignores online, offline)
    for item in result.json()["data"]:
        if item["user"]["status"] != "ingame":
            continue
        ingame_orders.append(item)

    ingame_orders = sorted(ingame_orders, key=lambda x: x["platinum"])

    # create output msg
    idx: int = 0
    output_msg = f"## {ts.get(f'{pf}result')}: [{item_name}](https://warframe.market/{lang}/items/{item_slug}?type=sell)\n"
    output_msg += f"> {ts.get(f'{pf}link-to-market')}\n"
    for item in ingame_orders:
        if item["type"] != "sell":
            continue

        idx += 1
        if idx > THRESHOLD:
            break

        output_msg += f"- **{item['platinum']} {ts.get(f'{pf}platinum')}** : {item['quantity']} {ts.get(f'{pf}qty')} ({item['user']['ingameName']})\n"

    embed = discord.Embed(
        description=output_msg,
        color=0x3498DB,  # discord.Color.blue,
    )
    embed.set_thumbnail(url=f"{base_url_market_image}{item_img_url}")
    return embed
