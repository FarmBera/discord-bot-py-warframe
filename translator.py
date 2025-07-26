import yaml

from module.color import color


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
        키를 받아 번역문을 반환 (ex: 'main_screen.title')
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
language = input("Select Language (en/ko) >> ")
if language not in ["en", "ko"]:  # input check
    # print(f"{color['red']}Selection ERR:{color['yellow']}'{language}'. {color['red']}abort.")
    print(
        f"{color['red']}Unknown string: {color['yellow']}'{language}'. {color['white']}will setup default lang: {color['cyan']}'en'{color['default']}"
    )
    language = "en"
    # exit(1)
ts = Translator(lang=language)

print(color["yellow"], ts.get("init.init"), end="", sep="")
print(ts.get("init.components"), end="")
print(color["green"], ts.get("init.done"), sep="")
print(color["yellow"], ts.get("init.start"), end="", sep="")
