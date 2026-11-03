import re

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

start_sig = "public ExistingStageAlignment detectExistingConstruction"
start_idx = code.find(start_sig)
end_idx = code.find("return bestAlignment;\n    }", start_idx) + len("return bestAlignment;\n    }")

new_method = """public ExistingStageAlignment detectExistingConstruction(BuildingSchematic schem, World world, Set<ChunkCoord> assignedChunks) {
        if (schem == null || world == null || assignedChunks == null || assignedChunks.isEmpty()) {
            return null;
        }

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

        List<SchematicBlock> allBlocks = schem.getBlocks();
        if (allBlocks.isEmpty()) return null;

        // Создаем равномерную выборку из блоков схемы (до 150 блоков)
        List<SchematicBlock> sampleBlocks = new ArrayList<>();
        int step = Math.max(1, allBlocks.size() / 150);
        for (int i = 0; i < allBlocks.size(); i += step) {
            sampleBlocks.add(allBlocks.get(i));
        }

        ExistingStageAlignment bestAlignment = null;
        int maxMatchedBlocks = 0;
        
        plugin.getLogger().info("[AutoAlign] Scanning " + sampleBlocks.size() + " sample blocks from Y=" + minY + " to " + maxY);

        for (int testOriginY = minY; testOriginY <= maxY; testOriginY++) {
            int sampleMatches = 0;
            for (SchematicBlock sb : sampleBlocks) {
                int bx = testOriginX + sb.getDx();
                int by = testOriginY + sb.getDy();
                int bz = testOriginZ + sb.getDz();

                if (by >= world.getMinHeight() && by < world.getMaxHeight()) {
                    if (world.getBlockAt(bx, by, bz).getType() == sb.getMaterial()) {
                        sampleMatches++;
                    }
                }
            }

            double sampleRatio = (double) sampleMatches / sampleBlocks.size();
            
            // Если хотя бы 8% сэмпла совпадает, делаем полную проверку этого уровня Y
            if (sampleRatio >= 0.08 || sampleMatches >= 4) {
                Set<String> matchedBlockKeys = new HashSet<>();
                int totalMatched = 0;
                int completedLayersCount = 0;

                for (int l : schem.getLayers()) {
                    List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(l);
                    if (layerBlocks.isEmpty()) continue;

                    int matchedInLayer = 0;
                    for (SchematicBlock sb : layerBlocks) {
                        int bx = testOriginX + sb.getDx();
                        int by = testOriginY + sb.getDy();
                        int bz = testOriginZ + sb.getDz();

                        if (by >= world.getMinHeight() && by < world.getMaxHeight()) {
                            if (world.getBlockAt(bx, by, bz).getType() == sb.getMaterial()) {
                                matchedInLayer++;
                                matchedBlockKeys.add(sb.getDx() + "," + sb.getDy() + "," + sb.getDz());
                            }
                        }
                    }

                    totalMatched += matchedInLayer;
                    
                    double layerRatio = (double) matchedInLayer / layerBlocks.size();
                    if (layerRatio >= 0.90) {
                        completedLayersCount++;
                    }
                }

                if (totalMatched > maxMatchedBlocks && totalMatched >= 5) {
                    maxMatchedBlocks = totalMatched;
                    bestAlignment = new ExistingStageAlignment(testOriginX, testOriginY, testOriginZ, completedLayersCount, totalMatched, matchedBlockKeys);
                    plugin.getLogger().info("[AutoAlign] Found candidate at Y=" + testOriginY + " with " + totalMatched + "/" + allBlocks.size() + " blocks matched.");
                }
            }
        }

        // Если нашли совпадение, но оно слишком маленькое (< 5% от всей постройки), игнорируем
        if (bestAlignment != null) {
            double totalRatio = (double) bestAlignment.matchedBlocksCount / allBlocks.size();
            if (totalRatio < 0.05 && bestAlignment.matchedBlocksCount < 10) {
                plugin.getLogger().info("[AutoAlign] Rejected best candidate at Y=" + bestAlignment.matchedOriginY + " because it matched only " + bestAlignment.matchedBlocksCount + " blocks (" + (totalRatio*100) + "%).");
                return null;
            }
            plugin.getLogger().info("[AutoAlign] Accepted alignment at Y=" + bestAlignment.matchedOriginY + " with " + bestAlignment.matchedBlocksCount + " blocks.");
        } else {
            plugin.getLogger().info("[AutoAlign] No alignment found.");
        }

        return bestAlignment;
    }"""

new_code = code[:start_idx] + new_method + code[end_idx:]
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Replaced detectExistingConstruction (v3)")
