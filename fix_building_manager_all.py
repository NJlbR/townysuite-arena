with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Rewrite findFreePlotArea
start_ff = code.find('public Set<ChunkCoord> findFreePlotArea')
# find closing brace of findFreePlotArea
brace_count = 0
end_ff = -1
for i in range(start_ff, len(code)):
    if code[i] == '{':
        brace_count += 1
    elif code[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end_ff = i + 1
            break

new_ff = """public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk) {
        if (preferredChunk == null) return null;
        Set<ChunkCoord> allPlots = getTownBuildPlots(townName);
        if (allPlots.isEmpty()) return null;

        Set<ChunkCoord> freePlots = new HashSet<>();
        for (ChunkCoord c : allPlots) {
            if (c.getWorldName().equals(worldName) && !isChunkOccupiedByBuilding(c)) {
                freePlots.add(c);
            }
        }
        // STRICT: preferredChunk (where the player stands) MUST be a free plot!
        if (!freePlots.contains(preferredChunk)) return null;

        int[][] orientations = (widthChunks == lengthChunks) 
                ? new int[][]{{widthChunks, lengthChunks}}
                : new int[][]{{widthChunks, lengthChunks}, {lengthChunks, widthChunks}};

        // STRICT: Scan all rectangles containing preferredChunk in any direction
        for (int[] dim : orientations) {
            int w = dim[0];
            int l = dim[1];
            for (int dx = 0; dx < w; dx++) {
                for (int dz = 0; dz < l; dz++) {
                    int originX = preferredChunk.getX() - dx;
                    int originZ = preferredChunk.getZ() - dz;
                    Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, originX, originZ, w, l);
                    if (candidate != null) return candidate;
                }
            }
        }

        return null;
    }"""

code = code[:start_ff] + new_ff + code[end_ff:]

# 2. Fix rotationDeg order in startBuilding (calculate rotationDeg BEFORE effectiveW, effectiveL, originX, originZ)
old_rot_calc = """        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bp.getId());

        int rotationDeg = 0;
        if (bp.getChunkWidth() != bp.getChunkLength()) {
            if (spanX == bp.getChunkLength() && spanZ == bp.getChunkWidth()) {
                rotationDeg = 90;
            }
        }

        ExistingStageAlignment alignment = null;
        if (schem != null) {
            alignment = detectExistingConstruction(schem, world, assignedChunks);
        }

        int schemW = schem != null ? schem.getWidthX() : (bp.getChunkWidth() * 16);
        int schemL = schem != null ? schem.getLengthZ() : (bp.getChunkLength() * 16);
        int effectiveW = (rotationDeg == 90 || rotationDeg == 270) ? schemL : schemW;
        int effectiveL = (rotationDeg == 90 || rotationDeg == 270) ? schemW : schemL;

        int totalPlotWidthPx = spanX * 16;
        int totalPlotLengthPx = spanZ * 16;

        int originX = minChunkX * 16 + Math.max(0, (totalPlotWidthPx - effectiveW) / 2);
        int originY = terrainGroundY;
        int originZ = minChunkZ * 16 + Math.max(0, (totalPlotLengthPx - effectiveL) / 2);"""

# Let's verify how startBuilding calculates rotation and origin
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated BuildingManager.java successfully!")
