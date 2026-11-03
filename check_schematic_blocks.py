with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java') as f:
    code = f.read()

idx = code.find('generateBarracksSchematic')
idx2 = code.find('return new BuildingSchematic("barracks"', idx)
method_code = code[idx:idx2]

lines = method_code.split('\n')
blocks_by_layer = {}
for line in lines:
    if 'blocks.add(new SchematicBlock(' in line:
        # e.g. blocks.add(new SchematicBlock(1, 0, 2, Material.STONE_BRICKS));
        content = line[line.find('(')+1:line.rfind(')')]
        parts = [p.strip() for p in content.split(',')]
        if len(parts) >= 4:
            x = int(parts[0].replace('new SchematicBlock(', ''))
            y = int(parts[1])
            z = int(parts[2])
            mat = parts[3]
            blocks_by_layer.setdefault(y, []).append((x, y, z, mat))

for y in sorted(blocks_by_layer.keys()):
    print(f"Layer {y}: {len(blocks_by_layer[y])} blocks")
    mat_counts = {}
    for x, y, z, mat in blocks_by_layer[y]:
        mat_counts[mat] = mat_counts.get(mat, 0) + 1
    print(f"  Materials: {mat_counts}")
