import json
import yaml

from src.constants.color import C


# general files


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


def save_file(filepath: str, content: str) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    except IOError as e:
        print(f"An I/O error occurred while saving the file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


# json


def json_load(file_path):
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
        print(f"{C.yellow}ERR: File Not Found > {file_path}{C.default}")
        return None
    except json.JSONDecodeError:
        print(f"{C.yellow}ERR: JSON Decode Exception > {file_path}{C.default}")
        return None
    except Exception as e:
        print(f"{C.red}ERR: {e}")
        return None


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
        print(f"{C.red}[err] Convertion Error > {e}")
        return False
    except Exception as e:
        print(f"{C.red}[err] Unknown Error in [json_save] func > {e}")
        return False


# yaml


def yaml_open(fname):
    obj = None
    try:
        with open(f"{fname}.yml", "r", encoding="utf-8") as f:
            obj = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[warn]: '{fname}' not found.")

    return obj
