with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

import re

methods = ['generateBankSchematic', 'generateHospitalSchematic', 'generateBarracksSchematic', 
           'generateLibrarySchematic', 'generateWatchtowerSchematic', 'generateWonderColossusSchematic',
           'generateCityWallSchematic', 'generateTownHallSchematic']

for i, schem_name in enumerate(methods):
    idx = text.find(f'public BuildingSchematic {schem_name}()')
    next_idx = text.find('public BuildingSchematic ', idx + 20)
    if next_idx == -1:
        next_idx = text.find('private BuildingSchematic loadFromYaml', idx + 20)
    body = text[idx:next_idx]
    
    dys = set()
    for m in re.finditer(r'new SchematicBlock\(\s*(\d+|[a-zA-Z0-9_+ -]+)\s*,\s*(\d+)\s*,\s*(\d+|[a-zA-Z0-9_+ -]+)', body):
        dys.add(int(m.group(2)))
    
    print(f"{schem_name}: min layer = {min(dys) if dys else 'none'}, max layer = {max(dys) if dys else 'none'}, layers={sorted(list(dys))}")

