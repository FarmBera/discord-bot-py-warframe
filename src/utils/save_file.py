import os


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
