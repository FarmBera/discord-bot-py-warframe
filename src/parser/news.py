import discord
import datetime as dt

from src.translator import ts, language as lang
from src.constants.times import JSON_DATE_PAT
from src.utils.return_err import err_embed


def w_news(newses, LIMIT_OUTPUT_CNT: int = 20):
    if not newses:
        return err_embed("news")

    idx: int = 0
    output_msg: str = ""

    output_msg += f"# {ts.get('cmd.news.title')}\n\n"

    newses = sorted(
        newses,
        key=lambda item: dt.datetime.strptime(item["date"], JSON_DATE_PAT),
        reverse=True,
    )

    # process
    for item in newses:
        if item["message"] in [  # excluded news
            "Join the official Warframe Discord server",
            "Check out the official Warframe Wiki ",
            "Visit the official Warframe Forums!",
        ]:
            continue

        try:
            output_msg += f"- [{item['translations'][lang]}]({item['link']})\n"
        except:
            output_msg += f"- [{item['message']}]({item['link']})\n"

        idx += 1
        if idx >= LIMIT_OUTPUT_CNT:
            break

    embed = discord.Embed(
        description=output_msg,
        color=0x00FFFF,
    )
    embed.set_image(url=newses[0]["imageLink"])

    return embed
