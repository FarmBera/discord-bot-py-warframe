from src.constants.keys import SPECIAL_ITEM_LIST
from src.utils.data_manager import getLanguage


def checkInvasions(obj_prev, obj_new):
    should_save_data = False

    prev_ids_set = {item["_id"]["$oid"] for item in obj_prev}
    new_ids_set = {item["_id"]["$oid"] for item in obj_new}
    if prev_ids_set != new_ids_set:
        should_save_data = True

    # extract missing ids (new invasion's id)
    missed_ids = [
        item["_id"]["$oid"]
        for item in obj_new
        if item["_id"]["$oid"] not in prev_ids_set
    ]
    # filter new invasions obj
    missing_invasions = [item for item in obj_new if item["_id"]["$oid"] in missed_ids]

    # filter invasions which having special items
    special_invasions = []
    for inv in missing_invasions:
        special_item_exist: bool = False

        item_list = [
            getLanguage(item["ItemType"]).lower()
            for reward in [
                inv.get("AttackerReward"),
                inv.get("DefenderReward"),
            ]
            if isinstance(reward, dict) and "countedItems" in reward
            for item in reward["countedItems"]
        ]

        for item in item_list:
            for se in SPECIAL_ITEM_LIST:
                if se in item:
                    special_item_exist = True
        if special_item_exist:
            special_invasions.append(inv)

    return should_save_data, special_invasions, missing_invasions
