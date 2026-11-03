with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the duplicated loop in renderParticles()
old_part = """            // 1. Render active building boundaries, effect zones, and obstacle highlights
            for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                if (!bld.getWorldName().equals(pWorld.getName())) continue;
                if (bld.getAssignedChunks().isEmpty()) continue;

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                if (bp == null) continue;

                // C. Highlight obstacle blocks on current layer (trees, dirt, wrong blocks) in Bright Red!
                if (!bld.isFullyBuilt() && showBorders) {
                    renderObstacleWireframes(player, pWorld, bld, pX, pY, pZ);
                }
            for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                if (!bld.getWorldName().equals(pWorld.getName())) continue;
                if (bld.getAssignedChunks().isEmpty()) continue;

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                if (bp == null) continue;"""

new_part = """            // 1. Render active building boundaries, effect zones, and obstacle highlights
            for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                if (!bld.getWorldName().equals(pWorld.getName())) continue;
                if (bld.getAssignedChunks().isEmpty()) continue;

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                if (bp == null) continue;

                // C. Highlight obstacle blocks on current layer (trees, dirt, wrong blocks) in Bright Red!
                if (!bld.isFullyBuilt() && showBorders) {
                    renderObstacleWireframes(player, pWorld, bld, pX, pY, pZ);
                }"""

code = code.replace(old_part, new_part)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed BuildingHudManager.java!")
