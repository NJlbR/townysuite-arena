import sys

with open('tmp/minecraft-build/src/main/resources/buildings.yml', 'r', encoding='utf-8') as f:
    content = f.read()

target = """blueprints:
  hospital:"""

replacement = """blueprints:
  bank:
    name: "Central Bank"
    name-ru: "Центральный Банк"
    description: "Позволяет жителям и мэру совершать финансовые операции (пополнять/снимать деньги казны) в радиусе 5 чанков."
    icon: "GOLD_INGOT"
    required-skill-level: 5
    is-world-wonder: false
    chunk-footprint:
      width-chunks: 1
      length-chunks: 1
    dimensions:
      height-y: 10
    resources:
      STONE_BRICKS: 128
      QUARTZ_BLOCK: 64
      GOLD_BLOCK: 4
      IRON_BARS: 32
    buffs:
      economy-access: true
  hospital:"""

if target in content:
    with open('tmp/minecraft-build/src/main/resources/buildings.yml', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched buildings.yml successfully.")
else:
    print("Target content not found!")
