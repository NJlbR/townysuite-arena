def rotateRelativeCoords(dx, dz, rotDeg, w, l):
    if rotDeg == 90:
        return [dz, max(0, w - 1 - dx)]
    elif rotDeg == 180:
        return [max(0, w - 1 - dx), max(0, l - 1 - dz)]
    elif rotDeg == 270:
        return [max(0, l - 1 - dz), dx]
    else:
        return [dx, dz]

def getEffectiveDimensions(w, l, rotDeg):
    if rotDeg == 90 or rotDeg == 270:
        return l, w
    return w, l

# Test 1: Plot is 2x1 chunks (spanX = 2, spanZ = 1, minChunkX = 0, minChunkZ = 0)
# Total plot in blocks: X in [0..31], Z in [0..15]
schemW = 16
schemL = 32
spanX = 2
spanZ = 1
minChunkX = 0
minChunkZ = 0

totalPlotWidthPx = spanX * 16 # 32
totalPlotLengthPx = spanZ * 16 # 16

for rot in [0, 90, 180, 270]:
    effW, effL = getEffectiveDimensions(schemW, schemL, rot)
    originX = minChunkX * 16 + max(0, (totalPlotWidthPx - effW) // 2)
    originZ = minChunkZ * 16 + max(0, (totalPlotLengthPx - effL) // 2)
    
    # Check bounding box of all rotated blocks (dx in 0..15, dz in 0..31)
    minWorldX, maxWorldX = 9999, -9999
    minWorldZ, maxWorldZ = 9999, -9999
    for dx in range(schemW):
        for dz in range(schemL):
            rx, rz = rotateRelativeCoords(dx, dz, rot, schemW, schemL)
            wx = originX + rx
            wz = originZ + rz
            minWorldX = min(minWorldX, wx)
            maxWorldX = max(maxWorldX, wx)
            minWorldZ = min(minWorldZ, wz)
            maxWorldZ = max(maxWorldZ, wz)
            
    print(f"Rot {rot}°: origin=({originX},{originZ}), eff=({effW},{effL}), World X=[{minWorldX}..{maxWorldX}], World Z=[{minWorldZ}..{maxWorldZ}]")
    inPlotX = (minWorldX >= 0 and maxWorldX <= 31)
    inPlotZ = (minWorldZ >= 0 and maxWorldZ <= 15)
    print(f"  Fits in 2x1 plot (32x16 blocks)? X: {inPlotX}, Z: {inPlotZ} -> FULL FIT: {inPlotX and inPlotZ}")
