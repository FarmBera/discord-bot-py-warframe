import discord
import random

from src.translator import ts
from src.utils.times import timeNow, convert_remain
from src.utils.discord_file import img_file
from src.utils.emoji import get_emoji
from src.utils.return_err import err_embed
from src.utils.formatter import extract_last_part, add_space
from src.utils.data_manager import getSolNode, getLanguage


baro_img = ["baro-ki-teer", "baro"]  # VAR
baro_active: bool = False


def getBaroImg(name: str = "") -> str:
    if name and "evil" in name.lower():
        return "baro-evil"
    return baro_img[random.randrange(0, len(baro_img))]


def isBaroActive(act, exp) -> bool:
    curr: int = timeNow()

    t_list = [act, exp]

    for i in range(2):
        ts_str = str(t_list[i])
        # conert milliseconds to seconds
        if len(ts_str) == 13:
            t_list[i] = int(ts_str) / 1000
        else:
            t_list[i] = int(ts_str)

    act, exp = t_list
    return True if act < curr and curr < exp else False


def color_decision(arg):
    global baro_active

    for i in arg:
        if baro_active:
            return 0x4DD2FF
    return 0xFFA826


def w_voidTraders(trader, text_arg=None, embed_color=None) -> tuple:
    global baro_active

    if not trader:
        return err_embed("voidTraders")

    idx = 1
    length: int = len(trader)
    pf: str = "cmd.void-traders."

    # output_msg: str = f"# {ts.get(f'{pf}title')}\n\n"
    output_msg: str = f"# {text_arg if text_arg else ts.get(f'{pf}title')}\n\n"

    for td in trader:
        t_act: int = int(td["Activation"]["$date"]["$numberLong"])
        t_exp: int = int(td["Expiry"]["$date"]["$numberLong"])

        if length >= 2:
            output_msg += (
                f"{idx}. {ts.get(f'{pf}tdr-name')}: {ts.trs(td['Character'])}\n\n"
            )
            idx += 1
        else:
            output_msg += f"- {ts.get(f'{pf}tdr-name')}: {ts.trs(td['Character'])}\n"

        baro_active = isBaroActive(t_act, t_exp)

        # OO appeared
        if baro_active:
            output_msg += (
                f"- {ts.get(f'{pf}status')}: ✅ **{ts.get(f'{pf}activate')}**\n"
            )
            output_msg += f"- {ts.get(f'{pf}end').format(time=convert_remain(t_exp))}\n"
            output_msg += f"- {ts.get(f'{pf}location')}: "
        # XX NOT appeared
        else:
            output_msg += (
                f"- {ts.get(f'{pf}status')}: ❌ *{ts.get(f'{pf}deactivate')}*\n"
            )
            output_msg += (
                f"- {ts.get(f'{pf}appear').format(time=convert_remain(t_act))}\n"
            )
            output_msg += f"- {ts.get(f'{pf}place')}: "

        # appear location
        output_msg += f"**{getSolNode(td['Node'])}**\n"

    f = getBaroImg(trader[0]["Character"])
    embed = discord.Embed(
        description=output_msg,
        color=embed_color if embed_color else color_decision(trader),
    )
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f


# todo-delay: 한글화
def w_voidTradersItem(trader) -> discord.Embed:
    if not trader:
        return err_embed("voidTraders")

    output_msg: str = ""
    pf = "cmd.void-traders-item."

    for item in trader:
        listItem: list = []

        if item.get("Manifest", []) == []:
            listItem.append(
                f"{ts.get(f'{pf}not-yet').format(time=convert_remain(item['Activation']['$date']['$numberLong']))}"
            )

        for jtem in item.get("Manifest", []):
            itype: str = ""
            k: str = jtem["ItemType"].replace("/Lotus/StoreItems", "").lower()

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

            iname = getLanguage(jtem["ItemType"])
            if "/lotus" in iname.lower():
                iname = f"__{add_space(extract_last_part(iname))}__"

            out = f"{itype} / {iname} / {jtem['PrimePrice']} {get_emoji('ducat')} {int((jtem['RegularPrice'])):,} {get_emoji('credit')}"
            listItem.append(out)

        listItem.sort()

        output_msg += f"# {ts.trs(item['Character'])} at {getSolNode(item['Node'])}\n\n"
        for jtem in listItem:
            output_msg += f"- {jtem}\n"
        output_msg += "\n"

    # f = img_file(getBaroImg())
    embed = discord.Embed(description=output_msg, color=color_decision(trader))
    # embed.set_thumbnail(url="attachment://i.png")

    return embed  # , f
