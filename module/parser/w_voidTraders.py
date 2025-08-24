import discord

from translator import ts
from module.discord_file import img_file
from module.get_emoji import get_emoji


BARO_IMG_NAME = "baro-ki-teer"  # VAR


def color_decision(t):
    for item in t:
        if item["active"]:
            return 0x4DD2FF
    return 0xFFA826


def w_voidTraders(trader, *lang):
    if trader == False:
        return discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000)

    if trader is None:
        return None

    idx = 1
    length: int = len(trader)
    pf: str = "cmd.void-traders."

    output_msg: str = f"# {ts.get(f'{pf}title')}\n\n"

    for item in trader:
        if length >= 2:
            output_msg += f"{idx}. {ts.get(f'{pf}tdr-name')}: {item['character']}\n\n"
            idx += 1
        else:
            output_msg += f"- {ts.get(f'{pf}tdr-name')}: {item['character']}\n"

        status = item["active"]

        # OO appeared
        if status:
            output_msg += (
                f"- {ts.get(f'{pf}status')}: ✅ **{ts.get(f'{pf}activate')}**\n"
            )
            output_msg += f"- {ts.get(f'{pf}end')} {item['endString']}\n"
            output_msg += f"- {ts.get(f'{pf}location')}: "
        # XX NOT appeared
        else:
            output_msg += (
                f"- {ts.get(f'{pf}status')}: ❌ *{ts.get(f'{pf}deactivate')}*\n"
            )
            output_msg += f"- {ts.get(f'{pf}appear')} {item['startString']}\n"
            output_msg += f"- {ts.get(f'{pf}place')}: "

        # appear location
        output_msg += f"{item['location']}\n\n"

    f = img_file(BARO_IMG_NAME)
    embed = discord.Embed(description=output_msg, color=color_decision(trader))
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f


def W_voidTradersItem(trader, *lang):
    output_msg: str = ""
    pf = "cmd.void-traders-item."

    for item in trader:
        listItem: list = []

        if item["inventory"] == []:
            listItem.append(
                f"{ts.get(f'{pf}not-yet')}\n- {ts.get(f'{pf}arrives-in')} {item['startString']}"
            )

        for jtem in item["inventory"]:
            itype: str = ""
            k: str = jtem["uniqueName"].replace("/Lotus/StoreItems", "").lower()

            if "/mods/" in k:
                itype = ts.get(f"{pf}mods")
            elif "/skins/" in k:
                itype = ts.get(f"{pf}skin")
            elif "/shipdecos/" in k:
                itype = ts.get(f"{pf}deco")
            elif "/weapons/" in k:
                itype = ts.get(f"{pf}weapon")
            elif "/boosters/" in k:
                itype = ts.get(f"{pf}booster")
            elif "/avatarimages/" in k:
                itype = ts.get(f"{pf}glyph")
            elif "/songitems/" in k:
                itype = ts.get(f"{pf}music")
            elif "/projections/" in k:
                itype = ts.get(f"{pf}relic")
            elif "/keys/" in k:
                itype = ts.get(f"{pf}keys")
            else:
                itype = ts.get(f"{pf}other")

            out = f"{itype} / {get_emoji('ducat')} {jtem['ducats']} {get_emoji('credit')} {int((jtem['credits'])):,} / {jtem['item']}"
            listItem.append(out)

        listItem.sort()

        output_msg += f"# {item['character']} at {item['location']}\n\n"
        for jtem in listItem:
            output_msg += f"- {jtem}\n"
        output_msg += "\n"

    # f = img_file(BARO_IMG_NAME)
    embed = discord.Embed(description=output_msg, color=color_decision(trader))
    # embed.set_thumbnail(url="attachment://i.png")

    return embed  # , f
