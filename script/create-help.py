from src.utils.file_io import yaml_open

lang_cmd = input("Language for cmd (en/ko) > ")
lang_desc = input("Language for desc (en/ko) > ")


print()

cmds = yaml_open(f"locale/{lang_cmd}")
krms = yaml_open(f"locale/{lang_desc}")

e = cmds["cmd"]
k = krms["cmd"]
for key in e.keys():
    try:
        t = f"- `{e[key]['cmd']}`: {k[key]['desc']}"
        print(t)
    except:
        pass

print()
