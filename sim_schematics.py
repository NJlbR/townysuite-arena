with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

import re

for name in ['generateCityWallSchematic', 'generateTownHallSchematic']:
    idx = text.find(f'public BuildingSchematic {name}()')
    body = text[idx:idx+4000]
    print(f"=== {name} ===")
    print(body[:2000])

