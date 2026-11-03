package com.towny.respawn.hook;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Player;

import java.lang.reflect.Method;
import java.util.Collection;
import java.util.Collections;

public class TownyHook {

    public TownyHook() {
    }

    public boolean isTownyAvailable() {
        if (!Bukkit.getPluginManager().isPluginEnabled("Towny")) {
            return false;
        }
        try {
            Class<?> apiClass = Class.forName("com.palmergames.bukkit.towny.TownyAPI");
            Method getInstance = apiClass.getMethod("getInstance");
            return getInstance.invoke(null) != null;
        } catch (Throwable ignored) {
            return false;
        }
    }

    public Object getPlayerTown(Player player) {
        if (!isTownyAvailable() || player == null) return null;
        try {
            com.palmergames.bukkit.towny.TownyAPI api = com.palmergames.bukkit.towny.TownyAPI.getInstance();
            if (api == null) return null;
            com.palmergames.bukkit.towny.object.Resident resident = api.getResident(player);
            return (resident != null && resident.hasTown()) ? resident.getTownOrNull() : null;
        } catch (Throwable ignored) {
            return null;
        }
    }

    public String getPlayerTownName(Player player) {
        if (!isTownyAvailable() || player == null) return null;
        try {
            Object town = getPlayerTown(player);
            if (town instanceof com.palmergames.bukkit.towny.object.Town) {
                return ((com.palmergames.bukkit.towny.object.Town) town).getName();
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public Object getPlayerNation(Player player) {
        if (!isTownyAvailable() || player == null) return null;
        try {
            com.palmergames.bukkit.towny.TownyAPI api = com.palmergames.bukkit.towny.TownyAPI.getInstance();
            if (api == null) return null;
            com.palmergames.bukkit.towny.object.Resident resident = api.getResident(player);
            return (resident != null && resident.hasNation()) ? resident.getNationOrNull() : null;
        } catch (Throwable ignored) {
            return null;
        }
    }

    public String getPlayerNationName(Player player) {
        if (!isTownyAvailable() || player == null) return null;
        try {
            Object nation = getPlayerNation(player);
            if (nation instanceof com.palmergames.bukkit.towny.object.Nation) {
                return ((com.palmergames.bukkit.towny.object.Nation) nation).getName();
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public Location getTownSpawn(Object townObj) {
        if (townObj == null) return null;
        try {
            if (townObj instanceof com.palmergames.bukkit.towny.object.Town) {
                return ((com.palmergames.bukkit.towny.object.Town) townObj).getSpawn();
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public Location getNationSpawn(Object nationObj) {
        if (nationObj == null) return null;
        try {
            if (nationObj instanceof com.palmergames.bukkit.towny.object.Nation) {
                com.palmergames.bukkit.towny.object.Nation nation = (com.palmergames.bukkit.towny.object.Nation) nationObj;
                com.palmergames.bukkit.towny.object.Town capital = nation.getCapital();
                return capital != null ? capital.getSpawn() : null;
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public String getTownNameAt(Location loc) {
        if (!isTownyAvailable() || loc == null) return null;
        try {
            com.palmergames.bukkit.towny.TownyAPI api = com.palmergames.bukkit.towny.TownyAPI.getInstance();
            if (api == null) return null;
            com.palmergames.bukkit.towny.object.TownBlock tb = api.getTownBlock(loc);
            return (tb != null && tb.hasTown()) ? tb.getTownOrNull().getName() : null;
        } catch (Throwable ignored) {
            return null;
        }
    }

    public Object getTownAt(Location loc) {
        if (!isTownyAvailable() || loc == null) return null;
        try {
            com.palmergames.bukkit.towny.TownyAPI api = com.palmergames.bukkit.towny.TownyAPI.getInstance();
            if (api == null) return null;
            com.palmergames.bukkit.towny.object.TownBlock tb = api.getTownBlock(loc);
            return (tb != null && tb.hasTown()) ? tb.getTownOrNull() : null;
        } catch (Throwable ignored) {
            return null;
        }
    }

    public Collection<?> getAllTowns() {
        if (!isTownyAvailable()) return Collections.emptyList();
        try {
            com.palmergames.bukkit.towny.TownyAPI api = com.palmergames.bukkit.towny.TownyAPI.getInstance();
            if (api == null) return Collections.emptyList();
            return api.getTowns();
        } catch (Throwable ignored) {
            return Collections.emptyList();
        }
    }
}

