def rotateRelativeCoords(dx, dz, rotDeg, w, l):
    if rotDeg == 90:
        return [dz, max(0, w - 1 - dx)]
    elif rotDeg == 180:
        return [max(0, w - 1 - dx), max(0, l - 1 - dz)]
    elif rotDeg == 270:
        return [max(0, l - 1 - dz), dx]
    else:
        return [dx, dz]

def unrotateRelativeCoords(rx, rz, rotDeg, w, l):
    if rotDeg == 90:
        return rotateRelativeCoords(rx, rz, 270, l, w)
    elif rotDeg == 180:
        return rotateRelativeCoords(rx, rz, 180, w, l)
    elif rotDeg == 270:
        return rotateRelativeCoords(rx, rz, 90, l, w)
    else:
        return [rx, rz]

w = 16
l = 32

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java') as f:
    code = f.read()

import re
matches = re.findall(r'new SchematicBlock\((\d+),\s*(\d+),\s*(\d+),\s*Material\.([A-Z_]+)\)', code[code.find('generateBarracksSchematic'):code.find('generateLibrarySchematic')])
layer1 = [(int(m[0]), int(m[1]), int(m[2]), m[3]) for m in matches if int(m[1]) == 1]

for rot in [0, 90, 180, 270]:
    for dx, dy, dz, mat in layer1:
        rx, rz = rotateRelativeCoords(dx, dz, rot, w, l)
        un_dx, un_dz = unrotateRelativeCoords(rx, rz, rot, w, l)
        if un_dx != dx or un_dz != dz:
            print(f"FAILED for rot={rot}: ({dx},{dz}) -> ({rx},{rz}) -> ({un_dx},{un_dz})")
            break
    else:
        print(f"Rot {rot}°: ALL {len(layer1)} blocks match 100%!")
