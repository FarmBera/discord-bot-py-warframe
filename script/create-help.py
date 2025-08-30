from src.utils.file_io import yaml_open

print()

cmds = yaml_open("locale/ko")
krms = yaml_open("locale/ko")

e = cmds["cmd"]
k = krms["cmd"]
for key in e.keys():
    t = f"- `{e[key]['cmd']}`: {k[key]['desc']}"
    print(t)

print()
