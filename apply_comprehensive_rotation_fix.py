with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Fix findFreePlotArea to consider player yaw facing direction
old_ff = """public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk) {
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
                : new int[][]{{widthChunks, lengthChunks}, {lengthChunks, widthChunks}};"""

new_ff = """public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk) {
        return findFreePlotArea(townName, worldName, widthChunks, lengthChunks, preferredChunk, 0.0f);
    }

    public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk, float playerYaw) {
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

        float normYaw = (playerYaw % 360 + 360) % 360;
        boolean facingX = (normYaw >= 45 && normYaw < 135) || (normYaw >= 225 && normYaw < 315);

        int maxChunkDim = Math.max(widthChunks, lengthChunks);
        int minChunkDim = Math.min(widthChunks, lengthChunks);

        int[][] orientations;
        if (widthChunks == lengthChunks) {
            orientations = new int[][]{{widthChunks, lengthChunks}};
        } else if (facingX) {
            orientations = new int[][]{{maxChunkDim, minChunkDim}, {minChunkDim, maxChunkDim}};
        } else {
            orientations = new int[][]{{minChunkDim, maxChunkDim}, {maxChunkDim, minChunkDim}};
        }"""

if old_ff in code:
    code = code.replace(old_ff, new_ff)
    print("Updated findFreePlotArea with yaw support!")
else:
    print("Warning: old_ff not found exactly, searching substring...")

# 2. Fix plotWidth / plotLength bug in checkFootprintFlatness call in startBuilding
old_flat = "TerrainFlatnessResult flatness = checkFootprintFlatness(world, minChunkX * 16, minChunkZ * 16, plotWidth, plotLength, maxDiff);"
new_flat = "TerrainFlatnessResult flatness = checkFootprintFlatness(world, minChunkX * 16, minChunkZ * 16, totalPlotWidthPx, totalPlotLengthPx, maxDiff);"
if old_flat in code:
    code = code.replace(old_flat, new_flat)
    print("Fixed flatness check plot dimensions!")
else:
    print("Warning: old_flat not found")

# 3. Add rotateBuilding method to BuildingManager
if "public boolean rotateActiveBuilding" not in code:
    last_brace = code.rfind('}')
    rotate_method = """
    public boolean rotateActiveBuilding(Player player, ActiveBuilding building) {
        if (building == null || player == null) return false;
        String playerTown = plugin.getTownyHook().getPlayerTownName(player);
        if (playerTown == null || !playerTown.equalsIgnoreCase(building.getTownName())) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Вы не состоите в этом городе!");
            return false;
        }
        if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player) && !plugin.getTownyHook().hasBuilderPermission(player, building.getTownName())) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] У вас нет прав на изменение ориентации постройки!");
            return false;
        }
        if (building.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Нельзя поворачивать завершенное или поврежденное здание!");
            return false;
        }
        if (building.getCompletedBlockCount() > 0) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Нельзя поворачивать проект, в котором уже установлены блоки! Сначала снесите блоки.");
            return false;
        }

        BuildingBlueprint bp = blueprints.get(building.getBlueprintId());
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(building.getBlueprintId());
        if (bp == null) return false;

        int currentRot = building.getRotationDeg();
        int newRot = (currentRot + 90) % 360;

        int minCX = Integer.MAX_VALUE, maxCX = Integer.MIN_VALUE;
        int minCZ = Integer.MAX_VALUE, maxCZ = Integer.MIN_VALUE;
        for (ChunkCoord cc : building.getAssignedChunks()) {
            minCX = Math.min(minCX, cc.getX());
            maxCX = Math.max(maxCX, cc.getX());
            minCZ = Math.min(minCZ, cc.getZ());
            maxCZ = Math.max(maxCZ, cc.getZ());
        }
        int totalWidthPx = (maxCX - minCX + 1) * 16;
        int totalLengthPx = (maxCZ - minCZ + 1) * 16;

        int schemW = schem != null ? schem.getWidthX() : (bp.getChunkWidth() * 16);
        int schemL = schem != null ? schem.getLengthZ() : (bp.getChunkLength() * 16);
        int effectiveW = (newRot == 90 || newRot == 270) ? schemL : schemW;
        int effectiveL = (newRot == 90 || newRot == 270) ? schemW : schemL;

        int newOriginX = minCX * 16 + Math.max(0, (totalWidthPx - effectiveW) / 2);
        int newOriginZ = minCZ * 16 + Math.max(0, (totalLengthPx - effectiveL) / 2);

        building.setRotationDeg(newRot);
        building.setOrigin(newOriginX, building.getOriginY(), newOriginZ);
        saveData();

        // Refresh holograms
        plugin.getHologramDisplayManager().initHologramsForBuilding(building);
        return true;
    }
"""
    code = code[:last_brace] + rotate_method + code[last_brace:]
    print("Added rotateActiveBuilding method to BuildingManager!")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("BuildingManager.java updated successfully!")
