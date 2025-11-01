import discord
import datetime as dt

from config.config import Lang
from src.translator import ts, language as lang
from src.utils.return_err import err_embed
from src.utils.data_manager import getLanguage


def w_news(newses, LIMIT_OUTPUT_CNT: int = 50):
    if not newses:
        return err_embed("news")

    pf: str = "cmd.news."

    # idx: int = 0
    output_msg: str = ""

    output_msg += f"# {ts.get(f'{pf}title')}\n\n"

    news_news = []
    news_community = []

    class News:
        def __init__(self, id, date, title, url, img):
            self.id = id
            self.date = date
            self.title = title
            self.url = url
            self.img = img

    # process
    for item in newses:
        t_id = item["_id"]
        try:
            t_date = int(item["Date"]["$date"]["$numberLong"])
        except:
            t_date = ""
        t_title: str = ""
        t_url: str = ""
        t_img: str = ""

        t_url = item["Prop"].replace(" ", "")
        if not t_url:
            t_url = str(item["Links"][0]["Link"]).replace(" ", "")

        t_img = item.get("ImageUrl")

        for t_title in item["Messages"]:
            if item.get("Community") and t_title["LanguageCode"] == Lang.EN:
                t_title = getLanguage(t_title["Message"])
                news_community.append(
                    News(id=t_id, date=t_date, title=t_title, url=t_url, img=t_img)
                )
                continue

            if t_title["LanguageCode"] == lang:
                t_title = getLanguage(t_title["Message"])
                news_news.append(
                    News(id=t_id, date=t_date, title=t_title, url=t_url, img=t_img)
                )

    # reverse list
    news_news = news_news[::-1]
    news_community = news_community[::-1]

    if news_news:
        output_msg += f"## {ts.get(f'{pf}ingame')}\n\n"
        for item in news_news:
            output_msg += f"- [{item.title}]({item.url})\n"

    if news_community:
        output_msg += f"\n## {ts.get(f'{pf}comu')}\n\n"
        for item in news_community:
            output_msg += f"- [{item.title}]({item.url})\n"

        # idx += 1
        # if idx >= LIMIT_OUTPUT_CNT:
        #     break

    embed = discord.Embed(
        description=output_msg,
        color=0x00FFFF,
    )
    img_url = news_news[0].img
    embed.set_image(
        url=(
            img_url
            if img_url
            else "https://cdn.warframestat.us/genesis/img/news-placeholder.png"
        )
    )
    return embed
