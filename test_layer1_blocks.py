with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java') as f:
    code = f.read()

idx = code.find('public BuildingSchematic generateBarracksSchematic')
idx2 = code.find('public BuildingSchematic generateLibrarySchematic')
text = code[idx:idx2]

import re
matches = re.findall(r'new SchematicBlock\((\d+),\s*(\d+),\s*(\d+),\s*Material\.([A-Z_]+)\)', text)
layer1_blocks = []
for m in matches:
    x, y, z, mat = int(m[0]), int(m[1]), int(m[2]), m[3]
    if y == 1:
        layer1_blocks.append((x, y, z, mat))

print(f"Total Layer 1 blocks: {len(layer1_blocks)}")
for b in layer1_blocks:
    print(b)
