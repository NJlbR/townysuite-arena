package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingSchematic;
import com.towny.architecture.model.SchematicBlock;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.ChunkCoord;
import com.towny.architecture.util.RussianTranslator;
import org.bukkit.*;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.entity.Player;

import java.util.*;

public class BuildingHudManager {
    private final TownyArchitecturePlugin plugin;
    private final Map<UUID, BossBar> playerBossBars = new HashMap<>();
    private final Map<UUID, Integer> playerCycleIndex = new HashMap<>();
    private final Map<UUID, Integer> playerTicksHeld = new HashMap<>();
    private final Set<UUID> playersParticlesDisabled = new HashSet<>();
    private final Set<UUID> playersEffectParticlesDisabled = new HashSet<>();

    private static Particle dustParticle;
    static {
        for (String pName : new String[]{"DUST", "REDSTONE", "END_ROD", "FLAME"}) {
            try {
                dustParticle = Particle.valueOf(pName);
                break;
            } catch (Throwable ignored) {}
        }
    }

    public BuildingHudManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
    }

    public boolean hasParticlesEnabled(Player player) {
        return player != null && !playersParticlesDisabled.contains(player.getUniqueId());
    }

    public boolean hasEffectParticlesEnabled(Player player) {
        return player != null && !playersEffectParticlesDisabled.contains(player.getUniqueId());
    }

    public boolean toggleParticles(Player player) {
        if (player == null) return false;
        UUID uuid = player.getUniqueId();
        if (playersParticlesDisabled.contains(uuid)) {
            playersParticlesDisabled.remove(uuid);
            return true;
        } else {
            playersParticlesDisabled.add(uuid);
            return false;
        }
    }

    public boolean toggleEffectParticles(Player player) {
        if (player == null) return false;
        UUID uuid = player.getUniqueId();
        if (playersEffectParticlesDisabled.contains(uuid)) {
            playersEffectParticlesDisabled.remove(uuid);
            return true;
        } else {
            playersEffectParticlesDisabled.add(uuid);
            return false;
        }
    }

    public void setParticlesEnabled(Player player, boolean enabled) {
        if (player == null) return;
        if (enabled) {
            playersParticlesDisabled.remove(player.getUniqueId());
        } else {
            playersParticlesDisabled.add(player.getUniqueId());
        }
    }

    public void renderParticles() {
        boolean particlesEnabled = plugin.getConfig().getBoolean("settings.particles-enabled", true);
        boolean wireframeEnabled = plugin.getConfig().getBoolean("settings.hologram.wireframe.enabled", true);
        if (!particlesEnabled && !wireframeEnabled) return;

        int radiusChunks = plugin.getConfig().getInt("settings.buff-1x1-chunk-radius", 2);

        Particle.DustOptions plotAquaDust = new Particle.DustOptions(Color.fromRGB(0, 180, 255), 0.95f);
        Particle.DustOptions footprintCyanDust = new Particle.DustOptions(Color.fromRGB(0, 230, 255), 0.95f);

        for (Player player : Bukkit.getOnlinePlayers()) {
            boolean showBorders = hasParticlesEnabled(player);
            boolean showEffects = hasEffectParticlesEnabled(player);
            if (!showBorders && !showEffects) continue;

            Location pLoc = player.getLocation();
            World pWorld = pLoc.getWorld();
            if (pWorld == null) continue;

            double pX = pLoc.getX();
            double pY = pLoc.getY();
            double pZ = pLoc.getZ();

            // 1. Render active building boundaries and effect zones
            for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                if (!bld.getWorldName().equals(pWorld.getName())) continue;
                if (bld.getAssignedChunks().isEmpty()) continue;

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                if (bp == null) continue;

                int minCX = Integer.MAX_VALUE, maxCX = Integer.MIN_VALUE;
                int minCZ = Integer.MAX_VALUE, maxCZ = Integer.MIN_VALUE;
                for (ChunkCoord c : bld.getAssignedChunks()) {
                    minCX = Math.min(minCX, c.getX());
                    maxCX = Math.max(maxCX, c.getX());
                    minCZ = Math.min(minCZ, c.getZ());
                    maxCZ = Math.max(maxCZ, c.getZ());
                }

                double bMinX = minCX << 4;
                double bMaxX = (maxCX + 1) << 4;
                double bMinZ = minCZ << 4;
                double bMaxZ = (maxCZ + 1) << 4;

                // Footprint boundary line along plot perimeter
                if (showBorders && pX >= bMinX - 50 && pX <= bMaxX + 50 && pZ >= bMinZ - 50 && pZ <= bMaxZ + 50) {
                    renderSolidLine(player, pWorld, bMinX, bMaxX, bMinZ, bMaxZ, pX, pY, pZ, footprintCyanDust);
                }

                // Hologram & Obstacle layer wireframe edge highlighting (4-cell adjacency rule)
                if (showBorders && bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                    BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
                    if (schem != null) {
                        if (pX >= bMinX - 48 && pX <= bMaxX + 48 && pZ >= bMinZ - 48 && pZ <= bMaxZ + 48) {
                            renderLayerWireframes(player, pWorld, bld, schem);
                        }
                    }
                }

                // C. Buff Zone boundary for 1x1 buildings (Clean, thin, continuous glowing line)
                if (showEffects && bp.getChunkWidth() == 1 && bp.getChunkLength() == 1) {
                    double effMinX = (minCX - radiusChunks) << 4;
                    double effMaxX = (maxCX + radiusChunks + 1) << 4;
                    double effMinZ = (minCZ - radiusChunks) << 4;
                    double effMaxZ = (maxCZ + radiusChunks + 1) << 4;

                    if (pX >= effMinX - 50 && pX <= effMaxX + 50 && pZ >= effMinZ - 50 && pZ <= effMaxZ + 50) {
                        Color buffColor;
                        String bpId = bld.getBlueprintId().toLowerCase();
                        if (bpId.contains("hospital") || bpId.contains("infirmary") || bpId.contains("barracks")) {
                            buffColor = Color.fromRGB(255, 35, 65); // Vivid Crimson Red
                        } else {
                            buffColor = Color.fromRGB(0, 200, 255); // Vivid Electric Cyan
                        }
                        Particle.DustOptions effectDust = new Particle.DustOptions(buffColor, 0.95f);
                        renderSolidLine(player, pWorld, effMinX, effMaxX, effMinZ, effMaxZ, pX, pY, pZ, effectDust);
                    }
                }
            }

            // 2. Render designated town build plots (Vivid Aqua / Sky Blue - NO yellow!)
            if (showBorders) {
                String playerTown = plugin.getTownyHook().getPlayerTownName(player);
                if (playerTown != null) {
                    Set<ChunkCoord> plots = plugin.getBuildingManager().getTownBuildPlots(playerTown);
                    if (!plots.isEmpty()) {
                        for (ChunkCoord cc : plots) {
                            if (plugin.getBuildingManager().isChunkOccupiedByBuilding(cc)) continue;
                            double minX = cc.getX() << 4;
                            double maxX = (cc.getX() + 1) << 4;
                            double minZ = cc.getZ() << 4;
                            double maxZ = (cc.getZ() + 1) << 4;

                            if (pX >= minX - 50 && pX <= maxX + 50 && pZ >= minZ - 50 && pZ <= maxZ + 50) {
                                renderSolidLine(player, pWorld, minX, maxX, minZ, maxZ, pX, pY, pZ, plotAquaDust);
                            }
                        }
                    }
                }
            }
        }
    }



    /**
     * Renders a smooth, dense, continuous solid perimeter line at terrain ground level
     */
    private void renderSolidLine(Player player, World world, double minX, double maxX, double minZ, double maxZ,
                                 double pX, double pY, double pZ, Particle.DustOptions dust) {
        double maxDist = 64.0;
        if (pX < minX - maxDist || pX > maxX + maxDist || pZ < minZ - maxDist || pZ > maxZ + maxDist) {
            return;
        }

        double startX = Math.max(minX, pX - 32.0);
        double endX = Math.min(maxX, pX + 32.0);
        double startZ = Math.max(minZ, pZ - 32.0);
        double endZ = Math.min(maxZ, pZ + 32.0);

        // North edge (Z = minZ)
        for (double x = startX; x <= endX; x += 0.35) {
            spawnVisibleParticle(player, world, x, minZ, pY, dust);
        }

        // South edge (Z = maxZ)
        for (double x = startX; x <= endX; x += 0.35) {
            spawnVisibleParticle(player, world, x, maxZ, pY, dust);
        }

        // West edge (X = minX)
        for (double z = startZ; z <= endZ; z += 0.35) {
            spawnVisibleParticle(player, world, minX, z, pY, dust);
        }

        // East edge (X = maxX)
        for (double z = startZ; z <= endZ; z += 0.35) {
            spawnVisibleParticle(player, world, maxX, z, pY, dust);
        }
    }

    private double findGroundY(World world, double x, double z, double playerY) {
        int bx = (int) Math.floor(x);
        int bz = (int) Math.floor(z);
        if (!world.isChunkLoaded(bx >> 4, bz >> 4)) return -1000;

        int py = (int) Math.floor(playerY);
        int startY = Math.min(py + 6, world.getMaxHeight() - 1);
        int minY = Math.max(py - 10, world.getMinHeight());

        for (int y = startY; y >= minY; y--) {
            org.bukkit.block.Block b = world.getBlockAt(bx, y, bz);
            Material m = b.getType();
            if (m.isSolid() && isTrueTerrainGround(m)) {
                return y + 1.05;
            }
        }
        return playerY + 0.1;
    }

    private boolean isTrueTerrainGround(Material m) {
        if (m == null || m.isAir()) return false;
        String name = m.name();
        if (name.contains("LEAVES") || name.contains("FENCE") || name.contains("GLASS") ||
            name.contains("SCAFFOLD") || name.contains("BANNER") || name.contains("CARPET") ||
            name.contains("CHAIN") || name.contains("LANTERN") || name.contains("TORCH") ||
            name.contains("WALL") || name.contains("STAIR") || name.contains("DOOR") ||
            name.contains("SLAB") || name.contains("FENCE_GATE") || name.contains("SIGN") ||
            name.contains("PRESSURE_PLATE") || name.contains("BUTTON") || name.contains("TRAPDOOR")) {
            return false;
        }
        return true;
    }

    private void spawnVisibleParticle(Player player, World world, double x, double z, double playerY, Particle.DustOptions dust) {
        double gy = findGroundY(world, x, z, playerY);
        if (gy < -500) return;
        player.spawnParticle(dustParticle, x, gy, z, 0, 0, 0, 0, 0, dust);
    }

    private static final byte TYPE_AIR = 0;
    private static final byte TYPE_HOLOGRAM = 1;
    private static final byte TYPE_OTHER_LAYER = 2;
    private static final byte TYPE_OBSTACLE = 3;

    private static final Particle.DustOptions DUST_HOLOGRAM = new Particle.DustOptions(Color.fromRGB(60, 190, 239), 0.85f);
    private static final Particle.DustOptions DUST_OBSTACLE = new Particle.DustOptions(Color.fromRGB(235, 75, 75), 0.85f);

    private byte getCellType(World world, ActiveBuilding bld, BuildingSchematic schem, int wx, int wy, int wz) {
        if (bld == null || schem == null || world == null) return TYPE_AIR;

        int layerWorldY = bld.getOriginY() + bld.getCurrentLayer();
        int rx = wx - bld.getOriginX();
        int dy = wy - bld.getOriginY();
        int rz = wz - bld.getOriginZ();

        int[] unrot = BuildingManager.unrotateRelativeCoords(rx, rz, bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
        int dx = unrot[0];
        int dz = unrot[1];

        boolean insideFootprint = (dx >= 0 && dx < schem.getWidthX() && dz >= 0 && dz < schem.getLengthZ());

        org.bukkit.block.Block block = world.getBlockAt(wx, wy, wz);
        Material mat = block.getType();
        boolean isSolidPhysical = !mat.isAir() && mat != Material.WATER && mat != Material.LAVA;

        if (!isSolidPhysical) {
            if (wy == layerWorldY && insideFootprint) {
                SchematicBlock sb = schem.getBlock(dx, dy, dz);
                if (sb != null && !bld.isBlockCompleted(dx, dy, dz)) {
                    return TYPE_HOLOGRAM;
                }
            }
            return TYPE_AIR;
        } else {
            if (wy < layerWorldY) {
                return TYPE_OTHER_LAYER;
            } else if (wy > layerWorldY) {
                return TYPE_OBSTACLE;
            } else {
                if (insideFootprint) {
                    SchematicBlock sb = schem.getBlock(dx, dy, dz);
                    if (sb != null) {
                        if (bld.isBlockCompleted(dx, dy, dz) || BuildingManager.isMaterialMatch(mat, sb.getMaterial())) {
                            return TYPE_OTHER_LAYER;
                        } else {
                            return TYPE_OBSTACLE;
                        }
                    } else {
                        return TYPE_OBSTACLE;
                    }
                } else {
                    return TYPE_OBSTACLE;
                }
            }
        }
    }

    private boolean isAirFace(byte a, byte b, byte targetType) {
        return (a == TYPE_AIR && b == targetType) || (b == TYPE_AIR && a == targetType);
    }

    private Particle.DustOptions getEdgeColor(byte t1, byte t2, byte t3, byte t4) {
        boolean hasObstacleAirFace = isAirFace(t1, t3, TYPE_OBSTACLE) ||
                                     isAirFace(t2, t4, TYPE_OBSTACLE) ||
                                     isAirFace(t1, t2, TYPE_OBSTACLE) ||
                                     isAirFace(t3, t4, TYPE_OBSTACLE);

        boolean hasHologramAirFace = isAirFace(t1, t3, TYPE_HOLOGRAM) ||
                                     isAirFace(t2, t4, TYPE_HOLOGRAM) ||
                                     isAirFace(t1, t2, TYPE_HOLOGRAM) ||
                                     isAirFace(t3, t4, TYPE_HOLOGRAM);

        if (hasObstacleAirFace) {
            return DUST_OBSTACLE;
        } else if (hasHologramAirFace) {
            return DUST_HOLOGRAM;
        }
        return null;
    }

    private void drawLineSegment(Player player, World world, double x1, double y1, double z1, double x2, double y2, double z2, Particle.DustOptions dust) {
        double dx = x2 - x1;
        double dy = y2 - y1;
        double dz = z2 - z1;
        double length = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (length < 0.001) return;

        double step = 0.25;
        int count = (int) Math.round(length / step);
        if (count < 1) count = 1;

        for (int i = 0; i <= count; i++) {
            double t = (double) i / count;
            double px = x1 + dx * t;
            double py = y1 + dy * t;
            double pz = z1 + dz * t;
            player.spawnParticle(dustParticle, px, py, pz, 0, 0.0, 0.0, 0.0, 0.0, dust);
        }
    }

    private void renderLayerWireframes(Player player, World world, ActiveBuilding bld, BuildingSchematic schem) {
        if (bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) return;

        int effW = schem.getWidthX();
        int effL = schem.getLengthZ();
        if (bld.getRotationDeg() == 90 || bld.getRotationDeg() == 270) {
            effW = schem.getLengthZ();
            effL = schem.getWidthX();
        }

        int minX = bld.getOriginX();
        int maxX = bld.getOriginX() + effW - 1;
        int minZ = bld.getOriginZ();
        int maxZ = bld.getOriginZ() + effL - 1;
        int Y = bld.getOriginY() + bld.getCurrentLayer();

        // Use top elevation (+1.015) for top face open-air contact
        double yPillarStart = Y + 0.85;
        double yTop = Y + 1.015;

        // 1. Top Horizontal X edges at Y + 1 (ON TOP of layer Y, contacting sky/air)
        for (int z = minZ; z <= maxZ + 1; z++) {
            int startX = -1;
            Particle.DustOptions currentDust = null;

            for (int x = minX; x <= maxX; x++) {
                byte t1 = getCellType(world, bld, schem, x, Y, z - 1);
                byte t2 = getCellType(world, bld, schem, x, Y, z);
                byte t3 = getCellType(world, bld, schem, x, Y + 1, z - 1);
                byte t4 = getCellType(world, bld, schem, x, Y + 1, z);

                Particle.DustOptions edgeDust = getEdgeColor(t1, t2, t3, t4);

                if (edgeDust != currentDust) {
                    if (currentDust != null && startX != -1) {
                        drawLineSegment(player, world, startX, yTop, z, x, yTop, z, currentDust);
                    }
                    startX = x;
                    currentDust = edgeDust;
                }
            }
            if (currentDust != null && startX != -1) {
                drawLineSegment(player, world, startX, yTop, z, maxX + 1, yTop, z, currentDust);
            }
        }

        // 2. Top Horizontal Z edges at Y + 1 (ON TOP of layer Y, contacting sky/air)
        for (int x = minX; x <= maxX + 1; x++) {
            int startZ = -1;
            Particle.DustOptions currentDust = null;

            for (int z = minZ; z <= maxZ; z++) {
                byte t1 = getCellType(world, bld, schem, x - 1, Y, z);
                byte t2 = getCellType(world, bld, schem, x, Y, z);
                byte t3 = getCellType(world, bld, schem, x - 1, Y + 1, z);
                byte t4 = getCellType(world, bld, schem, x, Y + 1, z);

                Particle.DustOptions edgeDust = getEdgeColor(t1, t2, t3, t4);

                if (edgeDust != currentDust) {
                    if (currentDust != null && startZ != -1) {
                        drawLineSegment(player, world, x, yTop, startZ, x, yTop, z, currentDust);
                    }
                    startZ = z;
                    currentDust = edgeDust;
                }
            }
            if (currentDust != null && startZ != -1) {
                drawLineSegment(player, world, x, yTop, startZ, x, yTop, maxZ + 1, currentDust);
            }
        }

        // 3. Vertical Y pillar edges from Y + 0.5 to Y + 1 (UPPER SIDES ONLY, avoiding bottom face)
        for (int x = minX; x <= maxX + 1; x++) {
            for (int z = minZ; z <= maxZ + 1; z++) {
                byte t1 = getCellType(world, bld, schem, x - 1, Y, z - 1);
                byte t2 = getCellType(world, bld, schem, x, Y, z - 1);
                byte t3 = getCellType(world, bld, schem, x - 1, Y, z);
                byte t4 = getCellType(world, bld, schem, x, Y, z);

                Particle.DustOptions edgeDust = getEdgeColor(t1, t2, t3, t4);
                if (edgeDust != null) {
                    drawLineSegment(player, world, x, yPillarStart, z, x, yTop, z, edgeDust);
                }
            }
        }
    }

    public void updateHud() {
        int cycleIntervalSeconds = plugin.getConfig().getInt("settings.hud-material-cycle-interval-seconds", 5);
        if (cycleIntervalSeconds < 1) cycleIntervalSeconds = 5;

        for (Player player : Bukkit.getOnlinePlayers()) {
            ActiveBuilding building = plugin.getBuildingManager().getBuildingAt(player.getLocation());
            if (building != null && !building.isFullyBuilt()) {
                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(building.getBlueprintId());
                String bpName = bp != null ? bp.getNameRu() : building.getBlueprintId();
                int percent = building.getProgressPercent();

                // Clean Blue/Cyan BossBar instead of Yellow
                BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), k -> {
                    BossBar b = Bukkit.createBossBar(
                            "",
                            BarColor.BLUE,
                            BarStyle.SEGMENTED_10
                    );
                    b.addPlayer(player);
                    return b;
                });

                bar.setProgress(Math.max(0.0, Math.min(1.0, percent / 100.0)));
                bar.setVisible(true);

                StringBuilder reqStr = new StringBuilder();
                Map<Material, Integer> required = building.getRequiredMaterials();
                
                List<Map.Entry<Material, Integer>> uncompleted = new ArrayList<>();
                List<Map.Entry<Material, Integer>> completed = new ArrayList<>();
                for (Map.Entry<Material, Integer> entry : required.entrySet()) {
                    int placed = building.getPlacedCount(entry.getKey());
                    int need = entry.getValue();
                    if (placed < need) {
                        uncompleted.add(entry);
                    } else {
                        completed.add(entry);
                    }
                }
                
                List<Map.Entry<Material, Integer>> sortedList = new ArrayList<>(uncompleted);
                sortedList.addAll(completed);

                if (!sortedList.isEmpty()) {
                    int currentCycle = playerCycleIndex.getOrDefault(player.getUniqueId(), 0);
                    int ticksHeld = playerTicksHeld.getOrDefault(player.getUniqueId(), 0) + 1;
                    
                    if (ticksHeld >= cycleIntervalSeconds) {
                        ticksHeld = 0;
                        currentCycle = (currentCycle + 1) % sortedList.size();
                        playerCycleIndex.put(player.getUniqueId(), currentCycle);
                    }
                    playerTicksHeld.put(player.getUniqueId(), ticksHeld);
                    
                    int idx1 = currentCycle % sortedList.size();
                    Map.Entry<Material, Integer> e1 = sortedList.get(idx1);
                    int placed1 = building.getPlacedCount(e1.getKey());
                    int need1 = e1.getValue();
                    boolean done1 = placed1 >= need1;
                    
                    reqStr.append(done1 ? "§a✔ " : "§b■ ")
                          .append("§f").append(RussianTranslator.getShortMaterialRu(e1.getKey())).append(": ")
                          .append(done1 ? "§a" : "§b").append(placed1).append("§7/§a").append(need1);
                          
                    if (sortedList.size() > 1) {
                        int idx2 = (idx1 + 1) % sortedList.size();
                        Map.Entry<Material, Integer> e2 = sortedList.get(idx2);
                        int placed2 = building.getPlacedCount(e2.getKey());
                        int need2 = e2.getValue();
                        boolean done2 = placed2 >= need2;
                        
                        reqStr.append(" §8| ")
                              .append(done2 ? "§a✔ " : "§b■ ")
                              .append("§f").append(RussianTranslator.getShortMaterialRu(e2.getKey())).append(": ")
                              .append(done2 ? "§a" : "§b").append(placed2).append("§7/§a").append(need2);
                    }
                }

                // Crisp Aqua & White formatting - Zero Yellow!
                String layerInfo = (building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) ? 
                        ("§bСлой " + (building.getCurrentLayer() + 1) + ChatColor.DARK_GRAY + " | ") : "";
                String prefix = ChatColor.AQUA + "⚡ [" + building.getTownName() + "] " + ChatColor.WHITE + bpName + ChatColor.DARK_GRAY + " | " + layerInfo;
                if (reqStr.length() > 0) {
                    bar.setTitle(prefix + reqStr.toString() + " §8| §a" + percent + "%");
                } else {
                    bar.setTitle(prefix + "§a" + percent + "%");
                }
            } else {
                BossBar bar = playerBossBars.remove(player.getUniqueId());
                if (bar != null) {
                    bar.removePlayer(player);
                    bar.setVisible(false);
                }
                playerTicksHeld.remove(player.getUniqueId());
            }
        }
    }

    public void removePlayer(Player player) {
        BossBar bar = playerBossBars.remove(player.getUniqueId());
        if (bar != null) {
            bar.removePlayer(player);
            bar.setVisible(false);
        }
        playerCycleIndex.remove(player.getUniqueId());
        playerTicksHeld.remove(player.getUniqueId());
        playersParticlesDisabled.remove(player.getUniqueId());
        playersEffectParticlesDisabled.remove(player.getUniqueId());
    }

    public void clearAll() {
        for (BossBar bar : playerBossBars.values()) {
            bar.removeAll();
            bar.setVisible(false);
        }
        playerBossBars.clear();
        playerCycleIndex.clear();
        playerTicksHeld.clear();
        playersParticlesDisabled.clear();
        playersEffectParticlesDisabled.clear();
    }
}
