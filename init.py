# TODO: 기본 디렉토리 구조 만들어주는 코드 생성

# essential custom module
from translator import ts, language
from module.color import color
from module.api_request import API_Request
from module.save_log import save_log

from module.yaml_open import yaml_open
from module.json_load import json_load
from module.json_save import json_save
from module.get_obj import get_obj
from module.set_obj import set_obj
from module.cmd_obj_check import cmd_obj_check

from variables.keys import keys

if __name__ == "__main__":
    obj_origin = json_load()
    for item in keys:
        res = get_obj(item)
        if not res or res is None:
            set_obj(obj_origin[item], item)
        else:
            print(item)
