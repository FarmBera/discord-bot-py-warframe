import discord

from config.TOKEN import base_url_market_image
from src.translator import language as lang
from src.utils.api_request import API_MarketSearch
from src.utils.file_io import json_load

THRESHOLD: int = 7
SLUGS: list = json_load("data/market-item-list.json")["data"]


def w_market_search(name) -> discord.Embed:
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

        # ko pattern
        # TODO: korean pattern

        # pattern not found
        else:
            iname.append(item)

    item_slug: str = " ".join(iname)

    # find slug data
    flag: bool = False
    for i in SLUGS:
        if item_slug in i["i18n"][lang]["name"]:
            item_slug = i["slug"]
            item_name = i["i18n"][lang]["name"]
            item_img_url = i["i18n"][lang]["icon"]
            flag = True
            break

    if not flag:  # data not found
        return discord.Embed(
            description=f"## 검색 결과가 없습니다.\n- 데이터: `{name}`",
            color=0xE67E22,  # discord.Color.orange
        )

    # api request
    result = API_MarketSearch(item_name=item_slug)

    if not result:
        return discord.Embed(
            description=f"API 요청에 실패하였습니다. 잠시 후 다시 시도해주세요.\n\n문제가 지속된다면 관리자에게 문의해주세요.",
            color=0xE67E22,  # discord.Color.orange,
        )

    if result.status_code != 200:  # api not found
        return discord.Embed(
            description=f"## 검색 결과가 없습니다.\n- `{name}`\n- (Market API)",
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
    output_msg = f"## 검색 결과: [{item_name}](https://warframe.market/{lang}/items/{item_slug}?type=sell)\n"
    output_msg += f"(파란색 링크를 클릭하면 마켓으로 이동합니다.)\n"
    for item in ingame_orders:
        if item["type"] != "sell":
            continue

        idx += 1
        if idx > THRESHOLD:
            break

        output_msg += f"- **{item['platinum']} 플레** : {item['quantity']} 개 ({item['user']['ingameName']})\n"

    embed = discord.Embed(
        description=output_msg,
        color=0x3498DB,  # discord.Color.blue,
    )
    embed.set_thumbnail(url=f"{base_url_market_image}{item_img_url}")
    return embed
