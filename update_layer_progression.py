with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'r', encoding='utf-8') as f:
    h_code = f.read()

# 1. Update HologramDisplayManager.handleBlockPlaced and add checkAndAdvanceLayer
new_h_logic = """    /**
     * Checks if all blocks of the current layer are finished (both in memory and in the physical world)
     * and advances the building to subsequent layers if complete.
     */
    public boolean checkAndAdvanceLayer(ActiveBuilding bld, BuildingSchematic schem, World world) {
        if (bld == null || schem == null || world == null) return false;

        int currentLayer = bld.getCurrentLayer();
        boolean layerDone = true;
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(currentLayer);

        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                continue;
            }
            // Verify physical world block at calculated coordinate
            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            int wx = bld.getOriginX() + rPos[0];
            int wy = bld.getOriginY() + sb.getDy();
            int wz = bld.getOriginZ() + rPos[1];

            if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                Material wm = world.getBlockAt(wx, wy, wz).getType();
                if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                    bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                    bld.addPlacedBlock(sb.getMaterial());
                    continue;
                }
            }
            layerDone = false;
            break;
        }

        if (!layerDone) {
            return false;
        }

        // Layer is complete! Advance forward!
        clearHologramsForBuilding(bld.getInstanceId());

        while (layerDone && currentLayer < schem.getMaxLayer()) {
            currentLayer++;
            bld.setCurrentLayer(currentLayer);

            layerDone = true;
            for (SchematicBlock sb : schem.getBlocksAtLayer(currentLayer)) {
                if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                    continue;
                }
                int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
                int wx = bld.getOriginX() + rPos[0];
                int wy = bld.getOriginY() + sb.getDy();
                int wz = bld.getOriginZ() + rPos[1];
                if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                    Material wm = world.getBlockAt(wx, wy, wz).getType();
                    if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                        bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                        bld.addPlacedBlock(sb.getMaterial());
                        continue;
                    }
                }
                layerDone = false;
                break;
            }

            if (!layerDone) {
                spawnLayerHolograms(bld, schem, world, currentLayer);
                Location loc = new Location(world,
                        bld.getOriginX() + (schem.getWidthX() / 2),
                        bld.getOriginY() + currentLayer,
                        bld.getOriginZ() + (schem.getLengthZ() / 2));
                world.playSound(loc, Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.3f);
                world.spawnParticle(Particle.VILLAGER_HAPPY, loc, 35, 4, 1, 4, 0.2);
                return true; // Successfully advanced to next layer!
            }
        }

        if (layerDone && currentLayer >= schem.getMaxLayer()) {
            clearHologramsForBuilding(bld.getInstanceId());
            return true;
        }
        return false;
    }

    /**
     * Handles when a correct block was placed: removes the single hologram and checks layer progression
     */
    public boolean handleBlockPlaced(ActiveBuilding bld, int dx, int dy, int dz) {
        String coordKey = dx + "," + dy + "," + dz;
        Map<String, BlockDisplay> map = activeDisplays.get(bld.getInstanceId());
        if (map != null) {
            BlockDisplay display = map.remove(coordKey);
            if (display != null && display.isValid()) {
                display.remove();
            }
        }

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return false;

        World world = Bukkit.getWorld(bld.getWorldName());
        return checkAndAdvanceLayer(bld, schem, world);
    }"""

idx_hp_start = h_code.find('public boolean handleBlockPlaced(ActiveBuilding bld, int dx, int dy, int dz)')
idx_hp_end = h_code.find('public void respawnHologramForMissingBlock', idx_hp_start)
h_code = h_code[:idx_hp_start] + new_h_logic + "\n\n    " + h_code[idx_hp_end:]

# Also in spawnLayerHolograms: auto-complete if the block was already physically placed in the world!
old_spawn_check = """            // If block was already marked as completed by building system, skip
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                continue;
            }"""

new_spawn_check = """            // If block is already completed or already physically placed in world, mark and skip
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                continue;
            }
            if (BuildingManager.isMaterialMatch(world.getBlockAt(spawnLoc).getType(), sb.getMaterial())) {
                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                bld.addPlacedBlock(sb.getMaterial());
                continue;
            }"""

if old_spawn_check in h_code:
    h_code = h_code.replace(old_spawn_check, new_spawn_check)
    print("Updated spawnLayerHolograms in HologramDisplayManager!")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'w', encoding='utf-8') as f:
    f.write(h_code)

print("HologramDisplayManager updated successfully!")
