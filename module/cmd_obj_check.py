from module.get_obj import get_obj
from variables.color import color
from translator import ts


def cmd_obj_check(name):
    obj = get_obj(name)
    if obj is None:  # or not obj:
        print(
            f"{color['red']}[err] Unknown '{name}' command. (from cmd_obj_check){color['default']}"
        )
        return False

    return obj
