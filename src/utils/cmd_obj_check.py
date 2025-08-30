from module.get_obj import get_obj
from var.color import C
from translator import ts


def cmd_obj_check(name):
    obj = get_obj(name)
    if obj is None:  # or not obj:
        print(f"{C.red}[err] Unknown '{name}' command. (from cmd_obj_check){C.default}")
        return False

    return obj
