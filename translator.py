import yaml

from module.save_log import save_log
from variables.color import color
from variables.keys import MSG_BOT


class Translator:
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        try:
            with open(f"locale/{self.lang}.yml", "r", encoding="utf-8") as f:
                self.translations = yaml.safe_load(f)
        except FileNotFoundError:
            msg = f"{color['yellow']}[warn]: Translation file for '{self.lang}' not found.{color['default']}"
            save_log(cmd="translator.py", user=MSG_BOT, msg=msg)
            print(msg)
            # retry with default language: English
            try:
                with open("locale/en.yml", "r", encoding="utf-8") as f:
                    self.translations = yaml.safe_load(f)
            except FileNotFoundError:
                msg = f"{color['red']}[warn]: Default translation file 'en.yml' also not found.{color['default']}"
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
            return key


# language initialize
# language = input("Select Language (en/ko) >> ")  # TEMPORARYˇ
language = "en"  # temporary
if language not in ["en", "ko"]:  # input check
    print(
        f"{color['red']}Unknown string: {color['yellow']}'{language}'. {color['white']}will setup default lang: {color['cyan']}'en'{color['default']}"
    )
    language = "en"
ts = Translator(lang=language)
