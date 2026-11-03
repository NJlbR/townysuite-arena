package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
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
        try {
            dustParticle = Particle.valueOf("DUST");
        } catch (Throwable t1) {
            try {
                dustParticle = Particle.valueOf("REDSTONE");
            } catch (Throwable t2) {
                dustParticle = Particle.valueOf("SPELL_MOB");
            }
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
        if (!plugin.getConfig().getBoolean("settings.particles-enabled", true)) return;

        int radiusChunks = plugin.getConfig().getInt("settings.buff-1x1-chunk-radius", 2);

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

            // 1. Render active building boundaries and effect ranges
            for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                if (!bld.getWorldName().equals(pWorld.getName())) continue;
                if (bld.getAssignedChunks().isEmpty()) continue;

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                if (bp == null) continue;

                Color color = parseColor(bp.getParticleColorHex());
                Particle.DustOptions dust = new Particle.DustOptions(color, 2.0f);

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

                // A. Plot boundary: if player is within 64 blocks of building
                if (showBorders && pX >= bMinX - 64 && pX <= bMaxX + 64 && pZ >= bMinZ - 64 && pZ <= bMaxZ + 64) {
                    renderBoxBoundary(player, pWorld, bMinX, bMaxX, bMinZ, bMaxZ, pX, pY, pZ, dust);
                    renderCornerPillar(player, pWorld, bMinX, bMinZ, pY, dust);
                    renderCornerPillar(player, pWorld, bMaxX, bMinZ, pY, dust);
                    renderCornerPillar(player, pWorld, bMinX, bMaxZ, pY, dust);
                    renderCornerPillar(player, pWorld, bMaxX, bMaxZ, pY, dust);
                }

                // B. Effect area boundary for 1x1 buildings
                // Distinct vivid electric azure blue (zero green tint, high contrast with grass)
                if (showEffects && bp.getChunkWidth() == 1 && bp.getChunkLength() == 1) {
                    double effMinX = (minCX - radiusChunks) << 4;
                    double effMaxX = (maxCX + radiusChunks + 1) << 4;
                    double effMinZ = (minCZ - radiusChunks) << 4;
                    double effMaxZ = (maxCZ + radiusChunks + 1) << 4;

                    Particle.DustOptions effectDust = new Particle.DustOptions(Color.fromRGB(0, 150, 255), 2.0f);
                    renderBoxBoundary(player, pWorld, effMinX, effMaxX, effMinZ, effMaxZ, pX, pY, pZ, effectDust);
                    
                    // Diagonals from building corners to effect boundaries
                    renderLineOnGround(player, pWorld, bMinX, bMinZ, effMinX, effMinZ, pX, pY, pZ, effectDust); // NW
                    renderLineOnGround(player, pWorld, bMaxX, bMinZ, effMaxX, effMinZ, pX, pY, pZ, effectDust); // NE
                    renderLineOnGround(player, pWorld, bMinX, bMaxZ, effMinX, effMaxZ, pX, pY, pZ, effectDust); // SW
                    renderLineOnGround(player, pWorld, bMaxX, bMaxZ, effMaxX, effMaxZ, pX, pY, pZ, effectDust); // SE
                    
                    // Orthogonals from middle of building sides to middle of effect boundaries
                    double midX = bMinX + 8.0;
                    double midZ = bMinZ + 8.0;
                    renderLineOnGround(player, pWorld, midX, bMinZ, midX, effMinZ, pX, pY, pZ, effectDust); // North
                    renderLineOnGround(player, pWorld, midX, bMaxZ, midX, effMaxZ, pX, pY, pZ, effectDust); // South
                    renderLineOnGround(player, pWorld, bMinX, midZ, effMinX, midZ, pX, pY, pZ, effectDust); // West
                    renderLineOnGround(player, pWorld, bMaxX, midZ, effMaxX, midZ, pX, pY, pZ, effectDust); // East
                }
            }

            // 2. Render designated town build plots
            // Intense luminous Gold/Amber (RGB: 255, 160, 0) - super high contrast on grass
            if (showBorders) {
                String playerTown = plugin.getTownyHook().getPlayerTownName(player);
                if (playerTown != null) {
                    Set<ChunkCoord> plots = plugin.getBuildingManager().getTownBuildPlots(playerTown);
                    if (!plots.isEmpty()) {
                        Particle.DustOptions plotAmberDust = new Particle.DustOptions(Color.fromRGB(255, 160, 0), 2.0f);
                        for (ChunkCoord cc : plots) {
                            if (plugin.getBuildingManager().isChunkOccupiedByBuilding(cc)) continue;

                            double minX = cc.getX() << 4;
                            double maxX = (cc.getX() + 1) << 4;
                            double minZ = cc.getZ() << 4;
                            double maxZ = (cc.getZ() + 1) << 4;

                            if (pX >= minX - 50 && pX <= maxX + 50 && pZ >= minZ - 50 && pZ <= maxZ + 50) {
                                renderBoxBoundary(player, pWorld, minX, maxX, minZ, maxZ, pX, pY, pZ, plotAmberDust);
                                renderCornerPillar(player, pWorld, minX, minZ, pY, plotAmberDust);
                                renderCornerPillar(player, pWorld, maxX, minZ, pY, plotAmberDust);
                                renderCornerPillar(player, pWorld, minX, maxZ, pY, plotAmberDust);
                                renderCornerPillar(player, pWorld, maxX, maxZ, pY, plotAmberDust);
                            }
                        }
                    }
                }
            }
        }
    }

    private void renderBoxBoundary(Player player, World world, double minX, double maxX, double minZ, double maxZ, 
                                   double pX, double pY, double pZ, Particle.DustOptions dust) {
        // North edge (Z = minZ)
        if (Math.abs(pZ - minZ) <= 48.0 && pX >= minX - 24.0 && pX <= maxX + 24.0) {
            double start = Math.max(minX, pX - 36.0);
            double end = Math.min(maxX, pX + 36.0);
            for (double x = start; x <= end; x += 0.5) {
                spawnVisibleParticle(player, world, x, minZ, pY, dust);
            }
        }
        // South edge (Z = maxZ)
        if (Math.abs(pZ - maxZ) <= 48.0 && pX >= minX - 24.0 && pX <= maxX + 24.0) {
            double start = Math.max(minX, pX - 36.0);
            double end = Math.min(maxX, pX + 36.0);
            for (double x = start; x <= end; x += 0.5) {
                spawnVisibleParticle(player, world, x, maxZ, pY, dust);
            }
        }
        // West edge (X = minX)
        if (Math.abs(pX - minX) <= 48.0 && pZ >= minZ - 24.0 && pZ <= maxZ + 24.0) {
            double start = Math.max(minZ, pZ - 36.0);
            double end = Math.min(maxZ, pZ + 36.0);
            for (double z = start; z <= end; z += 0.5) {
                spawnVisibleParticle(player, world, minX, z, pY, dust);
            }
        }
        // East edge (X = maxX)
        if (Math.abs(pX - maxX) <= 48.0 && pZ >= minZ - 24.0 && pZ <= maxZ + 24.0) {
            double start = Math.max(minZ, pZ - 36.0);
            double end = Math.min(maxZ, pZ + 36.0);
            for (double z = start; z <= end; z += 0.5) {
                spawnVisibleParticle(player, world, maxX, z, pY, dust);
            }
        }
    }

    private void renderLineOnGround(Player player, World world, double startX, double startZ, double endX, double endZ, double pX, double pY, double pZ, Particle.DustOptions dust) {
        double length = Math.hypot(endX - startX, endZ - startZ);
        if (length < 0.1) return;
        
        double minX = Math.min(startX, endX) - 36.0;
        double maxX = Math.max(startX, endX) + 36.0;
        double minZ = Math.min(startZ, endZ) - 36.0;
        double maxZ = Math.max(startZ, endZ) + 36.0;
        
        if (pX < minX || pX > maxX || pZ < minZ || pZ > maxZ) return;
        
        double dx = (endX - startX) / length;
        double dz = (endZ - startZ) / length;
        
        for (double t = 0; t <= length; t += 0.5) {
            double x = startX + dx * t;
            double z = startZ + dz * t;
            
            if (Math.abs(x - pX) <= 36.0 && Math.abs(z - pZ) <= 36.0) {
                spawnVisibleParticle(player, world, x, z, pY, dust);
            }
        }
    }

    private void renderCornerPillar(Player player, World world, double x, double z, double pY, Particle.DustOptions dust) {
        double gy = findGroundY(world, x, z, pY);
        if (gy < world.getMinHeight()) return;
        // Tall luminous corner beacon pillar (4 meters high, step 0.35)
        for (double yOffset = 0.1; yOffset <= 3.8; yOffset += 0.35) {
            Location loc = new Location(world, x, gy + yOffset, z);
            try {
                if (dustParticle.getDataType() == Particle.DustOptions.class) {
                    player.spawnParticle(dustParticle, loc, 1, 0.0, 0.0, 0.0, 0.0, dust);
                } else {
                    player.spawnParticle(dustParticle, loc, 1, 0.0, 0.0, 0.0, 0.0);
                }
            } catch (Exception ignored) {}
        }
        try {
            Location topLoc = new Location(world, x, gy + 4.0, z);
            player.spawnParticle(Particle.VILLAGER_HAPPY, topLoc, 1, 0.0, 0.0, 0.0, 0.0);
        } catch (Exception ignored) {}
    }

    private double findGroundY(World world, double x, double z, double playerY) {
        int bx = (int) Math.floor(x);
        int bz = (int) Math.floor(z);
        if (!world.isChunkLoaded(bx >> 4, bz >> 4)) return -1000;

        int py = (int) Math.floor(playerY);
        int startY = Math.min(py + 10, world.getMaxHeight() - 1);
        int minY = Math.max(py - 14, world.getMinHeight());

        for (int y = startY; y >= minY; y--) {
            org.bukkit.block.Block b = world.getBlockAt(bx, y, bz);
            if (b.getType().isSolid()) {
                return y + 1.05;
            }
        }
        try {
            int hy = world.getHighestBlockYAt(bx, bz);
            if (Math.abs(hy - py) <= 24) {
                return hy + 1.05;
            }
        } catch (Exception ignored) {}
        return playerY + 0.2;
    }

    private void spawnVisibleParticle(Player player, World world, double x, double z, double playerY, Particle.DustOptions dust) {
        double groundY = findGroundY(world, x, z, playerY);
        if (groundY < world.getMinHeight()) return;

        Location loc = new Location(world, x, groundY + 0.1, z);
        try {
            if (dustParticle.getDataType() == Particle.DustOptions.class) {
                player.spawnParticle(dustParticle, loc, 1, 0.0, 0.0, 0.0, 0.0, dust);
            } else {
                player.spawnParticle(dustParticle, loc, 1, 0.0, 0.0, 0.0, 0.0);
            }
        } catch (Exception e) {
            try {
                player.spawnParticle(Particle.VILLAGER_HAPPY, loc, 1, 0.0, 0.0, 0.0, 0.0);
            } catch (Exception ignored) {}
        }
    }

    private Color parseColor(String hex) {
        if (hex == null || hex.isEmpty()) return Color.fromRGB(255, 170, 0);
        if (hex.startsWith("#")) hex = hex.substring(1);
        try {
            int rgb = Integer.parseInt(hex, 16);
            int r = (rgb >> 16) & 0xFF;
            int g = (rgb >> 8) & 0xFF;
            int b = rgb & 0xFF;

            // Strict filter: never allow green-dominant tints that blend with grass
            if (g > 130 && g > r * 1.1 && g > b * 1.1) {
                return Color.fromRGB(255, 170, 0); // shift to bright warm amber/gold
            }
            if (g > 180 && (r < 100 || b < 100)) {
                return Color.fromRGB(255, 140, 0); // shift to vivid flame orange
            }
            return Color.fromRGB(r, g, b);
        } catch (Exception e) {
            return Color.fromRGB(255, 170, 0);
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

                BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), k -> {
                    BossBar b = Bukkit.createBossBar(
                            "",
                            BarColor.YELLOW,
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
                    
                    reqStr.append(done1 ? "§a✔ " : "§e■ ")
                          .append("§f").append(RussianTranslator.getShortMaterialRu(e1.getKey())).append(": ")
                          .append(done1 ? "§a" : "§e").append(placed1).append("§7/§a").append(need1);
                          
                    if (sortedList.size() > 1) {
                        int idx2 = (idx1 + 1) % sortedList.size();
                        Map.Entry<Material, Integer> e2 = sortedList.get(idx2);
                        int placed2 = building.getPlacedCount(e2.getKey());
                        int need2 = e2.getValue();
                        boolean done2 = placed2 >= need2;
                        
                        reqStr.append(" §8| ")
                              .append(done2 ? "§a✔ " : "§e■ ")
                              .append("§f").append(RussianTranslator.getShortMaterialRu(e2.getKey())).append(": ")
                              .append(done2 ? "§a" : "§e").append(placed2).append("§7/§a").append(need2);
                    }
                }

                String prefix = ChatColor.GOLD + "⚡ [" + building.getTownName() + "] " + ChatColor.YELLOW + bpName + ChatColor.DARK_GRAY + " | ";
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
    }
}
