import discord
import datetime as dt

from translator import ts


def W_news(newses, *lang):
    if newses == False:
        return ts.get("general.error-cmd")

    if newses is None:
        return None

    idx: int = 0
    limit: int = 20
    output_msg: str = ""
    date_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"

    # output_msg: str = "# [Warframe News](https://www.warframe.com/search)\n\n"
    output_msg += f"# {ts.get('cmd.news.title')}\n\n"

    # sort data
    newses = sorted(
        newses,
        key=lambda item: dt.datetime.strptime(item["date"], date_format),
        reverse=True,  # asc/desc order
    )

    # process each news
    for item in newses:
        # exclude news
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
        # output_msg += f"- [{item['message']}]({item['link']})\n"
        # - time: {item['date']}"
        # - image: {item['imageLink']}

        idx += 1
        if idx >= limit:
            break

    embed = discord.Embed(
        # title=f"# {ts.get('cmd.news.title')}\n\n",
        description=output_msg,
        color=0x00FFFF,
        url=newses[-1]["link"],
    )
    embed.set_thumbnail(url=newses[-1]["imageLink"])

    # return output_msg
    return embed
