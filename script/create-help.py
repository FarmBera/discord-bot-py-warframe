from module.yaml_open import yaml_open

print()

cmds = yaml_open("locale/en")
krms = yaml_open("locale/ko")

e = cmds["cmd"]
k = krms["cmd"]
for key in e.keys():
    t = f"- `{e[key]['cmd']}`: {k[key]['desc']}"
    print(t)

print()
