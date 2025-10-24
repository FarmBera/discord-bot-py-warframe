import os

from src.translator import ts
from src.constants.color import C
from src.utils.api_request import API_Request
from src.utils.logging_utils import save_log
from src.utils.file_io import json_load
from src.utils.data_manager import get_obj
from src.utils.data_manager import set_obj
from src.constants.keys import keys, JSON


print("API Requesting...")
RESPONSE_CODE = API_Request("init")
if RESPONSE_CODE != 200:
    raise ValueError("Response code is NOT 200! Aborted!")
print(f"Done! Code: {RESPONSE_CODE}")

dir_base = os.getcwd()

prefix: str = "mkdir > "
prefix_err: str = "Already exists dir > "

try:
    os.mkdir(f"{dir_base}/{JSON}")
    print(f"{prefix}{JSON}")
except:
    msg = f"{prefix_err}'json'"
    save_log(cmd="init.py", user="console", msg=msg)
    print(C.yellow, msg)

try:
    os.mkdir("log")
    print(f"{prefix}log")
except:
    msg = f"{prefix_err}'log'"
    save_log(cmd="init.py", user="console", msg=msg)
    print(C.yellow, msg)


dir_json = [item.replace(".json", "") for item in os.listdir(f"{dir_base}/{JSON}")]

obj_origin = json_load()
for item in keys:
    if item in dir_json:
        print(f"{C.green}File exists > {item}.json")  # VAR
        # continue

    # res = get_obj(item)
    # if not res:
    set_obj(obj_origin[item], item)
    # else:
    print(f"{C.cyan}{item}")

print(C.default, end="")
