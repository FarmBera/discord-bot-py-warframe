import discord
import datetime as dt

from src.translator import ts, language as lang
from src.utils.return_err import err_embed


def w_news(newses, LIMIT_OUTPUT_CNT: int = 30):
    if not newses:
        return err_embed("news")

    # idx: int = 0
    output_msg: str = ""

    output_msg += f"# {ts.get('cmd.news.title')}\n\n"

    news_news = []
    news_community = []

    class News:
        def __init__(self, id, date, title, link, url):
            self.id = id
            self.date = date
            self.title = title
            self.link = link
            self.url = url

    # process
    for item in newses:
        t_id = item["_id"]
        try:
            t_date = int(item["Date"]["$date"]["$numberLong"])
        except:
            t_date = ""
        t_title: str = ""
        t_link: str = ""
        t_url: str = ""

        t_link = item["Prop"]
        t_url = item.get("ImageUrl")

        for t_title in item["Messages"]:
            if t_title["LanguageCode"] == lang:
                t_title = t_title["Message"]

                if item.get("Community"):
                    news_community.append(
                        News(
                            id=t_id, date=t_date, title=t_title, link=t_link, url=t_url
                        )
                    )
                else:
                    news_news.append(
                        News(
                            id=t_id, date=t_date, title=t_title, link=t_link, url=t_url
                        )
                    )

    # reverse list
    news_news = news_news[::-1]
    news_community = news_community[::-1]

    output_msg += "## InGame News\n\n"
    for item in news_news:
        output_msg += f"- [{item.title}]({item.link})\n"

    output_msg += "\n## Community News\n\n"
    for item in news_community:
        output_msg += f"- [{item.title}]({item.link})\n"

        # idx += 1
        # if idx >= LIMIT_OUTPUT_CNT:
        #     break

    embed = discord.Embed(
        description=output_msg,
        color=0x00FFFF,
    )
    embed.set_image(
        url=newses[0].get(
            "ImageUrl", "https://cdn.warframestat.us/genesis/img/news-placeholder.png"
        )
    )

    return embed
