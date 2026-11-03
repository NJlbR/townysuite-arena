import re

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/hook/TownyHook.java', 'r') as f:
    content = f.read()

# Add missing methods that BuildingManager and others are calling

methods_to_add = """
    public String getPlayerTownName(Player player) {
        return getPlayerTown(player);
    }
    
    public boolean isPlayerMayorOrAssistant(Player player) {
        if (!isTownyEnabled) return true;
        try {
            var res = TownyAPI.getInstance().getResident(player.getUniqueId());
            if (res != null && res.hasTown()) {
                Town town = res.getTown();
                return town.getMayor().getUUID().equals(player.getUniqueId()) || 
                       town.getRank(res).contains("assistant");
            }
        } catch (Exception e) {}
        return false;
    }

    public boolean hasBuilderPermission(Player player, String townName) {
        if (!isTownyEnabled) return true;
        try {
            var res = TownyAPI.getInstance().getResident(player.getUniqueId());
            if (res != null && res.hasTown() && res.getTown().getName().equalsIgnoreCase(townName)) {
                Town town = res.getTown();
                return town.getMayor().getUUID().equals(player.getUniqueId()) || 
                       town.getRank(res).contains("assistant") ||
                       town.getRank(res).contains("builder");
            }
        } catch (Exception e) {}
        return false;
    }

    public boolean isLocationInTown(Location loc, String townName) {
        if (!isTownyEnabled) return true;
        try {
            TownBlock tb = TownyAPI.getInstance().getTownBlock(loc);
            if (tb != null && tb.hasTown()) {
                return tb.getTown().getName().equalsIgnoreCase(townName);
            }
        } catch (Exception e) {}
        return false;
    }
    
    public boolean isLocationInPlayerTown(Location loc, Player player) {
        String pTown = getPlayerTownName(player);
        if (pTown == null) return false;
        return isLocationInTown(loc, pTown);
    }
    
    public boolean tagPlotAsBuild(Location loc, String name) {
        // Fallback for older method signature without Player
        if (!isTownyEnabled) return true;
        try {
            TownBlock townBlock = TownyAPI.getInstance().getTownBlock(loc);
            if (townBlock != null && townBlock.hasTown()) {
                java.lang.reflect.Method setTypeMethod = townBlock.getClass().getMethod("setType", int.class);
                setTypeMethod.invoke(townBlock, 0);

                java.lang.reflect.Method getPermissionsMethod = townBlock.getClass().getMethod("getPermissions");
                Object perms = getPermissionsMethod.invoke(townBlock);
                if (perms != null) {
                    try {
                        perms.getClass().getField("pvp").set(perms, false);
                    } catch (Exception e1) {
                        try {
                            perms.getClass().getMethod("setPvP", boolean.class).invoke(perms, false);
                        } catch (Exception e2) {}
                    }
                }
                
                try {
                    java.lang.reflect.Method saveMethod = townBlock.getClass().getMethod("save");
                    saveMethod.invoke(townBlock);
                } catch (Exception ignored) {}
                
                return true;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
    }
"""

content = content.replace("public class TownyHook {", "public class TownyHook {\n" + methods_to_add)

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/hook/TownyHook.java', 'w') as f:
    f.write(content)
