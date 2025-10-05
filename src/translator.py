import yaml

from src.utils.logging_utils import save_log
from src.constants.color import C
from src.constants.keys import MSG_BOT


class Lang:
    EN: str = "en"
    KO: str = "ko"


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
            save_log(cmd="translator.py", user=MSG_BOT, msg=msg)
            print(msg)
            # retry with default language: English
            try:
                with open(f"locale/{self.EN}.yml", "r", encoding="utf-8") as f:
                    self.translations = yaml.safe_load(f)
            except FileNotFoundError:
                msg = f"{C.red}[warn]: Default translation file 'en.yml' also not found.{C.default}"
                save_log(type="error", cmd="translator.py", user=MSG_BOT, msg=msg)
                print(msg)

    def get(self, key, **kwargs):
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
            return keys[-1]

    # TODO: 인자 하나만 받게 수정
    def trs(self, key):
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


# language initialize
language = input("Select Language (en/ko) >> ")
# language = Lang.EN  # temporary
# language = Lang.KO  # temporary
if language not in [Lang.EN, Lang.KO]:  # input check
    print(
        f"{C.red}Unknown string: {C.yellow}'{language}'. {C.white}will setup default lang: {C.cyan}{Lang.EN}{C.default}"
    )
    language = Lang.EN
ts = Translator(lang=language)
