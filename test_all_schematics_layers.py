with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java') as f:
    code = f.read()

import re

for schem_name in ['Bank', 'Hospital', 'Barracks', 'Library', 'Watchtower']:
    idx = code.find(f'generate{schem_name}Schematic')
    if idx == -1: continue
    idx2 = code.find('return new BuildingSchematic', idx)
    sub = code[idx:idx2]
    matches = re.findall(r'new SchematicBlock\((\d+),\s*(\d+),\s*(\d+),\s*Material\.([A-Z_]+)\)', sub)
    by_layer = {}
    for m in matches:
        y = int(m[1])
        mat = m[3]
        by_layer.setdefault(y, {})
        by_layer[y][mat] = by_layer[y].get(mat, 0) + 1
    print(f"=== {schem_name} ===")
    for y in sorted(by_layer.keys()):
        total = sum(by_layer[y].values())
        print(f"  Layer {y} ({total} bl.): {by_layer[y]}")
