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

for rot in [0, 90, 180, 270]:
    for w, l in [(32, 16), (16, 16), (32, 32)]:
        for dx in range(w):
            for dz in range(l):
                r = rotateRelativeCoords(dx, dz, rot, w, l)
                u = unrotateRelativeCoords(r[0], r[1], rot, w, l)
                if u != [dx, dz]:
                    print(f"FAILED for rot={rot}, w={w}, l={l}, dx={dx}, dz={dz}: got {u}")
                    break
print("Rotation check completed!")
