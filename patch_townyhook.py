import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/hook/TownyHook.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    public boolean isLocationInPlayerTown(Location loc, Player player) {
        String pTown = getPlayerTownName(player);
        if (pTown == null) return false;
        return isLocationInTown(loc, pTown);
    }"""

replacement = """    public boolean isLocationInPlayerTown(Location loc, Player player) {
        String pTown = getPlayerTownName(player);
        if (pTown == null) return false;
        return isLocationInTown(loc, pTown);
    }

    public boolean isLocationTownHomeBlock(Location loc) {
        if (!isTownyEnabled) return false;
        try {
            com.palmergames.bukkit.towny.object.TownBlock townBlock = com.palmergames.bukkit.towny.TownyAPI.getInstance().getTownBlock(loc);
            if (townBlock != null && townBlock.hasTown()) {
                com.palmergames.bukkit.towny.object.Town town = townBlock.getTown();
                com.palmergames.bukkit.towny.object.TownBlock homeBlock = town.getHomeBlock();
                if (homeBlock != null) {
                    return townBlock.getX() == homeBlock.getX() && townBlock.getZ() == homeBlock.getZ();
                }
            }
        } catch (Exception e) {
            // Error checking homeblock
        }
        return false;
    }"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/hook/TownyHook.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched TownyHook.java successfully.")
else:
    print("Target content not found!")
