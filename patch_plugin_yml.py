import sys

with open('tmp/minecraft-build/src/main/resources/plugin.yml', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("version: 1.2.0", "version: 1.3.0")

with open('tmp/minecraft-build/src/main/resources/plugin.yml', 'w', encoding='utf-8') as f:
    f.write(content)
