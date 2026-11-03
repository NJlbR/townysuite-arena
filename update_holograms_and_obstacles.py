import re

# 1. Update HologramDisplayManager.java
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace spawnLayerHolograms block spawn
old_spawn_section = """            try {
                BlockDisplay display = world.spawn(spawnLoc, BlockDisplay.class, entity -> {
                    entity.setBlock(sb.getMaterial().createBlockData());
                    // Bright, clear hologram visibility (not dark or murky)
                    entity.setBrightness(getConfiguredBrightness());
                    entity.setShadowRadius(0f);
                    entity.setShadowStrength(0f);
                    
                    // Slightly smaller transformation (scale 0.98) with centered offset (0.01) to prevent z-fighting
                    Transformation transformation = new Transformation(
                            new Vector3f(0.01f, 0.01f, 0.01f),
                            new AxisAngle4f(),
                            new Vector3f(0.98f, 0.98f, 0.98f),
                            new AxisAngle4f()
                    );
                    entity.setTransformation(transformation);
                    entity.setGlowing(false); // Clean projection without distracting glowing outline
                    
                    // Mark with persistent data tags
                    entity.getPersistentDataContainer().set(hologramKey, PersistentDataType.STRING, bld.getInstanceId());
                    entity.getPersistentDataContainer().set(blockCoordKey, PersistentDataType.STRING, coordKey);
                    entity.setPersistent(false); // Do not save into chunk save files
                });
                buildingMap.put(coordKey, display);
            }"""

new_spawn_section = """            try {
                Material worldMat = world.getBlockAt(spawnLoc).getType();
                boolean isObstacle = !worldMat.isAir() && !worldMat.isLiquid() && !BuildingManager.isMaterialMatch(worldMat, sb.getMaterial());

                BlockDisplay display = world.spawn(spawnLoc, BlockDisplay.class, entity -> {
                    entity.setBlock(sb.getMaterial().createBlockData());
                    entity.setBrightness(getConfiguredBrightness());
                    entity.setShadowRadius(0f);
                    entity.setShadowStrength(0f);
                    
                    Transformation transformation = new Transformation(
                            new Vector3f(0.01f, 0.01f, 0.01f),
                            new AxisAngle4f(),
                            new Vector3f(0.98f, 0.98f, 0.98f),
                            new AxisAngle4f()
                    );
                    entity.setTransformation(transformation);
                    
                    // BRIGHT EDGE HIGHLIGHTING:
                    // 1. Vivid Neon Cyan (RGB 0, 220, 255) for ghost hologram blocks so white/grey/black blocks stand out
                    // 2. Vivid Warning Red (RGB 255, 30, 30) if an obstacle block (tree/dirt/wrong block) is blocking it!
                    entity.setGlowing(true);
                    try {
                        if (isObstacle) {
                            entity.setGlowColorOverride(Color.fromRGB(255, 30, 30)); // Red Warning for Obstacles
                        } else if (bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                            entity.setGlowColorOverride(Color.fromRGB(255, 50, 50));
                        } else {
                            entity.setGlowColorOverride(Color.fromRGB(0, 220, 255)); // Bright Cyan Glowing Edges
                        }
                    } catch (Throwable ignored) {}
                    
                    entity.getPersistentDataContainer().set(hologramKey, PersistentDataType.STRING, bld.getInstanceId());
                    entity.getPersistentDataContainer().set(blockCoordKey, PersistentDataType.STRING, coordKey);
                    entity.setPersistent(false);
                });
                buildingMap.put(coordKey, display);
            }"""

if old_spawn_section in code:
    code = code.replace(old_spawn_section, new_spawn_section)
    print("Replaced spawnLayerHolograms display in HologramDisplayManager")
else:
    # Try regex replace if formatting differed slightly
    pattern = r'try\s*\{\s*BlockDisplay\s+display\s*=\s*world\.spawn\(spawnLoc,\s*BlockDisplay\.class,\s*entity\s*->\s*\{.*?entity\.setGlowing\(false\);.*?\}\);\s*buildingMap\.put\(coordKey,\s*display\);\s*\}'
    code = re.sub(pattern, new_spawn_section, code, flags=re.DOTALL)
    print("Replaced spawnLayerHolograms display with regex in HologramDisplayManager")

# Also update respawnHologramForMissingBlock
old_respawn = """                // Only glow if building was fully active and got damaged in war/siege
                if (bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                    entity.setGlowing(true);
                    try {
                        entity.setGlowColorOverride(Color.RED);
                    } catch (Throwable ignored) {}
                } else {
                    entity.setGlowing(false);
                }"""

new_respawn = """                entity.setGlowing(true);
                try {
                    Material currentWorldMat = world.getBlockAt(spawnLoc).getType();
                    if (!currentWorldMat.isAir() && !currentWorldMat.isLiquid() && !BuildingManager.isMaterialMatch(currentWorldMat, displayMat)) {
                        entity.setGlowColorOverride(Color.fromRGB(255, 30, 30)); // Red Obstacle
                    } else if (bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                        entity.setGlowColorOverride(Color.fromRGB(255, 50, 50));
                    } else {
                        entity.setGlowColorOverride(Color.fromRGB(0, 220, 255)); // Bright Cyan Edges
                    }
                } catch (Throwable ignored) {}"""

code = code.replace(old_respawn, new_respawn)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated HologramDisplayManager.java successfully!")

# 2. Update BuildingHudManager.java with Obstacle Wireframe Particle Highlights
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'r', encoding='utf-8') as f:
    hud_code = f.read()

# Add obstacle highlighting loop inside renderParticles()
render_anchor = "// 1. Render active building boundaries and effect zones"
new_obstacle_call = """// 1. Render active building boundaries, effect zones, and obstacle highlights
            for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                if (!bld.getWorldName().equals(pWorld.getName())) continue;
                if (bld.getAssignedChunks().isEmpty()) continue;

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                if (bp == null) continue;

                // C. Highlight obstacle blocks on current layer (trees, dirt, wrong blocks) in Bright Red!
                if (!bld.isFullyBuilt() && showBorders) {
                    renderObstacleWireframes(player, pWorld, bld, pX, pY, pZ);
                }"""

hud_code = hud_code.replace(render_anchor, new_obstacle_call)

# Add renderObstacleWireframes method before findGroundY
find_ground_anchor = "private double findGroundY(World world, double x, double z, double playerY) {"
new_wireframe_method = """    /**
     * Renders bright warning wireframes around obstacle blocks (trees, dirt, wrong blocks)
     * that are standing where blueprint blocks need to be placed.
     */
    private void renderObstacleWireframes(Player player, World world, ActiveBuilding bld, double pX, double pY, double pZ) {
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return;

        int currentLayer = bld.getCurrentLayer();
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(currentLayer);
        if (layerBlocks == null || layerBlocks.isEmpty()) return;

        Particle.DustOptions obstacleDust = new Particle.DustOptions(Color.fromRGB(255, 30, 30), 1.8f);

        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) continue;

            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            int wx = bld.getOriginX() + rPos[0];
            int wy = bld.getOriginY() + sb.getDy();
            int wz = bld.getOriginZ() + rPos[1];

            // Only check within player view range (32 blocks)
            if (Math.abs(wx - pX) > 32.0 || Math.abs(wz - pZ) > 32.0 || Math.abs(wy - pY) > 20.0) continue;

            Material wm = world.getBlockAt(wx, wy, wz).getType();
            if (wm.isAir() || wm.isLiquid() || BuildingManager.isMaterialMatch(wm, sb.getMaterial())) continue;

            // This block is an OBSTACLE! Draw bright glowing red box wireframe on its 12 edges
            renderBlockBox(player, world, wx, wy, wz, obstacleDust);
        }
    }

    private void renderBlockBox(Player player, World world, int bx, int by, int bz, Particle.DustOptions dust) {
        double minX = bx, maxX = bx + 1.0;
        double minY = by, maxY = by + 1.0;
        double minZ = bz, maxZ = bz + 1.0;

        // 8 corners
        for (double x : new double[]{minX, maxX}) {
            for (double y : new double[]{minY, maxY}) {
                for (double z : new double[]{minZ, maxZ}) {
                    player.spawnParticle(dustParticle, x, y, z, 1, 0, 0, 0, 0, dust);
                }
            }
        }

        // Center warning pulse
        player.spawnParticle(dustParticle, bx + 0.5, by + 0.5, bz + 0.5, 1, 0.1, 0.1, 0.1, 0, dust);
    }

    private double findGroundY(World world, double x, double z, double playerY) {"""

hud_code = hud_code.replace(find_ground_anchor, new_wireframe_method)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'w', encoding='utf-8') as f:
    f.write(hud_code)

print("Updated BuildingHudManager.java successfully!")
