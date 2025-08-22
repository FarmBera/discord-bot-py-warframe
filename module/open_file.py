import json
from variables.color import color


def open_file(file_path):
    """
    read file at provided path and return

    Args:
        file_path (str): every text file path

    Returns:
        string
        None: file not found || parse error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
        return data
    except FileNotFoundError:
        print(f"{color['yellow']}ERR: File Not Found > {file_path}{color['default']}")
        return None
    except Exception as e:
        print(f"{color['red']}ERR: {e}")
        return None
