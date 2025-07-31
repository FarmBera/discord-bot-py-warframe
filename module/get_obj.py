from module.json_load import json_load


def get_obj(json_name: str):
    return json_load(f"json/{json_name}.json")
