import os

from translator import ts
from var.color import color
from module.api_request import API_Request
from module.save_log import save_log
from module.json_load import json_load
from module.get_obj import get_obj
from module.set_obj import set_obj
from var.keys import keys

if __name__ == "__main__":
    print("API Requesting...")
    RESPONSE_CODE = API_Request()
    if RESPONSE_CODE != 200:
        raise ValueError("Response code is NOT 200!")
    print(f"Done! Code: {RESPONSE_CODE}")

    dir_base = os.getcwd()

    dir_json = [item.replace(".json", "") for item in os.listdir(f"{dir_base}/json")]

    prefix: str = "mkdir > "
    prefix_err: str = "Already exists dir > "

    try:
        os.mkdir("json")
        print(f"{prefix}json")
    except:
        msg = f"{color['yellow']}{prefix_err}'json'"
        save_log(cmd="init.py", user="console", msg=msg)
        print(msg)

    try:
        os.mkdir("log")
        print(f"{prefix}json")
    except:
        msg = f"{color['yellow']}{prefix_err}'log'"
        save_log(cmd="init.py", user="console", msg=msg)
        print(msg)

    obj_origin = json_load()
    for item in keys:
        if item in dir_json:
            print(f"{color['green']}File exists > {item}.json")  # VAR
            continue

        res = get_obj(item)
        if not res or res is None:
            set_obj(obj_origin[item], item)
        else:
            print(item)

    print(color["default"], end="")
