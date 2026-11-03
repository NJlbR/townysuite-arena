import re

with open('tmp/minecraft-build/src/main/resources/config.yml', 'r', encoding='utf-8') as f:
    cfg = f.read()

cfg = cfg.replace('title: "&f\\uE000\\uE001\\uE002&8Чертежи и постройки"', 'title: "&f\\uE000\\uE001\\uE002&fЧертежи и постройки"')

with open('tmp/minecraft-build/src/main/resources/config.yml', 'w', encoding='utf-8') as f:
    f.write(cfg)

print("Title verified")
