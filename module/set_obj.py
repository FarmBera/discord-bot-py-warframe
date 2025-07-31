from module.json_save import json_save


def set_obj(obj, filename: str) -> bool:
    return json_save(obj, f"json/{filename}.json")
