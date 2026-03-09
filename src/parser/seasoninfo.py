import discord

from config.TOKEN import base_url_bounty, BOUNTY_JSON_PATH
from src.constants.keys import BOUNTY, SEASONINFO
from src.translator import ts
from src.utils.api_request import API_Request
from src.utils.data_manager import get_obj, getLanguage
from src.utils.return_err import err_embed
from src.utils.times import convert_remain

pf: str = "cmd.seasoninfo."


async def handleNewSeasoninfo(pool):
    prev: dict = get_obj(BOUNTY)
    new = await API_Request(pool, base_url_bounty, BOUNTY_JSON_PATH)
    new = new.json()
    if not prev or not new:
        return None, False

    if prev.get("rot") == new.get("rot"):
        return new, False

    return new, True


def w_nightwave(season) -> tuple[discord.Embed, str]:
    """
    parse nightwave data

    :param season: nightwave data (SeasonInfo)
    :return: parsed nightwave data & img file name
    """
    if not season:
        return err_embed("nightwave (seasoninfo)"), ""

    output_msg: str = ts.get(f"{pf}title")
    output_msg += ts.get(f"{pf}expiry").format(
        time=convert_remain(season["Expiry"]["$date"]["$numberLong"])
    )
    preset=ts.get(f'{pf}output')
    for chal in season["ActiveChallenges"]:
        output_msg += preset.format(
            value=getLanguage(chal["Challenge"], "value"),
            desc=getLanguage(chal["Challenge"], "desc"),
        )

    embed = discord.Embed(description=output_msg, color=discord.Color.darker_grey())
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "nightwave"


print(w_nightwave(get_obj(SEASONINFO))[0].description)
