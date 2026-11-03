with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update isNaturalTerrainMaterial
old_is_natural = """    public static boolean isNaturalTerrainMaterial(Material mat) {
        if (mat == null) return false;
        String name = mat.name();
        return name.contains("GRASS") || name.contains("DIRT") || name.contains("STONE") || 
               name.contains("GRAVEL") || name.contains("SAND") || name.contains("WATER") || 
               name.contains("LAVA") || name.contains("LEAVES") || name.contains("LOG") || 
               name.contains("WOOD") || name.contains("SNOW") || name.contains("ICE");
    }"""

new_is_natural = """    public static boolean isNaturalTerrainMaterial(Material mat) {
        if (mat == null || mat.isAir()) return false;
        String name = mat.name();

        // Structural / crafted building materials must NEVER be treated as natural terrain:
        if (name.contains("PLANK") || name.contains("BRICK") || name.contains("SLAB") || 
            name.contains("STAIR") || name.contains("WALL") || name.contains("PILLAR") || 
            name.contains("SMOOTH") || name.contains("CHISELED") || name.contains("CRACKED") || 
            name.contains("POLISHED") || name.contains("TERRACOTTA") || name.contains("CONCRETE") || 
            name.contains("WOOL") || name.contains("GLASS") || name.contains("CARPET") || 
            name.contains("FENCE") || name.contains("DOOR") || name.contains("TRAPDOOR") || 
            name.contains("BOOKSHELF") || name.contains("OBSIDIAN") || name.contains("COPPER") ||
            name.contains("IRON") || name.contains("GOLD") || name.contains("DIAMOND") ||
            name.contains("NETHERITE") || name.contains("EMERALD") || name.contains("QUARTZ") ||
            name.contains("PURPUR") || name.contains("PRISMARINE") || name.contains("LANTERN") ||
            name.contains("TORCH") || name.contains("LADDER") || name.contains("BANNER") ||
            name.contains("SIGN") || name.contains("BED") || name.contains("ANVIL") ||
            name.contains("TABLE") || name.contains("FURNACE") || name.contains("CHEST") ||
            name.contains("HOPPER") || name.contains("DROPPER") || name.contains("DISPENSER") ||
            name.contains("SHULKER") || name.contains("CRAFTING") || name.contains("CAMPFIRE")) {
            return false;
        }

        return mat == Material.GRASS_BLOCK || mat == Material.DIRT || mat == Material.COARSE_DIRT ||
               mat == Material.PODZOL || mat == Material.ROOTED_DIRT || mat == Material.MUD ||
               mat == Material.MUDDY_MANGROVE_ROOTS || mat == Material.MYCELIUM ||
               mat == Material.STONE || mat == Material.DEEPSLATE || mat == Material.TUFF ||
               mat == Material.DIORITE || mat == Material.ANDESITE || mat == Material.GRANITE ||
               mat == Material.SAND || mat == Material.RED_SAND || mat == Material.GRAVEL ||
               mat == Material.SANDSTONE || mat == Material.RED_SANDSTONE || mat == Material.CLAY ||
               mat == Material.SNOW_BLOCK || mat == Material.POWDER_SNOW || mat == Material.ICE ||
               mat == Material.PACKED_ICE || mat == Material.BLUE_ICE || mat == Material.WATER ||
               mat == Material.LAVA || mat == Material.BEDROCK || mat == Material.CALCITE ||
               mat == Material.DRIPSTONE_BLOCK || mat == Material.NETHERRACK || mat == Material.END_STONE ||
               mat == Material.BASALT || mat == Material.BLACKSTONE || mat == Material.SOUL_SAND ||
               mat == Material.SOUL_SOIL;
    }"""

assert old_is_natural in content, "old_is_natural not found"
content = content.replace(old_is_natural, new_is_natural, 1)

# 2. Update calculateTerrainGroundY to scan down past buildings to true natural terrain
old_calc_terrain = """    public int calculateTerrainGroundY(World world, Set<ChunkCoord> assignedChunks) {
        if (world == null || assignedChunks == null || assignedChunks.isEmpty()) return 64;
        List<Integer> heights = new ArrayList<>();
        for (ChunkCoord cc : assignedChunks) {
            int cx = cc.getX() << 4;
            int cz = cc.getZ() << 4;
            for (int x = 2; x < 16; x += 4) {
                for (int z = 2; z < 16; z += 4) {
                    int h = world.getHighestBlockYAt(cx + x, cz + z);
                    heights.add(h);
                }
            }
        }
        if (heights.isEmpty()) return 64;
        Collections.sort(heights);
        return heights.get(heights.size() / 2);
    }"""

new_calc_terrain = """    public int calculateTerrainGroundY(World world, Set<ChunkCoord> assignedChunks) {
        if (world == null || assignedChunks == null || assignedChunks.isEmpty()) return 64;
        List<Integer> heights = new ArrayList<>();
        for (ChunkCoord cc : assignedChunks) {
            int cx = cc.getX() << 4;
            int cz = cc.getZ() << 4;
            for (int x = 2; x < 16; x += 4) {
                for (int z = 2; z < 16; z += 4) {
                    int highestY = world.getHighestBlockYAt(cx + x, cz + z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                    int checkY = Math.min(highestY, 150);
                    // Scan downwards through man-made building structures (roofs, walls, slabs, planks)
                    // until hitting the actual natural terrain foundation/ground
                    while (checkY >= Math.max(50, world.getMinHeight())) {
                        Material mat = world.getBlockAt(cx + x, checkY, cz + z).getType();
                        if (isNaturalTerrainMaterial(mat)) {
                            break;
                        }
                        checkY--;
                    }
                    if (checkY >= 50) {
                        heights.add(checkY + 1);
                    } else {
                        heights.add(highestY);
                    }
                }
            }
        }
        if (heights.isEmpty()) return 64;
        Collections.sort(heights);
        return heights.get(heights.size() / 2);
    }"""

assert old_calc_terrain in content, "old_calc_terrain not found"
content = content.replace(old_calc_terrain, new_calc_terrain, 1)

# 3. Update detectExistingConstruction with roof protection & candidate evaluation
old_detect = """        public ExistingStageAlignment detectExistingConstruction(BuildingSchematic schem, World world, Set<ChunkCoord> assignedChunks) {
        if (schem == null || world == null || assignedChunks == null || assignedChunks.isEmpty()) {
            return null;
        }

        int minChunkX = Integer.MAX_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        int maxChunkX = Integer.MIN_VALUE;
        int maxChunkZ = Integer.MIN_VALUE;

        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
            if (cc.getX() > maxChunkX) maxChunkX = cc.getX();
            if (cc.getZ() > maxChunkZ) maxChunkZ = cc.getZ();
        }

        int plotMinX = minChunkX * 16;
        int plotMinZ = minChunkZ * 16;
        int plotMaxX = (maxChunkX + 1) * 16;
        int plotMaxZ = (maxChunkZ + 1) * 16;

        int plotWidth = plotMaxX - plotMinX;
        int plotLength = plotMaxZ - plotMinZ;

        List<SchematicBlock> allBlocks = schem.getBlocks();
        if (allBlocks.isEmpty()) return null;

        List<SchematicBlock> layer0Blocks = schem.getBlocksAtLayer(0);
        if (layer0Blocks.isEmpty()) return null;

        int medianGroundY = calculateTerrainGroundY(world, assignedChunks);
        int minY = Math.max(world.getMinHeight() + 1, medianGroundY - 1);
        int maxY = Math.min(world.getMaxHeight() - schem.getHeightY(), medianGroundY + 3);

        int[] rotations = {0, 90, 180, 270};
        ExistingStageAlignment bestAlignment = null;
        int bestMatchedCount = 0;

        for (int rot : rotations) {
            int effW = (rot == 90 || rot == 270) ? schem.getLengthZ() : schem.getWidthX();
            int effL = (rot == 90 || rot == 270) ? schem.getWidthX() : schem.getLengthZ();

            int maxOffsetX = plotWidth - effW;
            int maxOffsetZ = plotLength - effL;
            if (maxOffsetX < 0 || maxOffsetZ < 0) continue;

            for (int offX = 0; offX <= maxOffsetX; offX++) {
                int testOriginX = plotMinX + offX;
                for (int offZ = 0; offZ <= maxOffsetZ; offZ++) {
                    int testOriginZ = plotMinZ + offZ;

                    for (int testOriginY = minY; testOriginY <= maxY; testOriginY++) {
                        // 1. Strict Layer 0 Check: A real building MUST start with the foundation!
                        int layer0Matched = 0;
                        for (SchematicBlock sb : layer0Blocks) {
                            int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                            int wx = testOriginX + rc[0];
                            int wy = testOriginY + sb.getDy();
                            int wz = testOriginZ + rc[1];
                            if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                                Material wm = world.getBlockAt(wx, wy, wz).getType();
                                if (wm == sb.getMaterial()) {
                                    layer0Matched++;
                                }
                            }
                        }

                        // Must match at least 40% of Layer 0 blocks and at least 12 blocks
                        int minReqLayer0 = Math.max(12, (int) (layer0Blocks.size() * 0.40));
                        if (layer0Matched < minReqLayer0) {
                            continue;
                        }

                        // 2. Scan layers sequentially from 0 to maxLayer
                        int totalMatched = 0;
                        Set<String> matchedKeys = new HashSet<>();
                        int completedLayers = 0;
                        boolean previousLayerFullyDone = true;

                        for (int l = 0; l <= schem.getMaxLayer(); l++) {
                            List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(l);
                            if (layerBlocks.isEmpty()) continue;

                            int layerMatchCount = 0;
                            for (SchematicBlock sb : layerBlocks) {
                                int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                                int wx = testOriginX + rc[0];
                                int wy = testOriginY + sb.getDy();
                                int wz = testOriginZ + rc[1];
                                if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                                    Material wm = world.getBlockAt(wx, wy, wz).getType();
                                    if (wm == sb.getMaterial()) {
                                        layerMatchCount++;
                                        matchedKeys.add(sb.getKey());
                                    }
                                }
                            }

                            totalMatched += layerMatchCount;

                            if (layerMatchCount == layerBlocks.size()) {
                                if (previousLayerFullyDone) {
                                    completedLayers = l + 1;
                                }
                            } else {
                                previousLayerFullyDone = false;
                            }
                        }

                        if (totalMatched > bestMatchedCount) {
                            bestMatchedCount = totalMatched;
                            boolean isFull = (totalMatched >= schem.getTotalBlockCount());
                            bestAlignment = new ExistingStageAlignment(
                                    testOriginX,
                                    testOriginY,
                                    testOriginZ,
                                    rot,
                                    completedLayers,
                                    totalMatched,
                                    matchedKeys,
                                    isFull
                            );
                        }
                    }
                }
            }
        }

        return bestAlignment;
    }"""

new_detect = """        public ExistingStageAlignment detectExistingConstruction(BuildingSchematic schem, World world, Set<ChunkCoord> assignedChunks) {
        if (schem == null || world == null || assignedChunks == null || assignedChunks.isEmpty()) {
            return null;
        }

        int minChunkX = Integer.MAX_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        int maxChunkX = Integer.MIN_VALUE;
        int maxChunkZ = Integer.MIN_VALUE;

        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
            if (cc.getX() > maxChunkX) maxChunkX = cc.getX();
            if (cc.getZ() > maxChunkZ) maxChunkZ = cc.getZ();
        }

        int plotMinX = minChunkX * 16;
        int plotMinZ = minChunkZ * 16;
        int plotMaxX = (maxChunkX + 1) * 16;
        int plotMaxZ = (maxChunkZ + 1) * 16;

        int plotWidth = plotMaxX - plotMinX;
        int plotLength = plotMaxZ - plotMinZ;

        List<SchematicBlock> allBlocks = schem.getBlocks();
        if (allBlocks.isEmpty()) return null;

        List<SchematicBlock> layer0Blocks = schem.getBlocksAtLayer(0);
        if (layer0Blocks.isEmpty()) return null;

        int terrainGroundY = calculateTerrainGroundY(world, assignedChunks);
        int highestPlotY = Integer.MIN_VALUE;
        int lowestPlotY = Integer.MAX_VALUE;
        for (ChunkCoord cc : assignedChunks) {
            int cx = cc.getX() << 4;
            int cz = cc.getZ() << 4;
            for (int x = 0; x < 16; x += 4) {
                for (int z = 0; z < 16; z += 4) {
                    int h = world.getHighestBlockYAt(cx + x, cz + z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                    if (h > highestPlotY) highestPlotY = h;
                    if (h < lowestPlotY) lowestPlotY = h;
                }
            }
        }
        if (highestPlotY == Integer.MIN_VALUE) highestPlotY = terrainGroundY;
        if (lowestPlotY == Integer.MAX_VALUE) lowestPlotY = terrainGroundY;

        // Search Y range covering natural terrain ground and any potential foundation:
        int minY = Math.max(world.getMinHeight() + 1, Math.min(terrainGroundY - 3, lowestPlotY - 1));
        int maxY = Math.min(world.getMaxHeight() - schem.getHeightY(), Math.max(terrainGroundY + 3, highestPlotY - schem.getHeightY() + 2));

        int[] rotations = {0, 90, 180, 270};
        ExistingStageAlignment bestAlignment = null;
        int bestMatchedCount = 0;
        int bestLayersWithMatches = 0;
        int bestCompletedLayers = 0;

        for (int rot : rotations) {
            int effW = (rot == 90 || rot == 270) ? schem.getLengthZ() : schem.getWidthX();
            int effL = (rot == 90 || rot == 270) ? schem.getWidthX() : schem.getLengthZ();

            int maxOffsetX = plotWidth - effW;
            int maxOffsetZ = plotLength - effL;
            if (maxOffsetX < 0 || maxOffsetZ < 0) continue;

            for (int offX = 0; offX <= maxOffsetX; offX++) {
                int testOriginX = plotMinX + offX;
                for (int offZ = 0; offZ <= maxOffsetZ; offZ++) {
                    int testOriginZ = plotMinZ + offZ;

                    for (int testOriginY = minY; testOriginY <= maxY; testOriginY++) {
                        // 1. Strict Layer 0 Check: A real building MUST start with the foundation!
                        int layer0Matched = 0;
                        for (SchematicBlock sb : layer0Blocks) {
                            int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                            int wx = testOriginX + rc[0];
                            int wy = testOriginY + sb.getDy();
                            int wz = testOriginZ + rc[1];
                            if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                                Material wm = world.getBlockAt(wx, wy, wz).getType();
                                if (isMaterialMatch(wm, sb.getMaterial())) {
                                    layer0Matched++;
                                }
                            }
                        }

                        // Must match at least 40% of Layer 0 blocks and at least 12 blocks
                        int minReqLayer0 = Math.max(12, (int) (layer0Blocks.size() * 0.40));
                        if (layer0Matched < minReqLayer0) {
                            continue;
                        }

                        // 2. Scan layers sequentially from 0 to maxLayer
                        int totalMatched = 0;
                        Set<String> matchedKeys = new HashSet<>();
                        int completedLayers = 0;
                        boolean previousLayerFullyDone = true;
                        int layersWithMatches = 0;

                        for (int l = 0; l <= schem.getMaxLayer(); l++) {
                            List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(l);
                            if (layerBlocks.isEmpty()) continue;

                            int layerMatchCount = 0;
                            for (SchematicBlock sb : layerBlocks) {
                                int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                                int wx = testOriginX + rc[0];
                                int wy = testOriginY + sb.getDy();
                                int wz = testOriginZ + rc[1];
                                if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                                    Material wm = world.getBlockAt(wx, wy, wz).getType();
                                    if (isMaterialMatch(wm, sb.getMaterial())) {
                                        layerMatchCount++;
                                        matchedKeys.add(sb.getKey());
                                    }
                                }
                            }

                            totalMatched += layerMatchCount;
                            if (layerMatchCount > 0) {
                                layersWithMatches++;
                            }

                            if (layerMatchCount == layerBlocks.size()) {
                                if (previousLayerFullyDone) {
                                    completedLayers = l + 1;
                                }
                            } else {
                                previousLayerFullyDone = false;
                            }
                        }

                        // 3. Roof Artifact Guard (Защита от ложного распознавания крыши/потолка как фундамента):
                        // Если в схеме пол и крыша состоят из одного материала (например, тёмные доски в Библиотеке Чар),
                        // то крыша уже построенного здания может совпасть со Слоем 0.
                        // Если совпал только Слой 0 (layersWithMatches <= 1), а непосредственно под ним (Y - 1)
                        // находятся блоки стен/интерьера здания, значит testOriginY — это КРЫША, а не фундамент!
                        if (layersWithMatches <= 1 && schem.getMaxLayer() > 0) {
                            int blocksBelowCount = 0;
                            for (SchematicBlock sb : layer0Blocks) {
                                int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                                int wx = testOriginX + rc[0];
                                int wyBelow = testOriginY - 1;
                                int wz = testOriginZ + rc[1];
                                if (wyBelow >= world.getMinHeight()) {
                                    Material matBelow = world.getBlockAt(wx, wyBelow, wz).getType();
                                    if (!isNaturalTerrainMaterial(matBelow) && !matBelow.isAir()) {
                                        blocksBelowCount++;
                                    }
                                }
                            }
                            if (blocksBelowCount >= Math.max(8, (int) (layer0Blocks.size() * 0.20))) {
                                continue; // Отклоняем: это крыша уже существующей постройки снизу!
                            }
                        }

                        // 4. Candidate Ranking:
                        // Полностью построенное здание (100%) всегда имеет наивысший приоритет над частичным.
                        // При равенстве побеждает наибольшее количество совпавших блоков и слоев.
                        boolean isFull = (totalMatched >= schem.getTotalBlockCount());
                        boolean isBetter = false;
                        if (bestAlignment == null) {
                            isBetter = true;
                        } else if (isFull && !bestAlignment.isFullyBuilt) {
                            isBetter = true; // 100% готовое здание безусловно побеждает!
                        } else if (!isFull && bestAlignment.isFullyBuilt) {
                            isBetter = false;
                        } else if (totalMatched > bestMatchedCount) {
                            isBetter = true;
                        } else if (totalMatched == bestMatchedCount && layersWithMatches > bestLayersWithMatches) {
                            isBetter = true;
                        } else if (totalMatched == bestMatchedCount && completedLayers > bestCompletedLayers) {
                            isBetter = true;
                        } else if (totalMatched == bestMatchedCount && testOriginY < bestAlignment.matchedOriginY) {
                            // При прочих равных отдаём предпочтение более глубокому уровню земли/фундамента, а не верхушке
                            isBetter = true;
                        }

                        if (isBetter) {
                            bestMatchedCount = totalMatched;
                            bestLayersWithMatches = layersWithMatches;
                            bestCompletedLayers = completedLayers;
                            bestAlignment = new ExistingStageAlignment(
                                    testOriginX,
                                    testOriginY,
                                    testOriginZ,
                                    rot,
                                    completedLayers,
                                    totalMatched,
                                    matchedKeys,
                                    isFull
                            );
                        }
                    }
                }
            }
        }

        return bestAlignment;
    }"""

assert old_detect in content, "old_detect not found"
content = content.replace(old_detect, new_detect, 1)

# 4. Update checkFootprintFlatness in startBuilding so already built/partially built buildings don't get rejected
old_flat_check = """        // 2. Check flat ground requirement for fresh plots so no blocks are buried underground
        if (plugin.getConfig().getBoolean("settings.require-flat-plot", true)) {"""

new_flat_check = """        // 2. Check flat ground requirement for fresh plots so no blocks are buried underground
        if (!isFullyConstructed && !isPartiallyConstructed && plugin.getConfig().getBoolean("settings.require-flat-plot", true)) {"""

assert old_flat_check in content, "old_flat_check not found"
content = content.replace(old_flat_check, new_flat_check, 1)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated BuildingManager.java successfully!")
