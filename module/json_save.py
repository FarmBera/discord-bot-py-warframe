import json
from module.color import color


def json_save(data, file_path) -> bool:
    """
    convert object(dict or list) and save as JSON file

    Args:
        data (dict or list): to save data
        file_path (str): JSON file path

    Returns:
        bool: save success True, failed to save
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except TypeError as e:
        print(f"{color['yellow']}ERR: Convertion Exception > {e}")
        return False
    except Exception as e:
        print(f"{color['red']}ERR > {e}")
        return False
