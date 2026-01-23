from config.config import Lang


def processNews(obj_prev, obj_new) -> tuple[list, list]:
    news_old: list = []
    news_new: list = []

    # extract selected language only
    for item in obj_prev:
        for msg in item["Messages"]:
            if msg["LanguageCode"] in [Lang.EN, Lang.KO]:
                news_old.append(item)
                break
    for item in obj_new:
        for msg in item["Messages"]:
            if msg["LanguageCode"] in [Lang.EN, Lang.KO]:
                news_new.append(item)
                break

    return news_old, news_new
