with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

old_block = """        World world = player.getWorld();
        int minChunkX = Integer.MAX_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
        }
        // 1. Calculate natural terrain ground level (never roof!)
        int terrainGroundY = calculateTerrainGroundY(world, assignedChunks);
        if (terrainGroundY < 50) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Защита от бункеров: Постройка не может быть заложена под землей (Y < 50)! Все здания должны возводиться на поверхности мира."));
            return null;
        }
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bp.getId());
        // 2. Strict 3D schematic scan for existing construction in relative coordinates
        ExistingStageAlignment alignment = null;
        if (schem != null) {
            alignment = detectExistingConstruction(schem, world, assignedChunks);
        }
        int plotWidth = bp.getChunkWidth() * 16;
        int plotLength = bp.getChunkLength() * 16;
        int originX = minChunkX * 16 + Math.max(0, (plotWidth - (schem != null ? schem.getWidthX() : 16)) / 2);
        int originY = terrainGroundY;
        int originZ = minChunkZ * 16 + Math.max(0, (plotLength - (schem != null ? schem.getLengthZ() : 16)) / 2);
        int rotationDeg = 0;"""

new_block = """        World world = player.getWorld();
        int minChunkX = Integer.MAX_VALUE;
        int maxChunkX = Integer.MIN_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        int maxChunkZ = Integer.MIN_VALUE;
        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getX() > maxChunkX) maxChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
            if (cc.getZ() > maxChunkZ) maxChunkZ = cc.getZ();
        }
        int spanX = (maxChunkX - minChunkX + 1);
        int spanZ = (maxChunkZ - minChunkZ + 1);

        // 1. Calculate natural terrain ground level (never roof!)
        int terrainGroundY = calculateTerrainGroundY(world, assignedChunks);
        if (terrainGroundY < 50) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Защита от бункеров: Постройка не может быть заложена под землей (Y < 50)! Все здания должны возводиться на поверхности мира."));
            return null;
        }

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bp.getId());

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

if old_block in code:
    code = code.replace(old_block, new_block)
    with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully updated rotation and origin in BuildingManager.java!")
else:
    print("Error: old_block not found")
