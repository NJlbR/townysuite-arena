with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update detectExistingConstruction method with strict sequential layer order and exact material matching
new_detect_method = """    public ExistingStageAlignment detectExistingConstruction(BuildingSchematic schem, World world, Set<ChunkCoord> assignedChunks) {
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

idx_det_start = code.find('public ExistingStageAlignment detectExistingConstruction(')
idx_det_end = code.find('private void applyExistingStageBlocks(', idx_det_start)
code = code[:idx_det_start] + new_detect_method + "\n\n    " + code[idx_det_end:]

# 2. Update startBuilding to use the new strict detectExistingConstruction
old_start_chunk = """        int schemW = schem != null ? schem.getWidthX() : (bp.getChunkWidth() * 16);
        int schemL = schem != null ? schem.getLengthZ() : (bp.getChunkLength() * 16);
        int effectiveW = (rotationDeg == 90 || rotationDeg == 270) ? schemL : schemW;
        int effectiveL = (rotationDeg == 90 || rotationDeg == 270) ? schemW : schemL;

        int totalPlotWidthPx = spanX * 16;
        int totalPlotLengthPx = spanZ * 16;

        int originX = minChunkX * 16 + Math.max(0, (totalPlotWidthPx - effectiveW) / 2);
        int originY = terrainGroundY;
        int originZ = minChunkZ * 16 + Math.max(0, (totalPlotLengthPx - effectiveL) / 2);

        boolean isFullyConstructed = false;
        boolean isPartiallyConstructed = false;"""

new_start_chunk = """        ExistingStageAlignment alignment = null;
        if (schem != null) {
            alignment = detectExistingConstruction(schem, world, assignedChunks);
        }

        int schemW = schem != null ? schem.getWidthX() : (bp.getChunkWidth() * 16);
        int schemL = schem != null ? schem.getLengthZ() : (bp.getChunkLength() * 16);

        int totalPlotWidthPx = spanX * 16;
        int totalPlotLengthPx = spanZ * 16;

        boolean isFullyConstructed = false;
        boolean isPartiallyConstructed = false;

        int originX;
        int originY;
        int originZ;

        if (alignment != null && schem != null && alignment.matchedBlocksCount >= Math.max(12, (int) (schem.getBlocksAtLayer(0).size() * 0.40))) {
            // Auto-detected player-built partial or full structure!
            originX = alignment.matchedOriginX;
            originY = alignment.matchedOriginY;
            originZ = alignment.matchedOriginZ;
            rotationDeg = alignment.rotationDeg;
            if (alignment.isFullyBuilt) {
                isFullyConstructed = true;
            } else {
                isPartiallyConstructed = true;
            }
        } else {
            // Fresh clean plot
            int effectiveW = (rotationDeg == 90 || rotationDeg == 270) ? schemL : schemW;
            int effectiveL = (rotationDeg == 90 || rotationDeg == 270) ? schemW : schemL;
            originX = minChunkX * 16 + Math.max(0, (totalPlotWidthPx - effectiveW) / 2);
            originY = terrainGroundY;
            originZ = minChunkZ * 16 + Math.max(0, (totalPlotLengthPx - effectiveL) / 2);
        }"""

code = code.replace(old_start_chunk, new_start_chunk)

# Also in startBuilding, handle the case where isPartiallyConstructed or isFullyConstructed is true
old_active_init = """        building.setRotationDeg(rotationDeg);
        building.setCurrentLayer(0);
        building.setStatus(ActiveBuilding.Status.CONSTRUCTING);

        activeBuildings.put(instanceId, building);
        saveData();

        for (ChunkCoord cc : assignedChunks) {
            Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
            plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "В процессе постройки: " + bp.getNameRu());
        }

        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&a[!] Мэр утвердил проект «&6" + bp.getNameRu() + 
                        "&a». Город приступает к строительству!"));
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&e✦ Начните установку блоков фундамента (&fСлой 1&e) по 3D-голограммам чертежа."));
                p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.2f);
            }
        }

        plugin.getHologramDisplayManager().initHologramsForBuilding(building);
        return building;"""

new_active_init = """        building.setRotationDeg(rotationDeg);

        if (isFullyConstructed) {
            for (Map.Entry<Material, Integer> entry : req.entrySet()) {
                building.setPlacedCount(entry.getKey(), entry.getValue());
            }
            if (schem != null) {
                for (SchematicBlock sb : schem.getBlocks()) {
                    building.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                }
                building.setCurrentLayer(schem.getMaxLayer() + 1);
            }
            building.setStatus(ActiveBuilding.Status.ACTIVE);
            activeBuildings.put(instanceId, building);
            completeBuilding(building, bp, player);
            saveData();

            for (ChunkCoord cc : assignedChunks) {
                Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
                plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "Постройка: " + bp.getNameRu() + " (Завершена)");
            }

            for (Player p : Bukkit.getOnlinePlayers()) {
                String pTown = plugin.getTownyHook().getPlayerTownName(p);
                if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&a[!] Мэр утвердил проект «&6" + bp.getNameRu() + 
                            "&a». Постройка уже &eна 100% физически возведена &aна участке!"));
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&6✦ Здание введено в строй! Город получил все бонусы и пассивные эффекты."));
                    p.playSound(p.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.0f, 1.0f);
                }
            }
            return building;
        }

        if (isPartiallyConstructed && alignment != null && schem != null) {
            applyExistingStageBlocks(building, schem, alignment);
            activeBuildings.put(instanceId, building);
            saveData();

            for (ChunkCoord cc : assignedChunks) {
                Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
                plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "В процессе постройки: " + bp.getNameRu());
            }

            for (Player p : Bukkit.getOnlinePlayers()) {
                String pTown = plugin.getTownyHook().getPlayerTownName(p);
                if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&a[!] Мэр утвердил проект «&6" + bp.getNameRu() + 
                            "&a». Обнаружена частично возведенная конструкция (&e" + building.getProgressPercent() + "%&a)!"));
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&b✦ 3D-Чертеж автоматически повернут (" + rotationDeg + "°) и выровнен по высоте (Y=" + originY + 
                            "). Продолжайте возведение со Слоя " + (building.getCurrentLayer() + 1) + "!"));
                    p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.2f);
                }
            }

            plugin.getHologramDisplayManager().initHologramsForBuilding(building);
            return building;
        }

        // Clean fresh construction
        building.setCurrentLayer(0);
        building.setStatus(ActiveBuilding.Status.CONSTRUCTING);

        activeBuildings.put(instanceId, building);
        saveData();

        for (ChunkCoord cc : assignedChunks) {
            Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
            plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "В процессе постройки: " + bp.getNameRu());
        }

        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&a[!] Мэр утвердил проект «&6" + bp.getNameRu() + 
                        "&a». Город приступает к строительству!"));
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&e✦ Начните установку блоков фундамента (&fСлой 1&e) по 3D-голограммам чертежа."));
                p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.2f);
            }
        }

        plugin.getHologramDisplayManager().initHologramsForBuilding(building);
        return building;"""

code = code.replace(old_active_init, new_active_init)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated BuildingManager with strict auto-detection successfully!")
