import os
import requests

from src.constants.color import C
from src.utils.api_legacy import API_Request
from src.utils.data_manager import set_obj
from src.constants.keys import keys, JSON


print("API Requesting...")
RESPONSE: requests.Response = API_Request()
if RESPONSE.status_code != 200 or not RESPONSE:
    raise ValueError("Response code is NOT 200! Aborted!")
print(f"Done! Code: {RESPONSE.status_code} (eta: {RESPONSE.elapsed})")

dir_base = os.getcwd()

prefix: str = "mkdir > "
prefix_err: str = "Already exists dir > "

try:
    os.mkdir(f"{dir_base}/{JSON}")
    print(f"{prefix}{JSON}")
except:
    msg = f"{prefix_err}'json'"
    print(C.yellow, msg)

try:
    os.mkdir("log")
    print(f"{prefix}log")
except:
    msg = f"{prefix_err}'log'"
    print(C.yellow, msg)


dir_json = [item.replace(".json", "") for item in os.listdir(f"{dir_base}/{JSON}")]

obj_origin = RESPONSE.json()
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
