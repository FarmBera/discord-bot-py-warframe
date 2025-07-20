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
            # 기본 언어(예: 영어)로 대체 로드하는 로직을 추가할 수도 있습니다.
            try:
                with open("locale/en.yml", "r", encoding="utf-8") as f:
                    self.translations = yaml.safe_load(f)
            except FileNotFoundError:
                print("[warn]: Default translation file 'en.yml' also not found.")

    def get(self, key, **kwargs):
        """
        계층적인 키를 받아 번역문을 반환합니다. (예: 'main_screen.title')
        """
        keys = key.split(".")
        value = self.translations
        try:
            for k in keys:
                value = value[k]
            # kwargs가 있으면 format을 적용하여 변수를 치환합니다.
            return value.format(**kwargs) if kwargs else value
        except (KeyError, TypeError):
            # 키를 찾지 못하면 키 자체를 반환하여 어떤 텍스트가 누락되었는지 쉽게 알 수 있게 합니다.
            return key


# 사용 예시 (이 파일에서 직접 실행 시)
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
