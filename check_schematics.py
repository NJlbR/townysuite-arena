with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

import re

# Let's find all methods generate*Schematic
methods = re.findall(r'public BuildingSchematic generate(\w+Schematic)\(\)\s*\{(.*?)\n    \}', text, re.DOTALL)
for name, body in methods:
    # Check for direct calls or loops
    print(f"=== {name} ===")
    lines = body.splitlines()
    direct_blocks = []
    has_loops = False
    for line in lines:
        if 'for (' in line or 'while (' in line:
            has_loops = True
        m = re.search(r'blocks\.add\(new SchematicBlock\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*Material\.([A-Z_]+)\)\)', line)
        if m:
            direct_blocks.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)))
    
    unique_coords = set((b[0], b[1], b[2]) for b in direct_blocks)
    print(f"Direct blocks: {len(direct_blocks)}, unique coords: {len(unique_coords)}, has_loops: {has_loops}")
    if len(direct_blocks) != len(unique_coords):
        from collections import Counter
        counts = Counter((b[0], b[1], b[2]) for b in direct_blocks)
        dups = [k for k, v in counts.items() if v > 1]
        print(f"  DUPLICATES FOUND ({len(dups)}): {dups[:10]}")

