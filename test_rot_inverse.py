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

for rot in [0, 90, 180, 270]:
    errors = 0
    for dx in range(w):
        for dz in range(l):
            rx, rz = rotateRelativeCoords(dx, dz, rot, w, l)
            un_dx, un_dz = unrotateRelativeCoords(rx, rz, rot, w, l)
            if un_dx != dx or un_dz != dz:
                print(f"ERROR at rot={rot}: ({dx},{dz}) -> ({rx},{rz}) -> ({un_dx},{un_dz})")
                errors += 1
                if errors > 5:
                    break
        if errors > 0:
            break
    if errors == 0:
        print(f"Rot {rot}°: PERFECT INVERSE for all {w*l} coordinates!")
