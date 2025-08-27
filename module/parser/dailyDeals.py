import discord
from translator import ts


def w_dailyDeals(deals, *lang):
    if deals == False:
        return discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000)

    if deals is None:
        return None

    pf = f"cmd.dailyDeals"

    output_msg: str = f"## {ts.get(f'{pf}.title')}\n\n"

    for item in deals:
        output_msg += f"""# {item['item']}

- ~~{item['originalPrice']}~~ --> **{item['salePrice']}**
- {item['sold']}/{item['total']} {ts.get(f'{pf}.remain')}
- {ts.get(f'{pf}.exp')} {item['eta']}

"""

    return discord.Embed(description=output_msg)
