import os

import discord

from src.translator import ts
from src.utils.data_manager import getLanguage
from src.utils.file_io import json_load
from src.utils.return_err import err_embed
from src.utils.times import convert_remain

NAME_DICTIONARY: dict = json_load("data/en/languages.json")
IMAGE_ORIGIN: list = os.listdir("img/items-webp")
IMAGE_ORIGIN.sort()
IMAGE_CACHE: dict = {}

pf = f"cmd.dailydeals."


def getItemName(data: str, query1: str = "value") -> str:
    result = NAME_DICTIONARY.get(data, {}).get(query1)
    return result if result else NAME_DICTIONARY.get(data.lower(), {}).get(query1, data)


def getThumbImg(origin_name: str) -> str:
    global IMAGE_CACHE
    prefix: str = "items-webp/"

    if not origin_name:
        return ""

    parsed_name = getItemName(origin_name).lower()

    # find cached
    cached_name = IMAGE_CACHE.get(parsed_name, None)
    if cached_name:
        return cached_name

    # find items in directory
    for item in IMAGE_ORIGIN:
        for jtem in item.split("-"):
            if jtem == parsed_name:
                final_name = f"{prefix}{item}".split(".")[0]  # trim file ext
                IMAGE_CACHE[parsed_name] = final_name
                return final_name

    return ""  # not found


def w_dailyDeals(deals) -> tuple[discord.Embed, str]:
    if not deals:
        return err_embed("dailyDeals"), ""

    origin_name: str = ""  # for item thunb img
    output_msg: str = ts.get(f"{pf}title")

    for item in deals:
        price_origin: int = item["OriginalPrice"]
        price_sale: int = item["SalePrice"]
        discount: int = item["Discount"]
        amount: int = item["AmountTotal"] - item["AmountSold"]
        remain: str = f"{item['AmountSold']}/{item['AmountTotal']}"
        expiry: str = convert_remain(item["Expiry"]["$date"]["$numberLong"])
        origin_name = item["StoreItem"].lower()
        item_name = getLanguage(origin_name)

        output_msg += ts.get(f"{pf}output").format(
            name=item_name,
            origin=price_origin,
            sale=price_sale,
            discount=discount,
            qty=amount,
            remain=remain,
            time=expiry,
        )

    img = getThumbImg(origin_name)
    embed = discord.Embed(description=output_msg, color=discord.Color.darker_grey())
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, img


# from src.utils.data_manager import get_obj
# from src.constants.keys import DAILYDEALS
# d = w_dailyDeals(get_obj(DAILYDEALS))
# print(d[0].description, d[1], sep="\n")
# print(IMAGE_CACHE)
