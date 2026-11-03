with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update findFreePlotArea to sort candidates by distance to preferredChunk
old_ff_body = """        // STRICT: Scan all rectangles containing preferredChunk in any direction
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

        return null;"""

new_ff_body = """        // STRICT: Collect all valid candidate rectangles containing preferredChunk, sort by distance to preferredChunk
        List<CandidateArea> candidates = new ArrayList<>();
        for (int[] dim : orientations) {
            int w = dim[0];
            int l = dim[1];
            for (int dx = 0; dx < w; dx++) {
                for (int dz = 0; dz < l; dz++) {
                    int originX = preferredChunk.getX() - dx;
                    int originZ = preferredChunk.getZ() - dz;
                    Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, originX, originZ, w, l);
                    if (candidate != null) {
                        double centerX = originX + (w - 1) / 2.0;
                        double centerZ = originZ + (l - 1) / 2.0;
                        double dist = Math.hypot(centerX - preferredChunk.getX(), centerZ - preferredChunk.getZ());
                        candidates.add(new CandidateArea(dist, candidate));
                    }
                }
            }
        }

        if (candidates.isEmpty()) return null;
        candidates.sort(Comparator.comparingDouble(a -> a.distance));
        return candidates.get(0).chunks;"""

if old_ff_body in code:
    code = code.replace(old_ff_body, new_ff_body)
    print("Replaced findFreePlotArea body successfully!")
else:
    print("Error: old_ff_body not found")

# Also add CandidateArea helper class if not present
if "class CandidateArea" not in code:
    # insert before last closing brace of BuildingManager
    last_brace = code.rfind('}')
    candidate_class = """
    private static class CandidateArea {
        final double distance;
        final Set<ChunkCoord> chunks;
        CandidateArea(double distance, Set<ChunkCoord> chunks) {
            this.distance = distance;
            this.chunks = chunks;
        }
    }
"""
    code = code[:last_brace] + candidate_class + code[last_brace:]
    print("Added CandidateArea helper class!")

# 2. Remove duplicate int rotationDeg = 0; near line 604
old_dup_rot = """        int originX = minChunkX * 16 + Math.max(0, (totalPlotWidthPx - effectiveW) / 2);
        int originY = terrainGroundY;
        int originZ = minChunkZ * 16 + Math.max(0, (totalPlotLengthPx - effectiveL) / 2);
        int rotationDeg = 0;"""

new_dup_rot = """        int originX = minChunkX * 16 + Math.max(0, (totalPlotWidthPx - effectiveW) / 2);
        int originY = terrainGroundY;
        int originZ = minChunkZ * 16 + Math.max(0, (totalPlotLengthPx - effectiveL) / 2);"""

if old_dup_rot in code:
    code = code.replace(old_dup_rot, new_dup_rot)
    print("Removed duplicate rotationDeg = 0 reset!")
else:
    print("Warning: old_dup_rot not found")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("BuildingManager.java successfully updated!")
