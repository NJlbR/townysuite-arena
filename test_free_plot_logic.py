class CC:
    def __init__(self, w, x, z):
        self.w = w
        self._x = x
        self._z = z
    def getX(self): return self._x
    def getZ(self): return self._z
    def getWorldName(self): return self.w
    def __hash__(self): return hash((self.w, self._x, self._z))
    def __eq__(self, o): return isinstance(o, CC) and self.w == o.w and self._x == o._x and self._z == o._z
    def __repr__(self): return f"({self._x},{self._z})"

def findFreePlotArea(freePlots, worldName, widthChunks, lengthChunks, preferredChunk):
    if not freePlots: return None
    
    orientations = [[widthChunks, lengthChunks]]
    if widthChunks != lengthChunks:
        orientations.append([lengthChunks, widthChunks])
        
    if preferredChunk is not None and preferredChunk in freePlots:
        for dim in orientations:
            w = dim[0]
            l = dim[1]
            for dx in range(w):
                for dz in range(l):
                    startX = preferredChunk.getX() - dx
                    startZ = preferredChunk.getZ() - dz
                    candidate = checkRectangle(freePlots, worldName, startX, startZ, w, l)
                    if candidate is not None:
                        return candidate
                        
    for anchor in freePlots:
        if anchor.getWorldName() != worldName: continue
        for dim in orientations:
            candidate = checkRectangle(freePlots, worldName, anchor.getX(), anchor.getZ(), dim[0], dim[1])
            if candidate is not None:
                return candidate
                
    return None

def checkRectangle(freePlots, worldName, startX, startZ, width, length):
    rect = []
    for x in range(width):
        for z in range(length):
            check = CC(worldName, startX + x, startZ + z)
            if check not in freePlots:
                return None
            rect.append(check)
    return rect

free = {CC('world', 0, 0), CC('world', -1, 0)}
pref = CC('world', 0, 0)
res = findFreePlotArea(free, 'world', 1, 2, pref)
print("Result for 1x2 at (0,0) with (-1,0) free:", res)
