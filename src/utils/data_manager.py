from src.utils.file_io import json_load, json_save
from src.constants.color import C


def get_obj(json_name: str):
    return json_load(f"json/{json_name}.json")


def set_obj(obj, filename: str) -> bool:
    return json_save(obj, f"json/{filename}.json")


def cmd_obj_check(name):
    obj = get_obj(name)
    if not obj:  # or not obj:
        print(f"{C.red}[err] Unknown '{name}' command. (from cmd_obj_check){C.default}")
        return False

    return obj
