from module.json_save import json_save


def set_obj(obj, name: str) -> bool:
    return json_save(obj, f"json/{name}.json")
