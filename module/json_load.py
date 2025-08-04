import json
from variables.color import color
from TOKEN import DEFAULT_JSON_PATH


def json_load(file_path=DEFAULT_JSON_PATH):
    """
    read json file at provided path and return

    Args:
        file_path (str): JSON file path

    Returns:
        dict or list: JSON file object.
        None: file not found || parse error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"{color['yellow']}ERR: File Not Found > {file_path}{color['default']}")
        return None
    except json.JSONDecodeError:
        print(
            f"{color['yellow']}ERR: JSON Decode Exception > {file_path}{color['default']}"
        )
        return None
    except Exception as e:
        print(f"{color['red']}ERR: {e}")
        return None
