import math

def findBestFreePlotArea(freePlots, worldName, widthChunks, lengthChunks, preferredChunk):
    if preferredChunk is None or preferredChunk not in freePlots:
        return None
        
    orientations = [[widthChunks, lengthChunks]]
    if widthChunks != lengthChunks:
        orientations.append([lengthChunks, widthChunks])
        
    candidates = []
    for dim in orientations:
        w = dim[0]
        l = dim[1]
        for dx in range(w):
            for dz in range(l):
                startX = preferredChunk[1] - dx
                startZ = preferredChunk[2] - dz
                candidate = checkRectangle(freePlots, worldName, startX, startZ, w, l)
                if candidate is not None:
                    # calculate center distance to preferredChunk
                    centerX = startX + (w - 1) / 2.0
                    centerZ = startZ + (l - 1) / 2.0
                    dist = math.hypot(centerX - preferredChunk[1], centerZ - preferredChunk[2])
                    candidates.append((dist, candidate))
                    
    if not candidates:
        return None
        
    # Sort by distance (closest to preferredChunk first)
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]

def checkRectangle(freePlots, worldName, startX, startZ, width, length):
    rect = []
    for x in range(width):
        for z in range(length):
            check = (worldName, startX + x, startZ + z)
            if check not in freePlots:
                return None
            rect.append(check)
    return rect

free = {('world', 0, 0), ('world', 1, 0), ('world', 0, 1)}
pref = ('world', 0, 0)
print("Best 1x2 area for pref (0,0):", findBestFreePlotArea(free, 'world', 1, 2, pref))
