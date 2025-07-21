import yaml


class Translator:
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        try:
            with open(f"locale/{self.lang}.yml", "r", encoding="utf-8") as f:
                self.translations = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"[warn]: Translation file for '{self.lang}' not found.")
            # 기본 언어(예: 영어)로 대체 로드하는 로직 추가
            try:
                with open("locale/en.yml", "r", encoding="utf-8") as f:
                    self.translations = yaml.safe_load(f)
            except FileNotFoundError:
                print("[warn]: Default translation file 'en.yml' also not found.")

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
#     # 한국어 번역기 생성
#     t_ko = Translator(lang="ko")
#     print(t_ko.get("main_screen.title"))
#     print(t_ko.get("main_screen.welcome_message", username="홍길동", mail_count=5))

#     print("-" * 20)

#     # 영어 번역기 생성
#     t_en = Translator(lang="en")
#     print(t_en.get("common.confirm"))
#     print(t_en.get("non_existent.key"))  # 존재하지 않는 키 테스트
