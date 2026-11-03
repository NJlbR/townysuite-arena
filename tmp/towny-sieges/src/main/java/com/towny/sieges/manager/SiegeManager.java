package com.towny.sieges.manager;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.event.SiegeCampDisbandEvent;
import com.towny.sieges.event.SiegePhaseChangeEvent;
import com.towny.sieges.model.ChunkCoord;
import com.towny.sieges.model.NationWar;
import com.towny.sieges.model.PreviousChunkStatus;
import com.towny.sieges.model.SiegeCamp;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.command.CommandSender;
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

                // Load initial chunk statuses
                Map<ChunkCoord, PreviousChunkStatus> initialStatuses = new LinkedHashMap<>();
                ConfigurationSection statusSec = s.getConfigurationSection("chunk-initial-statuses");
                if (statusSec != null) {
                    for (String key : statusSec.getKeys(false)) {
                        ChunkCoord cc = ChunkCoord.deserialize(key);
                        if (cc != null) {
                            String stName = statusSec.getString(key, "WILDERNESS");
                            try {
                                initialStatuses.put(cc, PreviousChunkStatus.valueOf(stName));
                            } catch (Exception ignored) {
                                initialStatuses.put(cc, PreviousChunkStatus.WILDERNESS);
                            }
                        }
                    }
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
                        initialStatuses, createdAt, prepEnds, activeEnds, status);

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

            // Save chunk initial statuses
            for (Map.Entry<ChunkCoord, PreviousChunkStatus> entry : camp.getInitialChunkStatuses().entrySet()) {
                dataConfig.set(path + ".chunk-initial-statuses." + entry.getKey().serialize(), entry.getValue().name());
            }

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

    public void registerSiege(SiegeCamp camp) {
        siegesById.put(camp.getSiegeId(), camp);
        siegesByDefendingTown.put(camp.getDefendingTown().toLowerCase(), camp);
        siegesByAttackingTown.put(camp.getAttackingTown().toLowerCase(), camp);
        for (ChunkCoord cc : camp.getClaimedChunks()) {
            chunkToCamp.put(cc, camp);
        }
    }

    public void addCapturedChunk(SiegeCamp camp, ChunkCoord coord) {
        if (camp == null || coord == null) return;
        PreviousChunkStatus status = plugin.getTownyHook().detectChunkStatus(coord, camp.getAttackingTown());
        camp.addClaimedChunk(coord, status);
        chunkToCamp.put(coord, camp);
    }

    public void unregisterSiege(SiegeCamp camp) {
        siegesById.remove(camp.getSiegeId());
        siegesByDefendingTown.remove(camp.getDefendingTown().toLowerCase());
        siegesByAttackingTown.remove(camp.getAttackingTown().toLowerCase());
        for (ChunkCoord cc : camp.getClaimedChunks()) {
            chunkToCamp.remove(cc);
        }
    }

    /**
     * Автоматический возврат всех чанков осадного лагеря к их исходному состоянию
     * (чанк города атакующих, официальный аванпост или дикие земли).
     * Вызывается при завершении осады/штурма независимо от результата,
     * а также при уничтожении лагеря мэром (/siege disband).
     */
    public void restoreAllCampChunks(SiegeCamp camp) {
        if (camp == null) return;
        String attackingTown = camp.getAttackingTown();

        for (ChunkCoord coord : camp.getClaimedChunks()) {
            PreviousChunkStatus prev = camp.getInitialStatus(coord);
            restoreSingleChunk(attackingTown, coord, prev);
        }


    }

    public void finalizeVictory(SiegeCamp camp) {
        if (camp == null) return;
        String attacker = camp.getAttackingTown();
        int secured = 0;

        // NEW: Transfer buildings on captured chunks to the attacker or deactivate them if partially captured
        plugin.getTownyHook().transferCapturedBuildings(attacker, camp.getClaimedChunks());

        for (ChunkCoord coord : camp.getClaimedChunks()) {
            // Если чанк и так был чанком города атакующих (или их аванпостом), TownyHook сам разберется.
            // Нам нужно закрепить за атакующим все чанки лагеря.
            boolean isAdjacent = plugin.getTownyHook().isChunkAdjacentToTown(coord, attacker);
            
            if (isAdjacent) {
                plugin.getTownyHook().claimChunkForTown(attacker, coord);
            } else {
                plugin.getTownyHook().createOutpostForTown(attacker, coord);
            }
            secured++;
        }
    }

    public void restoreSingleChunk(String attackingTown, ChunkCoord coord, PreviousChunkStatus prev) {
        if (coord == null) return;
        if (prev == null) prev = PreviousChunkStatus.WILDERNESS;

        switch (prev) {
            case WILDERNESS:
                plugin.getTownyHook().unclaimChunk(coord);
                break;
            case TOWN_CHUNK:
                plugin.getTownyHook().claimChunkForTown(attackingTown, coord);
                break;
            case OUTPOST:
                plugin.getTownyHook().createOutpostForTown(attackingTown, coord);
                break;
        }
    }

    /**
     * Команда мэра атакующего города: стоя на любом чанке своего осадного лагеря,
     * в любой момент осады или штурма уничтожить осадный лагерь с возвращением
     * всех его чанков в исходное состояние.
     */
    public boolean disbandCampByMayor(Player player) {
        if (player == null) return false;

        boolean isAdmin = player.hasPermission("townysieges.admin");
        String playerTown = plugin.getTownyHook().getPlayerTownName(player);

        ChunkCoord playerChunk = ChunkCoord.fromLocation(player.getLocation());
        SiegeCamp campAtChunk = getCampAtChunk(playerChunk);

        if (campAtChunk == null && playerTown != null) {
            campAtChunk = siegesByAttackingTown.get(playerTown.toLowerCase());
        }

        if (campAtChunk == null && isAdmin) {
            if (!siegesById.isEmpty()) {
                campAtChunk = siegesById.values().iterator().next();
            }
        }

        if (campAtChunk == null) {
            player.sendMessage(ChatColor.RED + "[TownySieges] В данный момент нет активного осадного лагеря для расформирования!");
            return false;
        }

        boolean isMayor = playerTown != null && plugin.getTownyHook().isMayor(player, playerTown);
        if (!isMayor && !isAdmin && !campAtChunk.getAttackingTown().equalsIgnoreCase(playerTown)) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Только Мэр атакующего города («" + campAtChunk.getAttackingTown() + "») или Администратор может расформировать этот осадный лагерь!");
            return false;
        }

        return executeDisband(campAtChunk, player, isAdmin && !isMayor);
    }

    public boolean executeDisband(SiegeCamp camp, Player mayor, boolean adminForced) {
        if (camp == null) return false;

        // 1. Cancel active banner captures on camp chunks and extinguish beacons
        if (plugin.getCaptureManager() != null) {
            plugin.getCaptureManager().cancelCapturesForCamp(camp);
        }

        // 2. Restore all chunks to their previous state (town chunk, outpost, or wilderness)
        restoreAllCampChunks(camp);

        // 3. Fire custom event for synchronization with other plugins
        try {
            Bukkit.getPluginManager().callEvent(new SiegeCampDisbandEvent(camp, mayor, adminForced));
        } catch (Throwable ignored) {}

        // 4. Update status and unregister
        camp.setStatus(SiegeCamp.Status.CANCELLED);
        unregisterSiege(camp);
        saveData();

        // 5. Visual and audio feedback
        if (mayor != null) {
            Location loc = mayor.getLocation();
            loc.getWorld().playSound(loc, Sound.ENTITY_GENERIC_EXPLODE, 1.8f, 0.7f);
            loc.getWorld().playSound(loc, Sound.BLOCK_ANVIL_DESTROY, 1.5f, 0.9f);
            loc.getWorld().spawnParticle(Particle.EXPLOSION_HUGE, loc, 3, 1, 1, 1, 0.1);
        }

        String whoText = adminForced ? "Администратор сервера" : "Мэр города " + camp.getAttackingTown() + (mayor != null ? " (" + mayor.getName() + ")" : "");
        String disbandAlert = ChatColor.translateAlternateColorCodes('&',
                "&c&l[ОСАДНЫЙ ЛАГЕРЬ УНИЧТОЖЕН] &e" + whoText +
                " &eрасформировал осадный лагерь против города &6" + camp.getDefendingTown() +
                "&e! Все &f" + camp.getClaimedChunks().size() +
                "&e чанков лагеря автоматически возвращены в исходный статус (городу / аванпосты / дикие земли).");

        Bukkit.broadcastMessage(disbandAlert);

        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (pTown != null) {
                if (pTown.equalsIgnoreCase(camp.getDefendingTown())) {
                    p.sendTitle(ChatColor.GREEN + "ОСАДА СНЯТА!", ChatColor.YELLOW + "Вражеский лагерь расформирован. Территории свободны.", 10, 80, 20);
                    p.playSound(p.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.2f, 1.0f);
                } else if (pTown.equalsIgnoreCase(camp.getAttackingTown())) {
                    p.sendTitle(ChatColor.GOLD + "ЛАГЕРЬ РАСФОРМИРОВАН", ChatColor.YELLOW + "Чанки возвращены в исходное состояние.", 10, 80, 20);
                }
            }
        }

        plugin.getBossBarManager().updateAllBossBars();
        return true;
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

        ChunkCoord campCoord = ChunkCoord.fromLocation(loc);
        if (chunkToCamp.containsKey(campCoord)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Здесь уже разбит другой осадный лагерь!");
            return false;
        }

        // Determine initial status of this chunk (Town Chunk, Outpost, or Wilderness)
        String townAtLoc = plugin.getTownyHook().getTownNameAt(loc);
        if (townAtLoc != null && !townAtLoc.equalsIgnoreCase(attackingTown)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Этот чанк принадлежит стороннему городу «" + townAtLoc + "»!");
            return false;
        }

        PreviousChunkStatus initialStatus = plugin.getTownyHook().detectChunkStatus(campCoord, attackingTown);

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

        if (initialStatus == PreviousChunkStatus.WILDERNESS) {
            if (actualDistance < minDistance) {
                mayor.sendMessage(ChatColor.RED + "[TownySieges] Слишком близко к городу «" + defendingTownName + "» на диких землях! Дистанция: " +
                        String.format("%.1f", actualDistance) + " чанков (минимум: " + minDistance + " ч.).");
                return false;
            }
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
        camp.setInitialStatus(campCoord, initialStatus);

        if (isPartOfNationWar) {
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
            registerSiege(camp);
            saveData();

            String prepTimeStr = (prepSeconds / 3600) + " ч.";
            String alertMsg = ChatColor.translateAlternateColorCodes('&',
                    "&c&l[ОСАДА] &eМэр города &6" + attackingTown + " &eразбил осадный лагерь против города &c" + defendingTownName +
                    "&e! Исходный статус чанка: &f" + initialStatus.getTitleRu() + "&e. До штурма осталось: &f" + prepTimeStr + ".");
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
        if (townAt != null && !townAt.equalsIgnoreCase(attackingTown)) {
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Нельзя приватить территорию стороннего города «" + townAt + "» под осадный лагерь!");
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

        PreviousChunkStatus prevStatus = plugin.getTownyHook().detectChunkStatus(coord, attackingTown);
        addCapturedChunk(camp, coord);
        saveData();

        mayor.sendMessage(ChatColor.GREEN + "[TownySieges] ✔ Чанк [" + coord.getX() + ", " + coord.getZ() +
                "] (исходно: " + prevStatus.getTitleRu() + ") присоединен к лагерю! Всего: " +
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
            mayor.sendMessage(ChatColor.RED + "[TownySieges] Нельзя расприватить центральный форпост осадного лагеря! Используйте /siege disband чтобы расформировать весь лагерь.");
            return false;
        }

        PreviousChunkStatus prev = camp.getInitialStatus(coord);
        restoreSingleChunk(camp.getAttackingTown(), coord, prev);

        camp.removeClaimedChunk(coord);
        chunkToCamp.remove(coord);
        saveData();

        mayor.sendMessage(ChatColor.YELLOW + "[TownySieges] Чанк осадного лагеря распривачен и возвращен в исходный статус (" + prev.getTitleRu() + ").");
        plugin.getBossBarManager().updateAllBossBars();
        return true;
    }

    /**
     * CRITICAL API FOR TOWNYEXPLOSIONUNBLOCKER & ARTILLERY:
     * Returns true if the town is currently in active 2-hour assault phase,
     * where cannons & explosives are allowed to damage town blocks.
     */
    public boolean isTownUnderActiveSiege(String townName) {
        if (townName == null) return false;

        // 1. Direct local siege against this town
        SiegeCamp camp = siegesByDefendingTown.get(townName.toLowerCase());
        if (camp != null && camp.isActiveSiege()) {
            return true;
        }

        // 2. Nation Wars: ALL towns of both nations are vulnerable during 2h active assault!
        NationWar war = getActiveNationWarForTown(townName);
        if (war != null && war.isActiveAssault()) {
            return true;
        }

        return false;
    }

    public boolean isLocationUnderActiveSiege(Location loc) {
        if (loc == null) return false;
        String townName = plugin.getTownyHook().getTownNameAt(loc);
        return isTownUnderActiveSiege(townName);
    }

    public SiegeCamp getCampAtChunk(ChunkCoord coord) {
        return chunkToCamp.get(coord);
    }

    public SiegeCamp getSiegeCampAt(ChunkCoord coord) {
        return chunkToCamp.get(coord);
    }

    public SiegeCamp getActiveSiegeForTown(String townName) {
        if (townName == null) return null;
        SiegeCamp c = siegesByDefendingTown.get(townName.toLowerCase());
        if (c != null) return c;
        return siegesByAttackingTown.get(townName.toLowerCase());
    }

    public Collection<SiegeCamp> getAllSieges() {
        return Collections.unmodifiableCollection(siegesById.values());
    }

    public void tick() {
        long now = System.currentTimeMillis();
        boolean needsSave = false;

        // 1. Tick Local Town Sieges
        for (SiegeCamp camp : new ArrayList<>(siegesById.values())) {
            if (camp.getStatus() == SiegeCamp.Status.PREPARATION) {
                if (now >= camp.getPreparationEndsAtMillis()) {
                    camp.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
                    needsSave = true;

                    try {
                        Bukkit.getPluginManager().callEvent(new SiegePhaseChangeEvent(camp, SiegeCamp.Status.PREPARATION, SiegeCamp.Status.ACTIVE_SIEGE));
                    } catch (Throwable ignored) {}

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

                    // Закрепляем захваченные чанки за атакующими!
                    finalizeVictory(camp);
                    unregisterSiege(camp);

                    try {
                        Bukkit.getPluginManager().callEvent(new SiegePhaseChangeEvent(camp, SiegeCamp.Status.ACTIVE_SIEGE, SiegeCamp.Status.COMPLETED));
                    } catch (Throwable ignored) {}

                    String msg = ChatColor.translateAlternateColorCodes('&',
                            "&a&l[ОСАДА ЗАВЕРШЕНА] &eАктивный штурм города &6" + camp.getDefendingTown() +
                            " &eзавершен! Город &6" + camp.getAttackingTown() + 
                            " &eуспешно закрепил за собой &f" + camp.getClaimedChunks().size() + " &eчанков (включая аванпосты).");

                    Bukkit.broadcastMessage(msg);
                }
            }
        }

        // 2. Tick Nation Wars (Unified Global Timer)
        for (NationWar war : new ArrayList<>(activeNationWars.values())) {
            if (war.getStatus() == NationWar.Status.PREPARATION) {
                if (now >= war.getPreparationEndsAtMillis()) {
                    war.setStatus(NationWar.Status.ACTIVE_ASSAULT);
                    // Sync all linked camps to active assault
                    for (String campId : war.getLinkedCampIds()) {
                        SiegeCamp c = siegesById.get(campId);
                        if (c != null) {
                            c.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
                            try {
                                Bukkit.getPluginManager().callEvent(new SiegePhaseChangeEvent(c, SiegeCamp.Status.PREPARATION, SiegeCamp.Status.ACTIVE_SIEGE));
                            } catch (Throwable ignored) {}
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
                            finalizeVictory(c);
                            unregisterSiege(c);
                            try {
                                Bukkit.getPluginManager().callEvent(new SiegePhaseChangeEvent(c, SiegeCamp.Status.ACTIVE_SIEGE, SiegeCamp.Status.COMPLETED));
                            } catch (Throwable ignored) {}
                        }
                    }
                    activeNationWars.remove(war.getWarId());
                    needsSave = true;

                    String msg = ChatColor.translateAlternateColorCodes('&',
                            "&a&l[ВОЙНА НАЦИЙ ЗАВЕРШЕНА] &eШтурм между &6" + war.getAttackerNation() +
                            " &eи &6" + war.getDefenderNation() + "&e завершён! Все захваченные чанки закреплены за атакующей стороной.");

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

    /**
     * Единая админская команда: Пропустить фазу подготовки (24ч) и мгновенно
     * начать активный 2-часовой штурм (7200 сек).
     * Аргумент target может быть: городом, нацией, либо null (по чанку/первой осаде).
     */
    public boolean skipPreparation(String target, CommandSender sender) {
        long now = System.currentTimeMillis();

        // 1. Проверяем, не указана ли нация
        if (target != null) {
            NationWar war = getActiveNationWar(target);
            if (war != null && war.getStatus() == NationWar.Status.PREPARATION) {
                war.setPreparationEndsAtMillis(now - 1000L);
                war.setActiveEndsAtMillis(now + 7200000L);
                war.setStatus(NationWar.Status.ACTIVE_ASSAULT);

                for (String campId : war.getLinkedCampIds()) {
                    SiegeCamp c = siegesById.get(campId);
                    if (c != null) {
                        c.setPreparationEndsAtMillis(now - 1000L);
                        c.setActiveEndsAtMillis(now + 7200000L);
                        c.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
                        try {
                            Bukkit.getPluginManager().callEvent(new SiegePhaseChangeEvent(c, SiegeCamp.Status.PREPARATION, SiegeCamp.Status.ACTIVE_SIEGE));
                        } catch (Throwable ignored) {}
                    }
                }
                saveData();
                plugin.getBossBarManager().updateAllBossBars();

                String alert = ChatColor.translateAlternateColorCodes('&',
                        "&4&l[АДМИН] &cПодготовка к Войне Наций (&6" + war.getAttackerNation() + " ➔ " + war.getDefenderNation() +
                        "&c) пропущена! АКТИВНЫЙ 2-ЧАСОВОЙ ШТУРМ НАЧАЛСЯ ПРЯМО СЕЙЧАС!");
                Bukkit.broadcastMessage(alert);
                return true;
            }

            // Проверяем локальную осаду по городу
            SiegeCamp camp = getActiveSiegeForTown(target);
            if (camp != null) {
                return triggerImmediateAssault(camp, sender);
            }
        }

        // 2. Если аргумент не указан, проверяем чанк админа
        if (sender instanceof Player) {
            Player p = (Player) sender;
            ChunkCoord cc = ChunkCoord.fromLocation(p.getLocation());
            SiegeCamp camp = getCampAtChunk(cc);
            if (camp != null) {
                return triggerImmediateAssault(camp, sender);
            }
        }

        // 3. Берем первую попавшуюся осаду в фазе PREPARATION
        for (SiegeCamp c : siegesById.values()) {
            if (c.getStatus() == SiegeCamp.Status.PREPARATION) {
                return triggerImmediateAssault(c, sender);
            }
        }

        for (NationWar w : activeNationWars.values()) {
            if (w.getStatus() == NationWar.Status.PREPARATION) {
                return skipPreparation(w.getAttackerNation(), sender);
            }
        }

        sender.sendMessage(ChatColor.RED + "[TownySieges] Не найдено активных осад или войн наций в фазе подготовки!");
        return false;
    }

    private boolean triggerImmediateAssault(SiegeCamp camp, CommandSender sender) {
        long now = System.currentTimeMillis();
        camp.setPreparationEndsAtMillis(now - 1000L);
        camp.setActiveEndsAtMillis(now + 7200000L);
        camp.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);

        try {
            Bukkit.getPluginManager().callEvent(new SiegePhaseChangeEvent(camp, SiegeCamp.Status.PREPARATION, SiegeCamp.Status.ACTIVE_SIEGE));
        } catch (Throwable ignored) {}

        saveData();
        plugin.getBossBarManager().updateAllBossBars();

        String alert = ChatColor.translateAlternateColorCodes('&',
                "&4&l[АДМИН] &cПодготовка к штурму города &6" + camp.getDefendingTown() +
                " &cпропущена! АКТИВНЫЙ 2-ЧАСОВОЙ ШТУРМ НАЧАЛСЯ! Орудия и взрывы РАЗБЛОКИРОВАНЫ!");

        Bukkit.broadcastMessage(alert);

        for (Player p : Bukkit.getOnlinePlayers()) {
            p.playSound(p.getLocation(), Sound.ENTITY_ENDER_DRAGON_GROWL, 1.5f, 0.6f);
        }

        if (sender != null) {
            sender.sendMessage(ChatColor.GREEN + "[TownySieges] Осада успешно переведена в активный 2-часовой штурм.");
        }
        return true;
    }

    /**
     * Единая админская команда: Досрочно завершить осаду со всеми возвратами чанков
     */
    public boolean endSiegeAdmin(String target, CommandSender sender) {
        if (target != null) {
            NationWar war = getActiveNationWar(target);
            if (war != null) {
                return endNationWar(target);
            }
            SiegeCamp camp = getActiveSiegeForTown(target);
            if (camp != null) {
                finalizeVictory(camp);
                camp.setStatus(SiegeCamp.Status.COMPLETED);
                unregisterSiege(camp);
                saveData();
                plugin.getBossBarManager().updateAllBossBars();
                Bukkit.broadcastMessage(ChatColor.YELLOW + "[TownySieges] Осада города " + camp.getDefendingTown() + " принудительно завершена администратором. Все захваченные чанки закреплены за атакующим.");
                return true;
            }
        }

        if (sender instanceof Player) {
            Player p = (Player) sender;
            ChunkCoord cc = ChunkCoord.fromLocation(p.getLocation());
            SiegeCamp camp = getCampAtChunk(cc);
            if (camp != null) {
                finalizeVictory(camp);
                camp.setStatus(SiegeCamp.Status.COMPLETED);
                unregisterSiege(camp);
                saveData();
                plugin.getBossBarManager().updateAllBossBars();
                sender.sendMessage(ChatColor.GREEN + "[TownySieges] Осада успешно завершена (результат зафиксирован).");
                return true;
            }
        }

        sender.sendMessage(ChatColor.RED + "[TownySieges] Осада не найдена. Укажите название города или нации: /siege admin end <Город|Нация>");
        return false;
    }

    public boolean endNationWar(String nationName) {
        NationWar war = getActiveNationWar(nationName);
        if (war != null) {
            war.setStatus(NationWar.Status.COMPLETED);
            for (String campId : war.getLinkedCampIds()) {
                SiegeCamp c = siegesById.get(campId);
                if (c != null) {
                    c.setStatus(SiegeCamp.Status.COMPLETED);
                    finalizeVictory(c);
                    unregisterSiege(c);
                }
            }
            activeNationWars.remove(war.getWarId());
            saveData();
            plugin.getBossBarManager().updateAllBossBars();
            Bukkit.broadcastMessage(ChatColor.YELLOW + "[TownySieges] Война нации " + nationName + " завершена администратором. Все захваченные территории закреплены за нациями-победителями.");
            return true;
        }
        return false;
    }

    /**
     * Admin command: Complete scan and recalculation of all wars, siege camps,
     * banner captures, bossbars, timers and Towny town existence.
     */
    public Map<String, Object> performFullRecalculation(CommandSender sender) {
        Map<String, Object> stats = new LinkedHashMap<>();
        int warsTotal = activeNationWars.size();
        int warsActive = 0;
        int warsEnded = 0;
        int campsTotal = siegesById.size();
        int campsActive = 0;
        int campsPrep = 0;
        int campsCleaned = 0;
        int prepAdvancedToAssault = 0;

        long now = System.currentTimeMillis();

        // 1. Recalculate and validate Nation Wars
        for (NationWar nw : new ArrayList<>(activeNationWars.values())) {
            boolean attExists = plugin.getTownyHook().getNation(nw.getAttackerNation()) != null;
            boolean defExists = plugin.getTownyHook().getNation(nw.getDefenderNation()) != null;
            if (!attExists || !defExists) {
                endNationWar(nw.getAttackerNation());
                warsEnded++;
            } else {
                warsActive++;
            }
        }

        // 2. Recalculate and validate Siege Camps
        for (SiegeCamp camp : new ArrayList<>(siegesById.values())) {
            boolean attTownExists = plugin.getTownyHook().getTown(camp.getAttackingTown()) != null;
            boolean defTownExists = plugin.getTownyHook().getTown(camp.getDefendingTown()) != null;

            if (!attTownExists || !defTownExists) {
                executeDisband(camp, null, true);
                campsCleaned++;
                continue;
            }

            if (camp.getStatus() == SiegeCamp.Status.PREPARATION) {
                if (now >= camp.getPreparationEndsAtMillis()) {
                    camp.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
                    prepAdvancedToAssault++;
                    campsActive++;
                } else {
                    campsPrep++;
                }
            } else if (camp.getStatus() == SiegeCamp.Status.ACTIVE_SIEGE) {
                if (now >= camp.getActiveEndsAtMillis()) {
                    finalizeVictory(camp);
                    campsCleaned++;
                } else {
                    campsActive++;
                }
            }

            // Sync camp chunks
            for (ChunkCoord cc : camp.getClaimedChunks()) {
                chunkToCamp.put(cc, camp);
            }
        }

        // 3. Recalculate bossbars
        if (plugin.getBossBarManager() != null) {
            plugin.getBossBarManager().updateAllBossBars();
        }

        // 4. Save data
        saveData();

        stats.put("warsTotal", warsTotal);
        stats.put("warsActive", warsActive);
        stats.put("warsEnded", warsEnded);
        stats.put("campsTotal", campsTotal);
        stats.put("campsActive", campsActive);
        stats.put("campsPrep", campsPrep);
        stats.put("campsCleaned", campsCleaned);
        stats.put("prepAdvancedToAssault", prepAdvancedToAssault);
        stats.put("bannerCapturesActive", (plugin.getCaptureManager() != null) ? plugin.getCaptureManager().getActiveCaptures().size() : 0);

        return stats;
    }
}
