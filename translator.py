import yaml

from variables.color import color


class Translator:
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        try:
            with open(f"locale/{self.lang}.yml", "r", encoding="utf-8") as f:
                self.translations = yaml.safe_load(f)
        except FileNotFoundError:
            print(
                f"{color['yellow']}[warn]: Translation file for '{self.lang}' not found.{color['default']}"
            )
            # retry with default language: English
            try:
                with open("locale/en.yml", "r", encoding="utf-8") as f:
                    self.translations = yaml.safe_load(f)
            except FileNotFoundError:
                print(
                    f"{color['red']}[warn]: Default translation file 'en.yml' also not found.{color['default']}"
                )

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


# if __name__ == "__main__":
# language initialize
# language = input("Select Language (en/ko) >> ")  # TEMPORARYˇ
language = "en"  # temporary
if language not in ["en", "ko"]:  # input check
    print(
        f"{color['red']}Unknown string: {color['yellow']}'{language}'. {color['white']}will setup default lang: {color['cyan']}'en'{color['default']}"
    )
    language = "en"
ts = Translator(lang=language)
