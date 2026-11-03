import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    public Set<ChunkCoord> getTownBuildPlots(String townName) {
        if (townName == null) return Collections.emptySet();
        return townBuildPlots.getOrDefault(townName.toLowerCase(), Collections.emptySet());
    }"""

replacement = """    public Set<ChunkCoord> getTownBuildPlots(String townName) {
        if (townName == null) return Collections.emptySet();
        return townBuildPlots.getOrDefault(townName.toLowerCase(), Collections.emptySet());
    }

    public void demolishBuilding(ActiveBuilding bld) {
        activeBuildings.remove(bld.getId());
        
        BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
        if (bp != null && bp.isWorldWonder()) {
            bp.setWonderCompletedByTown(null);
            if (dataConfig != null) {
                dataConfig.set("wonders." + bp.getId(), null);
            }
        }
        
        // Remove hologram/hud
        plugin.getBuildingHudManager().removeHologram(bld.getId());
        
        saveData();
    }"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched BuildingManager.java demolish successfully.")
else:
    print("Target content not found!")
