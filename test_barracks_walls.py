with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java') as f:
    code = f.read()

idx = code.find('public BuildingSchematic generateBarracksSchematic')
idx2 = code.find('public BuildingSchematic generateLibrarySchematic')
text = code[idx:idx2]

import re
matches = re.findall(r'new SchematicBlock\((\d+),\s*(\d+),\s*(\d+),\s*Material\.([A-Z_]+)\)', text)
layer1 = {}
for m in matches:
    x, y, z, mat = int(m[0]), int(m[1]), int(m[2]), m[3]
    if y == 1:
        layer1[(x, z)] = mat

print("Barracks Layer 1 grid (x from 1 to 14, z from 2 to 29):")
for z in range(2, 30):
    row = ""
    for x in range(1, 15):
        if (x, z) in layer1:
            m = layer1[(x, z)]
            if m == 'STONE_BRICKS': row += "S"
            elif m == 'COBBLESTONE': row += "C"
            elif m == 'IRON_BLOCK': row += "I"
            elif m == 'LADDER': row += "L"
            else: row += "?"
        else:
            row += "."
    print(f"z={z:2d}: {row}")
