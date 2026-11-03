with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

idx = text.find('public BuildingSchematic generateWatchtowerSchematic()')
next_idx = text.find('public BuildingSchematic generateWonderColossusSchematic()')
body = text[idx:next_idx]

import re
lines = body.splitlines()
blocks = []
for i, line in enumerate(lines):
    m = re.search(r'blocks\.add\(new SchematicBlock\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*Material\.([A-Z_]+)\)\)', line)
    if m:
        blocks.append((i, int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4), line))

coords = {}
for i, x, y, z, mat, line in blocks:
    key = (x, y, z)
    if key in coords:
        print("Duplicate:", key)
        print("  First at:", coords[key])
        print("  Second at:", (i, mat, line.strip()))
    else:
        coords[key] = (i, mat, line.strip())

