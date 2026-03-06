import discord

from config.TOKEN import base_url_bounty, BOUNTY_JSON_PATH
from src.constants.keys import BOUNTY
from src.translator import ts
from src.utils.api_request import API_Request
from src.utils.data_manager import (
    get_obj,
    getLanguage,
    solNodes,
)
from src.utils.return_err import err_embed

pf: str = "cmd.bounty."


async def handleNewBounty(pool):
    prev: dict = get_obj(BOUNTY)
    new: dict = await API_Request(pool, base_url_bounty, BOUNTY_JSON_PATH)
    if not prev or not new:
        return None, False

    if prev.get("rot") == new.get("rot"):
        return new, False

    return new, True


def generateBounty(bounty, b_key):
    output = ""
    for i in bounty[b_key]:
        node = solNodes[i["node"]]
        output += f"- **{node['type']}** - {getLanguage(i['challenge'])}\n"
    return output


def w_bounty(bounty) -> discord.Embed:
    """
    parse bounty data (zariman & entrati)

    :param bounty: bounty data
    :return: parsed bounty data & img file name
    """
    if not bounty:
        return err_embed("bounty")

    output_msg: str = ""
    bty = bounty["bounties"]

    output_msg += ts.get(f"{pf}title-z")
    output_msg += generateBounty(bty, "ZarimanSyndicate")

    output_msg += ts.get(f"{pf}title-e")
    output_msg += generateBounty(bty, "EntratiLabSyndicate")

    embed = discord.Embed(description=output_msg, color=discord.Color.darker_grey())
    # embed.set_thumbnail(url="attachment://i.webp")
    return embed


# print(w_bounty(get_obj(BOUNTY)).description)
