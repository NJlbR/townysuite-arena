package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.*;
import com.towny.architecture.util.RussianTranslator;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.*;
import org.bukkit.command.CommandSender;
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

        // Guaranteed registration: Town Hall and City Wall must always be available in the blueprints catalog!
        if (!blueprints.containsKey("town_hall")) {
            Map<Material, Integer> thRes = new LinkedHashMap<>();
            thRes.put(Material.STONE_BRICKS, 738);
            thRes.put(Material.DARK_OAK_PLANKS, 640);
            thRes.put(Material.DEEPSLATE_BRICKS, 172);
            thRes.put(Material.GLASS, 60);
            thRes.put(Material.IRON_BARS, 46);
            thRes.put(Material.LANTERN, 8);
            thRes.put(Material.GOLD_BLOCK, 8);
            thRes.put(Material.BELL, 1);
            Map<String, Object> thBuffs = new HashMap<>();
            thBuffs.put("hero-of-the-village", 1);
            blueprints.put("town_hall", new BuildingBlueprint(
                "town_hall", "Town Hall", "Мэрия",
                "Сердце города (2x2). Центр дипломатии и обороны. Обладает Щитом Мэрии, защищающим город во время войны!",
                Material.BELL, 25, false, 2, 2, 8, thRes, thBuffs, "#FFD700"
            ));
        }
        if (!blueprints.containsKey("city_wall")) {
            Map<Material, Integer> cwRes = new LinkedHashMap<>();
            cwRes.put(Material.STONE_BRICKS, 1054);
            cwRes.put(Material.COBBLESTONE, 254);
            cwRes.put(Material.CRACKED_STONE_BRICKS, 164);
            cwRes.put(Material.IRON_BARS, 20);
            cwRes.put(Material.LANTERN, 4);
            Map<String, Object> cwBuffs = new HashMap<>();
            cwBuffs.put("town_shield", 100);
            blueprints.put("city_wall", new BuildingBlueprint(
                "city_wall", "Fortified City Wall", "Городская Стена",
                "Фортификационный вал (2x1). Массивная модульная стена (2x взрывоустойчивость). Каждая стена дает +100 HP к Щиту Мэрии!",
                Material.BRICKS, 10, false, 2, 1, 6, cwRes, cwBuffs, "#808080"
            ));
        }

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
                BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bpId);
                Map<Material, Integer> req = (schem != null) ? schem.getTotalMaterials() : 
                        (bp != null ? bp.getResources() : Collections.emptyMap());

                int originX = item.getInt("origin_x", 0);
                int originY = item.getInt("origin_y", 64);
                int originZ = item.getInt("origin_z", 0);
                int layer = item.getInt("current_layer", 0);
                int rotDeg = item.getInt("rotation_deg", 0);

                ActiveBuilding bld = new ActiveBuilding(instId, bpId, town, uuid, world, chunks, req, originX, originY, originZ);
                bld.setCurrentLayer(layer);
                bld.setRotationDeg(rotDeg);
                bld.setHealthPercent(item.getDouble("health_percent", 100.0));
                bld.setExteriorExposurePercent(item.getDouble("exterior_exposure_percent", 100.0));
                String statusStr = item.getString("status", "CONSTRUCTING");
                try {
                    bld.setStatus(ActiveBuilding.Status.valueOf(statusStr));
                } catch (Exception ignored) {}

                List<String> completedList = item.getStringList("completed_blocks");
                for (String cb : completedList) {
                    String[] parts = cb.split(",");
                    if (parts.length == 3) {
                        try {
                            bld.markBlockCompleted(Integer.parseInt(parts[0]), Integer.parseInt(parts[1]), Integer.parseInt(parts[2]));
                        } catch (Exception ignored) {}
                    }
                }

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
                }

                activeBuildings.put(instId, bld);

                // Re-initialize BlockDisplay holograms if building is under construction or damaged
                if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                    Bukkit.getScheduler().runTaskLater(plugin, () -> {
                        plugin.getHologramDisplayManager().initHologramsForBuilding(bld);
                    }, 40L);
                }
            }
        }
        
        // Synchronize wonder limits
        for (BuildingBlueprint bp : blueprints.values()) {
            if (bp.isWorldWonder()) bp.setWonderCompletedByTown(null);
        }
        for (ActiveBuilding bld : activeBuildings.values()) {
            BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
            if (bp != null && bp.isWorldWonder() && bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
                bp.setWonderCompletedByTown(bld.getTownName());
            }
        }
        saveData();
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
        for (Map.Entry<String, Set<ChunkCoord>> entry : townBuildPlots.entrySet()) {
            List<String> list = new ArrayList<>();
            for (ChunkCoord cc : entry.getValue()) {
                list.add(cc.serialize());
            }
            dataConfig.set("build_plots." + entry.getKey(), list);
        }

        // 3. Active buildings
        for (ActiveBuilding bld : activeBuildings.values()) {
            String path = "active_buildings." + bld.getInstanceId();
            dataConfig.set(path + ".blueprint_id", bld.getBlueprintId());
            dataConfig.set(path + ".town_name", bld.getTownName());
            dataConfig.set(path + ".world_name", bld.getWorldName());
            dataConfig.set(path + ".placed_by", bld.getPlacedBy().toString());
            dataConfig.set(path + ".health_percent", bld.getHealthPercent());
            dataConfig.set(path + ".exterior_exposure_percent", bld.getExteriorExposurePercent());
            dataConfig.set(path + ".status", bld.getStatus().name());
            dataConfig.set(path + ".origin_x", bld.getOriginX());
            dataConfig.set(path + ".origin_y", bld.getOriginY());
            dataConfig.set(path + ".origin_z", bld.getOriginZ());
            dataConfig.set(path + ".rotation_deg", bld.getRotationDeg());
            dataConfig.set(path + ".current_layer", bld.getCurrentLayer());
            dataConfig.set(path + ".completed_blocks", new ArrayList<>(bld.getCompletedBlocks()));

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
        
        String bldToRemove = null;
        for (ActiveBuilding bld : activeBuildings.values()) {
            if (bld.occupiesChunk(chunk)) {
                bldToRemove = bld.getInstanceId();
                break;
            }
        }
        if (bldToRemove != null) {
            plugin.getHologramDisplayManager().clearHologramsForBuilding(bldToRemove);
            activeBuildings.remove(bldToRemove);
        }

        if (removed || bldToRemove != null) saveData();
        return removed;
    }

    public Set<ChunkCoord> getTownBuildPlots(String townName) {
        if (townName == null) return Collections.emptySet();
        return townBuildPlots.getOrDefault(townName.toLowerCase(), Collections.emptySet());
    }

    /**
     * Перерасчет построек при аннексии/поглощении города:
     * 1. Перевод всех зданий побежденного города под юрисдикцию победителя.
     * 2. 1x1 постройки (1 чанк): безлимитны, не ограничиваются при объединении.
     * 3. Уникальные постройки 1x2 / 2x1 (Казармы и др.) и 2x2 (Мэрии, Чудеса Света):
     *    В объединенном городе разрешена максимум 1 активная постройка каждого чертежа (за исключением стен).
     * 4. При обнаружении дубликатов чертежей приоритет отдается постройкам победившего города (они остаются активными),
     *    а дублирующиеся постройки захваченного города деактивируются (деспавн голограмм, статус DAMAGED, отключение баффов).
     */
    public void recalculateAndEnforceBuildingLimits(String victoriousTown, String capturedTown) {
        if (victoriousTown == null) return;

        // 1. Reassign all buildings from capturedTown to victoriousTown
        if (capturedTown != null) {
            for (ActiveBuilding bld : activeBuildings.values()) {
                if (bld.getTownName().equalsIgnoreCase(capturedTown)) {
                    bld.setTownName(victoriousTown);
                }
            }
        }

        // Group all active & constructing buildings for victoriousTown
        List<ActiveBuilding> allTownBuildings = new ArrayList<>();
        for (ActiveBuilding bld : activeBuildings.values()) {
            if (bld.getTownName().equalsIgnoreCase(victoriousTown)) {
                allTownBuildings.add(bld);
            }
        }

        // Group buildings by blueprint ID for unique blueprint checking
        Map<String, List<ActiveBuilding>> buildingsByBlueprint = new HashMap<>();
        for (ActiveBuilding bld : allTownBuildings) {
            BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
            if (bp == null) continue;

            // City walls are multi-segment structures and exempt from uniqueness limits
            if (bp.getId().equalsIgnoreCase("city_wall")) continue;

            int footprint = bp.getChunkWidth() * bp.getChunkLength();

            // 1x2 / 2x1 buildings (like Barracks), 2x2 buildings (Town Hall, Wonders)
            if (footprint >= 2 || bp.isWorldWonder()) {
                buildingsByBlueprint.computeIfAbsent(bp.getId(), k -> new ArrayList<>()).add(bld);
            }
        }

        // Enforce max 1 active per unique blueprint type, prioritizing victorious town's buildings
        int deactivatedCount = 0;
        for (Map.Entry<String, List<ActiveBuilding>> entry : buildingsByBlueprint.entrySet()) {
            List<ActiveBuilding> list = entry.getValue();
            if (list.size() > 1) {
                // Sort: buildings originally belonging to victoriousTown stay active first
                list.sort((b1, b2) -> {
                    boolean b1WasCaptured = capturedTown != null && b1.getTownName().equalsIgnoreCase(capturedTown);
                    boolean b2WasCaptured = capturedTown != null && b2.getTownName().equalsIgnoreCase(capturedTown);
                    if (!b1WasCaptured && b2WasCaptured) return -1;
                    if (b1WasCaptured && !b2WasCaptured) return 1;
                    return Long.compare(b1.getCreatedAt(), b2.getCreatedAt());
                });

                // Keep index 0 ACTIVE, deactivate remaining duplicate buildings
                for (int i = 1; i < list.size(); i++) {
                    ActiveBuilding excess = list.get(i);
                    deactivateBuildingDueToLimit(excess);
                    deactivatedCount++;
                }
            }
        }

        saveData();

    }

    /**
     * Передача построек с захваченных чанков атакующему городу.
     * Если постройка занимает несколько чанков, она передается только если ВСЕ её чанки захвачены.
     * В противном случае постройка деактивируется.
     * 
     * Используется Object для capturedChunks для совместимости между плагинами (разные классы ChunkCoord).
     */
    public void transferBuildingsOnCapturedChunks(String winnerTown, Set<?> capturedCoordsRaw) {
        if (winnerTown == null || capturedCoordsRaw == null || capturedCoordsRaw.isEmpty()) return;

        // Convert raw objects to our local ChunkCoord for efficient lookup
        Set<ChunkCoord> capturedChunks = new HashSet<>();
        for (Object obj : capturedCoordsRaw) {
            if (obj == null) continue;
            try {
                // If it's already our class
                if (obj instanceof ChunkCoord cc) {
                    capturedChunks.add(cc);
                    continue;
                }
                // Otherwise use reflection to extract fields (from TownySieges.ChunkCoord)
                String world = (String) obj.getClass().getMethod("getWorld").invoke(obj);
                int x = (int) obj.getClass().getMethod("getX").invoke(obj);
                int z = (int) obj.getClass().getMethod("getZ").invoke(obj);
                capturedChunks.add(new ChunkCoord(world, x, z));
            } catch (Exception e) {

            }
        }

        if (capturedChunks.isEmpty()) return;

        List<ActiveBuilding> toTransfer = new ArrayList<>();
        List<ActiveBuilding> toDeactivate = new ArrayList<>();

        for (ActiveBuilding bld : activeBuildings.values()) {
            boolean overlaps = false;
            boolean allCaptured = true;
            for (ChunkCoord cc : bld.getAssignedChunks()) {
                if (capturedChunks.contains(cc)) {
                    overlaps = true;
                } else {
                    allCaptured = false;
                }
            }

            if (overlaps) {
                if (allCaptured) {
                    toTransfer.add(bld);
                } else {
                    toDeactivate.add(bld);
                }
            }
        }

        for (ActiveBuilding bld : toTransfer) {
            String oldTown = bld.getTownName();
            bld.setTownName(winnerTown);
            bld.setStatus(ActiveBuilding.Status.ACTIVE);
            bld.setHealthPercent(100.0);

            // Move plots from old town to new town in the tracking map
            if (oldTown != null && !oldTown.equalsIgnoreCase(winnerTown)) {
                Set<ChunkCoord> oldPlots = townBuildPlots.get(oldTown.toLowerCase());
                if (oldPlots != null) {
                    for (ChunkCoord cc : bld.getAssignedChunks()) {
                        oldPlots.remove(cc);
                    }
                }
            }
            Set<ChunkCoord> newPlots = townBuildPlots.computeIfAbsent(winnerTown.toLowerCase(), k -> new HashSet<>());
            newPlots.addAll(bld.getAssignedChunks());


        }

        for (ActiveBuilding bld : toDeactivate) {
            deactivateBuildingDueToLimit(bld);

        }

        // Run limit enforcement for the winner town to handle duplicates (e.g. unique buildings)
        recalculateAndEnforceBuildingLimits(winnerTown, null);
        
        saveData();
    }

    private void deactivateBuildingDueToLimit(ActiveBuilding bld) {
        if (bld == null) return;
        bld.setStatus(ActiveBuilding.Status.DAMAGED);
        bld.setHealthPercent(0.0);
        plugin.getHologramDisplayManager().clearHologramsForBuilding(bld.getInstanceId());
    }

    public Set<String> getAllTownsWithPlots() {
        return townBuildPlots.keySet();
    }

    public void syncAllPlotTags() {
        for (Map.Entry<String, Set<ChunkCoord>> entry : townBuildPlots.entrySet()) {
            for (ChunkCoord cc : entry.getValue()) {
                World w = Bukkit.getWorld(cc.getWorldName());
                if (w != null) {
                    Location loc = new Location(w, (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
                    ActiveBuilding occupying = getBuildingOccupyingChunk(cc);
                    if (occupying != null) {
                        BuildingBlueprint bp = blueprints.get(occupying.getBlueprintId());
                        String name = bp != null ? bp.getNameRu() : occupying.getBlueprintId();
                        if (occupying.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                            plugin.getTownyHook().tagPlotAsBuild(loc, "Стройка: " + name);
                        } else {
                            plugin.getTownyHook().tagPlotAsBuild(loc, name);
                        }
                    } else {
                        plugin.getTownyHook().tagPlotAsBuild(loc, "Стройплощадка");
                    }
                }
            }
        }
    }

    public void demolishBuilding(ActiveBuilding bld) {
        plugin.getHologramDisplayManager().clearHologramsForBuilding(bld.getInstanceId());
        activeBuildings.remove(bld.getInstanceId());
        
        BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
        if (bp != null && bp.isWorldWonder()) {
            bp.setWonderCompletedByTown(null);
            if (dataConfig != null) {
                dataConfig.set("wonders." + bp.getId(), null);
            }
        }
        
        for (ChunkCoord cc : bld.getAssignedChunks()) {
            Location loc = new Location(Bukkit.getWorld(bld.getWorldName()), cc.getX() << 4, 70, cc.getZ() << 4);
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

    public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk) {
        return findFreePlotArea(townName, worldName, widthChunks, lengthChunks, preferredChunk, 0.0f);
    }

    public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk, float playerYaw) {
        if (preferredChunk == null) return null;
        Set<ChunkCoord> allPlots = getTownBuildPlots(townName);
        if (allPlots.isEmpty()) return null;

        Set<ChunkCoord> freePlots = new HashSet<>();
        for (ChunkCoord c : allPlots) {
            if (c.getWorldName().equals(worldName) && !isChunkOccupiedByBuilding(c)) {
                freePlots.add(c);
            }
        }
        // STRICT: preferredChunk (where the player stands) MUST be a free plot!
        if (!freePlots.contains(preferredChunk)) return null;

        float normYaw = (playerYaw % 360 + 360) % 360;
        boolean facingX = (normYaw >= 45 && normYaw < 135) || (normYaw >= 225 && normYaw < 315);

        int maxChunkDim = Math.max(widthChunks, lengthChunks);
        int minChunkDim = Math.min(widthChunks, lengthChunks);

        int[][] orientations;
        if (widthChunks == lengthChunks) {
            orientations = new int[][]{{widthChunks, lengthChunks}};
        } else if (facingX) {
            orientations = new int[][]{{maxChunkDim, minChunkDim}, {minChunkDim, maxChunkDim}};
        } else {
            orientations = new int[][]{{minChunkDim, maxChunkDim}, {maxChunkDim, minChunkDim}};
        }

        // STRICT: Collect all valid candidate rectangles containing preferredChunk, sort by distance to preferredChunk
        List<CandidateArea> candidates = new ArrayList<>();
        for (int[] dim : orientations) {
            int w = dim[0];
            int l = dim[1];
            for (int dx = 0; dx < w; dx++) {
                for (int dz = 0; dz < l; dz++) {
                    int originX = preferredChunk.getX() - dx;
                    int originZ = preferredChunk.getZ() - dz;
                    Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, originX, originZ, w, l);
                    if (candidate != null) {
                        double centerX = originX + (w - 1) / 2.0;
                        double centerZ = originZ + (l - 1) / 2.0;
                        double dist = Math.hypot(centerX - preferredChunk.getX(), centerZ - preferredChunk.getZ());
                        candidates.add(new CandidateArea(dist, candidate));
                    }
                }
            }
        }

        if (candidates.isEmpty()) return null;
        candidates.sort(Comparator.comparingDouble(a -> a.distance));
        return candidates.get(0).chunks;
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

    public static class TerrainFlatnessResult {
        public final boolean isFlat;
        public final int minGroundY;
        public final int maxGroundY;
        public final int suggestedGroundY;
        public final int difference;

        public TerrainFlatnessResult(boolean isFlat, int minGroundY, int maxGroundY, int suggestedGroundY, int difference) {
            this.isFlat = isFlat;
            this.minGroundY = minGroundY;
            this.maxGroundY = maxGroundY;
            this.suggestedGroundY = suggestedGroundY;
            this.difference = difference;
        }
    }

    public TerrainFlatnessResult checkFootprintFlatness(World world, int plotMinX, int plotMinZ, int plotWidth, int plotLength, int maxAllowedDiff) {
        int minGround = Integer.MAX_VALUE;
        int maxGround = Integer.MIN_VALUE;
        Map<Integer, Integer> heightFreq = new HashMap<>();

        for (int x = plotMinX; x < plotMinX + plotWidth; x += 2) {
            for (int z = plotMinZ; z < plotMinZ + plotLength; z += 2) {
                int highestY = world.getHighestBlockYAt(x, z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                int checkY = Math.min(highestY, 130);
                while (checkY >= Math.max(50, world.getMinHeight())) {
                    Material mat = world.getBlockAt(x, checkY, z).getType();
                    if (isNaturalTerrainMaterial(mat)) {
                        break;
                    }
                    checkY--;
                }
                if (checkY >= 50) {
                    if (checkY < minGround) minGround = checkY;
                    if (checkY > maxGround) maxGround = checkY;
                    heightFreq.put(checkY, heightFreq.getOrDefault(checkY, 0) + 1);
                }
            }
        }

        if (minGround == Integer.MAX_VALUE) {
            return new TerrainFlatnessResult(true, 64, 64, 65, 0);
        }

        int mostCommon = minGround;
        int maxCount = 0;
        for (Map.Entry<Integer, Integer> entry : heightFreq.entrySet()) {
            if (entry.getValue() > maxCount) {
                maxCount = entry.getValue();
                mostCommon = entry.getKey();
            }
        }

        int diff = maxGround - minGround;
        // Allow up to 5 blocks variation for natural terrain micro-relief (prevent false positives on flat plots)
        boolean isFlat = diff <= Math.max(maxAllowedDiff, 5);
        return new TerrainFlatnessResult(isFlat, minGround, maxGround, mostCommon + 1, diff);
    }

    public ActiveBuilding startBuilding(Player player, BuildingBlueprint bp) {
        String townName = plugin.getTownyHook().getPlayerTownName(player);
        if (townName == null) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cВы должны состоять в городе для возведения построек!"));
            return null;
        }

        if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player)) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cТолько мэр или помощник города могут утверждать строительные проекты!"));
            return null;
        }

        if (plugin.getConfig().getBoolean("settings.enforce-skill-level", true)) {
            int level = plugin.getArchitectManager().getLevel(player);
            if (level < bp.getRequiredSkillLevel()) {
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&cВаш уровень Архитектора (" + level + 
                        ") недостаточен для этого чертежа! Требуется минимум: " + bp.getRequiredSkillLevel()));
                return null;
            }
        }

        if (bp.isWorldWonder() && bp.getWonderCompletedByTown() != null) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&4[!] Это Чудо Света уже воздвигнуто городом «" + 
                    bp.getWonderCompletedByTown() + "» и заблокировано навсегда!"));
            return null;
        }

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

        boolean isWall = bp.getId().equalsIgnoreCase("city_wall");
        int maxAllowed = isWall ? 999 : 1;
        if (sameBlueprintCount >= maxAllowed) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cВаш город уже возвел здание «" + bp.getNameRu() + "»! (Лимит: " + maxAllowed + ")"));
            return null;
        }

        ChunkCoord playerChunk = ChunkCoord.fromLocation(player.getLocation());
        Set<ChunkCoord> assignedChunks = findFreePlotArea(
                townName,
                player.getWorld().getName(),
                bp.getChunkWidth(),
                bp.getChunkLength(),
                playerChunk,
                player.getLocation().getYaw()
        );

        if (assignedChunks == null || assignedChunks.isEmpty() || !assignedChunks.contains(playerChunk)) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Ошибка размещения: Постройка должна в обязательном порядке включать чанк [" + playerChunk.getX() + "," + playerChunk.getZ() + "], на котором вы стоите!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&eУбедитесь, что текущий чанк назначен через &f/plot set build&e и свободен."));
            return null;
        }

        World world = player.getWorld();
        int minChunkX = Integer.MAX_VALUE;
        int maxChunkX = Integer.MIN_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        int maxChunkZ = Integer.MIN_VALUE;
        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getX() > maxChunkX) maxChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
            if (cc.getZ() > maxChunkZ) maxChunkZ = cc.getZ();
        }
        int spanX = (maxChunkX - minChunkX + 1);
        int spanZ = (maxChunkZ - minChunkZ + 1);

        // 1. Calculate natural terrain ground level (never roof!)
        int terrainGroundY = calculateTerrainGroundY(world, assignedChunks);
        if (terrainGroundY < 50) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Защита от бункеров: Постройка не может быть заложена под землей (Y < 50)! Все здания должны возводиться на поверхности мира."));
            return null;
        }

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bp.getId());

        int rotationDeg = 0;
        float normYaw = (player.getLocation().getYaw() % 360 + 360) % 360;
        if (bp.getChunkWidth() != bp.getChunkLength()) {
            if (spanX > spanZ) {
                // Horizontal 2x1 plot (spanX = 2, spanZ = 1):
                // Unrotated schematic has width 32 (X) and length 16 (Z).
                // 0° and 180° rotations align with horizontal plot.
                rotationDeg = (normYaw >= 45 && normYaw < 225) ? 180 : 0;
            } else {
                // Vertical 1x2 plot (spanX = 1, spanZ = 2):
                // 90° and 270° rotations rotate the schematic to width 16 (X) and length 32 (Z).
                rotationDeg = (normYaw >= 135 && normYaw < 315) ? 270 : 90;
            }
        } else {
            // Square 1x1 or 2x2: align with facing quadrant
            if (normYaw >= 45 && normYaw < 135) rotationDeg = 90;
            else if (normYaw >= 135 && normYaw < 225) rotationDeg = 180;
            else if (normYaw >= 225 && normYaw < 315) rotationDeg = 270;
            else rotationDeg = 0;
        }

        ExistingStageAlignment alignment = null;
        if (schem != null) {
            alignment = detectExistingConstruction(schem, world, assignedChunks);
        }

        int schemW = schem != null ? schem.getWidthX() : (bp.getChunkWidth() * 16);
        int schemL = schem != null ? schem.getLengthZ() : (bp.getChunkLength() * 16);

        int totalPlotWidthPx = spanX * 16;
        int totalPlotLengthPx = spanZ * 16;

        boolean isFullyConstructed = false;
        boolean isPartiallyConstructed = false;

        int originX;
        int originY;
        int originZ;

        if (alignment != null && schem != null && alignment.matchedBlocksCount >= Math.max(12, (int) (schem.getBlocksAtLayer(0).size() * 0.40))) {
            // Auto-detected player-built partial or full structure!
            originX = alignment.matchedOriginX;
            originY = alignment.matchedOriginY;
            originZ = alignment.matchedOriginZ;
            rotationDeg = alignment.rotationDeg;
            if (alignment.isFullyBuilt) {
                isFullyConstructed = true;
            } else {
                isPartiallyConstructed = true;
            }
        } else {
            // Fresh clean plot
            int effectiveW = (rotationDeg == 90 || rotationDeg == 270) ? schemL : schemW;
            int effectiveL = (rotationDeg == 90 || rotationDeg == 270) ? schemW : schemL;
            originX = minChunkX * 16 + Math.max(0, (totalPlotWidthPx - effectiveW) / 2);
            originY = terrainGroundY;
            originZ = minChunkZ * 16 + Math.max(0, (totalPlotLengthPx - effectiveL) / 2);
        }

                // 2. Check flat ground requirement for fresh plots so no blocks are buried underground
        if (!isFullyConstructed && !isPartiallyConstructed && plugin.getConfig().getBoolean("settings.require-flat-plot", true)) {
            int maxDiff = plugin.getConfig().getInt("settings.max-allowed-height-diff", 1);
            TerrainFlatnessResult flatness = checkFootprintFlatness(world, minChunkX * 16, minChunkZ * 16, totalPlotWidthPx, totalPlotLengthPx, maxDiff);
            if (!flatness.isFlat) {
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&c[!] Строительная площадка не выровнена!"));
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&eРазница высот рельефа на участке: &6" + flatness.difference + " бл. &e(от Y=&f" + flatness.minGroundY + " &eдо Y=&f" + flatness.maxGroundY + "&e)"));
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&aРекомендация: &eРазровняйте поверхность площадки (на уровень &fY=" + (flatness.suggestedGroundY - 1) + "&e или любой желаемый уровень Y)."));
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&7(Ровная площадка гарантирует, что все блоки чертежа будут видны на поверхности)."));
                return null;
            }
        }

        // 3. Wall and Roof air contact constraint: exterior walls and roof must touch air >= 50%
        if (schem != null && schem.getExteriorFaceCount() > 0) {
            double initialExposure = checkTerrainWallExposure(schem, world, originX, originY, originZ, rotationDeg);
            if (initialExposure < 50.0) {
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&c[!] Ограничение планировки: Стены и крыша здания замурованы в ландшафт / защитную оболочку!"));
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&cПо чертежу открытость стен и крыши воздуху составит лишь &e" + 
                        String.format("%.1f", initialExposure) + "% &c(требуется минимум 50%)."));
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&cЗдания должны контактировать с воздухом (городская застройка), а не прятаться в бункерах или обстраиваться защитными оболочками снаружи!"));
                return null;
            }
        }

        Map<Material, Integer> req = (schem != null) ? schem.getTotalMaterials() : bp.getResources();
        String instanceId = "bld-" + bp.getId() + "-" + System.currentTimeMillis();
        ActiveBuilding building = new ActiveBuilding(
                instanceId,
                bp.getId(),
                townName,
                player.getUniqueId(),
                player.getWorld().getName(),
                assignedChunks,
                req,
                originX,
                originY,
                originZ
        );
        building.setRotationDeg(rotationDeg);

        if (isFullyConstructed) {
            for (Map.Entry<Material, Integer> entry : req.entrySet()) {
                building.setPlacedCount(entry.getKey(), entry.getValue());
            }
            if (schem != null) {
                for (SchematicBlock sb : schem.getBlocks()) {
                    building.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                }
                building.setCurrentLayer(schem.getMaxLayer() + 1);
            }
            building.setStatus(ActiveBuilding.Status.ACTIVE);
            activeBuildings.put(instanceId, building);
            completeBuilding(building, bp, player);
            saveData();

            for (ChunkCoord cc : assignedChunks) {
                Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
                plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "Постройка: " + bp.getNameRu() + " (Завершена)");
            }

            for (Player p : Bukkit.getOnlinePlayers()) {
                String pTown = plugin.getTownyHook().getPlayerTownName(p);
                if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&a[!] Мэр утвердил проект «&6" + bp.getNameRu() + 
                            "&a». Постройка уже &eна 100% физически возведена &aна участке!"));
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&6✦ Здание введено в строй! Город получил все бонусы и пассивные эффекты."));
                    p.playSound(p.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.0f, 1.0f);
                }
            }
            return building;
        }

        if (isPartiallyConstructed && alignment != null && schem != null) {
            applyExistingStageBlocks(building, schem, alignment);
            activeBuildings.put(instanceId, building);
            saveData();

            for (ChunkCoord cc : assignedChunks) {
                Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
                plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "В процессе постройки: " + bp.getNameRu());
            }

            for (Player p : Bukkit.getOnlinePlayers()) {
                String pTown = plugin.getTownyHook().getPlayerTownName(p);
                if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&a[!] Мэр утвердил проект «&6" + bp.getNameRu() + 
                            "&a». Обнаружена частично возведенная конструкция (&e" + building.getProgressPercent() + "%&a)!"));
                    p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&b✦ 3D-Чертеж автоматически повернут (" + rotationDeg + "°) и выровнен по высоте (Y=" + originY + 
                            "). Продолжайте возведение со Слоя " + (building.getCurrentLayer() + 1) + "!"));
                    p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.2f);
                }
            }

            plugin.getHologramDisplayManager().initHologramsForBuilding(building);
            return building;
        }

        // Clean fresh construction
        building.setCurrentLayer(0);
        building.setStatus(ActiveBuilding.Status.CONSTRUCTING);

        activeBuildings.put(instanceId, building);
        saveData();

        for (ChunkCoord cc : assignedChunks) {
            Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
            plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "В процессе постройки: " + bp.getNameRu());
        }

        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&a[!] Мэр утвердил проект «&6" + bp.getNameRu() + 
                        "&a». Город приступает к строительству!"));
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&e✦ Начните установку блоков фундамента (&fСлой 1&e) по 3D-голограммам чертежа."));
                p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.2f);
            }
        }

        plugin.getHologramDisplayManager().initHologramsForBuilding(building);
        return building;
    }

    public ActiveBuilding getBuildingAt(Location loc) {
        if (loc == null || loc.getWorld() == null) return null;
        ChunkCoord cc = ChunkCoord.fromLocation(loc);
        return getBuildingOccupyingChunk(cc);
    }

    /**
     * Checks if a block at a given location belongs to an active "city_wall" (Городская Стена)
     * building and is placed in its exact position according to the 3D blueprint schematic.
     */
    public boolean isProperCityWallBlock(Location loc) {
        if (loc == null || loc.getWorld() == null) return false;
        ActiveBuilding building = getBuildingAt(loc);
        if (building == null || !building.getBlueprintId().equalsIgnoreCase("city_wall")) {
            return false;
        }

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic("city_wall");
        if (schem == null) return false;

        int rx = loc.getBlockX() - building.getOriginX();
        int dy = loc.getBlockY() - building.getOriginY();
        int rz = loc.getBlockZ() - building.getOriginZ();

        int[] unrot = unrotateRelativeCoords(rx, rz, building.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
        int dx = unrot[0];
        int dz = unrot[1];

        SchematicBlock sb = schem.getBlock(dx, dy, dz);
        if (sb == null) return false;

        Material currentMat = loc.getBlock().getType();
        return currentMat == sb.getMaterial() || building.isBlockCompleted(dx, dy, dz);
    }

    public boolean handleBlockPlaced(Player player, Location loc, Material mat) {
        ActiveBuilding touchingBuilding = getBuildingAt(loc);
        if (touchingBuilding == null) {
            touchingBuilding = getBuildingTouching(loc);
        }
        if (touchingBuilding != null && wouldViolateWallExposure(touchingBuilding, loc, mat)) {
            double currentExp = calculateWallExposurePercent(touchingBuilding);
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Защита фасадов и крыши (v2): Нельзя замуровывать стены и крышу здания более чем на 50%!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cСтены зданий должны быть открыты воздуху, траве или зелени (городская застройка). Текущая открытость: &e" + 
                    String.format("%.1f", currentExp) + "%&c. Запрещено строить глухие бункерные оболочки вокруг постройки!"));
            player.playSound(loc, Sound.BLOCK_NOTE_BLOCK_BASS, 0.8f, 0.5f);
            return false;
        }

        ActiveBuilding building = getBuildingAt(loc);
        if (building == null) return true;

        BuildingBlueprint bp = blueprints.get(building.getBlueprintId());
        if (bp == null) return true;

        String playerTown = plugin.getTownyHook().getPlayerTownName(player);
        if (playerTown == null || !playerTown.equalsIgnoreCase(building.getTownName())) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Вы не состоите в городе «" + building.getTownName() + "»!");
            return false;
        }

        if (!plugin.getTownyHook().hasBuilderPermission(player, building.getTownName())) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Вы не назначены строителем мэром города!");
            return false;
        }

        if (plugin.getConfig().getBoolean("settings.enforce-skill-level", true)) {
            int level = plugin.getArchitectManager().getLevel(player);
            if (level < bp.getRequiredSkillLevel()) {
                player.sendMessage(ChatColor.RED + "[TownyArchitecture] Ваш уровень Архитектора (" + level + 
                        ") ниже требуемого (" + bp.getRequiredSkillLevel() + ") для чертежа «" + bp.getNameRu() + "»!");
                return false;
            }
        }

        // Check relative coordinates against 3D Schematic!
        int rx = loc.getBlockX() - building.getOriginX();
        int dy = loc.getBlockY() - building.getOriginY();
        int rz = loc.getBlockZ() - building.getOriginZ();

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(building.getBlueprintId());
        int[] unrot = (schem != null) ? unrotateRelativeCoords(rx, rz, building.getRotationDeg(), schem.getWidthX(), schem.getLengthZ()) : new int[]{rx, rz};
        int dx = unrot[0];
        int dz = unrot[1];
        if (schem != null) {
            SchematicBlock sb = schem.getBlock(dx, dy, dz);
            if (sb == null) {
                // Outside schematic cells can still occupy the current layer's footprint.
                // Refresh just this cell next tick (after Bukkit commits BlockPlaceEvent)
                // rather than waiting for the periodic full-layer watchdog scan.
                if (building.getStatus() == ActiveBuilding.Status.CONSTRUCTING
                        && dy == building.getCurrentLayer()) {
                    Location changedLoc = loc.clone();
                    Bukkit.getScheduler().runTask(plugin, () ->
                            plugin.getHologramDisplayManager().onWorldBlockChanged(building, changedLoc));
                }
                return true;
            }

            // If building is still constructing, check layer progression!
            if (building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                if (sb.getDy() > building.getCurrentLayer()) {
                    // Allow temporary scaffolding or ladders for climbing
                    if (mat == Material.SCAFFOLDING || mat == Material.LADDER) {
                        return true;
                    }
                    try {
                        player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                                new TextComponent("§b[!] Стройте послойно! Слой: §f" + (building.getCurrentLayer() + 1) + "§b. Завершите его!"));
                    } catch (Exception ignored) {}
                    player.playSound(loc, Sound.BLOCK_NOTE_BLOCK_BASS, 0.7f, 0.5f);
                    return false;
                }
            }

            if (!isMaterialMatch(mat, sb.getMaterial())) {
                // Wrong block placed!
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§c✖ Ошибка: Здесь по чертежу требуется §b" + RussianTranslator.getMaterialRu(sb.getMaterial())));
                } catch (Exception ignored) {}
                player.playSound(loc, Sound.BLOCK_NOTE_BLOCK_BASS, 0.7f, 0.5f);
                return false;
            }

            // Correct block matched!
            building.markBlockCompleted(dx, dy, dz);
            boolean layerAdvanced = plugin.getHologramDisplayManager().handleBlockPlaced(building, dx, dy, dz);
            if (layerAdvanced) {
                for (Player p : Bukkit.getOnlinePlayers()) {
                    String pTown = plugin.getTownyHook().getPlayerTownName(p);
                    if (pTown != null && pTown.equalsIgnoreCase(building.getTownName())) {
                        p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                plugin.getMsg("prefix") + "&a✦ Слой " + building.getCurrentLayer() + " завершен! Открыт &6Слой " + (building.getCurrentLayer() + 1) + "&a!"));
                    }
                }
            }
        }

        Material effectiveMat = mat;
        if (schem != null) {
            SchematicBlock sb = schem.getBlock(dx, dy, dz);
            if (sb != null) {
                effectiveMat = sb.getMaterial();
            }
        }

        building.addPlacedBlock(effectiveMat);
        if (schem != null) {
            building.syncPlacedMaterialsFromCompleted(schem);
        }

        // CASE A: Building is in construction
        if (building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
            int percent = (schem != null) ? building.getProgressPercent(schem) : building.getProgressPercent();

            try {
                if (schem != null) {
                    int cLayer = building.getCurrentLayer();
                    List<SchematicBlock> curLayerBlocks = schem.getBlocksAtLayer(cLayer);
                    int layerTotal = (curLayerBlocks != null) ? curLayerBlocks.size() : 0;
                    int layerPlaced = countCompletedBlocksInLayer(building, schem, cLayer);
                    int layerRem = Math.max(0, layerTotal - layerPlaced);

                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§a✔ +" + RussianTranslator.getShortMaterialRu(effectiveMat) + 
                                    " §8| §fСлой " + (cLayer + 1) + ": §e" + layerPlaced + "/" + layerTotal + 
                                    (layerRem > 0 ? " §8(Осталось: §c" + layerRem + "§8)" : " §a✔") + 
                                    " §8| §6Всего: §a" + percent + "%"));
                } else {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§a✔ +" + RussianTranslator.getShortMaterialRu(effectiveMat) + " §8(Слой " + (building.getCurrentLayer() + 1) + ") §8| §6Прогресс: §a" + percent + "%"));
                }
            } catch (Exception ignored) {}

            awardBuilderXp(player);
            playBuildEffects(loc, player);

            if (schem != null ? building.isFullyBuilt(schem) : building.isFullyBuilt()) {
                completeBuilding(building, bp, player);
            }

            saveData();
            return true;
        }

        // CASE B: Repairing damaged building
        int newCurrent = building.getPlacedCount(effectiveMat);
        int needed = building.getRequiredCount(effectiveMat);
        double newHealth = (schem != null) ? building.calculateHealthPercent(schem) : building.calculateHealthPercent();
        building.setHealthPercent(newHealth);

        double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);
        boolean fullyBuilt = (schem != null) ? building.isFullyBuilt(schem) : building.isFullyBuilt();

        if (fullyBuilt) {
            building.setHealthPercent(100.0);
            plugin.getHologramDisplayManager().clearHologramsForBuilding(building.getInstanceId());
            boolean wasDamaged = building.getStatus() == ActiveBuilding.Status.DAMAGED;
            building.setStatus(ActiveBuilding.Status.ACTIVE);
            if (wasDamaged) {
                for (Player p : Bukkit.getOnlinePlayers()) {
                    String town = plugin.getTownyHook().getPlayerTownName(p);
                    if (town != null && town.equalsIgnoreCase(building.getTownName())) {
                        p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                plugin.getMsg("prefix") + "&a✔ [ГОРОД] Здание «&e" + bp.getNameRu() + 
                                "&a» полностью восстановлено по чертежу! Баффы снова активны!"));
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

        awardBuilderXp(player);
        try {
            player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                    new TextComponent("§a✔ Восстановление блока схемы (" + newCurrent + "/" + needed + ") §8| §eПрочность: §a" + String.format("%.1f", newHealth) + "%"));
        } catch (Exception ignored) {}

        playBuildEffects(loc, player);
        saveData();
        return true;
    }

    public boolean handleBlockBroken(Player playerOrNull, Location loc, Material brokenMat) {
        ActiveBuilding building = getBuildingAt(loc);
        if (building == null) return true;

        if (playerOrNull != null) {
            String playerTown = plugin.getTownyHook().getPlayerTownName(playerOrNull);
            if (playerTown != null && playerTown.equalsIgnoreCase(building.getTownName())) {
                if (!plugin.getTownyHook().hasBuilderPermission(playerOrNull, building.getTownName())) {
                    playerOrNull.sendMessage(ChatColor.RED + "[TownyArchitecture] Вы не назначены строителем мэром города!");
                    return false;
                }
            }
        }

        int rx = loc.getBlockX() - building.getOriginX();
        int dy = loc.getBlockY() - building.getOriginY();
        int rz = loc.getBlockZ() - building.getOriginZ();

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(building.getBlueprintId());
        int[] unrot = (schem != null) ? unrotateRelativeCoords(rx, rz, building.getRotationDeg(), schem.getWidthX(), schem.getLengthZ()) : new int[]{rx, rz};
        int dx = unrot[0];
        int dz = unrot[1];
        SchematicBlock schemBlock = (schem != null) ? schem.getBlock(dx, dy, dz) : null;

        // CRITICAL CHECK FOR EXPLOSIONS & NON-PLAYER BREAKS:
        // If this event was triggered by an explosion/environmental check (playerOrNull == null),
        // verify whether the block at this location is ACTUALLY destroyed or if it survived (e.g. 2x blast resistance)!
        if (schemBlock != null && playerOrNull == null) {
            Material currentWorldMat = loc.getBlock().getType();
            if (isMaterialMatch(currentWorldMat, schemBlock.getMaterial())) {
                // The block is still intact in the world! Do NOT mark as broken, do NOT spawn blue holograms!
                building.markBlockCompleted(dx, dy, dz);
                return true;
            }
        }

        // КРИТИЧЕСКИЙ ФИЛЬТР: был ли этот блок реально построенным элементом здания?
        boolean wasBuildingCompletedBlock = building.isBlockCompleted(dx, dy, dz);

        if (!wasBuildingCompletedBlock) {
            // Player broke an obstacle or natural block at construction site: update hologram glow from Red to Blue
            Bukkit.getScheduler().runTask(plugin, () -> {
                plugin.getHologramDisplayManager().onWorldBlockChanged(building, loc);
            });
        }

        if (wasBuildingCompletedBlock && schemBlock != null) {
            building.markBlockBroken(dx, dy, dz);

            final int fDx = dx;
            final int fDy = dy;
            final int fDz = dz;
            final SchematicBlock fSb = schemBlock;
            final Location fLoc = loc.clone();
            Bukkit.getScheduler().runTask(plugin, () -> {
                building.markBlockBroken(fDx, fDy, fDz);
                if (fSb.getDy() <= building.getCurrentLayer() || building.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
                    plugin.getHologramDisplayManager().respawnHologramForMissingBlock(building, fDx, fDy, fDz, fSb.getMaterial());
                }
                plugin.getHologramDisplayManager().onWorldBlockChanged(building, fLoc);
            });

            Material targetMat = schemBlock.getMaterial();
            if (building.getRequiredMaterials().containsKey(targetMat)) {
                building.removePlacedBlock(targetMat);
            }
            if (schem != null) {
                building.syncPlacedMaterialsFromCompleted(schem);
            }

            int newCurrent = building.getPlacedCount(targetMat);
            int needed = building.getRequiredCount(targetMat);

            BuildingBlueprint bp = blueprints.get(building.getBlueprintId());
            String bpName = bp != null ? bp.getNameRu() : building.getBlueprintId();

            if (building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                int pct = (schem != null) ? building.getProgressPercent(schem) : building.getProgressPercent();
                if (playerOrNull != null) {
                    try {
                        playerOrNull.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                                new TextComponent("§c✖ -" + RussianTranslator.getShortMaterialRu(targetMat) + " (" + newCurrent + "/" + needed + ") §8| §6Прогресс: §c" + pct + "%"));
                    } catch (Exception ignored) {}
                }
            } else {
                double newHealth = (schem != null) ? building.calculateHealthPercent(schem) : building.calculateHealthPercent();
                building.setHealthPercent(newHealth);

                double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);
                if (newHealth < 100.0 && building.getStatus() == ActiveBuilding.Status.ACTIVE) {
                    building.setStatus(ActiveBuilding.Status.DAMAGED);
                    if (newHealth < threshold) {
                        for (Player p : Bukkit.getOnlinePlayers()) {
                            String town = plugin.getTownyHook().getPlayerTownName(p);
                            if (town != null && town.equalsIgnoreCase(building.getTownName())) {
                                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                        plugin.getMsg("prefix") + "&c[!] Здание «&e" + bpName + 
                                        "&c» сильно повреждено! Прочность: &e" + 
                                        String.format("%.1f", newHealth) + "%&c. Баффы ОТКЛЮЧЕНЫ до ремонта!"));
                                p.playSound(p.getLocation(), Sound.ENTITY_WITHER_DEATH, 0.6f, 1.2f);
                            }
                        }
                    }
                }

                if (playerOrNull != null) {
                    try {
                        playerOrNull.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                                new TextComponent("§c✖ Разрушен блок схемы §8| §cПрочность: " + String.format("%.1f", newHealth) + "%"));
                    } catch (Exception ignored) {}
                }
            }

            saveData();
            return true;
        }

        // Если блок НЕ являлся частью здания (например, срубили дерево, траву, землю или временные леса):
        // 1. Прогресс здания не уменьшается!
        // 2. Если на этом месте на ТЕКУЩЕМ слое по схеме должен быть блок - гарантируем показ штатной голограммы чертежа!
        if (schemBlock != null && building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
            if (schemBlock.getDy() == building.getCurrentLayer()) {
                // Дерево или мешающий блок очищены на позиции текущего слоя -> спавним нормальную чистую голограмму схемы!
                plugin.getHologramDisplayManager().respawnHologramForMissingBlock(building, dx, dy, dz, schemBlock.getMaterial());
            }
            // Если же schemBlock.getDy() > building.getCurrentLayer():
            // Это будущий этаж постройки - ничего не спавним и никаких следов не оставляем!
        }

        return true;
    }




    /**
     * Regular watchdog monitoring & diagnostic audit:
     * - Scans constructing buildings, auto-reconciles placed blocks, advances layers, heals dead/missing holograms, and auto-completes finished buildings.
     * - Scans active buildings, calculates accurate rotated integrity, detects grief/damage, switches to DAMAGED with warning holograms.
     * - Detects repaired buildings and auto-restores them to ACTIVE with town buffs and fanfare.
     * - Checks exterior facade exposure to prevent buried bunkers (ENTOMBED).
     * - Commits validated state to disk, protecting against server crashes and desyncs.
     */
    public void performWatchdogAudit() {
        double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);

        for (ActiveBuilding bld : activeBuildings.values()) {
            World world = Bukkit.getWorld(bld.getWorldName());
            if (world == null) continue;

            BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
            if (schem == null) continue;

            int rot = bld.getRotationDeg();
            int wX = schem.getWidthX();
            int lZ = schem.getLengthZ();

            // Safety check: skip buildings whose chunks are not loaded during automated background runs to prevent TPS drops
            boolean anyChunkLoaded = false;
            if (bld.getAssignedChunks() != null && !bld.getAssignedChunks().isEmpty()) {
                for (ChunkCoord cc : bld.getAssignedChunks()) {
                    if (world.isChunkLoaded(cc.getX(), cc.getZ())) {
                        anyChunkLoaded = true;
                        break;
                    }
                }
            } else {
                anyChunkLoaded = world.isChunkLoaded(bld.getOriginX() >> 4, bld.getOriginZ() >> 4);
            }

            if (!anyChunkLoaded) {
                continue;
            }

            BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
            String bpName = bp != null ? bp.getNameRu() : bld.getBlueprintId();

            // 1. Handling for CONSTRUCTING buildings
            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {

                // A. Auto-reconcile physical blocks up to current layer
                int currentLayer = bld.getCurrentLayer();
                for (int l = 0; l <= currentLayer && l <= schem.getMaxLayer(); l++) {
                    List<SchematicBlock> lBlocks = schem.getBlocksAtLayer(l);
                    if (lBlocks == null) continue;

                    for (SchematicBlock sb : lBlocks) {
                        int[] rPos = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, wX, lZ);
                        int wx = bld.getOriginX() + rPos[0];
                        int wy = bld.getOriginY() + sb.getDy();
                        int wz = bld.getOriginZ() + rPos[1];

                        if (wy < world.getMinHeight() || wy >= world.getMaxHeight()) continue;
                        Material wm = world.getBlockAt(wx, wy, wz).getType();

                        if (isMaterialMatch(wm, sb.getMaterial())) {
                            if (!bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                                bld.addPlacedBlock(sb.getMaterial());
                            }
                        } else {
                            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                                bld.markBlockBroken(sb.getDx(), sb.getDy(), sb.getDz());
                                bld.removePlacedBlock(sb.getMaterial());
                            }
                        }
                    }
                }

                // B. Layer advance check
                boolean advanced = plugin.getHologramDisplayManager().checkAndAdvanceLayer(bld, schem, world);
                if (advanced) {
                }

                // C. Full completion check
                if (schem != null ? bld.isFullyBuilt(schem) : bld.isFullyBuilt()) {
                    completeBuilding(bld, bp, null);
                } else {
                    plugin.getHologramDisplayManager().healOrRefreshLayerHolograms(bld);
                }
            } 
            // 2. Handling for ACTIVE, DAMAGED, and ENTOMBED buildings
            else {
                int total = schem.getTotalBlockCount();
                int intact = 0;
                Map<Material, Integer> currentCounts = new HashMap<>();

                for (SchematicBlock sb : schem.getBlocks()) {
                    int[] rPos = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, wX, lZ);
                    int wx = bld.getOriginX() + rPos[0];
                    int wy = bld.getOriginY() + sb.getDy();
                    int wz = bld.getOriginZ() + rPos[1];

                    if (wy < world.getMinHeight() || wy >= world.getMaxHeight()) continue;
                    Material wm = world.getBlockAt(wx, wy, wz).getType();

                    if (isMaterialMatch(wm, sb.getMaterial())) {
                        intact++;
                        bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                        currentCounts.put(sb.getMaterial(), currentCounts.getOrDefault(sb.getMaterial(), 0) + 1);
                    } else {
                        bld.markBlockBroken(sb.getDx(), sb.getDy(), sb.getDz());
                        if (bld.getStatus() == ActiveBuilding.Status.DAMAGED || bld.getHealthPercent() < 100.0) {
                            plugin.getHologramDisplayManager().respawnHologramForMissingBlock(bld, sb.getDx(), sb.getDy(), sb.getDz(), sb.getMaterial());
                        }
                    }
                }

                for (Map.Entry<Material, Integer> e : bld.getRequiredMaterials().entrySet()) {
                    bld.setPlacedCount(e.getKey(), currentCounts.getOrDefault(e.getKey(), 0));
                }

                double health = (total > 0) ? ((double) intact / total) * 100.0 : 100.0;
                bld.setHealthPercent(health);

                double exposure = calculateWallExposurePercent(bld);

                if (exposure < 50.0) {
                    if (bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
                        bld.setStatus(ActiveBuilding.Status.ENTOMBED);
                        for (Player p : Bukkit.getOnlinePlayers()) {
                            String town = plugin.getTownyHook().getPlayerTownName(p);
                            if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                        plugin.getMsg("prefix") + "&c[!] Фасады постройки «&e" + bpName + 
                                        "&c» замурованы/засыпаны (< 50% открытости: &e" + String.format("%.1f", exposure) + 
                                        "%&c)! Баффы отключены до расчистки стен."));
                                p.playSound(p.getLocation(), Sound.BLOCK_ANVIL_LAND, 0.6f, 0.8f);
                            }
                        }
                    }
                } else if (bld.getStatus() == ActiveBuilding.Status.ENTOMBED) {
                    if (health >= threshold) {
                        bld.setStatus(ActiveBuilding.Status.ACTIVE);
                        for (Player p : Bukkit.getOnlinePlayers()) {
                            String town = plugin.getTownyHook().getPlayerTownName(p);
                            if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                        plugin.getMsg("prefix") + "&a[✔] Фасады постройки «&e" + bpName + 
                                        "&a» снова открыты (" + String.format("%.1f", exposure) + "% >= 50%)! Баффы города восстановлены."));
                                p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 0.8f, 1.2f);
                            }
                        }
                    }
                } else if (health < 100.0 && bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
                    bld.setStatus(ActiveBuilding.Status.DAMAGED);
                    if (health < threshold) {
                        for (Player p : Bukkit.getOnlinePlayers()) {
                            String town = plugin.getTownyHook().getPlayerTownName(p);
                            if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                        plugin.getMsg("prefix") + "&c[⚠] Постройка «&e" + bpName + 
                                        "&c» повреждена (&e" + String.format("%.1f", health) + 
                                        "%&c < " + threshold + "%)! Баффы отключены до починки."));
                                p.playSound(p.getLocation(), Sound.BLOCK_ANVIL_LAND, 0.8f, 0.7f);
                            }
                        }
                    }
                } else if (health >= 100.0 && bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                    bld.setStatus(ActiveBuilding.Status.ACTIVE);
                    plugin.getHologramDisplayManager().clearHologramsForBuilding(bld.getInstanceId());
                    for (Player p : Bukkit.getOnlinePlayers()) {
                        String town = plugin.getTownyHook().getPlayerTownName(p);
                        if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                            p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                    plugin.getMsg("prefix") + "&a[✔] Постройка «&e" + bpName + 
                                    "&a» полностью восстановлена (&e100%&a)! Баффы города возобновлены."));
                            p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 0.9f, 1.2f);
                        }
                    }
                }
            }
        }

        saveData();
    }

    public void performPeriodicIntegrityCheck() {
        performWatchdogAudit();
    }

    /**
     * Admin command: Complete scan and recalculation of all buildings, blocks in world,
     * physical durability, wall exposures, town chunk ownership and limits.
     */
    public Map<String, Object> performFullRecalculation(CommandSender sender) {
        Map<String, Object> stats = new LinkedHashMap<>();
        int totalBuildings = activeBuildings.size();
        int activeCount = 0;
        int constructingCount = 0;
        int damagedCount = 0;
        int entombedCount = 0;
        int transferredCount = 0;
        int unlinkedFromDeletedTown = 0;
        int completedConstructing = 0;
        int restoredToActive = 0;
        int chunksForceLoaded = 0;
        Set<String> affectedTowns = new HashSet<>();

        double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);

        for (ActiveBuilding bld : new ArrayList<>(activeBuildings.values())) {
            World world = Bukkit.getWorld(bld.getWorldName());
            if (world == null) continue;

            // 1. Force load origin chunk & assigned chunks for physical scan
            int ocx = bld.getOriginX() >> 4;
            int ocz = bld.getOriginZ() >> 4;
            if (!world.isChunkLoaded(ocx, ocz)) {
                world.loadChunk(ocx, ocz, false);
                chunksForceLoaded++;
            }
            if (bld.getAssignedChunks() != null) {
                for (ChunkCoord cc : bld.getAssignedChunks()) {
                    if (!world.isChunkLoaded(cc.getX(), cc.getZ())) {
                        world.loadChunk(cc.getX(), cc.getZ(), false);
                        chunksForceLoaded++;
                    }
                }
            }

            // 2. Validate current town ownership in world
            Location originLoc = new Location(world, bld.getOriginX(), bld.getOriginY(), bld.getOriginZ());
            String townInWorld = plugin.getTownyHook().getTownName(originLoc);
            String oldTown = bld.getTownName();

            if (townInWorld != null) {
                if (!townInWorld.equalsIgnoreCase(oldTown)) {
                    bld.setTownName(townInWorld);
                    if (oldTown != null) {
                        Set<ChunkCoord> oldPlots = townBuildPlots.get(oldTown.toLowerCase());
                        if (oldPlots != null && bld.getAssignedChunks() != null) {
                            oldPlots.removeAll(bld.getAssignedChunks());
                        }
                    }
                    Set<ChunkCoord> newPlots = townBuildPlots.computeIfAbsent(townInWorld.toLowerCase(), k -> new HashSet<>());
                    if (bld.getAssignedChunks() != null) {
                        newPlots.addAll(bld.getAssignedChunks());
                    }
                    transferredCount++;
                }
                affectedTowns.add(townInWorld.toLowerCase());
            } else {
                if (!plugin.getTownyHook().townExists(oldTown)) {
                    deactivateBuildingDueToLimit(bld);
                    unlinkedFromDeletedTown++;
                }
                if (oldTown != null) {
                    affectedTowns.add(oldTown.toLowerCase());
                }
            }

            // 3. Physical Schematic & Durability Recalculation
            BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
            if (schem == null) continue;

            int rot = bld.getRotationDeg();
            int wX = schem.getWidthX();
            int lZ = schem.getLengthZ();
            BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());

            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                int maxL = schem.getMaxLayer();
                for (int l = 0; l <= maxL; l++) {
                    List<SchematicBlock> lBlocks = schem.getBlocksAtLayer(l);
                    if (lBlocks == null) continue;
                    for (SchematicBlock sb : lBlocks) {
                        int[] rPos = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, wX, lZ);
                        int wx = bld.getOriginX() + rPos[0];
                        int wy = bld.getOriginY() + sb.getDy();
                        int wz = bld.getOriginZ() + rPos[1];
                        if (wy < world.getMinHeight() || wy >= world.getMaxHeight()) continue;
                        Material wm = world.getBlockAt(wx, wy, wz).getType();
                        if (isMaterialMatch(wm, sb.getMaterial())) {
                            bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                            bld.addPlacedBlock(sb.getMaterial());
                        } else {
                            bld.markBlockBroken(sb.getDx(), sb.getDy(), sb.getDz());
                            bld.removePlacedBlock(sb.getMaterial());
                        }
                    }
                }
                plugin.getHologramDisplayManager().checkAndAdvanceLayer(bld, schem, world);
                if (bld.isFullyBuilt(schem)) {
                    completeBuilding(bld, bp, null);
                    completedConstructing++;
                    activeCount++;
                } else {
                    plugin.getHologramDisplayManager().healOrRefreshLayerHolograms(bld);
                    constructingCount++;
                }
            } else {
                int total = schem.getTotalBlockCount();
                int intact = 0;
                Map<Material, Integer> currentCounts = new HashMap<>();

                for (SchematicBlock sb : schem.getBlocks()) {
                    int[] rPos = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, wX, lZ);
                    int wx = bld.getOriginX() + rPos[0];
                    int wy = bld.getOriginY() + sb.getDy();
                    int wz = bld.getOriginZ() + rPos[1];
                    if (wy < world.getMinHeight() || wy >= world.getMaxHeight()) continue;
                    Material wm = world.getBlockAt(wx, wy, wz).getType();
                    if (isMaterialMatch(wm, sb.getMaterial())) {
                        intact++;
                        bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                        currentCounts.put(sb.getMaterial(), currentCounts.getOrDefault(sb.getMaterial(), 0) + 1);
                    } else {
                        bld.markBlockBroken(sb.getDx(), sb.getDy(), sb.getDz());
                    }
                }

                for (Map.Entry<Material, Integer> e : bld.getRequiredMaterials().entrySet()) {
                    bld.setPlacedCount(e.getKey(), currentCounts.getOrDefault(e.getKey(), 0));
                }

                double health = (total > 0) ? ((double) intact / total) * 100.0 : 100.0;
                bld.setHealthPercent(health);

                double exposure = calculateWallExposurePercent(bld);

                if (exposure < 50.0) {
                    bld.setStatus(ActiveBuilding.Status.ENTOMBED);
                    entombedCount++;
                } else if (health < threshold) {
                    bld.setStatus(ActiveBuilding.Status.DAMAGED);
                    damagedCount++;
                    plugin.getHologramDisplayManager().initHologramsForBuilding(bld);
                } else {
                    if (bld.getStatus() == ActiveBuilding.Status.DAMAGED || bld.getStatus() == ActiveBuilding.Status.ENTOMBED) {
                        restoredToActive++;
                    }
                    bld.setStatus(ActiveBuilding.Status.ACTIVE);
                    plugin.getHologramDisplayManager().clearHologramsForBuilding(bld.getInstanceId());
                    activeCount++;
                }
            }
        }

        // 4. Enforce limits for all affected towns
        for (String town : affectedTowns) {
            recalculateAndEnforceBuildingLimits(town, null);
        }

        // 5. Reapply town buffs
        plugin.getBuffManager().applyBuffs();

        // 6. Save data
        saveData();

        stats.put("totalBuildings", totalBuildings);
        stats.put("activeCount", activeCount);
        stats.put("constructingCount", constructingCount);
        stats.put("damagedCount", damagedCount);
        stats.put("entombedCount", entombedCount);
        stats.put("transferredCount", transferredCount);
        stats.put("unlinkedFromDeletedTown", unlinkedFromDeletedTown);
        stats.put("completedConstructing", completedConstructing);
        stats.put("restoredToActive", restoredToActive);
        stats.put("chunksForceLoaded", chunksForceLoaded);
        stats.put("affectedTownsCount", affectedTowns.size());

        return stats;
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
        plugin.getHologramDisplayManager().clearHologramsForBuilding(building.getInstanceId());

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
                        plugin.getMsg("prefix") + "&6&l[ГОРОД]&a Строительство по схеме «&e" + bp.getNameRu() + 
                        "&a» завершено на 100%! Все баффы активированы!"));
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

    public static boolean isNaturalOpenBlock(Material mat) {
        if (mat == null || mat.isAir()) return true;
        String name = mat.name();
        if (name.endsWith("_LEAVES") || name.endsWith("_SAPLING") || name.endsWith("_FLOWER") 
                || name.contains("GRASS") || name.contains("FERN") || name.contains("VINE")
                || name.contains("MOSS") || name.contains("LICHEN") || name.contains("ROOTS")
                || name.contains("MUSHROOM") || name.contains("FUNGUS") || name.contains("CORAL")
                || name.contains("LANTERN") || name.contains("TORCH") || name.contains("CHAIN")
                || name.contains("CARPET") || name.contains("SNOW") || name.contains("WATER")
                || name.contains("PATH") || name.equals("FARMLAND") || name.contains("BANNER")
                || name.contains("SIGN") || name.contains("HANGING_SIGN") || name.contains("CAMPFIRE")
                || name.contains("PRESSURE_PLATE") || name.contains("BUTTON") || name.contains("LEVER")) {
            return true;
        }
        return false;
    }

    public ActiveBuilding getBuildingTouching(Location loc) {
        if (loc == null || loc.getWorld() == null) return null;
        int x = loc.getBlockX();
        int y = loc.getBlockY();
        int z = loc.getBlockZ();
        String world = loc.getWorld().getName();

        for (ActiveBuilding bld : activeBuildings.values()) {
            if (!bld.getWorldName().equalsIgnoreCase(world)) continue;
            BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
            int w = schem != null ? schem.getWidthX() : 16;
            int h = schem != null ? schem.getHeightY() : 16;
            int l = schem != null ? schem.getLengthZ() : 16;

            if (x >= bld.getOriginX() - 1 && x <= bld.getOriginX() + w &&
                z >= bld.getOriginZ() - 1 && z <= bld.getOriginZ() + l &&
                y >= bld.getOriginY() && y <= bld.getOriginY() + h + 1) {
                return bld;
            }
        }
        return null;
    }

    public double calculateWallExposurePercent(ActiveBuilding bld) {
        if (bld == null) return 100.0;
        World world = Bukkit.getWorld(bld.getWorldName());
        if (world == null) return 100.0;

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null || schem.getExteriorFaceCount() == 0) {
            bld.setExteriorExposurePercent(100.0);
            return 100.0;
        }

        int totalFaces = schem.getExteriorFaceCount();
        int openFaces = 0;
        int rot = bld.getRotationDeg();

        for (BuildingSchematic.ExteriorFace face : schem.getExteriorFaces()) {
            int[] rPos = rotateRelativeCoords(face.getDx(), face.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
            int[] rDir = rotateDirection(face.getOx(), face.getOz(), rot);

            int wx = bld.getOriginX() + rPos[0] + rDir[0];
            int wy = bld.getOriginY() + face.getDy() + face.getOy();
            int wz = bld.getOriginZ() + rPos[1] + rDir[1];

            Material mat = world.getBlockAt(wx, wy, wz).getType();
            if (isNaturalOpenBlock(mat)) {
                openFaces++;
            }
        }

        double percent = ((double) openFaces / totalFaces) * 100.0;
        bld.setExteriorExposurePercent(percent);
        return percent;
    }

    public double checkTerrainWallExposure(BuildingSchematic schem, World world, int originX, int originY, int originZ, int rot) {
        if (schem == null || schem.getExteriorFaceCount() == 0 || world == null) return 100.0;
        int totalFaces = 0;
        int openFaces = 0;
        for (BuildingSchematic.ExteriorFace face : schem.getExteriorFaces()) {
            // Foundation bottom/sides at dy=0 rest on terrain; check dy >= 1 (walls & roof)
            if (face.getDy() == 0 && face.getOy() <= 0) {
                continue;
            }
            totalFaces++;
            int[] rPos = rotateRelativeCoords(face.getDx(), face.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
            int[] rDir = rotateDirection(face.getOx(), face.getOz(), rot);
            int wx = originX + rPos[0] + rDir[0];
            int wy = originY + face.getDy() + face.getOy();
            int wz = originZ + rPos[1] + rDir[1];
            Material mat = world.getBlockAt(wx, wy, wz).getType();
            if (isNaturalOpenBlock(mat)) {
                openFaces++;
            }
        }
        if (totalFaces == 0) return 100.0;
        return ((double) openFaces / totalFaces) * 100.0;
    }

    public boolean wouldViolateWallExposure(ActiveBuilding bld, Location placeLoc, Material placedMat) {
        if (isNaturalOpenBlock(placedMat)) return false;

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null || schem.getExteriorFaceCount() == 0) return false;

        World world = Bukkit.getWorld(bld.getWorldName());
        if (world == null) return false;

        int px = placeLoc.getBlockX();
        int py = placeLoc.getBlockY();
        int pz = placeLoc.getBlockZ();

        int totalFaces = schem.getExteriorFaceCount();
        int openFaces = 0;
        boolean faceAffected = false;
        int rot = bld.getRotationDeg();

        for (BuildingSchematic.ExteriorFace face : schem.getExteriorFaces()) {
            int[] rPos = rotateRelativeCoords(face.getDx(), face.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
            int[] rDir = rotateDirection(face.getOx(), face.getOz(), rot);

            int wx = bld.getOriginX() + rPos[0] + rDir[0];
            int wy = bld.getOriginY() + face.getDy() + face.getOy();
            int wz = bld.getOriginZ() + rPos[1] + rDir[1];

            if (wx == px && wy == py && wz == pz) {
                faceAffected = true;
            } else {
                Material mat = world.getBlockAt(wx, wy, wz).getType();
                if (isNaturalOpenBlock(mat)) {
                    openFaces++;
                }
            }
        }

        if (!faceAffected) {
            return false;
        }

        double newPercent = ((double) openFaces / totalFaces) * 100.0;
        return newPercent < 50.0;
    }

    public Collection<BuildingBlueprint> getBlueprints() { return blueprints.values(); }
    public BuildingBlueprint getBlueprint(String id) { return blueprints.get(id); }
    public Collection<ActiveBuilding> getActiveBuildings() { return activeBuildings.values(); }

    /**
     * Результат сканирования территории участка на предмет уже построенных этапов/слоев схемы.
     */
    public static class ExistingStageAlignment {
        public final int matchedOriginX;
        public final int matchedOriginY;
        public final int matchedOriginZ;
        public final int rotationDeg;
        public final int completedLayersCount;
        public final int matchedBlocksCount;
        public final Set<String> matchedBlockKeys;
        public final boolean isFullyBuilt;

        public ExistingStageAlignment(int originX, int originY, int originZ, int rotationDeg, int completedLayers, int matchedBlocks, Set<String> matchedKeys, boolean isFullyBuilt) {
            this.matchedOriginX = originX;
            this.matchedOriginY = originY;
            this.matchedOriginZ = originZ;
            this.rotationDeg = rotationDeg;
            this.completedLayersCount = completedLayers;
            this.matchedBlocksCount = matchedBlocks;
            this.matchedBlockKeys = matchedKeys;
            this.isFullyBuilt = isFullyBuilt;
        }
    }

        public ExistingStageAlignment detectExistingConstruction(BuildingSchematic schem, World world, Set<ChunkCoord> assignedChunks) {
        if (schem == null || world == null || assignedChunks == null || assignedChunks.isEmpty()) {
            return null;
        }

        int minChunkX = Integer.MAX_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        int maxChunkX = Integer.MIN_VALUE;
        int maxChunkZ = Integer.MIN_VALUE;

        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
            if (cc.getX() > maxChunkX) maxChunkX = cc.getX();
            if (cc.getZ() > maxChunkZ) maxChunkZ = cc.getZ();
        }

        int plotMinX = minChunkX * 16;
        int plotMinZ = minChunkZ * 16;
        int plotMaxX = (maxChunkX + 1) * 16;
        int plotMaxZ = (maxChunkZ + 1) * 16;

        int plotWidth = plotMaxX - plotMinX;
        int plotLength = plotMaxZ - plotMinZ;

        List<SchematicBlock> allBlocks = schem.getBlocks();
        if (allBlocks.isEmpty()) return null;

        List<SchematicBlock> layer0Blocks = schem.getBlocksAtLayer(0);
        if (layer0Blocks.isEmpty()) return null;

        int terrainGroundY = calculateTerrainGroundY(world, assignedChunks);
        int highestPlotY = Integer.MIN_VALUE;
        int lowestPlotY = Integer.MAX_VALUE;
        for (ChunkCoord cc : assignedChunks) {
            int cx = cc.getX() << 4;
            int cz = cc.getZ() << 4;
            for (int x = 0; x < 16; x += 4) {
                for (int z = 0; z < 16; z += 4) {
                    int h = world.getHighestBlockYAt(cx + x, cz + z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                    if (h > highestPlotY) highestPlotY = h;
                    if (h < lowestPlotY) lowestPlotY = h;
                }
            }
        }
        if (highestPlotY == Integer.MIN_VALUE) highestPlotY = terrainGroundY;
        if (lowestPlotY == Integer.MAX_VALUE) lowestPlotY = terrainGroundY;

        // Search Y range covering natural terrain ground and any potential foundation:
        int minY = Math.max(world.getMinHeight() + 1, Math.min(terrainGroundY - 3, lowestPlotY - 1));
        int maxY = Math.min(world.getMaxHeight() - schem.getHeightY(), Math.max(terrainGroundY + 3, highestPlotY - schem.getHeightY() + 2));

        int[] rotations = {0, 90, 180, 270};
        ExistingStageAlignment bestAlignment = null;
        int bestMatchedCount = 0;
        int bestLayersWithMatches = 0;
        int bestCompletedLayers = 0;

        for (int rot : rotations) {
            int effW = (rot == 90 || rot == 270) ? schem.getLengthZ() : schem.getWidthX();
            int effL = (rot == 90 || rot == 270) ? schem.getWidthX() : schem.getLengthZ();

            int maxOffsetX = plotWidth - effW;
            int maxOffsetZ = plotLength - effL;
            if (maxOffsetX < 0 || maxOffsetZ < 0) continue;

            for (int offX = 0; offX <= maxOffsetX; offX++) {
                int testOriginX = plotMinX + offX;
                for (int offZ = 0; offZ <= maxOffsetZ; offZ++) {
                    int testOriginZ = plotMinZ + offZ;

                    for (int testOriginY = minY; testOriginY <= maxY; testOriginY++) {
                        // 1. Strict Layer 0 Check: A real building MUST start with the foundation!
                        int layer0Matched = 0;
                        for (SchematicBlock sb : layer0Blocks) {
                            int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                            int wx = testOriginX + rc[0];
                            int wy = testOriginY + sb.getDy();
                            int wz = testOriginZ + rc[1];
                            if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                                Material wm = world.getBlockAt(wx, wy, wz).getType();
                                if (isMaterialMatch(wm, sb.getMaterial())) {
                                    layer0Matched++;
                                }
                            }
                        }

                        // Must match at least 40% of Layer 0 blocks and at least 12 blocks
                        int minReqLayer0 = Math.max(12, (int) (layer0Blocks.size() * 0.40));
                        if (layer0Matched < minReqLayer0) {
                            continue;
                        }

                        // 2. Scan layers sequentially from 0 to maxLayer
                        int totalMatched = 0;
                        Set<String> matchedKeys = new HashSet<>();
                        int completedLayers = 0;
                        boolean previousLayerFullyDone = true;
                        int layersWithMatches = 0;

                        for (int l = 0; l <= schem.getMaxLayer(); l++) {
                            List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(l);
                            if (layerBlocks.isEmpty()) continue;

                            int layerMatchCount = 0;
                            for (SchematicBlock sb : layerBlocks) {
                                int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                                int wx = testOriginX + rc[0];
                                int wy = testOriginY + sb.getDy();
                                int wz = testOriginZ + rc[1];
                                if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                                    Material wm = world.getBlockAt(wx, wy, wz).getType();
                                    if (isMaterialMatch(wm, sb.getMaterial())) {
                                        layerMatchCount++;
                                        matchedKeys.add(sb.getKey());
                                    }
                                }
                            }

                            totalMatched += layerMatchCount;
                            if (layerMatchCount > 0) {
                                layersWithMatches++;
                            }

                            if (layerMatchCount == layerBlocks.size()) {
                                if (previousLayerFullyDone) {
                                    completedLayers = l + 1;
                                }
                            } else {
                                previousLayerFullyDone = false;
                            }
                        }

                        // 3. Roof Artifact Guard (Защита от ложного распознавания крыши/потолка как фундамента):
                        // Если в схеме пол и крыша состоят из одного материала (например, тёмные доски в Библиотеке Чар),
                        // то крыша уже построенного здания может совпасть со Слоем 0.
                        // Если совпал только Слой 0 (layersWithMatches <= 1), а непосредственно под ним (Y - 1)
                        // находятся блоки стен/интерьера здания, значит testOriginY — это КРЫША, а не фундамент!
                        if (layersWithMatches <= 1 && schem.getMaxLayer() > 0) {
                            int blocksBelowCount = 0;
                            for (SchematicBlock sb : layer0Blocks) {
                                int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                                int wx = testOriginX + rc[0];
                                int wyBelow = testOriginY - 1;
                                int wz = testOriginZ + rc[1];
                                if (wyBelow >= world.getMinHeight()) {
                                    Material matBelow = world.getBlockAt(wx, wyBelow, wz).getType();
                                    if (!isNaturalTerrainMaterial(matBelow) && !matBelow.isAir()) {
                                        blocksBelowCount++;
                                    }
                                }
                            }
                            if (blocksBelowCount >= Math.max(8, (int) (layer0Blocks.size() * 0.20))) {
                                continue; // Отклоняем: это крыша уже существующей постройки снизу!
                            }
                        }

                        // 4. Candidate Ranking:
                        // Полностью построенное здание (100%) всегда имеет наивысший приоритет над частичным.
                        // При равенстве побеждает наибольшее количество совпавших блоков и слоев.
                        boolean isFull = (totalMatched >= schem.getTotalBlockCount());
                        boolean isBetter = false;
                        if (bestAlignment == null) {
                            isBetter = true;
                        } else if (isFull && !bestAlignment.isFullyBuilt) {
                            isBetter = true; // 100% готовое здание безусловно побеждает!
                        } else if (!isFull && bestAlignment.isFullyBuilt) {
                            isBetter = false;
                        } else if (totalMatched > bestMatchedCount) {
                            isBetter = true;
                        } else if (totalMatched == bestMatchedCount && layersWithMatches > bestLayersWithMatches) {
                            isBetter = true;
                        } else if (totalMatched == bestMatchedCount && completedLayers > bestCompletedLayers) {
                            isBetter = true;
                        } else if (totalMatched == bestMatchedCount && testOriginY < bestAlignment.matchedOriginY) {
                            // При прочих равных отдаём предпочтение более глубокому уровню земли/фундамента, а не верхушке
                            isBetter = true;
                        }

                        if (isBetter) {
                            bestMatchedCount = totalMatched;
                            bestLayersWithMatches = layersWithMatches;
                            bestCompletedLayers = completedLayers;
                            bestAlignment = new ExistingStageAlignment(
                                    testOriginX,
                                    testOriginY,
                                    testOriginZ,
                                    rot,
                                    completedLayers,
                                    totalMatched,
                                    matchedKeys,
                                    isFull
                            );
                        }
                    }
                }
            }
        }

        return bestAlignment;
    }

    private void applyExistingStageBlocks(ActiveBuilding building, BuildingSchematic schem, ExistingStageAlignment alignment) {
        if (building == null || schem == null || alignment == null) return;
        for (String key : alignment.matchedBlockKeys) {
            String[] parts = key.split(",");
            if (parts.length == 3) {
                try {
                    int dx = Integer.parseInt(parts[0]);
                    int dy = Integer.parseInt(parts[1]);
                    int dz = Integer.parseInt(parts[2]);
                    building.markBlockCompleted(dx, dy, dz);
                    SchematicBlock sb = schem.getBlock(dx, dy, dz);
                    if (sb != null) {
                        building.addPlacedBlock(sb.getMaterial());
                    }
                } catch (Exception ignored) {}
            }
        }
        int maxLayer = schem.getMaxLayer();
        int currentLayer = 0;
        for (int l = 0; l <= maxLayer; l++) {
            List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(l);
            if (layerBlocks.isEmpty()) continue;
            boolean allDone = true;
            for (SchematicBlock sb : layerBlocks) {
                if (!building.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                    allDone = false;
                    break;
                }
            }
            if (allDone) {
                currentLayer = Math.min(maxLayer + 1, l + 1);
            } else {
                currentLayer = l;
                break;
            }
        }
        building.setCurrentLayer(currentLayer);
    }

    
    private static class CandidateArea {
        final double distance;
        final Set<ChunkCoord> chunks;
        CandidateArea(double distance, Set<ChunkCoord> chunks) {
            this.distance = distance;
            this.chunks = chunks;
        }
    }

    public boolean rotateActiveBuilding(Player player, ActiveBuilding building) {
        if (building == null || player == null) return false;
        String playerTown = plugin.getTownyHook().getPlayerTownName(player);
        if (playerTown == null || !playerTown.equalsIgnoreCase(building.getTownName())) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Вы не состоите в этом городе!");
            return false;
        }
        if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player) && !plugin.getTownyHook().hasBuilderPermission(player, building.getTownName())) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] У вас нет прав на изменение ориентации постройки!");
            return false;
        }
        if (building.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Нельзя поворачивать завершенное или поврежденное здание!");
            return false;
        }
        if (building.getCompletedBlockCount() > 0) {
            player.sendMessage(ChatColor.RED + "[TownyArchitecture] Нельзя поворачивать проект, в котором уже установлены блоки! Сначала снесите блоки.");
            return false;
        }

        BuildingBlueprint bp = blueprints.get(building.getBlueprintId());
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(building.getBlueprintId());
        if (bp == null) return false;

                int currentRot = building.getRotationDeg();
        int minCX = Integer.MAX_VALUE, maxCX = Integer.MIN_VALUE;
        int minCZ = Integer.MAX_VALUE, maxCZ = Integer.MIN_VALUE;
        for (ChunkCoord cc : building.getAssignedChunks()) {
            minCX = Math.min(minCX, cc.getX());
            maxCX = Math.max(maxCX, cc.getX());
            minCZ = Math.min(minCZ, cc.getZ());
            maxCZ = Math.max(maxCZ, cc.getZ());
        }
        int totalWidthPx = (maxCX - minCX + 1) * 16;
        int totalLengthPx = (maxCZ - minCZ + 1) * 16;

        int newRot;
        if (bp.getChunkWidth() != bp.getChunkLength()) {
            // Rectangular building: preserve plot footprint (horizontal: 0 <-> 180, vertical: 90 <-> 270)
            if (totalWidthPx > totalLengthPx) {
                newRot = (currentRot == 0) ? 180 : 0;
            } else {
                newRot = (currentRot == 90) ? 270 : 90;
            }
        } else {
            // Square building: full 360 rotation
            newRot = (currentRot + 90) % 360;
        }

        int schemW = schem != null ? schem.getWidthX() : (bp.getChunkWidth() * 16);
        int schemL = schem != null ? schem.getLengthZ() : (bp.getChunkLength() * 16);
        int effectiveW = (newRot == 90 || newRot == 270) ? schemL : schemW;
        int effectiveL = (newRot == 90 || newRot == 270) ? schemW : schemL;

        int newOriginX = minCX * 16 + Math.max(0, (totalWidthPx - effectiveW) / 2);
        int newOriginZ = minCZ * 16 + Math.max(0, (totalLengthPx - effectiveL) / 2);

        building.setRotationDeg(newRot);
        building.setOrigin(newOriginX, building.getOriginY(), newOriginZ);
        saveData();

        // Refresh holograms
        plugin.getHologramDisplayManager().initHologramsForBuilding(building);
        return true;
    }

    public static int[] rotateRelativeCoords(int dx, int dz, int rotDeg, int w, int l) {
        switch (rotDeg) {
            case 90:
                return new int[]{dz, Math.max(0, w - 1 - dx)};
            case 180:
                return new int[]{Math.max(0, w - 1 - dx), Math.max(0, l - 1 - dz)};
            case 270:
                return new int[]{Math.max(0, l - 1 - dz), dx};
            case 0:
            default:
                return new int[]{dx, dz};
        }
    }

    public static int[] unrotateRelativeCoords(int rx, int rz, int rotDeg, int w, int l) {
        switch (rotDeg) {
            case 90:
                return rotateRelativeCoords(rx, rz, 270, l, w);
            case 180:
                return rotateRelativeCoords(rx, rz, 180, w, l);
            case 270:
                return rotateRelativeCoords(rx, rz, 90, l, w);
            case 0:
            default:
                return new int[]{rx, rz};
        }
    }

    public static int[] rotateDirection(int ox, int oz, int rotDeg) {
        switch (rotDeg) {
            case 90:
                return new int[]{oz, -ox};
            case 180:
                return new int[]{-ox, -oz};
            case 270:
                return new int[]{-oz, ox};
            case 0:
            default:
                return new int[]{ox, oz};
        }
    }

    public static boolean isMaterialMatch(Material worldMat, Material reqMat) {
        if (worldMat == reqMat) return true;
        if (worldMat == null || reqMat == null) return false;
        String w = worldMat.name();
        String r = reqMat.name();
        if (w.equals(r)) return true;
        if ((r.equals("STONE_BRICK") || r.equals("STONE_BRICKS")) && (w.equals("STONE_BRICK") || w.equals("STONE_BRICKS"))) return true;
        if (w.replace("WALL_", "").equals(r) || r.replace("WALL_", "").equals(w)) return true;
        if ((r.equals("TORCH") && w.equals("WALL_TORCH")) || (r.equals("SOUL_TORCH") && w.equals("SOUL_WALL_TORCH")) || (r.equals("REDSTONE_TORCH") && w.equals("REDSTONE_WALL_TORCH"))) return true;
        if (w.startsWith("INFESTED_") && w.replace("INFESTED_", "").equals(r)) return true;
        return false;
    }

    public int calculateTerrainGroundY(World world, Set<ChunkCoord> assignedChunks) {
        if (world == null || assignedChunks == null || assignedChunks.isEmpty()) return 64;
        List<Integer> heights = new ArrayList<>();
        for (ChunkCoord cc : assignedChunks) {
            int cx = cc.getX() << 4;
            int cz = cc.getZ() << 4;
            for (int x = 2; x < 16; x += 4) {
                for (int z = 2; z < 16; z += 4) {
                    int highestY = world.getHighestBlockYAt(cx + x, cz + z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                    int checkY = Math.min(highestY, 150);
                    // Scan downwards through man-made building structures (roofs, walls, slabs, planks)
                    // until hitting the actual natural terrain foundation/ground
                    while (checkY >= Math.max(50, world.getMinHeight())) {
                        Material mat = world.getBlockAt(cx + x, checkY, cz + z).getType();
                        if (isNaturalTerrainMaterial(mat)) {
                            break;
                        }
                        checkY--;
                    }
                    if (checkY >= 50) {
                        heights.add(checkY + 1);
                    } else {
                        heights.add(highestY);
                    }
                }
            }
        }
        if (heights.isEmpty()) return 64;
        Collections.sort(heights);
        return heights.get(heights.size() / 2);
    }


    public static boolean isNaturalTerrainMaterial(Material mat) {
        if (mat == null || mat.isAir()) return false;
        String name = mat.name();

        // Structural / crafted building materials must NEVER be treated as natural terrain:
        if (name.contains("PLANK") || name.contains("BRICK") || name.contains("SLAB") || 
            name.contains("STAIR") || name.contains("WALL") || name.contains("PILLAR") || 
            name.contains("SMOOTH") || name.contains("CHISELED") || name.contains("CRACKED") || 
            name.contains("POLISHED") || name.contains("TERRACOTTA") || name.contains("CONCRETE") || 
            name.contains("WOOL") || name.contains("GLASS") || name.contains("CARPET") || 
            name.contains("FENCE") || name.contains("DOOR") || name.contains("TRAPDOOR") || 
            name.contains("BOOKSHELF") || name.contains("OBSIDIAN") || name.contains("COPPER") ||
            name.contains("IRON") || name.contains("GOLD") || name.contains("DIAMOND") ||
            name.contains("NETHERITE") || name.contains("EMERALD") || name.contains("QUARTZ") ||
            name.contains("PURPUR") || name.contains("PRISMARINE") || name.contains("LANTERN") ||
            name.contains("TORCH") || name.contains("LADDER") || name.contains("BANNER") ||
            name.contains("SIGN") || name.contains("BED") || name.contains("ANVIL") ||
            name.contains("TABLE") || name.contains("FURNACE") || name.contains("CHEST") ||
            name.contains("HOPPER") || name.contains("DROPPER") || name.contains("DISPENSER") ||
            name.contains("SHULKER") || name.contains("CRAFTING") || name.contains("CAMPFIRE")) {
            return false;
        }

        return mat == Material.GRASS_BLOCK || mat == Material.DIRT || mat == Material.COARSE_DIRT ||
               mat == Material.PODZOL || mat == Material.ROOTED_DIRT || mat == Material.MUD ||
               mat == Material.MUDDY_MANGROVE_ROOTS || mat == Material.MYCELIUM ||
               mat == Material.STONE || mat == Material.DEEPSLATE || mat == Material.TUFF ||
               mat == Material.DIORITE || mat == Material.ANDESITE || mat == Material.GRANITE ||
               mat == Material.SAND || mat == Material.RED_SAND || mat == Material.GRAVEL ||
               mat == Material.SANDSTONE || mat == Material.RED_SANDSTONE || mat == Material.CLAY ||
               mat == Material.SNOW_BLOCK || mat == Material.POWDER_SNOW || mat == Material.ICE ||
               mat == Material.PACKED_ICE || mat == Material.BLUE_ICE || mat == Material.WATER ||
               mat == Material.LAVA || mat == Material.BEDROCK || mat == Material.CALCITE ||
               mat == Material.DRIPSTONE_BLOCK || mat == Material.NETHERRACK || mat == Material.END_STONE ||
               mat == Material.BASALT || mat == Material.BLACKSTONE || mat == Material.SOUL_SAND ||
               mat == Material.SOUL_SOIL;
    }


    public int countCompletedBlocksInLayer(ActiveBuilding bld, BuildingSchematic schem, int layerY) {
        if (bld == null || schem == null) return 0;
        int count = 0;
        for (SchematicBlock sb : schem.getBlocksAtLayer(layerY)) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                count++;
            }
        }
        return count;
    }

    public List<SchematicBlock> getMissingBlocksInLayer(ActiveBuilding bld, BuildingSchematic schem, int layerY) {
        if (bld == null || schem == null) return Collections.emptyList();
        List<SchematicBlock> missing = new ArrayList<>();
        for (SchematicBlock sb : schem.getBlocksAtLayer(layerY)) {
            if (!bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                missing.add(sb);
            }
        }
        return missing;
    }

}
