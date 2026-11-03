package com.towny.sieges.hook;

import com.palmergames.bukkit.towny.TownyAPI;
import com.palmergames.bukkit.towny.object.Nation;
import com.palmergames.bukkit.towny.object.Resident;
import com.palmergames.bukkit.towny.object.Town;
import com.palmergames.bukkit.towny.object.TownBlock;
import com.palmergames.bukkit.towny.object.WorldCoord;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Player;

import java.util.Collection;
import java.util.LinkedHashSet;
import java.util.Set;

public class TownyHook {

    public boolean isTownyEnabled() {
        return Bukkit.getPluginManager().isPluginEnabled("Towny");
    }

    public Town getTown(String townName) {
        if (!isTownyEnabled() || townName == null) return null;
        try {
            return TownyAPI.getInstance().getTown(townName);
        } catch (Throwable ignored) {
            return null;
        }
    }

    public Town getTownAt(Location loc) {
        if (!isTownyEnabled() || loc == null) return null;
        try {
            TownyAPI api = TownyAPI.getInstance();
            if (api != null) {
                Town town = api.getTown(loc);
                if (town != null) return town;
                TownBlock tb = api.getTownBlock(loc);
                if (tb != null) {
                    return tb.getTownOrNull();
                }
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public String getTownNameAt(Location loc) {
        if (!isTownyEnabled() || loc == null) return null;
        try {
            TownyAPI api = TownyAPI.getInstance();
            if (api != null) {
                String name = api.getTownName(loc);
                if (name != null && !name.isEmpty()) return name;
                Town town = getTownAt(loc);
                if (town != null) return town.getName();
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public String getPlayerTownName(Player player) {
        if (!isTownyEnabled() || player == null) return null;
        try {
            Resident res = TownyAPI.getInstance().getResident(player);
            if (res != null && res.hasTown()) {
                return res.getTown().getName();
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public boolean isMayor(Player player, String townName) {
        if (!isTownyEnabled() || player == null || townName == null) return false;
        try {
            Town town = getTown(townName);
            if (town != null && town.hasMayor()) {
                return town.getMayor().getName().equalsIgnoreCase(player.getName());
            }
        } catch (Throwable ignored) {}
        return false;
    }

    public boolean isResidentOfTown(Player player, String townName) {
        if (!isTownyEnabled() || player == null || townName == null) return false;
        try {
            Resident res = TownyAPI.getInstance().getResident(player);
            if (res != null && res.hasTown()) {
                return res.getTown().getName().equalsIgnoreCase(townName);
            }
        } catch (Throwable ignored) {}
        return false;
    }

    // --- Nation Wars Integration ---

    public Nation getNation(String nationName) {
        if (!isTownyEnabled() || nationName == null) return null;
        try {
            return TownyAPI.getInstance().getNation(nationName);
        } catch (Throwable ignored) {
            return null;
        }
    }

    public String getTownNationName(String townName) {
        if (!isTownyEnabled() || townName == null) return null;
        try {
            Town town = getTown(townName);
            if (town != null && town.hasNation()) {
                Nation n = town.getNationOrNull();
                if (n != null) return n.getName();
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public String getPlayerNationName(Player player) {
        if (!isTownyEnabled() || player == null) return null;
        try {
            String townName = getPlayerTownName(player);
            if (townName != null) {
                return getTownNationName(townName);
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public boolean isNationKing(Player player, String nationName) {
        if (!isTownyEnabled() || player == null || nationName == null) return false;
        try {
            Nation nation = getNation(nationName);
            if (nation != null && nation.getKing() != null) {
                return nation.getKing().getName().equalsIgnoreCase(player.getName());
            }
        } catch (Throwable ignored) {}
        return false;
    }

    public Set<String> getNationTownNames(String nationName) {
        Set<String> towns = new LinkedHashSet<>();
        if (!isTownyEnabled() || nationName == null) return towns;
        try {
            Nation nation = getNation(nationName);
            if (nation != null && nation.getTowns() != null) {
                for (Town t : nation.getTowns()) {
                    if (t != null && t.getName() != null) {
                        towns.add(t.getName());
                    }
                }
            }
        } catch (Throwable ignored) {}
        return towns;
    }

    public Set<com.towny.sieges.model.ChunkCoord> getTownChunks(String townName) {
        Set<com.towny.sieges.model.ChunkCoord> coords = new LinkedHashSet<>();
        if (!isTownyEnabled() || townName == null) return coords;
        try {
            Town town = getTown(townName);
            if (town != null && town.getTownBlocks() != null) {
                for (TownBlock tb : town.getTownBlocks()) {
                    WorldCoord wc = tb.getWorldCoord();
                    coords.add(new com.towny.sieges.model.ChunkCoord(wc.getWorldName(), wc.getX(), wc.getZ()));
                }
            }
        } catch (Throwable ignored) {}
        return coords;
    }

    public double getClosestDistanceInChunks(Location loc, String targetTownName) {
        if (!isTownyEnabled() || loc == null || targetTownName == null) return Double.MAX_VALUE;
        try {
            Town target = getTown(targetTownName);
            if (target == null) return Double.MAX_VALUE;

            Collection<TownBlock> blocks = target.getTownBlocks();
            if (blocks == null || blocks.isEmpty()) return Double.MAX_VALUE;

            int locChunkX = loc.getBlockX() >> 4;
            int locChunkZ = loc.getBlockZ() >> 4;
            String worldName = loc.getWorld().getName();

            double minDistance = Double.MAX_VALUE;
            for (TownBlock tb : blocks) {
                WorldCoord wc = tb.getWorldCoord();
                if (wc.getWorldName().equalsIgnoreCase(worldName)) {
                    double dx = wc.getX() - locChunkX;
                    double dz = wc.getZ() - locChunkZ;
                    double dist = Math.sqrt(dx * dx + dz * dz);
                    if (dist < minDistance) {
                        minDistance = dist;
                    }
                }
            }
            return minDistance;
        } catch (Throwable ignored) {
            return Double.MAX_VALUE;
        }
    }

    public boolean isTownBankHas(String townName, double amount) {
        if (!isTownyEnabled() || townName == null) return true;
        try {
            Town town = getTown(townName);
            if (town != null && town.getAccount() != null) {
                return town.getAccount().canPayFromHoldings(amount);
            }
        } catch (Throwable ignored) {}
        return true;
    }

    public boolean withdrawFromTownBank(String townName, double amount, String reason) {
        if (!isTownyEnabled() || townName == null) return true;
        try {
            Town town = getTown(townName);
            if (town != null && town.getAccount() != null) {
                if (town.getAccount().canPayFromHoldings(amount)) {
                    town.getAccount().withdraw(amount, reason);
                    return true;
                }
                return false;
            }
        } catch (Throwable ignored) {}
        return true;
    }

    public boolean isChunkAdjacentToTown(com.towny.sieges.model.ChunkCoord coord, String townName) {
        if (!isTownyEnabled() || coord == null || townName == null) return false;
        try {
            Town town = getTown(townName);
            if (town == null) return false;
            Collection<TownBlock> blocks = town.getTownBlocks();
            if (blocks == null || blocks.isEmpty()) return false;

            for (TownBlock tb : blocks) {
                WorldCoord wc = tb.getWorldCoord();
                if (wc.getWorldName().equalsIgnoreCase(coord.getWorld())) {
                    int dx = Math.abs(wc.getX() - coord.getX());
                    int dz = Math.abs(wc.getZ() - coord.getZ());
                    if ((dx == 1 && dz == 0) || (dx == 0 && dz == 1)) {
                        return true;
                    }
                }
            }
        } catch (Throwable ignored) {}
        return false;
    }

    public boolean claimChunkForTown(String townName, com.towny.sieges.model.ChunkCoord coord) {
        if (!isTownyEnabled() || townName == null || coord == null) return false;
        try {
            Town town = getTown(townName);
            if (town == null) return false;
            TownyAPI api = TownyAPI.getInstance();
            if (api != null) {
                WorldCoord wc = new WorldCoord(coord.getWorld(), coord.getX(), coord.getZ());
                TownBlock tb = api.getTownBlock(wc);
                if (tb == null) {
                    try {
                        tb = new TownBlock(coord.getX(), coord.getZ(), api.getTownyWorld(coord.getWorld()));
                    } catch (Throwable e) {
                        try {
                            java.lang.reflect.Method m = api.getTownyWorld(coord.getWorld()).getClass().getMethod("newTownBlock", int.class, int.class);
                            tb = (TownBlock) m.invoke(api.getTownyWorld(coord.getWorld()), coord.getX(), coord.getZ());
                        } catch (Throwable ignored) {}
                    }
                    if (tb == null) tb = api.getTownBlock(wc);
                }
                if (tb != null) {
                    tb.setTown(town);
                    tb.save();
                    town.save();
                    return true;
                }
            }
        } catch (Throwable ignored) {}
        return false;
    }

    /**
     * Создание официального аванпоста (Outpost) города в Towny:
     * Если отбитый защитниками чанк не граничит с основным городом, он регистрируется
     * с официальным статусом аванпоста (Outpost) в Towny со всеми вытекающими механиками.
     */
    public boolean createOutpostForTown(String townName, com.towny.sieges.model.ChunkCoord coord) {
        if (!isTownyEnabled() || townName == null || coord == null) return false;
        try {
            Town town = getTown(townName);
            if (town == null) return false;
            TownyAPI api = TownyAPI.getInstance();
            if (api != null) {
                WorldCoord wc = new WorldCoord(coord.getWorld(), coord.getX(), coord.getZ());
                TownBlock tb = api.getTownBlock(wc);
                if (tb == null) {
                    try {
                        tb = new TownBlock(coord.getX(), coord.getZ(), api.getTownyWorld(coord.getWorld()));
                    } catch (Throwable e) {
                        try {
                            java.lang.reflect.Method m = api.getTownyWorld(coord.getWorld()).getClass().getMethod("newTownBlock", int.class, int.class);
                            tb = (TownBlock) m.invoke(api.getTownyWorld(coord.getWorld()), coord.getX(), coord.getZ());
                        } catch (Throwable ignored) {}
                    }
                    if (tb == null) tb = api.getTownBlock(wc);
                }
                if (tb != null) {
                    tb.setTown(town);
                    try {
                        // Попытка пометить блок как Outpost через TownBlock API
                        tb.getClass().getMethod("setIsOutpost", boolean.class).invoke(tb, true);
                    } catch (Throwable ignored) {}
                    try {
                        // Регистрация в списке аванпостов Towny
                        town.getClass().getMethod("addOutpost", WorldCoord.class).invoke(town, wc);
                    } catch (Throwable ignored) {}
                    tb.save();
                    town.save();
                    return true;
                }
            }
        } catch (Throwable ignored) {}
        return false;
    }

    /**
     * Определение исходного статуса чанка перед его включением в осадный лагерь:
     * - TOWN_CHUNK: регулярный чанк атакующего города
     * - OUTPOST: официальный аванпост атакующего города
     * - WILDERNESS: ничейные дикие земли
     */
    public com.towny.sieges.model.PreviousChunkStatus detectChunkStatus(com.towny.sieges.model.ChunkCoord coord, String attackingTown) {
        if (!isTownyEnabled() || coord == null) return com.towny.sieges.model.PreviousChunkStatus.WILDERNESS;
        try {
            TownyAPI api = TownyAPI.getInstance();
            if (api != null) {
                WorldCoord wc = new WorldCoord(coord.getWorld(), coord.getX(), coord.getZ());
                TownBlock tb = api.getTownBlock(wc);
                if (tb != null && tb.hasTown()) {
                    String ownerTown = tb.getTownOrNull() != null ? tb.getTownOrNull().getName() : null;
                    if (ownerTown != null && attackingTown != null && ownerTown.equalsIgnoreCase(attackingTown)) {
                        try {
                            boolean isOutpost = (boolean) tb.getClass().getMethod("isOutpost").invoke(tb);
                            if (isOutpost) {
                                return com.towny.sieges.model.PreviousChunkStatus.OUTPOST;
                            }
                        } catch (Throwable ignored) {}
                        return com.towny.sieges.model.PreviousChunkStatus.TOWN_CHUNK;
                    }
                }
            }
        } catch (Throwable ignored) {}
        return com.towny.sieges.model.PreviousChunkStatus.WILDERNESS;
    }

    /**
     * Сброс чанка в статус диких земель (Wilderness):
     * Удаляет приват города и возвращает чанк серверу.
     */
    public boolean unclaimChunk(com.towny.sieges.model.ChunkCoord coord) {
        if (!isTownyEnabled() || coord == null) return false;
        try {
            TownyAPI api = TownyAPI.getInstance();
            if (api != null) {
                WorldCoord wc = new WorldCoord(coord.getWorld(), coord.getX(), coord.getZ());
                TownBlock tb = api.getTownBlock(wc);
                if (tb != null) {
                    try {
                        Town town = tb.getTownOrNull();
                        if (town != null) {
                            try {
                                town.getClass().getMethod("removeTownBlock", TownBlock.class).invoke(town, tb);
                            } catch (Throwable ignored) {}
                        }
                    } catch (Throwable ignored) {}
                    try {
                        try {
                        java.lang.reflect.Method m = api.getTownyWorld(coord.getWorld()).getClass().getMethod("removeTownBlock", TownBlock.class);
                        m.invoke(api.getTownyWorld(coord.getWorld()), tb);
                    } catch (Throwable ignored) {}
                    } catch (Throwable ignored) {}
                    try {
                        tb.save();
                    } catch (Throwable ignored) {}
                    return true;
                }
            }
        } catch (Throwable ignored) {}
        return false;
    }

    /**
     * Проверка: является ли данный чанк Домашним Чанком (Homeblock) указанного города.
     */
    public boolean isHomeBlock(com.towny.sieges.model.ChunkCoord coord, String townName) {
        if (!isTownyEnabled() || coord == null || townName == null) return false;
        try {
            Town town = getTown(townName);
            if (town != null && town.hasHomeBlock()) {
                WorldCoord home = town.getHomeBlockOrNull().getWorldCoord();
                return home.getWorldName().equalsIgnoreCase(coord.getWorld()) &&
                       home.getX() == coord.getX() &&
                       home.getZ() == coord.getZ();
            }
        } catch (Throwable ignored) {}
        return false;
    }

    /**
     * Получение текущей целостности Мэрии города (%) через TownyArchitecture.
     */
    public double getTownHallIntegrity(String townName) {
        try {
            org.bukkit.plugin.Plugin arch = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
            if (arch != null && arch.isEnabled()) {
                // Использование рефлексии для вызова: 
                // TownyArchitecturePlugin.getInstance().getTownHallShieldManager().getTownHallIntegrityPercent(townName)
                Object inst = arch.getClass().getMethod("getInstance").invoke(null);
                Object shieldMgr = inst.getClass().getMethod("getTownHallShieldManager").invoke(inst);
                return (double) shieldMgr.getClass().getMethod("getTownHallIntegrityPercent", String.class).invoke(shieldMgr, townName);
            }
        } catch (Throwable ignored) {}
        return 100.0;
    }

    /**
     * Получение суммарной мощности щита города (Мэрия + Стены) через TownyArchitecture.
     * Базовая мощность Мэрии: 300 ед. (если целостность > 50%)
     * Каждая целая секция Стены (CityWall): +100 ед.
     */
    public double getTownShieldPower(String townName) {
        try {
            org.bukkit.plugin.Plugin arch = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
            if (arch != null && arch.isEnabled()) {
                Object inst = arch.getClass().getMethod("getInstance").invoke(null);
                Object shieldMgr = inst.getClass().getMethod("getTownHallShieldManager").invoke(inst);
                
                // Проверяем целостность мэрии
                double integrity = (double) shieldMgr.getClass().getMethod("getTownHallIntegrityPercent", String.class).invoke(shieldMgr, townName);
                if (integrity <= 50.0) return 0.0;

                // Базовая мощность мэрии
                double power = 300.0;

                // Прибавляем за стены: shieldMgr.getWallCount(townName) * 100.0
                int wallCount = (int) shieldMgr.getClass().getMethod("getWallCount", String.class).invoke(shieldMgr, townName);
                power += (wallCount * 100.0);
                
                return power;
            }
        } catch (Throwable ignored) {}
        return 0.0;
    }

    /**
     * Конвертация мощности щита в дополнительные секунды захвата Домашнего Чанка.
     * 1 ед. мощности = 1 сек. времени.
     */
    public long getTownShieldBonusSeconds(String townName) {
        return (long) getTownShieldPower(townName);
    }

    /**
     * Перевод всей казны побежденного города в казну победившего города.
     */
    public double transferTownTreasury(String fromTownName, String toTownName) {
        if (!isTownyEnabled() || fromTownName == null || toTownName == null) return 0.0;
        try {
            Town fromTown = getTown(fromTownName);
            Town toTown = getTown(toTownName);
            if (fromTown != null && toTown != null) {
                double balance = fromTown.getAccount().getHoldingBalance();
                if (balance > 0) {
                    fromTown.getAccount().withdraw(balance, "Захват города " + toTownName);
                    toTown.getAccount().deposit(balance, "Трофеи и казна захваченного города " + fromTownName);
                    return balance;
                }
            }
        } catch (Throwable ignored) {
        }
        return 0.0;
    }

    /**
     * Полное уничтожение города в системе Towny:
     * 1. Изгнание всех жителей (жители становятся безнадежными кочевниками).
     * 2. Удаление файла города из файловой системы Towny и реестра памяти TownyUniverse.
     */
    public boolean destroyAndEraseTown(String townName) {
        if (!isTownyEnabled() || townName == null) return false;
        try {
            Town town = getTown(townName);
            if (town == null) return false;

            // 1. Force town ruin state to FALSE so Towny never creates or leaves a Ruin object
            try {
                town.setRuined(false);
            } catch (Throwable ignored) {}

            // 2. Remove town from Nation
            try {
                if (town.hasNation()) {
                    Nation n = town.getNationOrNull();
                    town.removeNation();
                    if (n != null) {
                        try {
                            java.lang.reflect.Method m = n.getClass().getDeclaredMethod("removeTown", Town.class);
                            m.setAccessible(true);
                            m.invoke(n, town);
                        } catch (Throwable ignored) {}
                        com.palmergames.bukkit.towny.TownyUniverse.getInstance().getDataSource().saveNation(n);
                    }
                }
            } catch (Throwable ignored) {}

            // 3. Evict all residents
            java.util.List<Resident> residents = new java.util.ArrayList<>(town.getResidents());
            for (Resident res : residents) {
                try {
                    town.removeResident(res);
                    com.palmergames.bukkit.towny.TownyUniverse.getInstance().getDataSource().saveResident(res);
                    Player p = Bukkit.getPlayer(res.getUUID());
                    if (p != null && p.isOnline()) {
                        p.sendMessage(org.bukkit.ChatColor.RED + "☠ Ваш город «" + townName + "» был полностью РАЗГРОМЛЕН и УНИЧТОЖЕН! Вы изгнаны и стали кочевником.");
                    }
                } catch (Throwable ignored) {}
            }

            // 4. Detach and unclaim all TownBlocks, clearing ruin status
            java.util.List<com.palmergames.bukkit.towny.object.TownBlock> blocks = new java.util.ArrayList<>(town.getTownBlocks());
            for (com.palmergames.bukkit.towny.object.TownBlock tb : blocks) {
                try {
                    try { tb.getClass().getMethod("setRuined", boolean.class).invoke(tb, false); } catch (Throwable ignored) {}
                    tb.setTown(null);
                    com.palmergames.bukkit.towny.TownyUniverse.getInstance().removeTownBlock(tb);
                    com.palmergames.bukkit.towny.TownyUniverse.getInstance().getDataSource().deleteTownBlock(tb);
                } catch (Throwable ignored) {}
            }

            // 5. Unregister and delete Town from TownyUniverse memory and database
            try {
                com.palmergames.bukkit.towny.TownyUniverse.getInstance().unregisterTown(town);
            } catch (Throwable ignored) {}

            try {
                com.palmergames.bukkit.towny.TownyUniverse.getInstance().getDataSource().deleteTown(town);
            } catch (Throwable t1) {
                try {
                    com.palmergames.bukkit.towny.TownyUniverse.getInstance().getDataSource().removeTown(town, com.palmergames.bukkit.towny.event.DeleteTownEvent.Cause.NO_TOWNBLOCKS);
                } catch (Throwable ignored) {}
            }

            // 6. Save Towny database
            try {
                com.palmergames.bukkit.towny.TownyUniverse.getInstance().getDataSource().saveTowns();
                com.palmergames.bukkit.towny.TownyUniverse.getInstance().getDataSource().saveAllWorlds();
            } catch (Throwable ignored) {}

            return true;
        } catch (Throwable ignored) {
        }
        return false;
    }

    /**
     * Вызов перерасчета зданий и принудительного соблюдения лимитов в TownyArchitecture.
     */
    public void recalculateTownyArchitectureBuildings(String victoriousTown, String capturedTown) {
        try {
            org.bukkit.plugin.Plugin arch = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
            if (arch != null && arch.isEnabled()) {
                Object inst = arch.getClass().getMethod("getInstance").invoke(null);
                Object bldMgr = inst.getClass().getMethod("getBuildingManager").invoke(inst);
                bldMgr.getClass().getMethod("recalculateAndEnforceBuildingLimits", String.class, String.class)
                      .invoke(bldMgr, victoriousTown, capturedTown);
            }
        } catch (Throwable ignored) {
        }
    }

    /**
     * Вызов переноса построек с захваченных чанков в TownyArchitecture.
     */
    public void transferCapturedBuildings(String winnerTown, Set<com.towny.sieges.model.ChunkCoord> capturedChunks) {
        try {
            org.bukkit.plugin.Plugin arch = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
            if (arch != null && arch.isEnabled()) {
                Object inst = arch.getClass().getMethod("getInstance").invoke(null);
                Object bldMgr = inst.getClass().getMethod("getBuildingManager").invoke(inst);
                bldMgr.getClass().getMethod("transferBuildingsOnCapturedChunks", String.class, Set.class)
                      .invoke(bldMgr, winnerTown, capturedChunks);
            }
        } catch (Throwable ignored) {
        }
    }
}


