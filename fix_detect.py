import re

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

start_sig = "public ExistingStageAlignment detectExistingConstruction"
start_idx = code.find(start_sig)
if start_idx == -1:
    print("Not found")
    exit(1)

end_idx = code.find("return bestAlignment;", start_idx)
if end_idx == -1:
    print("End not found")
    exit(1)

end_idx += len("return bestAlignment;\n    }")

new_method = """public ExistingStageAlignment detectExistingConstruction(BuildingSchematic schem, World world, Set<ChunkCoord> assignedChunks) {
        if (schem == null || world == null || assignedChunks == null || assignedChunks.isEmpty()) {
            return null;
        }

        List<SchematicBlock> layer0 = schem.getBlocksAtLayer(0);
        if (layer0.isEmpty()) {
            for (int l : schem.getLayers()) {
                layer0 = schem.getBlocksAtLayer(l);
                if (!layer0.isEmpty()) break;
            }
        }
        if (layer0.isEmpty()) return null;

        int minChunkX = Integer.MAX_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
        }

        int testOriginX = minChunkX * 16;
        int testOriginZ = minChunkZ * 16;

        int minY = world.getMinHeight();
        int maxY = world.getMaxHeight() - schem.getHeightY();

        ExistingStageAlignment bestAlignment = null;
        int maxMatchedBlocks = 0;

        for (int testOriginY = minY; testOriginY <= maxY; testOriginY++) {
            int layer0Matches = 0;
            for (SchematicBlock sb : layer0) {
                int bx = testOriginX + sb.getDx();
                int by = testOriginY + sb.getDy();
                int bz = testOriginZ + sb.getDz();

                if (world.getBlockAt(bx, by, bz).getType() == sb.getMaterial()) {
                    layer0Matches++;
                }
            }

            double layer0Ratio = (double) layer0Matches / layer0.size();
            if (layer0Ratio >= 0.50 || (layer0Matches >= 3 && layer0Ratio >= 0.30)) {
                Set<String> matchedBlockKeys = new HashSet<>();
                int completedLayers = 0;
                int totalMatched = 0;

                for (int l : schem.getLayers()) {
                    List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(l);
                    if (layerBlocks.isEmpty()) continue;

                    int matchedInLayer = 0;
                    for (SchematicBlock sb : layerBlocks) {
                        int bx = testOriginX + sb.getDx();
                        int by = testOriginY + sb.getDy();
                        int bz = testOriginZ + sb.getDz();

                        if (world.getBlockAt(bx, by, bz).getType() == sb.getMaterial()) {
                            matchedInLayer++;
                            matchedBlockKeys.add(bx + "," + by + "," + bz);
                        }
                    }

                    double layerRatio = (double) matchedInLayer / layerBlocks.size();
                    if (layerRatio >= 0.95 || (matchedInLayer == layerBlocks.size())) {
                        completedLayers++;
                        totalMatched += matchedInLayer;
                    } else {
                        break;
                    }
                }

                if (totalMatched > maxMatchedBlocks) {
                    maxMatchedBlocks = totalMatched;
                    bestAlignment = new ExistingStageAlignment(testOriginX, testOriginY, testOriginZ, completedLayers, totalMatched, matchedBlockKeys);
                }
            }
        }

        return bestAlignment;
    }"""

new_code = code[:start_idx] + new_method + code[end_idx:]
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Replaced successfully")
