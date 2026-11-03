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

        List<SchematicBlock> anchorLayer = null;
        for (int l : schem.getLayers()) {
            List<SchematicBlock> lb = schem.getBlocksAtLayer(l);
            if (!lb.isEmpty()) {
                anchorLayer = lb;
                break;
            }
        }
        if (anchorLayer == null || anchorLayer.isEmpty()) return null;

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
            int anchorMatches = 0;
            for (SchematicBlock sb : anchorLayer) {
                int bx = testOriginX + sb.getDx();
                int by = testOriginY + sb.getDy();
                int bz = testOriginZ + sb.getDz();

                if (world.getBlockAt(bx, by, bz).getType() == sb.getMaterial()) {
                    anchorMatches++;
                }
            }

            double anchorRatio = (double) anchorMatches / anchorLayer.size();
            // Смягчаем порог: достаточно 20% совпадения якоря (первого слоя) чтобы начать проверку всего здания
            if (anchorRatio >= 0.20 || anchorMatches >= 3) {
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

                        if (world.getBlockAt(bx, by, bz).getType() == sb.getMaterial()) {
                            matchedInLayer++;
                            matchedBlockKeys.add(sb.getDx() + "," + sb.getDy() + "," + sb.getDz());
                        }
                    }

                    totalMatched += matchedInLayer;
                    
                    double layerRatio = (double) matchedInLayer / layerBlocks.size();
                    if (layerRatio >= 0.90) {
                        completedLayersCount++;
                    }
                }

                // Если в сумме совпало более 10 блоков или > 10% от всей схемы - это точно наше здание!
                if (totalMatched > 10 && totalMatched > maxMatchedBlocks) {
                    maxMatchedBlocks = totalMatched;
                    bestAlignment = new ExistingStageAlignment(testOriginX, testOriginY, testOriginZ, completedLayersCount, totalMatched, matchedBlockKeys);
                }
            }
        }

        return bestAlignment;
    }"""

new_code = code[:start_idx] + new_method + code[end_idx:]
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Replaced detectExistingConstruction")
