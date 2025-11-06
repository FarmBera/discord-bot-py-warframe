import requests
import asyncio

from src.translator import language as lang
from config.TOKEN import (
    base_url_warframe,
    base_url_market,
)
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.utils.times import timeNowDT
from src.utils.logging_utils import save_log

params_market: dict = {"Language": lang, "Platform": "pc"}


# usage for main api
async def API_Request(log_lock: asyncio.Lock, res_source: str = "Unknown Source"):
    """API request function for Warframe status

    Args:
        log_lock (asyncio.Lock): Lock for log system. Requred!
        res_source (str, optional): code position of the api request. Defaults to "Unknown Source".

    Returns:

        None: failed to request api
    """
    start_time = timeNowDT()
    response = None

    # API Request
    try:
        response = requests.get(base_url_warframe, timeout=60)
    except Exception as e:
        elapsed_time = timeNowDT() - start_time
        msg = f"[err] API request failed!"
        obj = f"{elapsed_time}/{e}"
        print(timeNowDT(), C.red, msg, obj, elapsed_time, C.default)
        await save_log(
            lock=log_lock,
            type="err",
            cmd="send_request()",
            user=MSG_BOT,
            msg=msg,
            obj=obj,
        )
        return None

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        elapsed_time = timeNowDT() - start_time

        msg = f"[warn] response code is not 200"
        obj = f"{res_code}/{elapsed_time}"
        await save_log(
            lock=log_lock,
            type="err",
            cmd="API_REQUEST()",
            user=MSG_BOT,
            msg=msg,
            obj=obj,
        )
        print(timeNowDT(), C.red, msg, res_code, elapsed_time, C.default)
        return response

    # check response (is not empty or err value)
    if response is None:
        elapsed_time = timeNowDT() - start_time

        msg = f"[err] response is Empty!"
        obj = f"{res_code}/{elapsed_time}/{response}"
        print(timeNowDT(), C.red, msg, res_code, elapsed_time, C.default)
        await save_log(
            lock=log_lock,
            type="api",
            cmd="API_REQUEST()",
            user=MSG_BOT,
            msg=msg,
            obj=obj,
        )
        return None

    # save data
    # try:
    #     with open(JSON_PATH, "w", encoding="utf-8") as json_file:
    #         json.dump(response, json_file, ensure_ascii=False, indent=2)
    # except Exception as e:
    #     elapsed_time = timeNowDT() - start_time

    #     msg = f"[err] Error on saving file!"
    #     obj = f"{elapsed_time}/{e}"
    #     print(timeNowDT(), C.red, msg, elapsed_time, C.default)
    #     await save_log(
    #         lock=log_lock,
    #         type="err",
    #         cmd="API_REQUEST()",
    #         user=MSG_BOT,
    #         msg=msg,
    #         obj=obj,
    #     )
    #     return response

    elapsed_time = timeNowDT() - start_time
    msg = f"[info] API request successful. {res_source}"
    # print(C.red, msg, C.default, sep="")
    await save_log(
        lock=log_lock,
        type="api",
        cmd="API_REQUEST()",
        user=MSG_BOT,
        msg=msg,
        obj=f"{res_code}/{elapsed_time}",
    )

    return response


# usage for market api
def API_MarketSearch(item_name: str):
    """API request function for warframe.market search

    Args:
        req_source (str): code position of the api request (for debugging)
        query (str): fixed name
        item_name (str): item name to search

    Returns:
        _type_: _description_
    """
    response: requests.Response = None

    # API Request
    try:
        # orders/item/{slug}
        response = requests.get(
            url=f"{base_url_market}orders/item/{item_name}",
            headers=params_market,
            timeout=60,
        )
    except Exception as e:
        msg = f"[err] API request failed! (from API_MarketSearch)"
        print(timeNowDT(), C.yellow, msg, C.red, e, C.default)
        return None

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        msg = f"[warn] response code is not 200 (from API_MarketSearch)"
        print(C.red, res_code, msg, C.default)
        return response

    # check response (is not empty)
    if response is None:
        msg = f"[err] response is Empty!"
        print(C.red, msg, C.default)
        return response

    return response
