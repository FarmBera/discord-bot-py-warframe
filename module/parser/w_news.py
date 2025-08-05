import discord
import datetime as dt

from translator import ts
from times import JSON_DATE_PAT


def W_news(newses, *lang):
    if newses == False:
        return discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000)

    if newses is None:
        return None

    idx: int = 0
    limit: int = 20
    output_msg: str = ""

    # output_msg: str = "# [Warframe News](https://www.warframe.com/search)\n\n"
    output_msg += f"# {ts.get('cmd.news.title')}\n\n"

    newses = sorted(
        newses,
        key=lambda item: dt.datetime.strptime(item["date"], JSON_DATE_PAT),
        reverse=True,
    )

    # process
    for item in newses:
        # excluded news
        if item["message"] in [
            "Join the official Warframe Discord server",
            "Check out the official Warframe Wiki ",
            "Visit the official Warframe Forums!",
        ]:
            continue

        try:
            output_msg += f"- [{item['translations'][lang]}]({item['link']})\n"
        except:
            output_msg += f"- [{item['translations']['en']}]({item['link']})\n"

        idx += 1
        if idx >= limit:
            break

    embed = discord.Embed(
        description=output_msg,
        color=0x00FFFF,
    )
    embed.set_image(url=newses[-1]["imageLink"])

    return embed
