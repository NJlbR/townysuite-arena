import os
import subprocess
import shutil
import zipfile
import json
import base64
import hashlib

BASE_DIR = os.path.abspath(".")
SRC_DIR = os.path.join(BASE_DIR, "tmp", "towny-sieges", "src", "main", "java")
RES_DIR = os.path.join(BASE_DIR, "tmp", "towny-sieges", "src", "main", "resources")
BIN_DIR = os.path.join(BASE_DIR, "tmp", "towny-sieges", "bin")
LIB_DIR = os.path.join(BASE_DIR, "tmp", "minecraft-build-v2", "lib")
DIST_DIR = os.path.join(BASE_DIR, "dist")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

print("=== 1. Writing updated Java sources for TownySieges with Nation Wars ===")

# 1. TownyHook.java
towny_hook_code = """package com.towny.sieges.hook;

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
}
"""

with open(os.path.join(SRC_DIR, "com", "towny", "sieges", "hook", "TownyHook.java"), "w", encoding="utf-8") as f:
    f.write(towny_hook_code)

# 2. NationWar.java
nation_war_code = """package com.towny.sieges.model;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/**
 * Model for Nation War:
 * - Unified 24h preparation countdown across ALL towns of both nations.
 * - Unified 2h active assault phase: ALL towns of both nations are vulnerable to explosions!
 * - Siege camps placed during the war inherit and continue the unified nation timer.
 */
public class NationWar {

    public enum Status {
        PREPARATION,    // 24h: unified countdown, camps can be claimed, explosions blocked
        ACTIVE_ASSAULT, // 2h: active assault phase, explosions unblocked across ALL towns of both nations!
        COMPLETED       // Concluded
    }

    private final String warId;
    private final String attackerNation;
    private final String defenderNation;
    private final String declaredByLeader;

    private final Set<String> attackerTowns = new LinkedHashSet<>();
    private final Set<String> defenderTowns = new LinkedHashSet<>();
    private final List<String> linkedCampIds = new ArrayList<>();

    private long createdAtMillis;
    private long preparationEndsAtMillis;
    private long activeEndsAtMillis;
    private Status status;

    public NationWar(String warId, String attackerNation, String defenderNation, String declaredByLeader,
                     Set<String> attackerTowns, Set<String> defenderTowns,
                     long prepSeconds, long assaultSeconds) {
        this.warId = warId;
        this.attackerNation = attackerNation;
        this.defenderNation = defenderNation;
        this.declaredByLeader = declaredByLeader;
        if (attackerTowns != null) this.attackerTowns.addAll(attackerTowns);
        if (defenderTowns != null) this.defenderTowns.addAll(defenderTowns);
        this.createdAtMillis = System.currentTimeMillis();
        this.preparationEndsAtMillis = this.createdAtMillis + (prepSeconds * 1000L);
        this.activeEndsAtMillis = this.preparationEndsAtMillis + (assaultSeconds * 1000L);
        this.status = Status.PREPARATION;
    }

    public NationWar(String warId, String attackerNation, String defenderNation, String declaredByLeader,
                     Set<String> attackerTowns, Set<String> defenderTowns, List<String> linkedCampIds,
                     long createdAtMillis, long preparationEndsAtMillis, long activeEndsAtMillis, Status status) {
        this.warId = warId;
        this.attackerNation = attackerNation;
        this.defenderNation = defenderNation;
        this.declaredByLeader = declaredByLeader;
        if (attackerTowns != null) this.attackerTowns.addAll(attackerTowns);
        if (defenderTowns != null) this.defenderTowns.addAll(defenderTowns);
        if (linkedCampIds != null) this.linkedCampIds.addAll(linkedCampIds);
        this.createdAtMillis = createdAtMillis;
        this.preparationEndsAtMillis = preparationEndsAtMillis;
        this.activeEndsAtMillis = activeEndsAtMillis;
        this.status = status;
    }

    public boolean isTownParticipating(String townName) {
        if (townName == null) return false;
        for (String t : attackerTowns) {
            if (t.equalsIgnoreCase(townName)) return true;
        }
        for (String t : defenderTowns) {
            if (t.equalsIgnoreCase(townName)) return true;
        }
        return false;
    }

    public boolean isAttackerTown(String townName) {
        if (townName == null) return false;
        for (String t : attackerTowns) {
            if (t.equalsIgnoreCase(townName)) return true;
        }
        return false;
    }

    public boolean isDefenderTown(String townName) {
        if (townName == null) return false;
        for (String t : defenderTowns) {
            if (t.equalsIgnoreCase(townName)) return true;
        }
        return false;
    }

    public boolean isActiveAssault() {
        return status == Status.ACTIVE_ASSAULT;
    }

    public boolean isPreparation() {
        return status == Status.PREPARATION;
    }

    public String getWarId() { return warId; }
    public String getAttackerNation() { return attackerNation; }
    public String getDefenderNation() { return defenderNation; }
    public String getDeclaredByLeader() { return declaredByLeader; }
    public Set<String> getAttackerTowns() { return attackerTowns; }
    public Set<String> getDefenderTowns() { return defenderTowns; }
    public List<String> getLinkedCampIds() { return linkedCampIds; }
    public long getCreatedAtMillis() { return createdAtMillis; }
    public long getPreparationEndsAtMillis() { return preparationEndsAtMillis; }
    public void setPreparationEndsAtMillis(long ms) { this.preparationEndsAtMillis = ms; }
    public long getActiveEndsAtMillis() { return activeEndsAtMillis; }
    public void setActiveEndsAtMillis(long ms) { this.activeEndsAtMillis = ms; }
    public Status getStatus() { return status; }
    public void setStatus(Status s) { this.status = s; }

    public void addLinkedCamp(String campId) {
        if (!linkedCampIds.contains(campId)) {
            linkedCampIds.add(campId);
        }
    }

    public long getRemainingSeconds() {
        long now = System.currentTimeMillis();
        if (status == Status.PREPARATION) {
            return Math.max(0, (preparationEndsAtMillis - now) / 1000L);
        } else if (status == Status.ACTIVE_ASSAULT) {
            return Math.max(0, (activeEndsAtMillis - now) / 1000L);
        }
        return 0L;
    }

    public String getFormattedRemainingTime() {
        long sec = getRemainingSeconds();
        long h = sec / 3600;
        long m = (sec % 3600) / 60;
        long s = sec % 60;
        return String.format("%02d:%02d:%02d", h, m, s);
    }
}
"""

with open(os.path.join(SRC_DIR, "com", "towny", "sieges", "model", "NationWar.java"), "w", encoding="utf-8") as f:
    f.write(nation_war_code)

# 3. SiegeManager.java
siege_manager_code = """package com.towny.sieges.manager;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.ChunkCoord;
import com.towny.sieges.model.NationWar;
import com.towny.sieges.model.SiegeCamp;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Sound;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;

import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SiegeManager {

    private final TownySiegesPlugin plugin;
    private final Map<String, SiegeCamp> siegesById = new ConcurrentHashMap<>();
    private final Map<String, SiegeCamp> siegesByDefendingTown = new ConcurrentHashMap<>();
    private final Map<String, SiegeCamp> siegesByAttackingTown = new ConcurrentHashMap<>();
    private final Map<ChunkCoord, SiegeCamp> chunkToCamp = new ConcurrentHashMap<>();

    // Active Nation Wars
    private final Map<String, NationWar> activeNationWars = new ConcurrentHashMap<>();

    private File dataFile;
    private FileConfiguration dataConfig;

    public SiegeManager(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    public void loadData() {
        dataFile = new File(plugin.getDataFolder(), "data.yml");
        if (!dataFile.exists()) {
            try {
                dataFile.createNewFile();
            } catch (IOException e) {
                plugin.getLogger().severe("Не удалось создать data.yml: " + e.getMessage());
            }
        }
        dataConfig = YamlConfiguration.loadConfiguration(dataFile);

        siegesById.clear();
        siegesByDefendingTown.clear();
        siegesByAttackingTown.clear();
        chunkToCamp.clear();
        activeNationWars.clear();

        // Load local town sieges
        ConfigurationSection sec = dataConfig.getConfigurationSection("sieges");
        if (sec != null) {
            for (String id : sec.getKeys(false)) {
                ConfigurationSection s = sec.getConfigurationSection(id);
                if (s == null) continue;

                String attacker = s.getString("attacking-town");
                String defender = s.getString("defending-town");
                String mayor = s.getString("mayor");
                String world = s.getString("world", "world");
                String initialCoordStr = s.getString("initial-chunk");
                ChunkCoord initialChunk = ChunkCoord.deserialize(initialCoordStr);

                List<String> chunkList = s.getStringList("claimed-chunks");
                Set<ChunkCoord> claimed = new LinkedHashSet<>();
                for (String cStr : chunkList) {
                    ChunkCoord cc = ChunkCoord.deserialize(cStr);
                    if (cc != null) claimed.add(cc);
                }

                long createdAt = s.getLong("created-at", System.currentTimeMillis());
                long prepEnds = s.getLong("preparation-ends-at", createdAt + 86400000L);
                long activeEnds = s.getLong("active-ends-at", prepEnds + 7200000L);
                String statusStr = s.getString("status", "PREPARATION");
                SiegeCamp.Status status;
                try {
                    status = SiegeCamp.Status.valueOf(statusStr);
                } catch (Exception e) {
                    status = SiegeCamp.Status.PREPARATION;
                }

                SiegeCamp camp = new SiegeCamp(id, attacker, defender, mayor, world, initialChunk, claimed,
                        createdAt, prepEnds, activeEnds, status);

                registerSiege(camp);
            }
        }

        // Load Nation Wars
        ConfigurationSection nwSec = dataConfig.getConfigurationSection("nation-wars");
        if (nwSec != null) {
            for (String warId : nwSec.getKeys(false)) {
                ConfigurationSection ws = nwSec.getConfigurationSection(warId);
                if (ws == null) continue;

                String attackerNat = ws.getString("attacker-nation");
                String defenderNat = ws.getString("defender-nation");
                String leader = ws.getString("declared-by");
                List<String> atTowns = ws.getStringList("attacker-towns");
                List<String> defTowns = ws.getStringList("defender-towns");
                List<String> camps = ws.getStringList("linked-camps");
                long createdAt = ws.getLong("created-at", System.currentTimeMillis());
                long prepEnds = ws.getLong("preparation-ends-at", createdAt + 86400000L);
                long activeEnds = ws.getLong("active-ends-at", prepEnds + 7200000L);
                String stStr = ws.getString("status", "PREPARATION");
                NationWar.Status st;
                try {
                    st = NationWar.Status.valueOf(stStr);
                } catch (Exception e) {
                    st = NationWar.Status.PREPARATION;
                }

                NationWar war = new NationWar(warId, attackerNat, defenderNat, leader,
                        new LinkedHashSet<>(atTowns), new LinkedHashSet<>(defTowns), camps,
                        createdAt, prepEnds, activeEnds, st);

                activeNationWars.put(warId, war);
            }
        }

        plugin.getLogger().info("[TownySieges] Загружено осад: " + siegesById.size() + ", войн наций: " + activeNationWars.size());
    }

    public void saveData() {
        if (dataConfig == null || dataFile == null) return;
        dataConfig.set("sieges", null);
        dataConfig.set("nation-wars", null);

        // Save local sieges
        for (SiegeCamp camp : siegesById.values()) {
            String path = "sieges." + camp.getSiegeId();
            dataConfig.set(path + ".attacking-town", camp.getAttackingTown());
            dataConfig.set(path + ".defending-town", camp.getDefendingTown());
            dataConfig.set(path + ".mayor", camp.getMayorName());
            dataConfig.set(path + ".world", camp.getWorldName());
            dataConfig.set(path + ".initial-chunk", camp.getInitialCampChunk().serialize());

            List<String> chunkList = new ArrayList<>();
            for (ChunkCoord cc : camp.getClaimedChunks()) {
                chunkList.add(cc.serialize());
            }
            dataConfig.set(path + ".claimed-chunks", chunkList);
            dataConfig.set(path + ".created-at", camp.getCreatedAtMillis());
            dataConfig.set(path + ".preparation-ends-at", camp.getPreparationEndsAtMillis());
            dataConfig.set(path + ".active-ends-at", camp.getActiveEndsAtMillis());
            dataConfig.set(path + ".status", camp.getStatus().name());
        }

        // Save Nation Wars
        for (NationWar war : activeNationWars.values()) {
            String path = "nation-wars." + war.getWarId();
            dataConfig.set(path + ".attacker-nation", war.getAttackerNation());
            dataConfig.set(path + ".defender-nation", war.getDefenderNation());
            dataConfig.set(path + ".declared-by", war.getDeclaredByLeader());
            dataConfig.set(path + ".attacker-towns", new ArrayList<>(war.getAttackerTowns()));
            dataConfig.set(path + ".defender-towns", new ArrayList<>(war.getDefenderTowns()));
            dataConfig.set(path + ".linked-camps", war.getLinkedCampIds());
            dataConfig.set(path + ".created-at", war.getCreatedAtMillis());
            dataConfig.set(path + ".preparation-ends-at", war.getPreparationEndsAtMillis());
            dataConfig.set(path + ".active-ends-at", war.getActiveEndsAtMillis());
            dataConfig.set(path + ".status", war.getStatus().name());
        }

        try {
            dataConfig.save(dataFile);
        } catch (IOException e) {
            plugin.getLogger().severe("Не удалось сохранить data.yml: " + e.getMessage());
        }
    }

    private void registerSiege(SiegeCamp camp) {
        siegesById.put(camp.getSiegeId(), camp);
        siegesByDefendingTown.put(camp.getDefendingTown().toLowerCase(), camp);
        siegesByAttackingTown.put(camp.getAttackingTown().toLowerCase(), camp);
        for (ChunkCoord cc : camp.getClaimedChunks()) {
            chunkToCamp.put(cc, camp);
        }
    }

    private void unregisterSiege(SiegeCamp camp) {
        siegesById.remove(camp.getSiegeId());
        siegesByDefendingTown.remove(camp.getDefendingTown().toLowerCase());
        siegesByAttackingTown.remove(camp.getAttackingTown().toLowerCase());
        for (ChunkCoord cc : camp.getClaimedChunks()) {
            chunkToCamp.remove(cc);
        }
    }

    // --- Nation Wars Core Methods ---

    public boolean declareNationWar(Player leader, String targetNationName) {
        if (leader == null || targetNationName == null) return false;

        String playerTown = plugin.getTownyHook().getPlayerTownName(leader);
        if (playerTown == null) {
            leader.sendMessage(ChatColor.RED + "[TownySieges] Вы должны состоять в городе, чтобы объявить войну наций!");
            return false;
        }

        String playerNation = plugin.getTownyHook().getTownNationName(playerTown);
        if (playerNation == null) {
            leader.sendMessage(ChatColor.RED + "[TownySieges] Ваш город не состоит ни в одной нации!");
            return false;
        }

        if (!plugin.getTownyHook().isNationKing(leader, playerNation) && !leader.hasPermission("townysieges.admin")) {
            leader.sendMessage(ChatColor.RED + "[TownySieges] Только Глава (Король) нации может объявлять войну наций!");
            return false;
        }

        if (playerNation.equalsIgnoreCase(targetNationName)) {
            leader.sendMessage(ChatColor.RED + "[TownySieges] Вы не можете объявить войну собственной нации!");
            return false;
        }

        if (getActiveNationWar(playerNation) != null) {
            leader.sendMessage(ChatColor.RED + "[TownySieges] Ваша нация («" + playerNation + "») уже ведёт войну наций!");
            return false;
        }

        if (getActiveNationWar(targetNationName) != null) {
            leader.sendMessage(ChatColor.RED + "[TownySieges] Нация-цель («" + targetNationName + "») уже находится в состоянии войны!");
            return false;
        }

        Set<String> attackerTowns = plugin.getTownyHook().getNationTownNames(playerNation);
        Set<String> defenderTowns = plugin.getTownyHook().getNationTownNames(targetNationName);

        if (attackerTowns.isEmpty()) {
            attackerTowns.add(playerTown);
        }
        if (defenderTowns.isEmpty()) {
            leader.sendMessage(ChatColor.RED + "[TownySieges] Нация-цель «" + targetNationName + "» не найдена или не имеет городов в Towny!");
            return false;
        }

        long prepSeconds = plugin.getConfig().getLong("nationwar.preparation-duration-seconds", 86400L); // 24 hours
        long assaultSeconds = plugin.getConfig().getLong("nationwar.assault-duration-seconds", 7200L);     // 2 hours
        String warId = "war_" + playerNation.toLowerCase() + "_" + targetNationName.toLowerCase() + "_" + System.currentTimeMillis();

        NationWar war = new NationWar(warId, playerNation, targetNationName, leader.getName(),
                attackerTowns, defenderTowns, prepSeconds, assaultSeconds);

        activeNationWars.put(warId, war);
        saveData();

        String prepTimeStr = (prepSeconds / 3600) + " ч.";
        String broadcastMsg = ChatColor.translateAlternateColorCodes('&',
                "&4&l[ВОЙНА НАЦИЙ] &eГлава нации &6" + playerNation + " &e(&f" + leader.getName() +
                "&e) объявил войну нации &c" + targetNationName +
                "&e! ВСЕ города обеих наций переведены в режим подготовки к штурму с единым таймером (" + prepTimeStr + ")!");

        Bukkit.broadcastMessage(broadcastMsg);

        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (pTown != null) {
                String pNation = plugin.getTownyHook().getTownNationName(pTown);
                if (pNation != null) {
                    if (pNation.equalsIgnoreCase(targetNationName)) {
                        p.sendTitle(ChatColor.DARK_RED + "⚔ ВАШЕЙ НАЦИИ ОБЪЯВЛЕНА ВОЙНА! ⚔",
                                ChatColor.YELLOW + "Враг: " + playerNation + " | Штурм всех городов через: " + prepTimeStr, 10, 100, 20);
                        p.playSound(p.getLocation(), Sound.EVENT_RAID_HORN, 1.8f, 0.7f);
                    } else if (pNation.equalsIgnoreCase(playerNation)) {
                        p.sendTitle(ChatColor.GOLD + "⚔ ВОЙНА НАЦИЙ ОБЪЯВЛЕНА! ⚔",
                                ChatColor.YELLOW + "Цель: " + targetNationName + " | Штурм всех городов через: " + prepTimeStr, 10, 100, 20);
                        p.playSound(p.getLocation(), Sound.EVENT_RAID_HORN, 1.5f, 1.0f);
                    }
                }
            }
        }

        plugin.getBossBarManager().updateAllBossBars();
        return true;
    }

    public NationWar getActiveNationWar(String nationName) {
        if (nationName == null) return null;
        for (NationWar war : activeNationWars.values()) {
            if (war.getAttackerNation().equalsIgnoreCase(nationName) ||
                war.getDefenderNation().equalsIgnoreCase(nationName)) {
                return war;
            }
        }
        return null;
    }

    public NationWar getActiveNationWarForTown(String townName) {
        if (townName == null) return null;
        for (NationWar war : activeNationWars.values()) {
            if (war.isTownParticipating(townName)) {
                return war;
            }
        }
        return null;
    }

    public Collection<NationWar> getAllNationWars() {
        return Collections.unmodifiableCollection(activeNationWars.values());
    }

    public boolean createSiegeCamp(Player mayor, String defendingTownName, Location loc) {
        if (mayor == null || defendingTownName == null || loc == null) return false;

        String attackingTown = plugin.getTownyHook().getPlayerTownName(mayor);
        if (attackingTown == null) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Вы должны состоять в городе, чтобы объявить осаду!");
            return false;
        }

        if (!plugin.getTownyHook().isMayor(mayor, attackingTown) && !mayor.hasPermission("townysieges.admin")) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Только Мэр города может ставить осадный лагерь!");
            return false;
        }

        if (attackingTown.equalsIgnoreCase(defendingTownName)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Вы не можете осаждать собственный город!");
            return false;
        }

        if (plugin.getTownyHook().getTown(defendingTownName) == null) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Город-цель «" + defendingTownName + "» не найден в базе Towny!");
            return false;
        }

        // Check if current chunk is claimed by Towny
        String townAtLoc = plugin.getTownyHook().getTownNameAt(loc);
        if (townAtLoc != null) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Этот чанк уже принадлежит городу «" + townAtLoc + "»! Осадный лагерь ставится на свободной земле.");
            return false;
        }

        ChunkCoord campCoord = ChunkCoord.fromLocation(loc);
        if (chunkToCamp.containsKey(campCoord)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Здесь уже разбит другой осадный лагерь!");
            return false;
        }

        // Check active Nation War between both towns
        NationWar activeWar = getActiveNationWarForTown(attackingTown);
        boolean isPartOfNationWar = activeWar != null && activeWar.isTownParticipating(defendingTownName);

        if (!isPartOfNationWar) {
            // Standard individual siege restrictions
            if (siegesByAttackingTown.containsKey(attackingTown.toLowerCase())) {
                mayor.sendMessage(ChatColor.RED + "[TownySieges] Ваш город уже ведет осаду! Завершите текущую перед началом новой.");
                return false;
            }
            if (siegesByDefendingTown.containsKey(defendingTownName.toLowerCase())) {
                mayor.sendMessage(ChatColor.RED + "[TownySieges] Город «" + defendingTownName + "» уже находится под осадой!");
                return false;
            }
        }

        // Distance Checks
        double minDistance = plugin.getConfig().getDouble("siege.min-distance-chunks", 3.0);
        double maxDistance = plugin.getConfig().getDouble("siege.max-distance-chunks", 10.0);
        double actualDistance = plugin.getTownyHook().getClosestDistanceInChunks(loc, defendingTownName);

        if (actualDistance == Double.MAX_VALUE) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Город-цель «" + defendingTownName + "» не имеет приватов в этом мире!");
            return false;
        }

        if (actualDistance < minDistance) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Слишком близко к городу «" + defendingTownName + "»! Дистанция: " + 
                    String.format("%.1f", actualDistance) + " чанков (минимум: " + minDistance + " ч.).");
            return false;
        }

        if (actualDistance > maxDistance) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Слишком далеко от города «" + defendingTownName + "»! Дистанция: " + 
                    String.format("%.1f", actualDistance) + " чанков (максимум: " + maxDistance + " ч.).");
            return false;
        }

        // Economy Check
        double initialCost = plugin.getConfig().getDouble("siege.economy.initial-camp-cost", 5000.0);
        if (!plugin.getTownyHook().isTownBankHas(attackingTown, initialCost)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] В казне города недостаточно средств! Стоимость установки осадного лагеря: " + 
                    initialCost + " монет.");
            return false;
        }

        if (!plugin.getTownyHook().withdrawFromTownBank(attackingTown, initialCost, "Установка осадного лагеря против " + defendingTownName)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Ошибка списания средств из казны города!");
            return false;
        }

        // Create the Siege
        long prepSeconds = plugin.getConfig().getLong("siege.preparation-duration-seconds", 86400L); // 24 hours
        long activeSeconds = plugin.getConfig().getLong("siege.active-duration-seconds", 7200L);     // 2 hours
        String siegeId = "siege_" + attackingTown.toLowerCase() + "_" + defendingTownName.toLowerCase() + "_" + System.currentTimeMillis();

        SiegeCamp camp = new SiegeCamp(siegeId, attackingTown, defendingTownName, mayor.getName(),
                loc.getWorld().getName(), campCoord, prepSeconds, activeSeconds);

        if (isPartOfNationWar) {
            // NATION WAR SYNCHRONIZATION RULE:
            // "осада между городами не будет начинаться, а будет продолжаться таймер нации"
            camp.setPreparationEndsAtMillis(activeWar.getPreparationEndsAtMillis());
            camp.setActiveEndsAtMillis(activeWar.getActiveEndsAtMillis());
            if (activeWar.isActiveAssault()) {
                camp.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
            } else {
                camp.setStatus(SiegeCamp.Status.PREPARATION);
            }
            activeWar.addLinkedCamp(siegeId);

            registerSiege(camp);
            saveData();

            String warAlert = ChatColor.translateAlternateColorCodes('&',
                    "&c&l[ЛАГЕРЬ ВОЙНЫ НАЦИЙ] &eМэр города &6" + attackingTown + " &eразбил осадный лагерь против города &c" + defendingTownName +
                    "&e в рамках Войны Наций! Единый таймер нации продолжается: &f" + activeWar.getFormattedRemainingTime() + "&e.");
            Bukkit.broadcastMessage(warAlert);
            mayor.sendMessage(ChatColor.GREEN + "[TownySieges] Осадный лагерь привязан к фронту Войны Наций с единым таймером!");
        } else {
            // Standalone town siege
            registerSiege(camp);
            saveData();

            String prepTimeStr = (prepSeconds / 3600) + " ч.";
            String alertMsg = ChatColor.translateAlternateColorCodes('&', 
                    "&c&l[ОСАДА] &eМэр города &6" + attackingTown + " &eразбил осадный лагерь против города &c" + defendingTownName + 
                    "&e! До штурма осталось: &f" + prepTimeStr + ".");
            Bukkit.broadcastMessage(alertMsg);
        }

        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (pTown != null) {
                if (pTown.equalsIgnoreCase(defendingTownName)) {
                    p.sendTitle(ChatColor.RED + "⚔ ВАШ ГОРОД ОСАЖДЁН! ⚔", 
                            ChatColor.YELLOW + "Лагерь врага: " + attackingTown + " | Единый таймер: " + camp.getFormattedRemainingTime(), 10, 80, 20);
                    p.playSound(p.getLocation(), Sound.EVENT_RAID_HORN, 1.5f, 0.8f);
                } else if (pTown.equalsIgnoreCase(attackingTown)) {
                    p.sendTitle(ChatColor.GOLD + "⚔ ОСАДНЫЙ ЛАГЕРЬ РАЗБИТ! ⚔", 
                            ChatColor.YELLOW + "Цель: " + defendingTownName + " | Таймер: " + camp.getFormattedRemainingTime(), 10, 80, 20);
                    p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.2f);
                }
            }
        }

        plugin.getBossBarManager().updateAllBossBars();
        return true;
    }

    public boolean expandSiegeCamp(Player mayor, Location loc) {
        if (mayor == null || loc == null) return false;

        String attackingTown = plugin.getTownyHook().getPlayerTownName(mayor);
        if (attackingTown == null) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Вы должны состоять в городе!");
            return false;
        }

        SiegeCamp camp = siegesByAttackingTown.get(attackingTown.toLowerCase());
        if (camp == null) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] У вашего города нет активного осадного лагеря!");
            return false;
        }

        if (!plugin.getTownyHook().isMayor(mayor, attackingTown) && !mayor.hasPermission("townysieges.admin")) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Только Мэр города может расширять осадный лагерь!");
            return false;
        }

        ChunkCoord coord = ChunkCoord.fromLocation(loc);
        if (camp.containsChunk(coord)) {
            mayor.sendMessage(ChatColor.YELLOW + "[TownySieges] Этот чанк уже входит в ваш осадный лагерь!");
            return false;
        }

        if (chunkToCamp.containsKey(coord)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Этот чанк занят другим осадным лагерем!");
            return false;
        }

        String townAt = plugin.getTownyHook().getTownNameAt(loc);
        if (townAt != null) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Нельзя приватить территорию города «" + townAt + "» под осадный лагерь!");
            return false;
        }

        if (!camp.isAdjacentToCamp(coord)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Расширять осадный лагерь можно только на соседние прилегающие чанки!");
            return false;
        }

        int maxChunks = plugin.getConfig().getInt("siege.max-siege-chunks-per-camp", 8);
        if (camp.getClaimedChunks().size() >= maxChunks) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Достигнут лимит размера осадного лагеря (" + maxChunks + " чанков)!");
            return false;
        }

        double expandCost = plugin.getConfig().getDouble("siege.economy.expand-chunk-cost", 2500.0);
        if (!plugin.getTownyHook().isTownBankHas(attackingTown, expandCost)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] В казне города недостаточно средств! Стоимость расширения чанка: " + 
                    expandCost + " монет.");
            return false;
        }

        if (!plugin.getTownyHook().withdrawFromTownBank(attackingTown, expandCost, "Расширение осадного лагеря против " + camp.getDefendingTown())) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Ошибка списания средств из казны города!");
            return false;
        }

        camp.addClaimedChunk(coord);
        chunkToCamp.put(coord, camp);
        saveData();

        mayor.sendMessage(ChatColor.GREEN + "[TownySieges] ✔ Чанк успешно присоединен к осадному лагерю! Всего чанков лагеря: " + 
                camp.getClaimedChunks().size() + "/" + maxChunks + ".");
        mayor.playSound(loc, Sound.BLOCK_ANVIL_USE, 1.0f, 1.2f);
        plugin.getBossBarManager().updateAllBossBars();
        return true;
    }

    public boolean unclaimSiegeChunk(Player mayor, Location loc) {
        if (mayor == null || loc == null) return false;

        String town = plugin.getTownyHook().getPlayerTownName(mayor);
        if (town == null) return false;

        SiegeCamp camp = siegesByAttackingTown.get(town.toLowerCase());
        if (camp == null) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] У вашего города нет осадного лагеря.");
            return false;
        }

        ChunkCoord coord = ChunkCoord.fromLocation(loc);
        if (!camp.containsChunk(coord)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Этот чанк не входит в ваш осадный лагерь.");
            return false;
        }

        if (coord.equals(camp.getInitialCampChunk())) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Нельзя расприватить центральный форпост осадного лагеря!");
            return false;
        }

        camp.removeClaimedChunk(coord);
        chunkToCamp.remove(coord);
        saveData();

        mayor.sendMessage(ChatColor.YELLOW + "[TownySieges] Чанк осадного лагеря распривачен.");
        plugin.getBossBarManager().updateAllBossBars();
        return true;
    }

    /**
     * CRITICAL API FOR TOWNYEXPLOSIONUNBLOCKER & ARTILLERY:
     * Returns true if the town is currently in active 2-hour assault phase,
     * either via individual town siege OR via Nation War!
     * When true: all explosions, cannons, and block breaks are PERMITTED!
     */
    public boolean isTownUnderActiveSiege(String townName) {
        if (townName == null) return false;
        
        // 1. Direct local siege
        SiegeCamp camp = siegesByDefendingTown.get(townName.toLowerCase());
        if (camp != null && camp.isActiveSiege()) return true;

        // 2. Nation Wars: ALL towns of both nations are vulnerable during 2h active assault!
        for (NationWar war : activeNationWars.values()) {
            if (war.isActiveAssault() && war.isTownParticipating(townName)) {
                return true;
            }
        }

        return false;
    }

    public boolean isLocationUnderActiveSiege(Location loc) {
        if (loc == null) return false;
        String townName = plugin.getTownyHook().getTownNameAt(loc);
        return isTownUnderActiveSiege(townName);
    }

    public SiegeCamp getActiveSiegeForTown(String townName) {
        if (townName == null) return null;
        SiegeCamp def = siegesByDefendingTown.get(townName.toLowerCase());
        if (def != null) return def;
        return siegesByAttackingTown.get(townName.toLowerCase());
    }

    public SiegeCamp getSiegeCampAt(ChunkCoord coord) {
        return chunkToCamp.get(coord);
    }

    public Collection<SiegeCamp> getAllSieges() {
        return Collections.unmodifiableCollection(siegesById.values());
    }

    public void tick() {
        long now = System.currentTimeMillis();
        boolean needsSave = false;

        // 1. Tick Local Town Sieges
        for (SiegeCamp camp : siegesById.values()) {
            if (camp.getStatus() == SiegeCamp.Status.PREPARATION) {
                if (now >= camp.getPreparationEndsAtMillis()) {
                    camp.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
                    needsSave = true;

                    String msg = ChatColor.translateAlternateColorCodes('&', 
                            "&4&l[ШТУРМ] &c24 часа подготовки истекли! Начался активный 2-часовой штурм города &6" + 
                            camp.getDefendingTown() + " &cсилами &6" + camp.getAttackingTown() + "&c! Орудия и взрывы АКТИВИРОВАНЫ!");

                    Bukkit.broadcastMessage(msg);

                    for (Player p : Bukkit.getOnlinePlayers()) {
                        String pTown = plugin.getTownyHook().getPlayerTownName(p);
                        if (pTown != null) {
                            if (pTown.equalsIgnoreCase(camp.getDefendingTown())) {
                                p.sendTitle(ChatColor.DARK_RED + "⚡ ВРАГ ПОШЁЛ НА ШТУРМ! ⚡", 
                                        ChatColor.RED + "Взрывы и орудия активны! Обороняйте Мэрию!", 10, 100, 20);
                                p.playSound(p.getLocation(), Sound.ENTITY_ENDER_DRAGON_GROWL, 1.5f, 0.6f);
                            } else if (pTown.equalsIgnoreCase(camp.getAttackingTown())) {
                                p.sendTitle(ChatColor.RED + "⚡ ВРЕМЯ ШТУРМА НАСТАЛО! ⚡", 
                                        ChatColor.GOLD + "Фугасы и осадные орудия готовы к бою!", 10, 100, 20);
                                p.playSound(p.getLocation(), Sound.EVENT_RAID_HORN, 1.5f, 1.0f);
                            }
                        }
                    }
                }
            } else if (camp.getStatus() == SiegeCamp.Status.ACTIVE_SIEGE) {
                if (now >= camp.getActiveEndsAtMillis()) {
                    camp.setStatus(SiegeCamp.Status.COMPLETED);
                    needsSave = true;

                    String msg = ChatColor.translateAlternateColorCodes('&', 
                            "&a&l[ОСАДА ЗАВЕРШЕНА] &e2-часовой активный штурм города &6" + camp.getDefendingTown() + 
                            " &eзавершен! Город перешел в режим защиты и восстановления. Осадные взрывы ОТКЛЮЧЕНЫ.");

                    Bukkit.broadcastMessage(msg);
                }
            }
        }

        // 2. Tick Nation Wars (Unified Global Timer)
        for (NationWar war : activeNationWars.values()) {
            if (war.getStatus() == NationWar.Status.PREPARATION) {
                if (now >= war.getPreparationEndsAtMillis()) {
                    war.setStatus(NationWar.Status.ACTIVE_ASSAULT);
                    // Sync all linked camps to active assault
                    for (String campId : war.getLinkedCampIds()) {
                        SiegeCamp c = siegesById.get(campId);
                        if (c != null) {
                            c.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
                        }
                    }
                    needsSave = true;

                    String msg = ChatColor.translateAlternateColorCodes('&',
                            "&4&l[ШТУРМ НАЦИЙ 2Ч] &c24 часа подготовки истекли! Начался АКТИВНЫЙ 2-ЧАСОВОЙ ШТУРМ между нациями &6" +
                            war.getAttackerNation() + " &cи &6" + war.getDefenderNation() +
                            "&c! ВСЕ города обеих наций становятся УЯЗВИМЫ К ВЗРЫВАМ И ПУШКАМ!");

                    Bukkit.broadcastMessage(msg);

                    for (Player p : Bukkit.getOnlinePlayers()) {
                        String pTown = plugin.getTownyHook().getPlayerTownName(p);
                        if (pTown != null && war.isTownParticipating(pTown)) {
                            p.sendTitle(ChatColor.DARK_RED + "⚡ ШТУРМ НАЦИЙ НАЧАЛСЯ! ⚡",
                                    ChatColor.RED + "ВСЕ города уязвимы к взрывам (2 часа)! К орудиям!", 10, 120, 20);
                            p.playSound(p.getLocation(), Sound.ENTITY_ENDER_DRAGON_GROWL, 1.8f, 0.6f);
                        }
                    }
                }
            } else if (war.getStatus() == NationWar.Status.ACTIVE_ASSAULT) {
                if (now >= war.getActiveEndsAtMillis()) {
                    war.setStatus(NationWar.Status.COMPLETED);
                    for (String campId : war.getLinkedCampIds()) {
                        SiegeCamp c = siegesById.get(campId);
                        if (c != null) {
                            c.setStatus(SiegeCamp.Status.COMPLETED);
                        }
                    }
                    activeNationWars.remove(war.getWarId());
                    needsSave = true;

                    String msg = ChatColor.translateAlternateColorCodes('&',
                            "&a&l[ВОЙНА НАЦИЙ ЗАВЕРШЕНА] &e2-часовой штурм между &6" + war.getAttackerNation() +
                            " &eи &6" + war.getDefenderNation() + "&e завершён! Все города обеих наций возвращены в мирный режим с защитой от взрывов.");

                    Bukkit.broadcastMessage(msg);

                    for (Player p : Bukkit.getOnlinePlayers()) {
                        String pTown = plugin.getTownyHook().getPlayerTownName(p);
                        if (pTown != null && war.isTownParticipating(pTown)) {
                            p.sendTitle(ChatColor.GREEN + "ВОЙНА НАЦИЙ ОКОНЧЕНА", ChatColor.YELLOW + "Штурм завершён. Восстанавливайте повреждения.", 10, 80, 20);
                            p.playSound(p.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.0f, 1.0f);
                        }
                    }
                }
            }
        }

        if (needsSave) {
            saveData();
        }

        plugin.getBossBarManager().updateAllBossBars();
    }

    public void forceStartSiege(String defendingTownName) {
        SiegeCamp camp = siegesByDefendingTown.get(defendingTownName.toLowerCase());
        if (camp != null) {
            camp.setPreparationEndsAtMillis(System.currentTimeMillis() - 1000L);
            camp.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
            saveData();
            plugin.getBossBarManager().updateAllBossBars();
        }
    }

    public boolean forceStartNationAssault(String nationName) {
        NationWar war = getActiveNationWar(nationName);
        if (war != null) {
            war.setPreparationEndsAtMillis(System.currentTimeMillis() - 1000L);
            war.setStatus(NationWar.Status.ACTIVE_ASSAULT);
            for (String campId : war.getLinkedCampIds()) {
                SiegeCamp c = siegesById.get(campId);
                if (c != null) c.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
            }
            saveData();
            plugin.getBossBarManager().updateAllBossBars();
            return true;
        }
        return false;
    }

    public boolean skipNationWarTime(String nationName, long seconds) {
        NationWar war = getActiveNationWar(nationName);
        if (war == null) return false;

        long now = System.currentTimeMillis();
        if (war.getStatus() == NationWar.Status.PREPARATION) {
            long newPrepEnd = war.getPreparationEndsAtMillis() - (seconds * 1000L);
            if (newPrepEnd <= now) {
                war.setPreparationEndsAtMillis(now - 1000L);
                war.setStatus(NationWar.Status.ACTIVE_ASSAULT);
            } else {
                war.setPreparationEndsAtMillis(newPrepEnd);
            }
        } else if (war.getStatus() == NationWar.Status.ACTIVE_ASSAULT) {
            long newActiveEnd = war.getActiveEndsAtMillis() - (seconds * 1000L);
            if (newActiveEnd <= now) {
                war.setActiveEndsAtMillis(now - 1000L);
                war.setStatus(NationWar.Status.COMPLETED);
                activeNationWars.remove(war.getWarId());
            } else {
                war.setActiveEndsAtMillis(newActiveEnd);
            }
        }

        for (String campId : war.getLinkedCampIds()) {
            SiegeCamp c = siegesById.get(campId);
            if (c != null) {
                c.setPreparationEndsAtMillis(war.getPreparationEndsAtMillis());
                c.setActiveEndsAtMillis(war.getActiveEndsAtMillis());
                if (war.isActiveAssault()) c.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
            }
        }

        saveData();
        plugin.getBossBarManager().updateAllBossBars();
        return true;
    }

    public boolean endNationWar(String nationName) {
        NationWar war = getActiveNationWar(nationName);
        if (war != null) {
            war.setStatus(NationWar.Status.COMPLETED);
            for (String campId : war.getLinkedCampIds()) {
                SiegeCamp c = siegesById.get(campId);
                if (c != null) c.setStatus(SiegeCamp.Status.COMPLETED);
            }
            activeNationWars.remove(war.getWarId());
            saveData();
            plugin.getBossBarManager().updateAllBossBars();
            return true;
        }
        return false;
    }

    public boolean skipSiegeTime(String townName, long secondsToSkip) {
        SiegeCamp camp = getActiveSiegeForTown(townName);
        if (camp == null) return false;

        long now = System.currentTimeMillis();
        if (camp.getStatus() == SiegeCamp.Status.PREPARATION) {
            long newPrepEnd = camp.getPreparationEndsAtMillis() - (secondsToSkip * 1000L);
            if (newPrepEnd <= now) {
                camp.setPreparationEndsAtMillis(now - 1000L);
                camp.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
            } else {
                camp.setPreparationEndsAtMillis(newPrepEnd);
            }
        } else if (camp.getStatus() == SiegeCamp.Status.ACTIVE_SIEGE) {
            long newActiveEnd = camp.getActiveEndsAtMillis() - (secondsToSkip * 1000L);
            if (newActiveEnd <= now) {
                camp.setActiveEndsAtMillis(now - 1000L);
                camp.setStatus(SiegeCamp.Status.COMPLETED);
                unregisterSiege(camp);
            } else {
                camp.setActiveEndsAtMillis(newActiveEnd);
            }
        }
        saveData();
        plugin.getBossBarManager().updateAllBossBars();
        return true;
    }
}
"""

with open(os.path.join(SRC_DIR, "com", "towny", "sieges", "manager", "SiegeManager.java"), "w", encoding="utf-8") as f:
    f.write(siege_manager_code)

# 4. SiegeBossBarManager.java
bossbar_code = """package com.towny.sieges.bossbar;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.NationWar;
import com.towny.sieges.model.SiegeCamp;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.entity.Player;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SiegeBossBarManager {

    private final TownySiegesPlugin plugin;
    private final Map<UUID, BossBar> playerBossBars = new ConcurrentHashMap<>();

    public SiegeBossBarManager(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    public void updateAllBossBars() {
        if (!plugin.getConfig().getBoolean("bossbar.enabled", true)) {
            clearAll();
            return;
        }

        for (Player player : Bukkit.getOnlinePlayers()) {
            updatePlayerBossBar(player);
        }
    }

    public void updatePlayerBossBar(Player player) {
        if (player == null || !player.isOnline()) return;

        if (!plugin.getConfig().getBoolean("bossbar.enabled", true)) {
            removePlayerBossBar(player);
            return;
        }

        String townName = plugin.getTownyHook().getPlayerTownName(player);
        if (townName == null) {
            removePlayerBossBar(player);
            return;
        }

        // 1. Check Nation Wars First (Unified Global BossBar)
        NationWar war = plugin.getSiegeManager().getActiveNationWarForTown(townName);
        if (war != null && war.getStatus() != NationWar.Status.COMPLETED) {
            displayNationWarBossBar(player, war);
            return;
        }

        // 2. Check Individual Local Town Siege
        SiegeCamp camp = plugin.getSiegeManager().getActiveSiegeForTown(townName);
        if (camp == null || camp.getStatus() == SiegeCamp.Status.COMPLETED || camp.getStatus() == SiegeCamp.Status.CANCELLED) {
            removePlayerBossBar(player);
            return;
        }

        displayLocalSiegeBossBar(player, townName, camp);
    }

    private void displayNationWarBossBar(Player player, NationWar war) {
        BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), k -> {
            BossBar b = Bukkit.createBossBar(
                    "Война Наций",
                    BarColor.YELLOW,
                    BarStyle.SEGMENTED_10
            );
            b.addPlayer(player);
            b.setVisible(true);
            return b;
        });

        if (bar == null) return;
        if (!bar.getPlayers().contains(player)) {
            bar.addPlayer(player);
        }

        String timeStr = war.getFormattedRemainingTime();
        if (war.isPreparation()) {
            bar.setColor(BarColor.YELLOW);
            bar.setStyle(BarStyle.SEGMENTED_10);
            long totalPrep = plugin.getConfig().getLong("nationwar.preparation-duration-seconds", 86400L);
            long rem = war.getRemainingSeconds();
            double progress = Math.max(0.0, Math.min(1.0, (double) rem / (double) totalPrep));
            bar.setProgress(progress);

            String title = ChatColor.translateAlternateColorCodes('&',
                    "&6&l⚔ ВОЙНА НАЦИЙ: &e" + war.getAttackerNation() + " &7vs &c" + war.getDefenderNation() +
                    " &7| &eШтурм через: &b" + timeStr + " &7(Единый таймер)");
            bar.setTitle(title);
        } else if (war.isActiveAssault()) {
            bar.setColor(BarColor.RED);
            bar.setStyle(BarStyle.SOLID);
            long totalAssault = plugin.getConfig().getLong("nationwar.assault-duration-seconds", 7200L);
            long rem = war.getRemainingSeconds();
            double progress = Math.max(0.0, Math.min(1.0, (double) rem / (double) totalAssault));
            bar.setProgress(progress);

            String title = ChatColor.translateAlternateColorCodes('&',
                    "&4&l⚡ ШТУРМ НАЦИЙ! &e" + war.getAttackerNation() + " &4⚔ &c" + war.getDefenderNation() +
                    " &7| &cВЗРЫВЫ ВО ВСЕХ ГОРОДАХ! &7| &e" + timeStr + " &4⚡");
            bar.setTitle(title);
        }
    }

    private void displayLocalSiegeBossBar(Player player, String townName, SiegeCamp camp) {
        boolean isDefender = townName.equalsIgnoreCase(camp.getDefendingTown());
        boolean isAttacker = townName.equalsIgnoreCase(camp.getAttackingTown());

        if (!isDefender && !isAttacker) {
            removePlayerBossBar(player);
            return;
        }

        BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), k -> {
            BossBar b = Bukkit.createBossBar(
                    "Осада",
                    BarColor.YELLOW,
                    BarStyle.SEGMENTED_10
            );
            b.addPlayer(player);
            b.setVisible(true);
            return b;
        });

        if (bar == null) return;
        if (!bar.getPlayers().contains(player)) {
            bar.addPlayer(player);
        }

        String timeStr = camp.getFormattedRemainingTime();
        int chunkCount = camp.getClaimedChunks().size();

        if (camp.isPreparationPhase()) {
            long totalPrep = plugin.getConfig().getLong("siege.preparation-duration-seconds", 86400L);
            long rem = camp.getRemainingPreparationSeconds();
            double progress = Math.max(0.0, Math.min(1.0, (double) rem / (double) totalPrep));

            bar.setColor(BarColor.YELLOW);
            bar.setStyle(BarStyle.SEGMENTED_10);
            bar.setProgress(progress);

            String title = isDefender ?
                    "&c&l⚔ ВАШ ГОРОД ОСАЖДЁН! &eВраг: &6" + camp.getAttackingTown() + " &7| &eШтурм через: &b" + timeStr :
                    "&6&l⚔ ОСАДА ГОРОДА &c" + camp.getDefendingTown() + "&r &7| &eШтурм через: &b" + timeStr;
            bar.setTitle(ChatColor.translateAlternateColorCodes('&', title));
        } else if (camp.isActiveSiege()) {
            long totalActive = plugin.getConfig().getLong("siege.active-duration-seconds", 7200L);
            long rem = camp.getRemainingActiveSeconds();
            double progress = Math.max(0.0, Math.min(1.0, (double) rem / (double) totalActive));

            bar.setColor(BarColor.RED);
            bar.setStyle(BarStyle.SOLID);
            bar.setProgress(progress);

            String title = isDefender ?
                    "&4&l⚡ ИДЁТ ШТУРМ ВАШЕГО ГОРОДА! &cВзрывы активны! &7| &fОсталось: &e" + timeStr :
                    "&4&l⚡ ШТУРМ ГОРОДА &6" + camp.getDefendingTown() + "&4! &cОрудия активны! &7| &fОсталось: &e" + timeStr;
            bar.setTitle(ChatColor.translateAlternateColorCodes('&', title));
        }
    }

    public void removePlayerBossBar(Player player) {
        if (player == null) return;
        BossBar bar = playerBossBars.remove(player.getUniqueId());
        if (bar != null) {
            bar.removePlayer(player);
            bar.setVisible(false);
        }
    }

    public void clearAll() {
        for (BossBar bar : playerBossBars.values()) {
            bar.removeAll();
            bar.setVisible(false);
        }
        playerBossBars.clear();
    }
}
"""

with open(os.path.join(SRC_DIR, "com", "towny", "sieges", "bossbar", "SiegeBossBarManager.java"), "w", encoding="utf-8") as f:
    f.write(bossbar_code)

# 5. SiegeCommand.java
siege_command_code = """package com.towny.sieges.command;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.NationWar;
import com.towny.sieges.model.SiegeCamp;
import org.bukkit.ChatColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class SiegeCommand implements CommandExecutor, TabCompleter {

    private final TownySiegesPlugin plugin;

    public SiegeCommand(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 0 || args[0].equalsIgnoreCase("help")) {
            sendHelp(sender);
            return true;
        }

        String sub = args[0].toLowerCase();

        // --- Nation War Commands ---
        if (sub.equals("nationwar") || sub.equals("war") || sub.equals("nw")) {
            return handleNationWarCommand(sender, args);
        }

        if (sub.equals("camp") || sub.equals("declare") || sub.equals("create")) {
            if (!(sender instanceof Player)) {
                sender.sendMessage(ChatColor.RED + "Команда только для игроков!");
                return true;
            }
            if (args.length < 2) {
                sender.sendMessage(ChatColor.RED + "Использование: /siege camp <Город-Цель>");
                return true;
            }
            Player player = (Player) sender;
            String targetTown = args[1];
            plugin.getSiegeManager().createSiegeCamp(player, targetTown, player.getLocation());
            return true;
        }

        if (sub.equals("expand") || sub.equals("claim")) {
            if (!(sender instanceof Player)) {
                sender.sendMessage(ChatColor.RED + "Команда только для игроков!");
                return true;
            }
            Player player = (Player) sender;
            plugin.getSiegeManager().expandSiegeCamp(player, player.getLocation());
            return true;
        }

        if (sub.equals("unclaim")) {
            if (!(sender instanceof Player)) {
                sender.sendMessage(ChatColor.RED + "Команда только для игроков!");
                return true;
            }
            Player player = (Player) sender;
            plugin.getSiegeManager().unclaimSiegeChunk(player, player.getLocation());
            return true;
        }

        if (sub.equals("list") || sub.equals("status")) {
            sender.sendMessage(ChatColor.GOLD + "══════ Активные Осады и Войны Наций ══════");
            
            // List Nation Wars
            int nwCount = 0;
            for (NationWar war : plugin.getSiegeManager().getAllNationWars()) {
                nwCount++;
                String phaseStr = war.isActiveAssault() ?
                        ChatColor.RED + "" + ChatColor.BOLD + "[АКТИВНЫЙ ШТУРМ 2Ч]" :
                        ChatColor.YELLOW + "[Подготовка 24ч]";
                sender.sendMessage(ChatColor.GOLD + "⚔ ВОЙНА НАЦИЙ: " + ChatColor.YELLOW + war.getAttackerNation() +
                        ChatColor.GRAY + " vs " + ChatColor.RED + war.getDefenderNation() +
                        " " + phaseStr + ChatColor.GRAY + " | Таймер: " + ChatColor.WHITE + war.getFormattedRemainingTime() +
                        ChatColor.GRAY + " (Городов: " + (war.getAttackerTowns().size() + war.getDefenderTowns().size()) + ")");
            }

            int count = 0;
            for (SiegeCamp camp : plugin.getSiegeManager().getAllSieges()) {
                count++;
                String phaseStr = camp.isActiveSiege() ? 
                        ChatColor.RED + "" + ChatColor.BOLD + "[АКТИВНЫЙ ШТУРМ 2Ч]" : 
                        ChatColor.YELLOW + "[Подготовка 24ч]";
                sender.sendMessage(ChatColor.YELLOW + "• " + ChatColor.GOLD + camp.getAttackingTown() + 
                        ChatColor.GRAY + " ➔ " + ChatColor.RED + camp.getDefendingTown() + 
                        " " + phaseStr + ChatColor.GRAY + " | Осталось: " + ChatColor.WHITE + camp.getFormattedRemainingTime() + 
                        ChatColor.GRAY + " (Чанков: " + camp.getClaimedChunks().size() + ")");
            }
            if (count == 0 && nwCount == 0) {
                sender.sendMessage(ChatColor.GRAY + "На сервере нет активных осад и войн наций.");
            }
            sender.sendMessage(ChatColor.GOLD + "══════════════════════════════════════════");
            return true;
        }

        if (sub.equals("info")) {
            if (!(sender instanceof Player)) {
                sender.sendMessage(ChatColor.RED + "Команда для игроков.");
                return true;
            }
            Player player = (Player) sender;
            String townName = plugin.getTownyHook().getPlayerTownName(player);
            if (townName == null) {
                player.sendMessage(ChatColor.RED + "Вы не состоите в городе.");
                return true;
            }

            NationWar war = plugin.getSiegeManager().getActiveNationWarForTown(townName);
            if (war != null) {
                player.sendMessage(ChatColor.GOLD + "══════ Статус Войны Наций для города «" + townName + "» ══════");
                player.sendMessage(ChatColor.WHITE + "Война: " + ChatColor.GOLD + war.getAttackerNation() + ChatColor.GRAY + " vs " + ChatColor.RED + war.getDefenderNation());
                player.sendMessage(ChatColor.WHITE + "Фаза: " + (war.isActiveAssault() ? ChatColor.DARK_RED + "АКТИВНЫЙ ШТУРМ (2ч)" : ChatColor.YELLOW + "Подготовка (24ч)"));
                player.sendMessage(ChatColor.WHITE + "Единый таймер: " + ChatColor.AQUA + war.getFormattedRemainingTime());
                player.sendMessage(ChatColor.WHITE + "Уязвимость к взрывам: " + (war.isActiveAssault() ? ChatColor.RED + "АКТИВНА ВО ВСЕХ ГОРОДАХ" : ChatColor.GREEN + "ЗАБЛОКИРОВАНА"));
                player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════════════");
                return true;
            }

            SiegeCamp camp = plugin.getSiegeManager().getActiveSiegeForTown(townName);
            if (camp == null) {
                player.sendMessage(ChatColor.GREEN + "[TownySieges] Ваш город («" + townName + "») в состоянии полного мира.");
                return true;
            }

            player.sendMessage(ChatColor.GOLD + "══════ Статус Осады Города «" + townName + "» ══════");
            player.sendMessage(ChatColor.WHITE + "Атакующий город: " + ChatColor.RED + camp.getAttackingTown());
            player.sendMessage(ChatColor.WHITE + "Город-цель: " + ChatColor.GOLD + camp.getDefendingTown());
            player.sendMessage(ChatColor.WHITE + "Фаза: " + (camp.isActiveSiege() ? ChatColor.DARK_RED + "АКТИВНЫЙ ШТУРМ (2ч)" : ChatColor.YELLOW + "Подготовка (24ч)"));
            player.sendMessage(ChatColor.WHITE + "Осталось времени: " + ChatColor.AQUA + camp.getFormattedRemainingTime());
            player.sendMessage(ChatColor.WHITE + "Чанков осадного лагеря: " + ChatColor.YELLOW + camp.getClaimedChunks().size());
            player.sendMessage(ChatColor.WHITE + "Урон взрывов и пушек: " + (camp.isActiveSiege() ? ChatColor.RED + "АКТИВЕН" : ChatColor.GREEN + "ЗАБЛОКИРОВАН (мирный режим)"));
            player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");
            return true;
        }

        if (sub.equals("skip")) {
            if (!sender.hasPermission("townysieges.admin") && !sender.isOp()) {
                sender.sendMessage(ChatColor.RED + "Нет прав.");
                return true;
            }
            if (args.length >= 2) {
                try {
                    long sec = Long.parseLong(args[1]);
                    for (NationWar war : plugin.getSiegeManager().getAllNationWars()) {
                        plugin.getSiegeManager().skipNationWarTime(war.getAttackerNation(), sec);
                    }
                    for (SiegeCamp camp : plugin.getSiegeManager().getAllSieges()) {
                        plugin.getSiegeManager().skipSiegeTime(camp.getDefendingTown(), sec);
                    }
                    sender.sendMessage(ChatColor.GREEN + "[TownySieges] Пропущено " + sec + " сек. времени для всех осад и войн наций!");
                } catch (NumberFormatException e) {
                    sender.sendMessage(ChatColor.RED + "Укажите целое число секунд.");
                }
            }
            return true;
        }

        if (sub.equals("reload")) {
            if (!sender.hasPermission("townysieges.admin") && !sender.isOp()) {
                sender.sendMessage(ChatColor.RED + "Нет прав.");
                return true;
            }
            plugin.reloadConfig();
            sender.sendMessage(ChatColor.GREEN + "[TownySieges] Конфигурация успешно перезагружена.");
            return true;
        }

        return true;
    }

    private boolean handleNationWarCommand(CommandSender sender, String[] args) {
        if (args.length < 2) {
            sender.sendMessage(ChatColor.GOLD + "══════ Команды Войны Наций ══════");
            sender.sendMessage(ChatColor.YELLOW + "/siege nationwar declare <Нация> " + ChatColor.GRAY + "- Объявить войну нации (Король)");
            sender.sendMessage(ChatColor.YELLOW + "/siege nationwar status " + ChatColor.GRAY + "- Текущий статус и единый таймер");
            sender.sendMessage(ChatColor.YELLOW + "/siege nationwar assault <Нация> " + ChatColor.GRAY + "- Начать 2ч штурм (Админ)");
            sender.sendMessage(ChatColor.YELLOW + "/siege nationwar skip <Нация> <сек> " + ChatColor.GRAY + "- Пропустить время (Админ)");
            sender.sendMessage(ChatColor.YELLOW + "/siege nationwar end <Нация> " + ChatColor.GRAY + "- Завершить войну наций (Админ)");
            sender.sendMessage(ChatColor.GOLD + "═════════════════════════════════");
            return true;
        }

        String action = args[1].toLowerCase();

        if (action.equals("declare")) {
            if (!(sender instanceof Player)) {
                sender.sendMessage(ChatColor.RED + "Только для игроков!");
                return true;
            }
            if (args.length < 3) {
                sender.sendMessage(ChatColor.RED + "Использование: /siege nationwar declare <Нация>");
                return true;
            }
            Player p = (Player) sender;
            String targetNation = args[2];
            plugin.getSiegeManager().declareNationWar(p, targetNation);
            return true;
        }

        if (action.equals("status") || action.equals("info")) {
            if (plugin.getSiegeManager().getAllNationWars().isEmpty()) {
                sender.sendMessage(ChatColor.GREEN + "[TownySieges] На сервере нет активных войн наций.");
                return true;
            }
            for (NationWar war : plugin.getSiegeManager().getAllNationWars()) {
                sender.sendMessage(ChatColor.GOLD + "══════ Война Наций: " + war.getAttackerNation() + " vs " + war.getDefenderNation() + " ══════");
                sender.sendMessage(ChatColor.WHITE + "Фаза: " + (war.isActiveAssault() ? ChatColor.RED + "АКТИВНЫЙ ШТУРМ (2ч)" : ChatColor.YELLOW + "Подготовка (24ч)"));
                sender.sendMessage(ChatColor.WHITE + "Единый таймер для всех городов: " + ChatColor.AQUA + war.getFormattedRemainingTime());
                sender.sendMessage(ChatColor.WHITE + "Города Северной стороны: " + ChatColor.YELLOW + war.getAttackerTowns());
                sender.sendMessage(ChatColor.WHITE + "Города Южной стороны: " + ChatColor.RED + war.getDefenderTowns());
                sender.sendMessage(ChatColor.WHITE + "Осадных лагерей на фронте: " + ChatColor.GREEN + war.getLinkedCampIds().size());
                sender.sendMessage(ChatColor.WHITE + "Уязвимость к взрывам: " + (war.isActiveAssault() ? ChatColor.RED + "АКТИВНА" : ChatColor.GREEN + "ЗАБЛОКИРОВАНА"));
                sender.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════════");
            }
            return true;
        }

        if (action.equals("assault")) {
            if (!sender.hasPermission("townysieges.admin") && !sender.isOp()) {
                sender.sendMessage(ChatColor.RED + "Нет прав.");
                return true;
            }
            if (args.length < 3) {
                sender.sendMessage(ChatColor.RED + "Использование: /siege nationwar assault <Нация>");
                return true;
            }
            String nat = args[2];
            boolean ok = plugin.getSiegeManager().forceStartNationAssault(nat);
            if (ok) {
                sender.sendMessage(ChatColor.GREEN + "[TownySieges] 2-часовой штурм войны наций начат! Все города обеих наций уязвимы к взрывам.");
            } else {
                sender.sendMessage(ChatColor.RED + "[TownySieges] Война для нации «" + nat + "» не найдена.");
            }
            return true;
        }

        if (action.equals("skip")) {
            if (!sender.hasPermission("townysieges.admin") && !sender.isOp()) {
                sender.sendMessage(ChatColor.RED + "Нет прав.");
                return true;
            }
            if (args.length < 4) {
                sender.sendMessage(ChatColor.RED + "Использование: /siege nationwar skip <Нация> <секунды>");
                return true;
            }
            String nat = args[2];
            try {
                long sec = Long.parseLong(args[3]);
                boolean ok = plugin.getSiegeManager().skipNationWarTime(nat, sec);
                if (ok) {
                    sender.sendMessage(ChatColor.GREEN + "[TownySieges] Пропущено " + sec + " сек. для войны наций «" + nat + "»!");
                } else {
                    sender.sendMessage(ChatColor.RED + "[TownySieges] Война не найдена.");
                }
            } catch (NumberFormatException e) {
                sender.sendMessage(ChatColor.RED + "Укажите число секунд.");
            }
            return true;
        }

        if (action.equals("end")) {
            if (!sender.hasPermission("townysieges.admin") && !sender.isOp()) {
                sender.sendMessage(ChatColor.RED + "Нет прав.");
                return true;
            }
            if (args.length < 3) {
                sender.sendMessage(ChatColor.RED + "Использование: /siege nationwar end <Нация>");
                return true;
            }
            String nat = args[2];
            boolean ok = plugin.getSiegeManager().endNationWar(nat);
            if (ok) {
                sender.sendMessage(ChatColor.GREEN + "[TownySieges] Война наций для «" + nat + "» завершена. Мир восстановлен.");
            } else {
                sender.sendMessage(ChatColor.RED + "[TownySieges] Война не найдена.");
            }
            return true;
        }

        return true;
    }

    private void sendHelp(CommandSender sender) {
        sender.sendMessage(ChatColor.GOLD + "══════ Справка TownySieges & Войны Наций ══════");
        sender.sendMessage(ChatColor.YELLOW + "/siege camp <Город> " + ChatColor.GRAY + "- Поставить осадный лагерь (Мэр)");
        sender.sendMessage(ChatColor.YELLOW + "/siege expand " + ChatColor.GRAY + "- Расширить чанк осадного лагеря (Мэр)");
        sender.sendMessage(ChatColor.YELLOW + "/siege unclaim " + ChatColor.GRAY + "- Расприватить чанк лагеря");
        sender.sendMessage(ChatColor.YELLOW + "/siege info " + ChatColor.GRAY + "- Информация о статусе осады или войны наций");
        sender.sendMessage(ChatColor.YELLOW + "/siege list " + ChatColor.GRAY + "- Список активных осад и войн наций");
        sender.sendMessage(ChatColor.GOLD + "Войны Наций:");
        sender.sendMessage(ChatColor.YELLOW + "/siege nationwar declare <Нация> " + ChatColor.GRAY + "- Объявить войну нации (Король)");
        sender.sendMessage(ChatColor.YELLOW + "/siege nationwar status " + ChatColor.GRAY + "- Статус войны и единый таймер");
        sender.sendMessage(ChatColor.GOLD + "══════════════════════════════════════════════");
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (args.length == 1) {
            return Arrays.asList("camp", "expand", "unclaim", "info", "list", "nationwar");
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("nationwar")) {
            return Arrays.asList("declare", "status", "assault", "skip", "end");
        }
        return new ArrayList<>();
    }
}
"""

with open(os.path.join(SRC_DIR, "com", "towny", "sieges", "command", "SiegeCommand.java"), "w", encoding="utf-8") as f:
    f.write(siege_command_code)

# 6. config.yml update
config_code = """# ========================================================
# TownySieges Configuration
# ========================================================
# Плагин тактических осад, осадных лагерей, таймеров штурма и Войн Наций для Towny.
#
# Механика Войн Наций:
# 1. Глава первой нации объявляет войну другой нации:
#    /siege nationwar declare <Нация>
# 2. ВСЕ города обеих наций переводятся в режим подготовки к штурму (24 часа)
#    с ЕДИНЫМ для всех городов обеих наций таймером.
# 3. Во время подготовки и штурма города обеих наций могут ставить осадные лагеря
#    друг на друга, и осада не будет начинаться с нуля, а будет продолжать таймер нации.
# 4. При штурме на 2 часа ВСЕ города обеих наций становятся уязвимы к взрывам орудий!

enabled: true
debug-logging: false

siege:
  # Время подготовки до начала штурма в секундах (86400 сек = 24 часа)
  preparation-duration-seconds: 86400

  # Длительность активной фазы штурма в секундах (7200 сек = 2 часа)
  active-duration-seconds: 7200

  # Дистанция от ближайших чанков города-цели для установки осадного лагеря (в чанках)
  min-distance-chunks: 3.0
  max-distance-chunks: 10.0

  # Максимальное количество чанков в одном осадном лагере
  max-siege-chunks-per-camp: 8

  # Экономические настройки (списание из казны атакующего города)
  economy:
    initial-camp-cost: 15000.0
    expand-chunk-cost: 10000.0
    daily-upkeep-per-chunk: 2500.0

nationwar:
  enabled: true
  # Единое время подготовки к штурму для всех городов обеих наций (24 часа)
  preparation-duration-seconds: 86400
  # Единое время активного штурма, когда все города уязвимы к взрывам (2 часа)
  assault-duration-seconds: 7200

# Настройки Боссбара (BossBar) с таймером обратного отсчета
bossbar:
  enabled: true
  color-prep: "YELLOW"
  color-active: "RED"
  style-prep: "SEGMENTED_10"
  style-active: "SOLID"
"""

with open(os.path.join(RES_DIR, "config.yml"), "w", encoding="utf-8") as f:
    f.write(config_code)

print("=== 2. Compiling TownySieges with javac ===")
shutil.rmtree(BIN_DIR, ignore_errors=True)
os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

java_files = []
for root, dirs, files in os.walk(SRC_DIR):
    for f in sorted(files):
        if f.endswith(".java"):
            java_files.append(os.path.join(root, f))

print(f"Found {len(java_files)} Java files to compile in TownySieges.")

cp_str = f"{LIB_DIR}/*"
cmd = ["javac", "-cp", cp_str, "-d", BIN_DIR, "-encoding", "UTF-8"] + java_files
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("TownySieges compilation FAILED!")
    print(res.stderr)
    exit(1)

print("TownySieges Java compilation SUCCESSFUL!")

# Copy resources to bin
for res_file in ["plugin.yml", "config.yml"]:
    src_res = os.path.join(RES_DIR, res_file)
    if os.path.exists(src_res):
        shutil.copy2(src_res, os.path.join(BIN_DIR, res_file))
        print(f"Copied resource: {res_file}")

# Package JAR
print("=== 3. Creating TownySieges Jar ===")
SIEGES_VERSION = "1.0.0"
SIEGES_NAME = "TownySieges"
SIEGES_JAR_NAME = f"{SIEGES_NAME}-{SIEGES_VERSION}.jar"
SIEGES_BUNDLE_NAME = f"{SIEGES_NAME}-v{SIEGES_VERSION}-bundle.zip"

jar_out = os.path.join(DIST_DIR, SIEGES_JAR_NAME)

with zipfile.ZipFile(jar_out, "w", zipfile.ZIP_DEFLATED) as zf:
    manifest_content = "Manifest-Version: 1.0\r\nCreated-By: TownyArchitectureTeam\r\n\r\n"
    zf.writestr("META-INF/MANIFEST.MF", manifest_content)
    
    for root, dirs, files in os.walk(BIN_DIR):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BIN_DIR)
            zf.write(full_path, rel_path)

shutil.copy2(jar_out, os.path.join(DIST_DIR, "TownySieges.jar"))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, SIEGES_JAR_NAME))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, "TownySieges.jar"))

with open(jar_out, "rb") as f:
    jar_bytes = f.read()
jar_b64 = base64.b64encode(jar_bytes).decode("utf-8")
jar_sha256 = hashlib.sha256(jar_bytes).hexdigest()
jar_size = len(jar_bytes)
jar_size_kb = f"{jar_size / 1024:.1f} KB"
print(f"TownySieges JAR created: {jar_out} ({jar_size} bytes, {jar_size_kb}, SHA256: {jar_sha256[:12]}...)")

# Package Bundle ZIP
print("=== 4. Creating TownySieges Bundle ZIP ===")
bundle_out = os.path.join(DIST_DIR, SIEGES_BUNDLE_NAME)
with zipfile.ZipFile(bundle_out, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(jar_out, SIEGES_JAR_NAME)
    for res_file in ["config.yml", "plugin.yml"]:
        p = os.path.join(RES_DIR, res_file)
        if os.path.exists(p):
            zf.write(p, f"config/{res_file}")

shutil.copy2(bundle_out, os.path.join(DIST_DIR, "TownySieges-bundle.zip"))
shutil.copy2(bundle_out, os.path.join(PUBLIC_DIR, SIEGES_BUNDLE_NAME))
shutil.copy2(bundle_out, os.path.join(PUBLIC_DIR, "TownySieges-bundle.zip"))

with open(bundle_out, "rb") as f:
    bundle_bytes = f.read()
bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
bundle_size = len(bundle_bytes)
bundle_size_kb = f"{bundle_size / 1024:.1f} KB"
print(f"TownySieges Bundle created: {bundle_out} ({bundle_size} bytes, {bundle_size_kb})")

# Update src/data/townySiegesData.ts
print("=== 5. Updating src/data/townySiegesData.ts ===")
sources_list = []
source_files_meta = [
    ("src/main/java/com/towny/sieges/TownySiegesPlugin.java", "TownySiegesPlugin.java"),
    ("src/main/java/com/towny/sieges/listener/SiegeProtectionListener.java", "SiegeProtectionListener.java"),
    ("src/main/java/com/towny/sieges/manager/SiegeManager.java", "SiegeManager.java"),
    ("src/main/java/com/towny/sieges/model/NationWar.java", "NationWar.java"),
    ("src/main/java/com/towny/sieges/model/ChunkCoord.java", "ChunkCoord.java"),
    ("src/main/java/com/towny/sieges/model/SiegeCamp.java", "SiegeCamp.java"),
    ("src/main/java/com/towny/sieges/hook/TownyHook.java", "TownyHook.java"),
    ("src/main/java/com/towny/sieges/command/SiegeCommand.java", "SiegeCommand.java"),
    ("src/main/java/com/towny/sieges/bossbar/SiegeBossBarManager.java", "SiegeBossBarManager.java"),
    ("src/main/resources/plugin.yml", "plugin.yml"),
    ("src/main/resources/config.yml", "config.yml"),
]

for rel_p, name in source_files_meta:
    full_p = os.path.join(BASE_DIR, "tmp", "towny-sieges", rel_p)
    if os.path.exists(full_p):
        with open(full_p, "r", encoding="utf-8") as f:
            c = f.read()
        sources_list.append({
            "path": rel_p,
            "name": name,
            "content": c
        })

metadata_dict = {
    "name": "TownySieges",
    "version": "1.0.0",
    "jarFileName": SIEGES_JAR_NAME,
    "jarDownloadUrl": f"/{SIEGES_JAR_NAME}",
    "jarSizeFormatted": jar_size_kb,
    "jarSizeBytes": jar_size,
    "jarSha256": jar_sha256,
    "bundleFileName": SIEGES_BUNDLE_NAME,
    "bundleDownloadUrl": f"/{SIEGES_BUNDLE_NAME}",
    "bundleSizeFormatted": bundle_size_kb,
    "bundleSizeBytes": bundle_size,
    "bundleSha256": bundle_sha256,
    "description": "Плагин тактических осад, осадных лагерей, Войн Наций с единым таймером подготовки (24ч) и активного штурма (2ч), анимированным боссбаром и разблокировкой осадных разрушений во всех воюющих городах.",
    "releaseDate": "2026-10-10"
}

ts_content = f"""// Auto-generated by build_complete_nation_wars_plugin.py

export interface TownySiegesMetadata {{
  name: string;
  version: string;
  jarFileName: string;
  jarDownloadUrl: string;
  jarSizeFormatted: string;
  jarSizeBytes: number;
  jarSha256: string;
  bundleFileName: string;
  bundleDownloadUrl: string;
  bundleSizeFormatted: string;
  bundleSizeBytes: number;
  bundleSha256: string;
  description: string;
  releaseDate: string;
}}

export const TOWNY_SIEGES_METADATA: TownySiegesMetadata = {json.dumps(metadata_dict, indent=2, ensure_ascii=False)};

export const TOWNY_SIEGES_SOURCES = {json.dumps(sources_list, indent=2, ensure_ascii=False)};
"""

with open("src/data/townySiegesData.ts", "w", encoding="utf-8") as f:
    f.write(ts_content)

print("src/data/townySiegesData.ts successfully updated with new metadata and sources!")
