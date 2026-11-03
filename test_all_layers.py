with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

import re

for schem_name in ['generateBankSchematic', 'generateHospitalSchematic', 'generateBarracksSchematic', 
                   'generateLibrarySchematic', 'generateWatchtowerSchematic', 'generateWonderColossusSchematic',
                   'generateCityWallSchematic', 'generateTownHallSchematic']:
    idx = text.find(f'public BuildingSchematic {schem_name}()')
    body = text[idx:idx+8000]
    
    # find all SchematicBlock(..., y, ...)
    # For CityWall: y in 0..3 (loop), y4=4, y5=5 -> layers 0, 1, 2, 3, 4, 5
    # For TownHall: y=0, y in 1..3, y=4, y=5, y=6
    # For others, extract literal dy:
    dys = set()
    for m in re.finditer(r'new SchematicBlock\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', body):
        dys.add(int(m.group(2)))
    
    print(f"{schem_name}: min layer = {min(dys) if dys else 'loop'}, max layer = {max(dys) if dys else 'loop'}, layers count={len(dys)}")
    if dys:
        missing_layers = [l for l in range(min(dys), max(dys)+1) if l not in dys]
        if missing_layers:
            print(f"  MISSING LAYERS: {missing_layers}")

