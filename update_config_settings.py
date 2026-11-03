with open('tmp/minecraft-build-v2/src/main/resources/config.yml', 'r', encoding='utf-8') as f:
    conf = f.read()

# Add require-flat-plot setting under settings:
if 'require-flat-plot' not in conf:
    conf = conf.replace('settings:\n', 'settings:\n  # Требовать ли выравнивания участка перед началом строительства нового здания\n  require-flat-plot: true\n  # Максимально допустимая разница высот на строительной площадке (в блоках)\n  max-allowed-height-diff: 1\n\n')

with open('tmp/minecraft-build-v2/src/main/resources/config.yml', 'w', encoding='utf-8') as f:
    f.write(conf)

print("Updated config.yml successfully!")
