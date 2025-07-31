import requests
import json
import datetime as dt

# from TOKEN import base_url, headers, query
from module.color import color
from module.save_log import save_log

from module.json_save import json_save

# api link & args
base_api_url = "https://api.warframestat.us/"

"""
pc
items
mods
warframes
weapons
pc/rivens
"""
query = "pc"
base_url = f"{base_api_url}{query}"
headers = {"Accept-Language": "en"}  # en / ko


response = None
date_start = None
date_end = None
data = None


############
date_origin_pat: str = "%Y-%m-%dT%H:%M:%S.%fZ"


# default functions
def divider():
    print("=" * 45)


def convert_date_time(timestamp: str):
    return dt.datetime.strptime(timestamp, date_origin_pat)
    # .strftime("%Y-%m-%d %H:%M:%S")


def convert_remain_time(timestamp: str, footer: str = "남았습니다!") -> str:
    if timestamp == None:
        print(f"Timestamp ERR >> {timestamp}")
        raise ValueError("timestamp is NULL")
    try:
        td = dt.datetime.strptime(timestamp, date_origin_pat)
    except:
        td = timestamp
    timenow = dt.datetime.now()
    diff = timenow - td
    milisec = diff.microseconds // 1000 // 10

    diff = int(diff.total_seconds())

    hour = diff // 3600
    min = (diff % 3600) // 60
    sec = diff % 60

    # TODO: f-string 3자리 나오는 문제 수정
    result = f"{hour}시간 {min}분 {sec}.{milisec:02d}초"
    print(result)

    return None


# api request func
def send_request():
    date_start = dt.datetime.now()
    response = requests.get(base_url, headers=headers)
    return dt.datetime.now() - date_start, response


def check_request(est, response):
    # check response value
    if response is None:
        print(f"{color['red']}ERR: response is NULL{color['default']}")
        # raise ValueError("ERR: response is NULL")

    # check response code
    res_code = response.status_code
    if res_code != 200:
        print(f"{color['red']}ERR: Failed API Request >> {res_code}{color['default']}")
        # raise ArithmeticError(f"ERR: Failed API Request >> {res_code}")

    # process response
    response = response.json()  # convert response data
    fname = f"Warframe_{query}.json"  # file name to save

    # save received data to JSON file
    try:
        with open(fname, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{color['red']}ERR with saving file{color['default']}")

    return response


# usage
def API_Request(*args):
    if not args:
        save_log(cmd="API_Request()", user="bot.self", msg=f"API Requested")
    else:
        save_log(
            cmd="API_Request()", user="bot.self", msg=f"API Requested (from {args})"
        )

    est, response = send_request()
    response = check_request(est, response)
    return est, response
