def rotateRelativeCoords(dx, dz, rotDeg, w, l):
    if rotDeg == 90:
        return [dz, max(0, w - 1 - dx)]
    elif rotDeg == 180:
        return [max(0, w - 1 - dx), max(0, l - 1 - dz)]
    elif rotDeg == 270:
        return [max(0, l - 1 - dz), dx]
    else:
        return [dx, dz]

# Barracks: w = 16 (X), l = 32 (Z)
w = 16
l = 32

print("Testing rotDeg = 0:")
for dx in [0, 15]:
    for dz in [0, 31]:
        rx, rz = rotateRelativeCoords(dx, dz, 0, w, l)
        print(f"  ({dx},{dz}) -> ({rx},{rz})")

print("Testing rotDeg = 90:")
for dx in [0, 15]:
    for dz in [0, 31]:
        rx, rz = rotateRelativeCoords(dx, dz, 90, w, l)
        print(f"  ({dx},{dz}) -> ({rx},{rz})")
