def findFreePlotAreaStrict(freePlots, worldName, widthChunks, lengthChunks, preferredChunk):
    if preferredChunk is None or preferredChunk not in freePlots:
        return None
        
    orientations = [[widthChunks, lengthChunks]]
    if widthChunks != lengthChunks:
        orientations.append([lengthChunks, widthChunks])
        
    for dim in orientations:
        w = dim[0]
        l = dim[1]
        # Scan all starting offsets such that preferredChunk is inside [startX..startX+w-1, startZ..startZ+l-1]
        for dx in range(w):
            for dz in range(l):
                startX = preferredChunk[1] - dx
                startZ = preferredChunk[2] - dz
                candidate = checkRectangle(freePlots, worldName, startX, startZ, w, l)
                if candidate is not None:
                    return candidate, w, l
    return None, 0, 0

def checkRectangle(freePlots, worldName, startX, startZ, width, length):
    rect = []
    for x in range(width):
        for z in range(length):
            check = (worldName, startX + x, startZ + z)
            if check not in freePlots:
                return None
            rect.append(check)
    return rect

free = {('world', 0, 0), ('world', 1, 0)} # two chunks extending East from (0,0)
pref = ('world', 0, 0)

res, w, l = findFreePlotAreaStrict(free, 'world', 1, 2, pref)
print(f"1x2 building starting at (0,0) with free (0,0),(1,0): rect={res}, dim=({w}x{l})")
