with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

import re

for schem_name in ['generateBankSchematic', 'generateHospitalSchematic', 'generateBarracksSchematic', 
                   'generateLibrarySchematic', 'generateWatchtowerSchematic', 'generateWonderColossusSchematic']:
    idx = text.find(f'public BuildingSchematic {schem_name}()')
    next_idx = text.find('public BuildingSchematic ', idx + 20)
    body = text[idx:next_idx]
    
    layer0_mats = set()
    for m in re.finditer(r'new SchematicBlock\(\s*(\d+)\s*,\s*0\s*,\s*(\d+)\s*,\s*Material\.([A-Z_]+)\)', body):
        layer0_mats.add(m.group(3))
    print(f"{schem_name} layer 0 materials:", layer0_mats)

