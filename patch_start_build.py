import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """        // Check if there is already a building of this blueprint under construction in this town
        for (ActiveBuilding bld : activeBuildings.values()) {
            if (bld.getTownName().equalsIgnoreCase(townName) && 
                bld.getBlueprintId().equalsIgnoreCase(bp.getId()) && 
                bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&eПроект «" + bp.getNameRu() + "» уже находится в процессе строительства в вашем городе!"));
                return null;
            }
        }"""

replacement = """        // Check multiplicity limits
        int sameBlueprintCount = 0;
        for (ActiveBuilding bld : activeBuildings.values()) {
            if (bld.getTownName().equalsIgnoreCase(townName) && bld.getBlueprintId().equalsIgnoreCase(bp.getId())) {
                if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&eПроект «" + bp.getNameRu() + "» уже находится в процессе строительства в вашем городе!"));
                    return null;
                }
                sameBlueprintCount++;
            }
        }

        int areaChunks = bp.getChunkWidth() * bp.getChunkLength();
        if (areaChunks > 1 && sameBlueprintCount > 0) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cВаш город уже возвел здание «" + bp.getNameRu() + "»! (Лимит 1 для крупных построек)"));
            return null;
        }"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched startBuilding limit successfully.")
else:
    print("Target content not found!")
