with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java') as f:
    code = f.read()

idx = code.find('public BuildingSchematic generateBarracksSchematic')
idx2 = code.find('public BuildingSchematic generateLibrarySchematic')
text = code[idx:idx2]

import re
matches = re.findall(r'new SchematicBlock\((\d+),\s*(\d+),\s*(\d+),\s*Material\.([A-Z_]+)\)', text)
by_layer = {}
for m in matches:
    x, y, z, mat = int(m[0]), int(m[1]), int(m[2]), m[3]
    by_layer.setdefault(y, []).append((x, y, z, mat))

for y in sorted(by_layer.keys()):
    print(f"--- Layer {y} ({len(by_layer[y])} blocks) ---")
    mats = {}
    for x, y_val, z, mat in by_layer[y]:
        mats[mat] = mats.get(mat, 0) + 1
    print("  Materials:", mats)
    # Check if there are duplicate coordinates in this layer
    coords = set()
    dups = []
    for x, y_val, z, mat in by_layer[y]:
        if (x, z) in coords:
            dups.append((x, z, mat))
        coords.add((x, z))
    if dups:
        print(f"  WARNING: Duplicate coordinates in Layer {y}: {dups}")
