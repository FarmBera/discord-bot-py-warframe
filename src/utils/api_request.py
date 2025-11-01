import requests
import json
import datetime as dt
import asyncio

from config.TOKEN import (
    base_url_warframe,
    base_url_market,
    # params_warframe,
    params_market,
    DEFAULT_JSON_PATH,
    DEFAULT_MARKET_JSON_PATH,
)
from src.utils.file_io import json_load
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.constants.times import timeNowDT
from src.utils.logging_utils import save_log


async def send_request(
    log_lock: asyncio.Lock, res_source: str, query: str = ""
) -> int | None:
    """send API request and return response if return code exists

    Args:
        res_source (str): API request code source
        query (str, optional): additional URL query. market api usage only! Defaults to "".

    Returns:
        int: api request success and response code exist
        None: failed to request api
    """

    start_time = timeNowDT()
    response = None

    # setup variables
    if query:  # market api
        base_url = f"{base_url_market}/{query}"
        param = params_market
        JSON_PATH = DEFAULT_MARKET_JSON_PATH
    else:  # warframe api
        base_url = base_url_warframe
        param = None
        JSON_PATH = DEFAULT_JSON_PATH

    # API Request
    try:
        if param:
            response = requests.get(base_url, params=param, timeout=60)
        else:
            response = requests.get(base_url, timeout=60)
    except Exception as e:
        elapsed_time = timeNowDT() - start_time

        msg = f"[err] API request failed!"
        obj = f"{elapsed_time}/{e}"
        print(timeNowDT(), C.red, msg, elapsed_time, C.default)
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
        if not query:
            print(timeNowDT(), C.red, msg, res_code, elapsed_time, C.default)
        return res_code

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
        return res_code

    # parse JSON
    try:
        response = response.json()
    except Exception as e:
        elapsed_time = timeNowDT() - start_time

        msg = f"[err] JSON Decode ERROR ({elapsed_time})"
        obj = f"{elapsed_time}/{e}"
        print(timeNowDT(), C.red, msg, elapsed_time, C.default)
        await save_log(
            lock=log_lock,
            type="err",
            cmd="API_REQUEST()",
            user=MSG_BOT,
            msg=msg,
            obj=obj,
        )
        return res_code

    # save data
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        elapsed_time = timeNowDT() - start_time

        msg = f"[err] Error on saving file!"
        obj = f"{elapsed_time}/{e}"
        print(timeNowDT(), C.red, msg, elapsed_time, C.default)
        await save_log(
            lock=log_lock,
            type="err",
            cmd="API_REQUEST()",
            user=MSG_BOT,
            msg=msg,
            obj=obj,
        )
        return res_code

    elapsed_time = timeNowDT() - start_time
    msg = f"[info] API request successful. {res_source}"
    # print(C.red, msg, C.default, sep="")
    await save_log(
        lock=log_lock,
        type="api",
        cmd="API-Market" if query else "API_REQUEST()",
        user=MSG_BOT,
        msg=msg,
        obj=f"{res_code}/{elapsed_time}",
    )

    return res_code


# usage for main api
async def API_Request(lock: asyncio.Lock, args: str = "Unknown Source") -> int | None:
    """API request function for Warframe status

    Args:
        args (str, optional): code position of the api request. Defaults to "Unknown Source".

    Returns:
        int: api request success and response code exist
        None: failed to request api
    """
    return await send_request(lock, args)


# usage for market api
def API_MarketSearch(req_source: str, query: str, item_name: str):
    """API request function for warframe.market search

    Args:
        req_source (str): code position of the api request (for debugging)
        query (str): fixed name
        item_name (str): item name to search

    Returns:
        _type_: _description_
    """
    item_name = item_name.replace(" ", "_")
    return send_request(req_source, f"{query}/{item_name}/orders")
