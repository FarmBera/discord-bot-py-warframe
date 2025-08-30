import discord
from src.translator import ts
from src.utils.return_err import err_embed


def w_dailyDeals(deals) -> discord.Embed:
    if not deals:
        return err_embed("dailyDeals")

    pf = f"cmd.dailyDeals"

    output_msg: str = f"## {ts.get(f'{pf}.title')}\n\n"

    for item in deals:
        output_msg += f"""# {item['item']}

- ~~{item['originalPrice']}~~ --> **{item['salePrice']}**
- **{item['total'] - item['sold']}** {ts.get(f'{pf}.remain')} ({item['sold']}/{item['total']})
- {ts.get(f'{pf}.exp')} {item['eta']}
"""

    return discord.Embed(description=output_msg)
