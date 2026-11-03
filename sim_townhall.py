with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

idx = text.find('public BuildingSchematic generateTownHallSchematic()')
body = text[idx:idx+5000]

# Let's count duplicate coordinates in TownHall
import re
lines = body.splitlines()
blocks = []
for line in lines:
    m = re.search(r'blocks\.add\(new SchematicBlock\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*Material\.([A-Z_]+)\)\)', line)
    if m:
        blocks.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)))

from collections import Counter
c = Counter((b[0], b[1], b[2]) for b in blocks)
for k, v in c.items():
    if v > 1:
        print("Townhall duplicate:", k, v)

