import sys

with open('tmp/minecraft-build/src/main/resources/buildings.yml', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('    buffs:\n      economy-access: true', '    buffs:\n      economy-access: true\n    particle-color: "#FFD700"')
content = content.replace('    buffs:\n      health-boost-hearts: 1\n      regeneration-level: 1', '    buffs:\n      health-boost-hearts: 1\n      regeneration-level: 1\n    particle-color: "#FF5555"')
content = content.replace('    buffs:\n      strength-level: 1\n      speed-level: 1', '    buffs:\n      strength-level: 1\n      speed-level: 1\n    particle-color: "#AAAAAA"')
content = content.replace('    buffs:\n      haste-level: 1', '    buffs:\n      haste-level: 1\n    particle-color: "#5555FF"')
content = content.replace('    buffs:\n      night-vision: true', '    buffs:\n      night-vision: true\n    particle-color: "#FFFF55"')
content = content.replace('    buffs:\n      haste-level: 2\n      resistance-level: 1', '    buffs:\n      haste-level: 2\n      resistance-level: 1\n    particle-color: "#FFAA00"')

with open('tmp/minecraft-build/src/main/resources/buildings.yml', 'w', encoding='utf-8') as f:
    f.write(content)
