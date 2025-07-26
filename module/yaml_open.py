import yaml


def yaml_open(fname):
    obj = None
    try:
        with open(f"{fname}.yml", "r", encoding="utf-8") as f:
            obj = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[warn]: '{fname}' not found.")

    return obj
