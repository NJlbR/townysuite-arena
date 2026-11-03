with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java') as f:
    code = f.read()

idx = code.find('public BuildingSchematic generateBarracksSchematic')
idx2 = code.find('public BuildingSchematic generateLibrarySchematic')
text = code[idx:idx2]

import re
matches = re.findall(r'new SchematicBlock\((\d+),\s*(\d+),\s*(\d+),\s*Material\.([A-Z_]+)\)', text)
ladder_blocks = [m for m in matches if m[3] == 'LADDER']
print("Ladder blocks in barracks:")
for lb in ladder_blocks:
    print(lb)

# Check what blocks are around (2, y, 28) for y=0..4
for y in range(5):
    around = [m for m in matches if int(m[1]) == y and abs(int(m[0])-2) <= 1 and abs(int(m[2])-28) <= 1]
    print(f"Around (2, {y}, 28):", around)
