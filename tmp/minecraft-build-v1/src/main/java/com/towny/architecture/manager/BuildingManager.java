package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.ChunkCoord;
import com.towny.architecture.util.RussianTranslator;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.*;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Firework;
import org.bukkit.entity.Player;
import org.bukkit.inventory.meta.FireworkMeta;

import java.io.File;
import java.io.IOException;
import java.util.*;

public class BuildingManager {
    private final TownyArchitecturePlugin plugin;
    private final Map<String, BuildingBlueprint> blueprints = new LinkedHashMap<>();
    private final Map<String, ActiveBuilding> activeBuildings = new LinkedHashMap<>();
    private final Map<String, Set<ChunkCoord>> townBuildPlots = new LinkedHashMap<>();
    private File dataFile;
    private FileConfiguration dataConfig;

    public BuildingManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
    }

    public void loadBlueprints(FileConfiguration config) {
        blueprints.clear();
        ConfigurationSection section = config.getConfigurationSection("blueprints");
        if (section == null) return;

        for (String key : section.getKeys(false)) {
            ConfigurationSection bpSec = section.getConfigurationSection(key);
            if (bpSec == null) continue;

            String name = bpSec.getString("name", key);
            String nameRu = bpSec.getString("name-ru", name);
            String description = bpSec.getString("description", "");
            String iconName = bpSec.getString("icon", "STONE");
            Material icon = Material.matchMaterial(iconName);
            if (icon == null) icon = Material.STONE;

            int requiredLevel = bpSec.getInt("required-skill-level", 0);
            boolean isWonder = bpSec.getBoolean("is-world-wonder", false);

            int chunkWidth = bpSec.getInt("chunk-footprint.width-chunks", 
                    bpSec.getInt("dimensions.width-chunks", 1));
            int chunkLength = bpSec.getInt("chunk-footprint.length-chunks", 
                    bpSec.getInt("dimensions.length-chunks", 1));
            int heightY = bpSec.getInt("dimensions.height-y", 15);

            Map<Material, Integer> resources = new LinkedHashMap<>();
            ConfigurationSection resSec = bpSec.getConfigurationSection("resources");
            if (resSec != null) {
                for (String matKey : resSec.getKeys(false)) {
                    Material mat = Material.matchMaterial(matKey);
                    if (mat != null) {
                        resources.put(mat, resSec.getInt(matKey, 1));
                    }
                }
            }

            Map<String, Object> buffs = new HashMap<>();
            ConfigurationSection buffSec = bpSec.getConfigurationSection("buffs");
            if (buffSec != null) {
                for (String bKey : buffSec.getKeys(false)) {
                    buffs.put(bKey, buffSec.get(bKey));
                }
            }

            String pColor = section.getString("particle-color", "#00FF00");
            BuildingBlueprint blueprint = new BuildingBlueprint(
                    key, name, nameRu, description, icon,
                    requiredLevel, isWonder, chunkWidth, chunkLength, heightY,
                    resources, buffs, pColor
            );
            blueprints.put(key, blueprint);
        }
        plugin.getLogger().info("[TownyArchitecture] Загружено чертежей зданий: " + blueprints.size());
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

        // 1. Load wonders completed
        ConfigurationSection wondersSec = dataConfig.getConfigurationSection("wonders");
        if (wondersSec != null) {
            for (String wonderId : wondersSec.getKeys(false)) {
                BuildingBlueprint bp = blueprints.get(wonderId);
                if (bp != null && bp.isWorldWonder()) {
                    bp.setWonderCompletedByTown(wondersSec.getString(wonderId));
                }
            }
        }

        // 2. Load town build plots (/plot set build)
        townBuildPlots.clear();
        ConfigurationSection plotsSec = dataConfig.getConfigurationSection("build_plots");
        if (plotsSec != null) {
            for (String town : plotsSec.getKeys(false)) {
                List<String> list = plotsSec.getStringList(town);
                Set<ChunkCoord> set = new LinkedHashSet<>();
                for (String item : list) {
                    ChunkCoord cc = ChunkCoord.deserialize(item);
                    if (cc != null) set.add(cc);
                }
                townBuildPlots.put(town.toLowerCase(), set);
            }
        }

        // 3. Load active buildings
        activeBuildings.clear();
        ConfigurationSection bldSec = dataConfig.getConfigurationSection("active_buildings");
        if (bldSec != null) {
            for (String instId : bldSec.getKeys(false)) {
                ConfigurationSection item = bldSec.getConfigurationSection(instId);
                if (item == null) continue;

                String bpId = item.getString("blueprint_id");
                String town = item.getString("town_name");
                String world = item.getString("world_name", "world");
                String uuidStr = item.getString("placed_by");
                UUID uuid = uuidStr != null ? UUID.fromString(uuidStr) : UUID.randomUUID();

                List<String> chunkStrings = item.getStringList("chunks");
                Set<ChunkCoord> chunks = new LinkedHashSet<>();
                for (String cs : chunkStrings) {
                    ChunkCoord cc = ChunkCoord.deserialize(cs);
                    if (cc != null) chunks.add(cc);
                }

                BuildingBlueprint bp = blueprints.get(bpId);
                Map<Material, Integer> req = bp != null ? bp.getResources() : Collections.emptyMap();

                ActiveBuilding bld = new ActiveBuilding(instId, bpId, town, uuid, world, chunks, req);
                bld.setHealthPercent(item.getDouble("health_percent", 100.0));
                String statusStr = item.getString("status", "CONSTRUCTING");
                try {
                    bld.setStatus(ActiveBuilding.Status.valueOf(statusStr));
                } catch (Exception ignored) {}

                ConfigurationSection placedSec = item.getConfigurationSection("placed_materials");
                if (placedSec != null) {
                    for (String matKey : placedSec.getKeys(false)) {
                        Material m = Material.matchMaterial(matKey);
                        if (m != null) {
                            bld.setPlacedCount(m, placedSec.getInt(matKey, 0));
                        }
                    }
                }
                ConfigurationSection maxPlacedSec = item.getConfigurationSection("max_placed_materials");
                if (maxPlacedSec != null) {
                    for (String matKey : maxPlacedSec.getKeys(false)) {
                        Material m = Material.matchMaterial(matKey);
                        if (m != null) {
                            bld.setMaxPlacedCount(m, maxPlacedSec.getInt(matKey, 0));
                        }
                    }
                } else {
                    // Fallback for older saves
                    if (placedSec != null) {
                        for (String matKey : placedSec.getKeys(false)) {
                            Material m = Material.matchMaterial(matKey);
                            if (m != null) {
                                bld.setMaxPlacedCount(m, placedSec.getInt(matKey, 0));
                            }
                        }
                    }
                }

                activeBuildings.put(instId, bld);
            }
        }
        
        // Автопроверка и синхронизация лимитов Чудес Света (на случай сбоев/лагов)
        for (BuildingBlueprint bp : blueprints.values()) {
            if (bp.isWorldWonder()) bp.setWonderCompletedByTown(null);
        }
        for (ActiveBuilding bld : activeBuildings.values()) {
            BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
            if (bp != null && bp.isWorldWonder() && bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
                bp.setWonderCompletedByTown(bld.getTownName());
            }
        }
        saveData(); // Сохраняем актуализированные лимиты
    }

    public void saveData() {
        if (dataConfig == null || dataFile == null) return;
        
        dataConfig.set("wonders", null);
        dataConfig.set("town_build_plots", null);
        dataConfig.set("active_buildings", null);

        // 1. Wonders
        for (BuildingBlueprint bp : blueprints.values()) {
            if (bp.isWorldWonder() && bp.getWonderCompletedByTown() != null) {
                dataConfig.set("wonders." + bp.getId(), bp.getWonderCompletedByTown());
            }
        }

        // 2. Build plots
        dataConfig.set("build_plots", null);
        for (Map.Entry<String, Set<ChunkCoord>> entry : townBuildPlots.entrySet()) {
            List<String> list = new ArrayList<>();
            for (ChunkCoord cc : entry.getValue()) {
                list.add(cc.serialize());
            }
            dataConfig.set("build_plots." + entry.getKey(), list);
        }

        // 3. Active buildings
        dataConfig.set("active_buildings", null);
        for (ActiveBuilding bld : activeBuildings.values()) {
            String path = "active_buildings." + bld.getInstanceId();
            dataConfig.set(path + ".blueprint_id", bld.getBlueprintId());
            dataConfig.set(path + ".town_name", bld.getTownName());
            dataConfig.set(path + ".world_name", bld.getWorldName());
            dataConfig.set(path + ".placed_by", bld.getPlacedBy().toString());
            dataConfig.set(path + ".health_percent", bld.getHealthPercent());
            dataConfig.set(path + ".status", bld.getStatus().name());

            List<String> chunkList = new ArrayList<>();
            for (ChunkCoord cc : bld.getAssignedChunks()) {
                chunkList.add(cc.serialize());
            }
            dataConfig.set(path + ".chunks", chunkList);

            for (Map.Entry<Material, Integer> pEntry : bld.getPlacedMaterials().entrySet()) {
                dataConfig.set(path + ".placed_materials." + pEntry.getKey().name(), pEntry.getValue());
            }
            for (Map.Entry<Material, Integer> pEntry : bld.getRequiredMaterials().entrySet()) {
                int maxVal = bld.getMaxPlacedCount(pEntry.getKey());
                dataConfig.set(path + ".max_placed_materials." + pEntry.getKey().name(), maxVal);
            }
        }

        try {
            dataConfig.save(dataFile);
        } catch (IOException e) {
            plugin.getLogger().severe("Не удалось сохранить data.yml: " + e.getMessage());
        }
    }

    // ========================================================
    // Town Plot Management (/plot set build)
    // ========================================================

    public boolean addTownBuildPlot(String townName, ChunkCoord chunk) {
        if (townName == null || chunk == null) return false;
        Set<ChunkCoord> set = townBuildPlots.computeIfAbsent(townName.toLowerCase(), k -> new LinkedHashSet<>());
        boolean added = set.add(chunk);
        if (added) saveData();
        return added;
    }

    public boolean removeTownBuildPlot(String townName, ChunkCoord chunk) {
        if (townName == null || chunk == null) return false;
        Set<ChunkCoord> set = townBuildPlots.get(townName.toLowerCase());
        if (set == null) return false;
        boolean removed = set.remove(chunk);
        
        // Also remove any active building on this chunk
        String bldToRemove = null;
        for (ActiveBuilding bld : activeBuildings.values()) {
            if (bld.occupiesChunk(chunk)) {
                bldToRemove = bld.getInstanceId();
                break;
            }
        }
        if (bldToRemove != null) {
            activeBuildings.remove(bldToRemove);
        }

        if (removed || bldToRemove != null) saveData();
        return removed;
    }

    public Set<ChunkCoord> getTownBuildPlots(String townName) {
        if (townName == null) return Collections.emptySet();
        return townBuildPlots.getOrDefault(townName.toLowerCase(), Collections.emptySet());
    }

    public Set<String> getAllTownsWithPlots() {
        return townBuildPlots.keySet();
    }

    public void syncAllPlotTags() {
        if (!plugin.getTownyHook().isTownyEnabled()) return;

        // 1. Tag all active buildings
        for (ActiveBuilding bld : activeBuildings.values()) {
            BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
            String bpName = bp != null ? bp.getNameRu() : bld.getBlueprintId();
            String plotName;
            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                plotName = "В процессе постройки: " + bpName;
            } else if (bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                plotName = bpName + " [Повреждено]";
            } else {
                plotName = bpName;
            }

            World world = Bukkit.getWorld(bld.getWorldName());
            if (world != null) {
                for (ChunkCoord cc : bld.getAssignedChunks()) {
                    Location loc = new Location(world, (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
                    plugin.getTownyHook().tagPlotAsBuild(loc, plotName);
                }
            }
        }

        // 2. Tag standalone town build plots
        for (Map.Entry<String, Set<ChunkCoord>> entry : townBuildPlots.entrySet()) {
            for (ChunkCoord cc : entry.getValue()) {
                if (isChunkOccupiedByBuilding(cc)) continue;
                for (World w : Bukkit.getWorlds()) {
                    Location loc = new Location(w, (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
                    if (plugin.getTownyHook().getTownName(loc) != null) {
                        plugin.getTownyHook().tagPlotAsBuild(loc, "Стройплощадка");
                        break;
                    }
                }
            }
        }
    }

    public void demolishBuilding(ActiveBuilding bld) {
        activeBuildings.remove(bld.getInstanceId());
        
        BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
        if (bp != null && bp.isWorldWonder()) {
            bp.setWonderCompletedByTown(null);
            if (dataConfig != null) {
                dataConfig.set("wonders." + bp.getId(), null);
            }
        }
        
        // Remove hologram/hud
        // plugin.getBuildingHudManager().removeHologram(bld.getInstanceId());
        
        // Rename chunks back to build plot
        for (ChunkCoord cc : bld.getAssignedChunks()) {
            org.bukkit.Location loc = new org.bukkit.Location(org.bukkit.Bukkit.getWorld(bld.getWorldName()), cc.getX() << 4, 70, cc.getZ() << 4);
            plugin.getTownyHook().tagPlotAsBuild(loc, "Стройплощадка");
        }
        
        saveData();
    }

    public boolean isChunkOccupiedByBuilding(ChunkCoord chunk) {
        for (ActiveBuilding bld : activeBuildings.values()) {
            if (bld.occupiesChunk(chunk)) {
                return true;
            }
        }
        return false;
    }

    public ActiveBuilding getBuildingOccupyingChunk(ChunkCoord chunk) {
        for (ActiveBuilding bld : activeBuildings.values()) {
            if (bld.occupiesChunk(chunk)) {
                return bld;
            }
        }
        return null;
    }

    /**
     * Searches for a contiguous free rectangle of designated build plots
     * matching the footprint (W x L or L x W) in the town.
     */
    public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk) {
        Set<ChunkCoord> allPlots = getTownBuildPlots(townName);
        if (allPlots.isEmpty()) return null;

        // Filter out plots occupied by existing buildings
        Set<ChunkCoord> freePlots = new HashSet<>();
        for (ChunkCoord c : allPlots) {
            if (c.getWorldName().equals(worldName) && !isChunkOccupiedByBuilding(c)) {
                freePlots.add(c);
            }
        }

        if (freePlots.isEmpty()) return null;

        // Try orientation 1: (W, L) and orientation 2: (L, W)
        int[][] orientations = (widthChunks == lengthChunks) 
                ? new int[][]{{widthChunks, lengthChunks}}
                : new int[][]{{widthChunks, lengthChunks}, {lengthChunks, widthChunks}};

        // 1. If preferred chunk is provided, check if it can form a matching rectangle
        if (preferredChunk != null && freePlots.contains(preferredChunk)) {
            for (int[] dim : orientations) {
                int w = dim[0];
                int l = dim[1];
                for (int dx = 0; dx < w; dx++) {
                    for (int dz = 0; dz < l; dz++) {
                        int originX = preferredChunk.getX() - dx;
                        int originZ = preferredChunk.getZ() - dz;
                        Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, originX, originZ, w, l);
                        if (candidate != null) return candidate;
                    }
                }
            }
        }

        // 2. Otherwise scan all free plots in town
        for (ChunkCoord anchor : freePlots) {
            for (int[] dim : orientations) {
                Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, anchor.getX(), anchor.getZ(), dim[0], dim[1]);
                if (candidate != null) return candidate;
            }
        }

        return null;
    }

    private Set<ChunkCoord> checkRectangle(Set<ChunkCoord> freePlots, String worldName, int startX, int startZ, int width, int length) {
        Set<ChunkCoord> rect = new LinkedHashSet<>();
        for (int x = 0; x < width; x++) {
            for (int z = 0; z < length; z++) {
                ChunkCoord check = new ChunkCoord(worldName, startX + x, startZ + z);
                if (!freePlots.contains(check)) {
                    return null;
                }
                rect.add(check);
            }
        }
        return rect;
    }

    // ========================================================
    // Starting Buildings
    // ========================================================

    public ActiveBuilding startBuilding(Player player, BuildingBlueprint bp) {
        String townName = plugin.getTownyHook().getPlayerTownName(player);
        if (townName == null) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cВы должны состоять в городе для возведения построек!"));
            return null;
        }

        // Check Mayor / Assistant / Builder rank strictly!
        if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player)) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cТолько мэр или помощник города могут утверждать строительные проекты!"));
            return null;
        }

        // Check Architect level strictly!
        if (plugin.getConfig().getBoolean("settings.enforce-skill-level", true)) {
            int level = plugin.getArchitectManager().getLevel(player);
            if (level < bp.getRequiredSkillLevel()) {
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&cВаш уровень Архитектора (" + level + 
                        ") недостаточен для этого чертежа! Требуется минимум: " + bp.getRequiredSkillLevel()));
                return null;
            }
        }

        // Check World Wonder uniqueness
        if (bp.isWorldWonder() && bp.getWonderCompletedByTown() != null) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&4[!] Это Чудо Света уже воздвигнуто городом «" + 
                    bp.getWonderCompletedByTown() + "» и заблокировано навсегда!"));
            return null;
        }

        // Check multiplicity limits
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
        }

        // Find matching free plot area in town
        ChunkCoord playerChunk = ChunkCoord.fromLocation(player.getLocation());
        Set<ChunkCoord> assignedChunks = findFreePlotArea(
                townName,
                player.getWorld().getName(),
                bp.getChunkWidth(),
                bp.getChunkLength(),
                playerChunk
        );

        if (assignedChunks == null || assignedChunks.isEmpty()) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cВ вашем городе нет свободного строительного участка размера " +
                    bp.getFootprintDisplay() + "!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&eНазначьте нужные чанки города командой &f/plot set build&e."));
            if (bp.isWorldWonder()) {
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&6Для Чудес Света требуется квадрат 2x2 чанка (4 смежных чанка)!"));
            }
            return null;
        }

        // Create the active building instance
        String instanceId = "bld-" + bp.getId() + "-" + System.currentTimeMillis();
        ActiveBuilding building = new ActiveBuilding(
                instanceId,
                bp.getId(),
                townName,
                player.getUniqueId(),
                player.getWorld().getName(),
                assignedChunks,
                bp.getResources()
        );

        activeBuildings.put(instanceId, building);
        saveData();

        // Tag plots in Towny
        for (ChunkCoord cc : assignedChunks) {
            Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
            plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "В процессе постройки: " + bp.getNameRu());
        }

        // Broadcast to town
        String chunkDisplay = formatChunkList(assignedChunks);
        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&aМэр &e" + player.getName() + 
                        " &aутвердил проект «&6&l" + bp.getNameRu() + "&a» на чанках: &f" + chunkDisplay + "&a!"));
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&7Встаньте на любой из этих чанков, чтобы увидеть шкалы необходимых блоков."));
                p.playSound(p.getLocation(), Sound.BLOCK_ANVIL_USE, 1.0f, 1.0f);
            }
        }

        return building;
    }

    public ActiveBuilding getBuildingAt(Location loc) {
        if (loc == null) return null;
        for (ActiveBuilding bld : activeBuildings.values()) {
            if (bld.contains(loc)) {
                return bld;
            }
        }
        return null;
    }

    public boolean handleBlockPlaced(Player player, Location loc, Material mat) {
        ActiveBuilding building = getBuildingAt(loc);
        if (building == null) {
            return true; // Not in any building plot
        }

        BuildingBlueprint bp = blueprints.get(building.getBlueprintId());
        if (bp == null) return true;

        // 1. Verify player is citizen of this town
        String playerTown = plugin.getTownyHook().getPlayerTownName(player);
        if (playerTown == null || !playerTown.equalsIgnoreCase(building.getTownName())) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Вы не можете строить здания чужого города!");
            return false;
        }

        // 2. Verify player is assigned BUILDER rank by Mayor (or is Mayor/Assistant)!
        if (!plugin.getTownyHook().hasBuilderPermission(player, building.getTownName())) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Вы не можете строить на строительных чанках!");
            player.sendMessage(ChatColor.YELLOW + "Мэр города должен назначить вам роль строителя: /town rank add " + player.getName() + " builder");
            return false;
        }

        // 3. Verify player has required Architect level strictly!
        if (plugin.getConfig().getBoolean("settings.enforce-skill-level", true)) {
            int level = plugin.getArchitectManager().getLevel(player);
            if (level < bp.getRequiredSkillLevel()) {
                player.sendMessage(ChatColor.RED + "[TownyArchitecture] Ваш уровень Архитектора (" + level + 
                        ") ниже требуемого (" + bp.getRequiredSkillLevel() + ") для чертежа «" + bp.getNameRu() + "»!");
                return false;
            }
        }

        // 4. Check if this material is needed for this specific building
        if (!bp.getResources().containsKey(mat)) {
            // Decorative placement or unrelated block inside chunk
            return true;
        }

        int current = building.getPlacedCount(mat);
        int needed = building.getRequiredCount(mat);

        // CASE A: Building is in construction
        if (building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
            // Add to building quota / placed materials
            boolean isNewMax = building.addPlacedBlock(mat);
            int newCurrent = building.getPlacedCount(mat);
            int percent = building.getProgressPercent();

            if (current >= needed) {
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§a✔ +" + RussianTranslator.getShortMaterialRu(mat) + " (" + newCurrent + "/" + needed + ") §7[Сверх квоты] §8| §6Прогресс: §a" + percent + "%"));
                } catch (Exception ignored) {}
            } else {
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§a✔ +" + RussianTranslator.getShortMaterialRu(mat) + " (" + newCurrent + "/" + needed + ") §8| §6Прогресс: §a" + percent + "%"));
                } catch (Exception ignored) {}
            }

            // AuraSkills XP award - only if it's a new historical max block placement!
            if (isNewMax) {
                awardBuilderXp(player);
            }

            // Visual effects
            playBuildEffects(loc, player);

            // Check 100% completion
            if (building.isFullyBuilt()) {
                completeBuilding(building, bp, player);
            }

            saveData();
            return true;
        }

        // CASE B: Building is already completed (ACTIVE or DAMAGED)
        building.addPlacedBlock(mat);
        int newCurrent = building.getPlacedCount(mat);
        double newHealth = building.calculateHealthPercent();
        building.setHealthPercent(newHealth);

        double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);

        if (building.isFullyBuilt() || newHealth >= 100.0) {
            building.setHealthPercent(100.0);
            boolean wasDamaged = building.getStatus() == ActiveBuilding.Status.DAMAGED;
            building.setStatus(ActiveBuilding.Status.ACTIVE);
            if (wasDamaged) {
                for (Player p : Bukkit.getOnlinePlayers()) {
                    String town = plugin.getTownyHook().getPlayerTownName(p);
                    if (town != null && town.equalsIgnoreCase(building.getTownName())) {
                        p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                plugin.getMsg("prefix") + "&a✔ [ГОРОД] Здание «&e" + bp.getNameRu() + 
                                "&a» полностью восстановлено установкой недостающих блоков! Баффы снова активны!"));
                        p.playSound(p.getLocation(), Sound.BLOCK_ANVIL_USE, 1.0f, 1.5f);
                    }
                }
            }
        } else if (newHealth >= threshold && building.getStatus() == ActiveBuilding.Status.DAMAGED) {
            building.setStatus(ActiveBuilding.Status.ACTIVE);
            for (Player p : Bukkit.getOnlinePlayers()) {
                String town = plugin.getTownyHook().getPlayerTownName(p);
                if (town != null && town.equalsIgnoreCase(building.getTownName())) {
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&a[ГОРОД] Прочность здания «&e" + bp.getNameRu() + 
                            "&a» достигла " + String.format("%.1f", newHealth) + "%! Баффы активированы!"));
                }
            }
        }

        // Action bar and feedback
        if (current < needed) {
            // Was missing block being restored
            awardBuilderXp(player);
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                        new TextComponent("§a✔ Восстановление «" + RussianTranslator.getShortMaterialRu(mat) + "» (" + newCurrent + "/" + needed + ") §8| §eПрочность: §a" + String.format("%.1f", newHealth) + "%"));
            } catch (Exception ignored) {}
        } else {
            // Extra block above required quota
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                        new TextComponent("§a✔ +" + RussianTranslator.getShortMaterialRu(mat) + " (" + newCurrent + "/" + needed + ") §7[Сверх нормы] §8| §eПрочность: §a" + String.format("%.1f", newHealth) + "%"));
            } catch (Exception ignored) {}
        }

        playBuildEffects(loc, player);
        saveData();
        return true;
    }

    public boolean handleBlockBroken(Player playerOrNull, Location loc, Material brokenMat) {
        ActiveBuilding building = getBuildingAt(loc);
        if (building == null) return true;

        // If player broke it, check citizen and builder permission
        if (playerOrNull != null) {
            String playerTown = plugin.getTownyHook().getPlayerTownName(playerOrNull);
            if (playerTown != null && playerTown.equalsIgnoreCase(building.getTownName())) {
                if (!plugin.getTownyHook().hasBuilderPermission(playerOrNull, building.getTownName())) {
                    playerOrNull.sendMessage(ChatColor.RED + "[TownyArchitecture] Вы не назначены строителем мэром города!");
                    return false;
                }
            }
        }

        if (!building.getRequiredMaterials().containsKey(brokenMat)) {
            return true;
        }

        int current = building.getPlacedCount(brokenMat);
        if (current <= 0) return true;

        building.removePlacedBlock(brokenMat);
        int newCurrent = building.getPlacedCount(brokenMat);
        int needed = building.getRequiredCount(brokenMat);

        BuildingBlueprint bp = blueprints.get(building.getBlueprintId());
        String bpName = bp != null ? bp.getNameRu() : building.getBlueprintId();

        if (building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
            int pct = building.getProgressPercent();
            if (playerOrNull != null) {
                try {
                    playerOrNull.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§c✖ -" + RussianTranslator.getShortMaterialRu(brokenMat) + " (" + newCurrent + "/" + needed + ") §8| §6Прогресс: §c" + pct + "%"));
                } catch (Exception ignored) {}
            }
        } else {
            // Completed building (ACTIVE or DAMAGED) -> calculate health based on effective blocks
            double newHealth = building.calculateHealthPercent();
            building.setHealthPercent(newHealth);

            double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);
            if (newHealth < threshold && building.getStatus() == ActiveBuilding.Status.ACTIVE) {
                building.setStatus(ActiveBuilding.Status.DAMAGED);

                for (Player p : Bukkit.getOnlinePlayers()) {
                    String town = plugin.getTownyHook().getPlayerTownName(p);
                    if (town != null && town.equalsIgnoreCase(building.getTownName())) {
                        p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                plugin.getMsg("prefix") + "&c[!] Здание «&e" + bpName + 
                                "&c» повреждено (разрушен " + RussianTranslator.getMaterialRu(brokenMat) + ")! Прочность: &e" + 
                                String.format("%.1f", newHealth) + "%&c. Баффы ОТКЛЮЧЕНЫ до восстановления блоков!"));
                        p.playSound(p.getLocation(), Sound.ENTITY_WITHER_DEATH, 0.6f, 1.2f);
                    }
                }
            }

            if (playerOrNull != null) {
                try {
                    if (newCurrent >= needed) {
                        playerOrNull.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                                new TextComponent("§e✖ Разрушен " + RussianTranslator.getShortMaterialRu(brokenMat) + " (" + newCurrent + "/" + needed + ") §8| §aПрочность: 100% (норма соблюдена)"));
                    } else {
                        playerOrNull.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                                new TextComponent("§c✖ Разрушен " + RussianTranslator.getShortMaterialRu(brokenMat) + " (" + newCurrent + "/" + needed + ") §8| §cПрочность: " + String.format("%.1f", newHealth) + "%"));
                    }
                } catch (Exception ignored) {}
            }
        }

        saveData();
        return true;
    }

    /**
     * Periodic recount of required materials on building chunks in case of lag/desync.
     */
    public void performPeriodicIntegrityCheck() {
        double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);

        for (ActiveBuilding bld : activeBuildings.values()) {
            World world = Bukkit.getWorld(bld.getWorldName());
            if (world == null) continue;

            Map<Material, Integer> actualCounts = new HashMap<>();
            for (Material m : bld.getRequiredMaterials().keySet()) {
                actualCounts.put(m, 0);
            }

            boolean anyLoaded = false;
            for (ChunkCoord cc : bld.getAssignedChunks()) {
                if (!world.isChunkLoaded(cc.getX(), cc.getZ())) continue;
                anyLoaded = true;
                Chunk chunk = world.getChunkAt(cc.getX(), cc.getZ());
                ChunkSnapshot snap = chunk.getChunkSnapshot(false, false, false);
                int minY = world.getMinHeight();
                int maxY = world.getMaxHeight();
                for (int x = 0; x < 16; x++) {
                    for (int z = 0; z < 16; z++) {
                        for (int y = minY; y < maxY; y++) {
                            Material mat = snap.getBlockType(x, y, z);
                            if (actualCounts.containsKey(mat)) {
                                actualCounts.put(mat, actualCounts.get(mat) + 1);
                            }
                        }
                    }
                }
            }

            if (!anyLoaded) continue;

            boolean changed = false;
            for (Map.Entry<Material, Integer> entry : bld.getRequiredMaterials().entrySet()) {
                Material mat = entry.getKey();
                int actual = actualCounts.getOrDefault(mat, 0);
                if (bld.getPlacedCount(mat) != actual) {
                    bld.setPlacedCount(mat, actual);
                    changed = true;
                }
            }

            if (changed) {
                if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                    if (bld.isFullyBuilt()) {
                        BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
                        completeBuilding(bld, bp, null);
                    }
                } else {
                    double health = bld.calculateHealthPercent();
                    bld.setHealthPercent(health);
                    if (health < threshold && bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
                        bld.setStatus(ActiveBuilding.Status.DAMAGED);
                    } else if (health >= 100.0 && bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                        bld.setStatus(ActiveBuilding.Status.ACTIVE);
                    }
                }
                saveData();
            }
        }
    }

    private void awardBuilderXp(Player player) {
        int xp = plugin.getConfig().getInt("settings.skill-xp-per-block", 15);
        plugin.getArchitectManager().addXp(player, xp);
    }

    private void playBuildEffects(Location loc, Player player) {
        if (plugin.getConfig().getBoolean("settings.particles-enabled", true)) {
            loc.getWorld().spawnParticle(Particle.VILLAGER_HAPPY, loc.clone().add(0.5, 1.2, 0.5), 8, 0.3, 0.3, 0.3, 0.05);
        }
        player.playSound(loc, Sound.BLOCK_NOTE_BLOCK_BELL, 0.6f, 1.4f);
    }

    private void completeBuilding(ActiveBuilding building, BuildingBlueprint bp, Player lastBuilder) {
        building.setStatus(ActiveBuilding.Status.ACTIVE);
        building.setHealthPercent(100.0);

        // Spawn victory fireworks
        World world = Bukkit.getWorld(building.getWorldName());
        if (world != null && !building.getAssignedChunks().isEmpty()) {
            ChunkCoord firstChunk = building.getAssignedChunks().iterator().next();
            Location center = new Location(world, (firstChunk.getX() << 4) + 8, 80, (firstChunk.getZ() << 4) + 8);
            Firework fw = world.spawn(center, Firework.class);
            FireworkMeta fwm = fw.getFireworkMeta();
            fwm.addEffect(FireworkEffect.builder()
                    .withColor(Color.YELLOW, Color.ORANGE, Color.WHITE)
                    .withFade(Color.ORANGE)
                    .with(FireworkEffect.Type.BALL_LARGE)
                    .trail(true)
                    .build());
            fwm.setPower(2);
            fw.setFireworkMeta(fwm);
        }

        // Tag plots in Towny with completed building name
        for (ChunkCoord cc : building.getAssignedChunks()) {
            World w = Bukkit.getWorld(building.getWorldName());
            if (w != null) {
                Location sampleLoc = new Location(w, (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
                plugin.getTownyHook().tagPlotAsBuild(sampleLoc, bp.getNameRu());
            }
        }

        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (bp.isWorldWonder()) {
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        "&6&l═════════════════════════════════════════════════\n" +
                        "&6✦ &lЧУДО СВЕТА ВОЗДВИГНУТО! &6✦\n" +
                        "&eГород &f" + building.getTownName() + " &eзавершил возведение «&6&l" + bp.getNameRu() + "&e»!\n" +
                        "&7Все граждане города получают постоянные усиления. На этот мир проект заблокирован!\n" +
                        "&6&l═════════════════════════════════════════════════"));
                p.playSound(p.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.0f, 1.0f);
            } else if (pTown != null && pTown.equalsIgnoreCase(building.getTownName())) {
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&6&l[ГОРОД]&a Строительство «&e" + bp.getNameRu() + 
                        "&a» завершено на 100%%! Баффы активированы!"));
                p.playSound(p.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.0f, 1.0f);
            }
        }

        if (bp.isWorldWonder()) {
            bp.setWonderCompletedByTown(building.getTownName());
            saveData();
        }
    }

    private String formatChunkList(Set<ChunkCoord> chunks) {
        StringBuilder sb = new StringBuilder();
        int i = 0;
        for (ChunkCoord cc : chunks) {
            if (i++ > 0) sb.append(", ");
            sb.append("[").append(cc.getX()).append(",").append(cc.getZ()).append("]");
        }
        return sb.toString();
    }

    public Collection<BuildingBlueprint> getBlueprints() { return blueprints.values(); }
    public BuildingBlueprint getBlueprint(String id) { return blueprints.get(id); }
    public Collection<ActiveBuilding> getActiveBuildings() { return activeBuildings.values(); }
}
