import random

import discord

from src.translator import ts
from src.utils.data_manager import getLanguage
from src.utils.image import getThumbImg
from src.utils.return_err import err_embed
from src.utils.times import convert_remain

pf = f"cmd.dailydeals."

DARVO_MSG: list = ts.get(f"{pf}msg")
MSG_MAX_LENGTH: int = len(DARVO_MSG) - 1


def getDarvoRandomMsg() -> str:
    return f"*{DARVO_MSG[random.randint(0, MSG_MAX_LENGTH)]}*\n"


def w_dailyDeals(deals) -> discord.Embed:
    if not deals:
        return err_embed("dailyDeals")

    origin_name: str = ""  # for item thunb img
    output_msg: str = ts.get(f"{pf}title")

    for item in deals:
        origin_name = item["StoreItem"].lower()
        output_msg += ts.get(f"{pf}output").format(
            name=getLanguage(origin_name),
            origin=item["OriginalPrice"],
            sale=item["SalePrice"],
            discount=item["Discount"],
            qty=item["AmountTotal"] - item["AmountSold"],
            remain=f"{item['AmountSold']}/{item['AmountTotal']}",
            time=convert_remain(item["Expiry"]["$date"]["$numberLong"]),
        )

    embed = discord.Embed(description=output_msg, color=discord.Color.darker_grey())
    embed.set_thumbnail(url=getThumbImg(origin_name))
    return embed


# from src.utils.data_manager import get_obj
# from src.constants.keys import DAILYDEALS
# print(w_dailyDeals(get_obj(DAILYDEALS)).description)
