with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = "    public void respawnHologramForMissingBlock(ActiveBuilding bld, int dx, int dy, int dz, Material mat) {"

new_code = """    /**
     * Self-healing watchdog: checks if any holograms for the current layer of a constructing building
     * have been destroyed, despawned, or unloaded, and safely respawns them if the chunk is loaded.
     */
    public int healOrRefreshLayerHolograms(ActiveBuilding bld) {
        if (bld == null || bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) return 0;
        World world = Bukkit.getWorld(bld.getWorldName());
        if (world == null) return 0;

        // Ensure chunks are currently loaded in world so we do not force-load distant chunks
        boolean chunkLoaded = false;
        if (bld.getAssignedChunks() != null && !bld.getAssignedChunks().isEmpty()) {
            for (com.towny.architecture.model.ChunkCoord cc : bld.getAssignedChunks()) {
                if (world.isChunkLoaded(cc.getX(), cc.getZ())) {
                    chunkLoaded = true;
                    break;
                }
            }
        } else {
            chunkLoaded = world.isChunkLoaded(bld.getOriginX() >> 4, bld.getOriginZ() >> 4);
        }
        if (!chunkLoaded) return 0;

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return 0;

        int targetLayer = bld.getCurrentLayer();
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(targetLayer);
        if (layerBlocks == null || layerBlocks.isEmpty()) return 0;

        Map<String, BlockDisplay> buildingMap = activeDisplays.computeIfAbsent(bld.getInstanceId(), k -> new ConcurrentHashMap<>());
        buildingMap.entrySet().removeIf(e -> e.getValue() == null || !e.getValue().isValid() || e.getValue().isDead());

        int healed = 0;
        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                continue;
            }

            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            int wx = bld.getOriginX() + rPos[0];
            int wy = bld.getOriginY() + sb.getDy();
            int wz = bld.getOriginZ() + rPos[1];

            // If block is already physically placed in world, mark and skip
            Material wm = world.getBlockAt(wx, wy, wz).getType();
            if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                bld.addPlacedBlock(sb.getMaterial());
                BlockDisplay oldDisp = buildingMap.remove(sb.getKey());
                if (oldDisp != null && oldDisp.isValid()) {
                    oldDisp.remove();
                }
                continue;
            }

            String coordKey = sb.getKey();
            BlockDisplay existing = buildingMap.get(coordKey);
            if (existing == null || !existing.isValid() || existing.isDead()) {
                respawnHologramForMissingBlock(bld, sb.getDx(), sb.getDy(), sb.getDz(), sb.getMaterial());
                healed++;
            }
        }
        return healed;
    }

    public void respawnHologramForMissingBlock(ActiveBuilding bld, int dx, int dy, int dz, Material mat) {"""

assert target in content, "Target not found in HologramDisplayManager"
content = content.replace(target, new_code, 1)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated HologramDisplayManager.java with healOrRefreshLayerHolograms!")
