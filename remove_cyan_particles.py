with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update line 118 call
code = code.replace(
    "renderLayerBlockWireframes(player, pWorld, bld, pX, pY, pZ, ghostCyanDust, obstacleRedDust);",
    "renderLayerObstacleWireframes(player, pWorld, bld, pX, pY, pZ, obstacleRedDust);"
)

# 2. Update renderLayerBlockWireframes method to renderLayerObstacleWireframes
old_method = """    /**
     * Renders crisp 3D edge wireframes around all active layer blocks:
     * - CYAN wireframe for required Ghost Blocks so they are clearly visible
     * - RED wireframe for Obstacle Blocks (trees, dirt, wrong blocks) that must be cleared
     */
    private void renderLayerBlockWireframes(Player player, World world, ActiveBuilding bld, 
                                           double pX, double pY, double pZ,
                                           Particle.DustOptions cyanDust, Particle.DustOptions redDust) {
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return;

        int currentLayer = bld.getCurrentLayer();
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(currentLayer);
        if (layerBlocks == null || layerBlocks.isEmpty()) return;

        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) continue;

            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            int wx = bld.getOriginX() + rPos[0];
            int wy = bld.getOriginY() + sb.getDy();
            int wz = bld.getOriginZ() + rPos[1];

            // Only check within player view range (28 blocks)
            if (Math.abs(wx - pX) > 50.0 || Math.abs(wz - pZ) > 50.0 || Math.abs(wy - pY) > 16.0) continue;

            Material wm = world.getBlockAt(wx, wy, wz).getType();
            if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                continue; // Block placed and matching
            }

            boolean isObstacle = !wm.isAir() && !(wm == Material.WATER || wm == Material.LAVA);
            Particle.DustOptions dustToUse = isObstacle ? redDust : cyanDust;

            renderBlockWireframeBox(player, wx, wy, wz, dustToUse);
        }
    }"""

new_method = """    /**
     * Renders warning wireframes ONLY for Obstacle Blocks (trees, dirt, wrong blocks) that must be cleared.
     * Normal ghost blocks do NOT have cyan particle dust; their native BlockDisplay glowing cyan outlines are clean and sufficient!
     */
    private void renderLayerObstacleWireframes(Player player, World world, ActiveBuilding bld, 
                                              double pX, double pY, double pZ,
                                              Particle.DustOptions redDust) {
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return;

        int currentLayer = bld.getCurrentLayer();
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(currentLayer);
        if (layerBlocks == null || layerBlocks.isEmpty()) return;

        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) continue;

            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            int wx = bld.getOriginX() + rPos[0];
            int wy = bld.getOriginY() + sb.getDy();
            int wz = bld.getOriginZ() + rPos[1];

            // Only check within player view range (28 blocks)
            if (Math.abs(wx - pX) > 50.0 || Math.abs(wz - pZ) > 50.0 || Math.abs(wy - pY) > 16.0) continue;

            Material wm = world.getBlockAt(wx, wy, wz).getType();
            if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                continue; // Block placed and matching
            }

            boolean isObstacle = !wm.isAir() && !(wm == Material.WATER || wm == Material.LAVA);
            if (isObstacle) {
                renderBlockWireframeBox(player, wx, wy, wz, redDust);
            }
        }
    }"""

code = code.replace(old_method, new_method)

# Remove unused ghostCyanDust variable
code = code.replace(
    "Particle.DustOptions ghostCyanDust = new Particle.DustOptions(Color.fromRGB(0, 220, 255), 1.6f);\n        ",
    ""
)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Removed cyan particles from block holograms in BuildingHudManager.java successfully!")
