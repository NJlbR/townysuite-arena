with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Clean up startBuilding: remove auto partial matching so building always starts fresh at layer 0 and 0%
old_start_block = """        ExistingStageAlignment alignment = null;
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
        int originZ = minChunkZ * 16 + Math.max(0, (totalPlotLengthPx - effectiveL) / 2);

        boolean isFullyConstructed = false;
        boolean isPartiallyConstructed = false;

        // STRICT: Completion only at 100% of all required blocks at their relative positions!
        if (alignment != null && schem != null && alignment.isFullyBuilt && alignment.matchedBlocksCount >= schem.getTotalBlockCount()) {
            isFullyConstructed = true;
            originX = alignment.matchedOriginX;
            originY = alignment.matchedOriginY;
            originZ = alignment.matchedOriginZ;
            rotationDeg = alignment.rotationDeg;
        } else if (alignment != null && schem != null && alignment.matchedBlocksCount >= Math.max(16, (int) (schem.getTotalBlockCount() * 0.20))) {
            isPartiallyConstructed = true;
            originX = alignment.matchedOriginX;
            originY = alignment.matchedOriginY;
            originZ = alignment.matchedOriginZ;
            rotationDeg = alignment.rotationDeg;
        }"""

new_start_block = """        int schemW = schem != null ? schem.getWidthX() : (bp.getChunkWidth() * 16);
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

if old_start_block in code:
    code = code.replace(old_start_block, new_start_block)
    print("Cleaned up startBuilding to ensure 0% clean start!")
else:
    print("Warning: old_start_block not found exactly, inspecting...")

# Also ensure handleBlockPlaced notifies layer advancement to players
old_block_match = """            // Correct block matched!
            building.markBlockCompleted(dx, dy, dz);
            plugin.getHologramDisplayManager().handleBlockPlaced(building, dx, dy, dz);"""

new_block_match = """            // Correct block matched!
            building.markBlockCompleted(dx, dy, dz);
            boolean layerAdvanced = plugin.getHologramDisplayManager().handleBlockPlaced(building, dx, dy, dz);
            if (layerAdvanced) {
                for (Player p : Bukkit.getOnlinePlayers()) {
                    String pTown = plugin.getTownyHook().getPlayerTownName(p);
                    if (pTown != null && pTown.equalsIgnoreCase(building.getTownName())) {
                        p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                plugin.getMsg("prefix") + "&a✦ Слой " + building.getCurrentLayer() + " завершен! Открыт &6Слой " + (building.getCurrentLayer() + 1) + "&a!"));
                    }
                }
            }"""

if old_block_match in code:
    code = code.replace(old_block_match, new_block_match)
    print("Added layer advance town notification in BuildingManager!")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

# 2. Update HologramDisplayManager.java
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'r', encoding='utf-8') as f:
    h_code = f.read()

# Remove auto-marking in spawnLayerHolograms so ghost holograms are always shown for every block in the layer
old_h_check = """            // Check if world already has block there
            if (BuildingManager.isMaterialMatch(world.getBlockAt(spawnLoc).getType(), sb.getMaterial())) {
                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                continue;
            }"""

new_h_check = """            // If block was already marked as completed by building system, skip
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                continue;
            }"""

if old_h_check in h_code:
    h_code = h_code.replace(old_h_check, new_h_check)
    print("Fixed spawnLayerHolograms in HologramDisplayManager!")

# Also improve center calculation for sound/particle effect in layer completion
old_loc = "Location loc = new Location(world, bld.getOriginX() + 8, bld.getOriginY() + currentLayer, bld.getOriginZ() + 8);"
new_loc = "Location loc = new Location(world, bld.getOriginX() + (schem.getWidthX() / 2), bld.getOriginY() + currentLayer, bld.getOriginZ() + (schem.getLengthZ() / 2));"

if old_loc in h_code:
    h_code = h_code.replace(old_loc, new_loc)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'w', encoding='utf-8') as f:
    h_code = f.write(h_code)

print("All Java files updated successfully!")
