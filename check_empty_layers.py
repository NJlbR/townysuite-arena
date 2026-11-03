with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

# Let's inspect all schematics
# We already found:
# generateCityWallSchematic has loop y in 0..3, y4=4, y5=5 (all layers 0,1,2,3,4,5 present)
# But what about generateTownHallSchematic?
# Let's check all blocks in TownHall!
idx = text.find('public BuildingSchematic generateTownHallSchematic()')
body = text[idx:]

import re
layers = {}
for m in re.finditer(r'new SchematicBlock\(\s*(\d+|[a-zA-Z0-9_+ -]+)\s*,\s*(\d+)\s*,\s*(\d+|[a-zA-Z0-9_+ -]+)', body):
    y = int(m.group(2))
    layers[y] = layers.get(y, 0) + 1

print("TownHall literal y layers:", sorted(layers.keys()))
