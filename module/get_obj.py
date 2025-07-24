from module.json_load import json_load


def get_obj(name: str):
    return json_load(f"json/{name}.json")
