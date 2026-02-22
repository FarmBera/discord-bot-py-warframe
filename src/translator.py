import yaml

from config.config import Lang, language
from src.constants.color import C


class Translator:
    EN: str = Lang.EN
    KO: str = Lang.KO

    def __init__(self, lang=EN):
        self.lang = lang
        self.translations = {}
        try:
            with open(f"locale/{self.lang}.yml", "r", encoding="utf-8") as f:
                self.translations = yaml.safe_load(f)
        except FileNotFoundError:
            msg = f"{C.yellow}[warn]: Translation file for '{self.lang}' not found.{C.default}"
            print(msg)
            try:  # retry with default language: English
                with open(f"locale/{self.EN}.yml", "r", encoding="utf-8") as f:
                    self.translations = yaml.safe_load(f)
            except FileNotFoundError:
                msg = f"{C.red}[warn]: Default translation file 'en.yml' also not found.{C.default}"
                print(msg)

    def get(self, key, **kwargs) -> str:
        """
        receive keys and return translated text (ex: 'main_screen.title')
        """
        keys = key.split(".")
        value = self.translations
        try:
            for k in keys:
                value = value[k]
            return value.format(**kwargs) if kwargs else value
        except (KeyError, TypeError):
            return key

    def trs(self, key) -> str:
        """
        receive SPECIAL keys (not officialy translated text in API) and return translated text (ex: 'ts.trs(SEARCH_QUERY)')
        """
        if language == self.EN:
            return key

        value = self.translations
        try:
            for k in ["trs", key.lower()]:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return key


# initialize language
if language not in [Lang.EN, Lang.KO]:  # input check
    print(
        f"{C.red}Unknown string: {C.yellow}'{language}'. {C.white}will setup default lang: {C.cyan}{Lang.EN}{C.default}"
    )
    language = Lang.EN
ts = Translator(lang=language)
