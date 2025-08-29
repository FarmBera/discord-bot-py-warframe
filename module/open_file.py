import json
from var.color import C


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
        print(f"{C.red}[err] File Not Found > {file_path}{C.default}")
        return None
    except Exception as e:
        print(f"{C.red}[err] Unknown Error in [open_file] func: {e}")
        return None
