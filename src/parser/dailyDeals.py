import discord
from src.translator import ts
from src.utils.times import convert_remain
from src.utils.return_err import err_embed
from src.utils.data_manager import getLanguage


def w_dailyDeals(deals) -> discord.Embed:
    if not deals:
        return err_embed("dailyDeals")

    pf = f"cmd.dailyDeals."

    output_msg: str = f"## {ts.get(f'{pf}title')}\n\n"

    for item in deals:
        price_origin: str = item["OriginalPrice"]
        price_sale: str = price_origin - item["Discount"]
        amount: str = item["AmountTotal"] - item["AmountSold"]
        remain: str = f"{item['AmountSold']}/{item['AmountTotal']}"
        expiry: str = convert_remain(item["Expiry"]["$date"]["$numberLong"])
        item_name: str = getLanguage(item["StoreItem"].lower())

        output_msg += f"""# {item_name}

- ~~{price_origin}~~ --> **{price_sale}**
- **{amount}** {ts.get(f'{pf}remain')} ({remain})
- {ts.get(f'{pf}exp').format(time=expiry)}
"""

    return discord.Embed(description=output_msg)
