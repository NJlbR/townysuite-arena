package com.towny.architecture.hook;

import com.palmergames.bukkit.towny.TownyAPI;
import com.palmergames.bukkit.towny.object.Town;
import com.palmergames.bukkit.towny.object.TownBlock;
import com.palmergames.bukkit.towny.object.TownBlockType;
import com.palmergames.bukkit.towny.object.TownyPermission;
import com.towny.architecture.model.ChunkCoord;
import org.bukkit.Bukkit;
import org.bukkit.Chunk;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import java.util.Set;
import java.util.HashSet;

public class TownyHook {

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
                       res.hasTownRank("assistant");
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
                       res.hasTownRank("assistant") ||
                       res.hasTownRank("builder");
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
    }
    
    public boolean tagPlotAsBuild(Location loc, String name) {
        if (!isTownyEnabled) return true;
        try {
            TownBlock townBlock = TownyAPI.getInstance().getTownBlock(loc);
            if (townBlock != null && townBlock.hasTown()) {
                try {
                    townBlock.setType(TownBlockType.RESIDENTIAL);
                } catch (Throwable ignored) {}

                if (name != null && !name.isEmpty()) {
                    townBlock.setName(name);
                }

                try {
                    TownyPermission perms = townBlock.getPermissions();
                    if (perms != null) {
                        perms.pvp = false;
                    }
                } catch (Throwable ignored) {}

                townBlock.save();
                return true;
            }
        } catch (Exception e) {
            Bukkit.getLogger().warning("[TownyArchitecture] Ошибка при установке названия участка Towny: " + e.getMessage());
        }
        return false;
    }

    public boolean tagPlotAsBuild(Player player, Location loc) {
        if (!isTownyEnabled) return true;
        if (!hasBuildRights(player, loc)) return false;
        return tagPlotAsBuild(loc, "Стройплощадка");
    }

    public boolean clearPlotTag(Location loc) {
        if (!isTownyEnabled) return true;
        try {
            TownBlock townBlock = TownyAPI.getInstance().getTownBlock(loc);
            if (townBlock != null && townBlock.hasTown()) {
                townBlock.setName("");
                townBlock.save();
                return true;
            }
        } catch (Exception ignored) {}
        return false;
    }

    public String getPlotName(Location loc) {
        if (!isTownyEnabled) return null;
        try {
            TownBlock townBlock = TownyAPI.getInstance().getTownBlock(loc);
            if (townBlock != null) {
                return townBlock.getName();
            }
        } catch (Exception ignored) {}
        return null;
    }


    private boolean isTownyEnabled;

    public TownyHook() {
        this.isTownyEnabled = Bukkit.getPluginManager().getPlugin("Towny") != null;
    }

    public boolean isTownyEnabled() {
        return isTownyEnabled;
    }

    public String getTownName(Chunk chunk) {
        if (!isTownyEnabled) return null;
        try {
            TownBlock tb = TownyAPI.getInstance().getTownBlock(new Location(chunk.getWorld(), chunk.getX() * 16, 0, chunk.getZ() * 16));
            if (tb != null && tb.hasTown()) {
                return tb.getTown().getName();
            }
        } catch (Exception e) {}
        return null;
    }
    
    public String getTownName(Location loc) {
        if (!isTownyEnabled) return null;
        try {
            TownBlock tb = TownyAPI.getInstance().getTownBlock(loc);
            if (tb != null && tb.hasTown()) {
                return tb.getTown().getName();
            }
        } catch (Exception e) {}
        return null;
    }

    public boolean isResidentOfTownAt(Player player, Location loc) {
        if (!isTownyEnabled) return false;
        try {
            TownBlock tb = TownyAPI.getInstance().getTownBlock(loc);
            if (tb != null && tb.hasTown()) {
                return tb.getTown().hasResident(player.getName()) || tb.getTown().hasResident(player.getUniqueId());
            }
        } catch (Exception e) {}
        return false;
    }

    public boolean hasBuildRights(Player player, Location loc) {
        if (!isTownyEnabled) return true; // Standalone mode -> always allow
        try {
            TownBlock tb = TownyAPI.getInstance().getTownBlock(loc);
            if (tb != null && tb.hasTown()) {
                Town town = tb.getTown();
                boolean isMayor = town.getMayor().getUUID().equals(player.getUniqueId());
                boolean isAssistant = TownyAPI.getInstance().getResident(player).hasTownRank("assistant");
                boolean isBuilder = TownyAPI.getInstance().getResident(player).hasTownRank("builder");
                return isMayor || isAssistant || isBuilder;
            }
        } catch (Exception e) {}
        return false;
    }
    
    public String getPlayerTown(Player player) {
        if (!isTownyEnabled) return null;
        try {
            var res = TownyAPI.getInstance().getResident(player.getUniqueId());
            if (res != null && res.hasTown()) {
                return res.getTown().getName();
            }
        } catch (Exception e) {}
        return null;
    }

    public int getTownChunkCount(String townName) {
        if (!isTownyEnabled || townName == null) return 0;
        try {
            Town town = TownyAPI.getInstance().getTown(townName);
            if (town != null) {
                return town.getTownBlocks().size();
            }
        } catch (Exception ignored) {}
        return 0;
    }

    public Set<ChunkCoord> getTownChunks(String townName) {
        Set<ChunkCoord> set = new HashSet<>();
        if (!isTownyEnabled || townName == null) return set;
        try {
            Town town = TownyAPI.getInstance().getTown(townName);
            if (town != null) {
                for (TownBlock tb : town.getTownBlocks()) {
                    set.add(new ChunkCoord(tb.getWorldCoord().getWorldName(), tb.getX(), tb.getZ()));
                }
            }
        } catch (Exception ignored) {}
        return set;
    }

    public boolean townExists(String townName) {
        if (!isTownyEnabled || townName == null) return false;
        try {
            return TownyAPI.getInstance().getTown(townName) != null;
        } catch (Exception ignored) {}
        return false;
    }
}
