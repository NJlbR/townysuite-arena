with open('tmp/minecraft-build/src/main/resources/config.yml', 'r', encoding='utf-8') as f:
    cfg = f.read()

# Replace the title and fill-empty-slots using basic replace
cfg = cfg.replace('title: "&f\\uE001"', 'title: "&f\\uE000\\uE001\\uE002&8Чертежи и постройки"')
cfg = cfg.replace('title: "&f\uE001"', 'title: "&f\\uE000\\uE001\\uE002&8Чертежи и постройки"')
cfg = cfg.replace('fill-empty-slots: true', 'fill-empty-slots: false')

with open('tmp/minecraft-build/src/main/resources/config.yml', 'w', encoding='utf-8') as f:
    f.write(cfg)

print("Config updated for modern RP")
