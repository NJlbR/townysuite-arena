package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingSchematic;
import com.towny.architecture.model.SchematicBlock;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.ChunkCoord;
import com.towny.architecture.util.ModelShapeUtil;
import com.towny.architecture.util.RussianTranslator;
import org.bukkit.*;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.entity.Player;
import org.bukkit.block.data.BlockData;
import org.bukkit.util.BoundingBox;
import org.bukkit.util.Transformation;
import org.joml.AxisAngle4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.*;

public class BuildingHudManager {
    private final TownyArchitecturePlugin plugin;
    private final Map<UUID, BossBar> playerBossBars = new HashMap<>();
    private final Map<UUID, Integer> playerCycleIndex = new HashMap<>();
    private final Map<UUID, Integer> playerTicksHeld = new HashMap<>();
    private final Set<UUID> playersParticlesDisabled = new HashSet<>();
    private final Set<UUID> playersEffectParticlesDisabled = new HashSet<>();
    private final Map<UUID, Map<String, BlockDisplay>> playerWireframeDisplays = new HashMap<>();

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
        if (!particlesEnabled && !wireframeEnabled) {
            clearWireframeDisplays();
            return;
        }

        int radiusChunks = plugin.getConfig().getInt("settings.buff-1x1-chunk-radius", 2);

        Particle.DustOptions plotAquaDust = new Particle.DustOptions(Color.fromRGB(0, 180, 255), 0.95f);
        Particle.DustOptions footprintCyanDust = new Particle.DustOptions(Color.fromRGB(0, 230, 255), 0.95f);

        for (Player player : Bukkit.getOnlinePlayers()) {
            boolean showBorders = hasParticlesEnabled(player);
            boolean showEffects = hasEffectParticlesEnabled(player);
            if (!showBorders && !showEffects) {
                clearWireframeDisplays(player);
                continue;
            }

            Location pLoc = player.getLocation();
            World pWorld = pLoc.getWorld();
            if (pWorld == null) {
                clearWireframeDisplays(player);
                continue;
            }
            Set<String> desiredWireframeSegments = new HashSet<>();

            double pX = pLoc.getX();
            double pY = pLoc.getY();
            double pZ = pLoc.getZ();

            // 1. Render active building boundaries and effect zones
            try {
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
                    if (showBorders && wireframeEnabled && bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
                        if (schem != null) {
                            if (pX >= bMinX - 48 && pX <= bMaxX + 48 && pZ >= bMinZ - 48 && pZ <= bMaxZ + 48) {
                                try {
                                    renderLayerWireframes(player, pWorld, bld, schem, desiredWireframeSegments);
                                } catch (Throwable failure) {
                                    plugin.getLogger().fine("Не удалось подсветить слой постройки "
                                            + bld.getInstanceId() + ": " + failure.getMessage());
                                }
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

            } catch (Throwable failure) {
                // A broken model/blueprint must never leave stale highlights on the client:
                // the synchronisation below always removes everything that is not desired.
                plugin.getLogger().fine("Ошибка отрисовки подсветки слоя для "
                        + player.getName() + ": " + failure.getMessage());
            }

            syncWireframeDisplays(player, desiredWireframeSegments);

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


    private static String cellKey(int x, int y, int z) {
        return x + "," + y + "," + z;
    }

    private byte getCellType(World world, ActiveBuilding bld, BuildingSchematic schem,
                             int wx, int wy, int wz, Set<String> opaqueDisplayCells) {
        if (bld == null || schem == null || world == null) return TYPE_AIR;

        int layerWorldY = bld.getOriginY() + bld.getCurrentLayer();
        int rx = wx - bld.getOriginX();
        int dy = wy - bld.getOriginY();
        int rz = wz - bld.getOriginZ();

        int[] unrot = BuildingManager.unrotateRelativeCoords(rx, rz, bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
        int dx = unrot[0];
        int dz = unrot[1];
        boolean insideFootprint = dx >= 0 && dx < schem.getWidthX() && dz >= 0 && dz < schem.getLengthZ();

        org.bukkit.block.Block block = world.getBlockAt(wx, wy, wz);
        Material mat = block.getType();
        boolean physicalOccupancy = !mat.isAir() && mat != Material.WATER && mat != Material.LAVA;
        boolean displayOccupancy = opaqueDisplayCells.contains(cellKey(wx, wy, wz));

        if (!physicalOccupancy) {
            if (displayOccupancy) {
                // A display entity occupies its whole logical cell regardless of the
                // rendered block's material or transparency.
                if (wy == layerWorldY && insideFootprint) {
                    SchematicBlock schematicBlock = schem.getBlock(dx, dy, dz);
                    if (schematicBlock != null && !bld.isBlockCompleted(dx, dy, dz)) return TYPE_HOLOGRAM;
                }
                return TYPE_OBSTACLE;
            }
            if (wy == layerWorldY && insideFootprint) {
                SchematicBlock sb = schem.getBlock(dx, dy, dz);
                if (sb != null && !bld.isBlockCompleted(dx, dy, dz)) return TYPE_HOLOGRAM;
            }
            return TYPE_AIR;
        }

        if (wy < layerWorldY) return TYPE_OTHER_LAYER;
        if (wy > layerWorldY) return TYPE_OBSTACLE;
        if (insideFootprint) {
            SchematicBlock sb = schem.getBlock(dx, dy, dz);
            if (sb != null) {
                if (bld.isBlockCompleted(dx, dy, dz) || BuildingManager.isMaterialMatch(mat, sb.getMaterial())) {
                    return TYPE_OTHER_LAYER;
                }
                return TYPE_OBSTACLE;
            }
        }
        return TYPE_OBSTACLE;
    }

    private boolean isAirCell(byte type) {
        return type == TYPE_AIR;
    }

    private boolean isOpaqueForWireframe(World world, int x, int y, int z, Set<String> opaqueDisplayCells) {
        if (opaqueDisplayCells.contains(cellKey(x, y, z))) return true;
        if (y < world.getMinHeight() || y >= world.getMaxHeight()) return false;
        if (!world.isChunkLoaded(x >> 4, z >> 4)) return true; // Unknown geometry is conservatively occluding.
        Material material = world.getBlockAt(x, y, z).getType();
        return !material.isAir() && material != Material.WATER && material != Material.LAVA;
    }

    /** True only when no opaque block/display lies between the eye and this point. */
    private boolean hasWireframeLineOfSight(Player player, World world, double x, double y, double z,
                                            int sourceX, int sourceY, int sourceZ,
                                            Set<String> opaqueDisplayCells) {
        Location eye = player.getEyeLocation();
        double dx = x - eye.getX();
        double dy = y - eye.getY();
        double dz = z - eye.getZ();
        double distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (distance > 64.0) return false;
        if (distance < 0.001) return true;
        int bx = (int) Math.floor(eye.getX());
        int by = (int) Math.floor(eye.getY());
        int bz = (int) Math.floor(eye.getZ());
        double invX = dx == 0.0 ? Double.POSITIVE_INFINITY : Math.abs(1.0 / dx);
        double invY = dy == 0.0 ? Double.POSITIVE_INFINITY : Math.abs(1.0 / dy);
        double invZ = dz == 0.0 ? Double.POSITIVE_INFINITY : Math.abs(1.0 / dz);
        int stepX = Double.compare(dx, 0.0);
        int stepY = Double.compare(dy, 0.0);
        int stepZ = Double.compare(dz, 0.0);
        double maxX = dx == 0.0 ? Double.POSITIVE_INFINITY : ((stepX > 0 ? bx + 1.0 - eye.getX() : eye.getX() - bx) * invX);
        double maxY = dy == 0.0 ? Double.POSITIVE_INFINITY : ((stepY > 0 ? by + 1.0 - eye.getY() : eye.getY() - by) * invY);
        double maxZ = dz == 0.0 ? Double.POSITIVE_INFINITY : ((stepZ > 0 ? bz + 1.0 - eye.getZ() : eye.getZ() - bz) * invZ);

        // Amanatides-Woo traversal. Advance every axis crossed at the same ray
        // parameter together: checking side voxels one-by-one at an exact corner
        // falsely occludes edges from oblique camera angles.
        final double tieEpsilon = 1.0e-10;
        for (int traversed = 0; traversed < 512; traversed++) {
            double nextT = Math.min(maxX, Math.min(maxY, maxZ));
            if (nextT >= 1.0) return true;

            if (Math.abs(maxX - nextT) <= tieEpsilon) {
                bx += stepX;
                maxX += invX;
            }
            if (Math.abs(maxY - nextT) <= tieEpsilon) {
                by += stepY;
                maxY += invY;
            }
            if (Math.abs(maxZ - nextT) <= tieEpsilon) {
                bz += stepZ;
                maxZ += invZ;
            }

            // The target block itself is the surface being outlined, not an occluder.
            if (bx == sourceX && by == sourceY && bz == sourceZ) continue;
            if (isOpaqueForWireframe(world, bx, by, bz, opaqueDisplayCells)) return false;
        }
        return false;
    }

    private String particlePointKey(double x, double y, double z) {
        return Math.round(x * 10000.0) + "," + Math.round(y * 10000.0) + "," + Math.round(z * 10000.0);
    }

    private String wireframeSegmentKey(String buildingId, double[] a, double[] b, Color color) {
        String first = particlePointKey(a[0], a[1], a[2]);
        String second = particlePointKey(b[0], b[1], b[2]);
        if (first.compareTo(second) > 0) {
            String swap = first;
            first = second;
            second = swap;
        }
        return buildingId + "|" + first + "|" + second + "|" + color.asRGB();
    }

    private float getWireframeThickness() {
        double configured = plugin.getConfig().getDouble("settings.hologram.wireframe.line-thickness", 0.035);
        // Old configs used 0.95 as particle density; map that legacy value to a thin display line.
        if (configured <= 0.0 || configured > 0.12) return 0.035f;
        return (float) configured;
    }

    private void showWireframeSegment(Player player, World world, String buildingId,
                                      double[] a, double[] b, Color color,
                                      Set<String> desiredSegments) {
        String key = wireframeSegmentKey(buildingId, a, b, color);
        if (!desiredSegments.add(key)) return;

        Map<String, BlockDisplay> playerDisplays = playerWireframeDisplays.computeIfAbsent(
                player.getUniqueId(), ignored -> new HashMap<>());
        BlockDisplay existing = playerDisplays.get(key);
        if (existing != null && existing.isValid() && !existing.isDead()) return;

        double dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2];
        double length = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (length < 0.005) return;

        float thickness = getWireframeThickness();
        Vector3f direction = new Vector3f((float) dx, (float) dy, (float) dz).normalize();
        Quaternionf rotation = new Quaternionf().rotationTo(new Vector3f(1.0f, 0.0f, 0.0f), direction);
        Vector3f translation = rotation.transform(new Vector3f(
                (float) length / 2.0f, thickness / 2.0f, thickness / 2.0f)).negate();
        Vector3f scale = new Vector3f((float) length, thickness, thickness);
        Location spawnLocation = new Location(world,
                (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (a[2] + b[2]) / 2.0);

        try {
            BlockDisplay display = world.spawn(spawnLocation, BlockDisplay.class, entity -> {
                // A flat neutral texture avoids the patterned sea-lantern pixels
                // showing through as artificial plates on diagonal shape edges.
                entity.setBlock(Material.WHITE_CONCRETE.createBlockData());
                entity.setBrightness(new Display.Brightness(15, 15));
                entity.setShadowRadius(0.0f);
                entity.setShadowStrength(0.0f);
                entity.setInterpolationDuration(0);
                entity.setTeleportDuration(0);
                entity.setTransformation(new Transformation(
                        translation,
                        new AxisAngle4f(rotation),
                        scale,
                        new AxisAngle4f()));
                entity.setGlowColorOverride(color);
                entity.setGlowing(true);
                entity.setInvulnerable(true);
                entity.setPersistent(false);
                entity.setVisibleByDefault(false);
            });
            player.showEntity(plugin, display);
            playerDisplays.put(key, display);
        } catch (Exception e) {
            plugin.getLogger().fine("Не удалось показать контурный сегмент игроку " + player.getName() + ": " + e.getMessage());
        }
    }

    private boolean isWireframePointVisible(Player player, World world, double[] start,
                                            double dx, double dy, double dz, double t,
                                            int sourceX, int sourceY, int sourceZ,
                                            Set<String> opaqueDisplayCells) {
        return hasWireframeLineOfSight(player, world,
                start[0] + dx * t, start[1] + dy * t, start[2] + dz * t,
                sourceX, sourceY, sourceZ, opaqueDisplayCells);
    }

    /**
     * Converts the already-culled geometric edge into a player-only glowing BlockDisplay.
     * Visible intervals are split at occluders so a hologram can never reveal a hidden line.
     */
    private void drawVisibleEdge(Player player, World world, String buildingId,
                                 int sourceX, int sourceY, int sourceZ,
                                 double[] a, double[] b, Color color,
                                 Set<String> desiredSegments, Set<String> opaqueDisplayCells) {
        double dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2];
        double length = Math.sqrt(dx * dx + dy * dy + dz * dz);
        int intervals = Math.max(1, (int) Math.ceil(length / 0.12));
        boolean visibleRun = false;
        double runStart = 0.0;

        for (int i = 0; i < intervals; i++) {
            double t0 = (double) i / intervals;
            double t1 = (double) (i + 1) / intervals;
            // Test interior points, not exact vertices: a ray to a shared voxel
            // boundary can touch an opaque neighbor without entering it.
            double quarter = t0 + (t1 - t0) * 0.25;
            double mid = (t0 + t1) / 2.0;
            double threeQuarter = t0 + (t1 - t0) * 0.75;
            boolean visible = isWireframePointVisible(player, world, a, dx, dy, dz, quarter,
                    sourceX, sourceY, sourceZ, opaqueDisplayCells)
                    && isWireframePointVisible(player, world, a, dx, dy, dz, mid,
                    sourceX, sourceY, sourceZ, opaqueDisplayCells)
                    && isWireframePointVisible(player, world, a, dx, dy, dz, threeQuarter,
                    sourceX, sourceY, sourceZ, opaqueDisplayCells);

            if (visible && !visibleRun) {
                visibleRun = true;
                runStart = t0;
            } else if (!visible && visibleRun) {
                showWireframeSegment(player, world, buildingId,
                        new double[]{a[0] + dx * runStart, a[1] + dy * runStart, a[2] + dz * runStart},
                        new double[]{a[0] + dx * t0, a[1] + dy * t0, a[2] + dz * t0},
                        color, desiredSegments);
                visibleRun = false;
            }
        }
        if (visibleRun) {
            showWireframeSegment(player, world, buildingId,
                    new double[]{a[0] + dx * runStart, a[1] + dy * runStart, a[2] + dz * runStart},
                    b, color, desiredSegments);
        }
    }

    private void syncWireframeDisplays(Player player, Set<String> desiredSegments) {
        Map<String, BlockDisplay> playerDisplays = playerWireframeDisplays.get(player.getUniqueId());
        if (playerDisplays == null) return;
        Iterator<Map.Entry<String, BlockDisplay>> iterator = playerDisplays.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<String, BlockDisplay> entry = iterator.next();
            if (desiredSegments.contains(entry.getKey()) && entry.getValue() != null && entry.getValue().isValid()) continue;
            BlockDisplay display = entry.getValue();
            if (display != null && display.isValid()) {
                player.hideEntity(plugin, display);
                display.remove();
            }
            iterator.remove();
        }
        if (playerDisplays.isEmpty()) playerWireframeDisplays.remove(player.getUniqueId());
    }

    private void clearWireframeDisplays(Player player) {
        Map<String, BlockDisplay> playerDisplays = playerWireframeDisplays.remove(player.getUniqueId());
        if (playerDisplays == null) return;
        for (BlockDisplay display : playerDisplays.values()) {
            if (display != null && display.isValid()) {
                player.hideEntity(plugin, display);
                display.remove();
            }
        }
    }

    private void clearWireframeDisplays() {
        for (Map.Entry<UUID, Map<String, BlockDisplay>> playerEntry : playerWireframeDisplays.entrySet()) {
            Player player = Bukkit.getPlayer(playerEntry.getKey());
            for (BlockDisplay display : playerEntry.getValue().values()) {
                if (display != null && display.isValid()) {
                    if (player != null) player.hideEntity(plugin, display);
                    display.remove();
                }
            }
        }
        playerWireframeDisplays.clear();
    }

    private BlockData getWireframeBlockData(byte cellType, World world, ActiveBuilding bld,
                                            BuildingSchematic schem, int x, int y, int z) {
        if (cellType == TYPE_OBSTACLE) return world.getBlockAt(x, y, z).getBlockData();
        int[] local = BuildingManager.unrotateRelativeCoords(
                x - bld.getOriginX(), z - bld.getOriginZ(), bld.getRotationDeg(),
                schem.getWidthX(), schem.getLengthZ());
        SchematicBlock schematicBlock = schem.getBlock(local[0], y - bld.getOriginY(), local[1]);
        return schematicBlock == null ? null : schematicBlock.getMaterial().createBlockData();
    }

    private static final double FACE_EPSILON = 1.0e-4;

    private static double boxMin(BoundingBox box, int axis) {
        return axis == 0 ? box.getMinX() : axis == 1 ? box.getMinY() : box.getMinZ();
    }

    private static double boxMax(BoundingBox box, int axis) {
        return axis == 0 ? box.getMaxX() : axis == 1 ? box.getMaxY() : box.getMaxZ();
    }

    private static double facePlane(BoundingBox box, int axis, int direction) {
        return direction > 0 ? boxMax(box, axis) : boxMin(box, axis);
    }

    private static boolean isOnCellBoundary(double plane, int direction) {
        return direction > 0 ? plane >= 1.0 - FACE_EPSILON : plane <= FACE_EPSILON;
    }

    /**
     * True when another box of the same model continues behind this face and covers it
     * completely, i.e. the face is internal to the model and must stay invisible.
     */
    private boolean isFaceCoveredBySibling(Collection<BoundingBox> boxes, BoundingBox box,
                                           int axis, int direction) {
        double plane = facePlane(box, axis, direction);
        for (BoundingBox other : boxes) {
            if (other == box) continue;
            boolean continues = direction > 0
                    ? boxMax(other, axis) > plane + FACE_EPSILON && boxMin(other, axis) <= plane + FACE_EPSILON
                    : boxMin(other, axis) < plane - FACE_EPSILON && boxMax(other, axis) >= plane - FACE_EPSILON;
            if (!continues) continue;

            boolean covers = true;
            for (int otherAxis = 0; otherAxis < 3; otherAxis++) {
                if (otherAxis == axis) continue;
                if (boxMin(other, otherAxis) > boxMin(box, otherAxis) + FACE_EPSILON
                        || boxMax(other, otherAxis) < boxMax(box, otherAxis) - FACE_EPSILON) {
                    covers = false;
                    break;
                }
            }
            if (covers) return true;
        }
        return false;
    }

    private static double[][] faceCorners(BoundingBox box, int axis, double plane) {
        double minA = boxMin(box, (axis + 1) % 3);
        double maxA = boxMax(box, (axis + 1) % 3);
        double minB = boxMin(box, (axis + 2) % 3);
        double maxB = boxMax(box, (axis + 2) % 3);
        double[][] corners = new double[4][3];
        corners[0] = corner(axis, plane, minA, minB);
        corners[1] = corner(axis, plane, maxA, minB);
        corners[2] = corner(axis, plane, maxA, maxB);
        corners[3] = corner(axis, plane, minA, maxB);
        return corners;
    }

    private static double[] corner(int axis, double plane, double valueA, double valueB) {
        if (axis == 0) return new double[]{plane, valueA, valueB};
        if (axis == 1) return new double[]{valueB, plane, valueA};
        return new double[]{valueA, valueB, plane};
    }

    /** Draws the four edges of a quad, offset by the given block cell. */
    private void drawQuadOutline(Player player, World world, String buildingId,
                                 int cellX, int cellY, int cellZ, double[][] corners,
                                 Color color, Set<String> desiredSegments, Set<String> opaqueDisplayCells) {
        for (int edge = 0; edge < 4; edge++) {
            double[] from = corners[edge];
            double[] to = corners[(edge + 1) % 4];
            drawVisibleEdge(player, world, buildingId, cellX, cellY, cellZ,
                    new double[]{cellX + from[0], cellY + from[1], cellZ + from[2]},
                    new double[]{cellX + to[0], cellY + to[1], cellZ + to[2]},
                    color, desiredSegments, opaqueDisplayCells);
        }
    }

    /**
     * Highlights the real model of a non-cubic block: only the outer faces of its own box
     * set are outlined, with the same glowing line segments that the cube wireframe uses.
     * A stair therefore glows along its steps, a slab along its half, a sign along its
     * panel - the enclosing 1x1x1 cube is never drawn.
     */
    private void drawModelOutline(Player player, World world, String buildingId,
                                  int cellX, int cellY, int cellZ, List<BoundingBox> boxes,
                                  Location eye, Color color, Set<String> desiredSegments,
                                  Set<String> opaqueDisplayCells) {
        // Hard cap per cell: a single exotic model (or a fence with many arms) may not cost
        // more than a cube wireframe, so layers of hundreds of blocks stay cheap.
        int faceBudget = 8;
        for (BoundingBox box : boxes) {
            for (int axis = 0; axis < 3; axis++) {
                for (int direction = -1; direction <= 1; direction += 2) {
                    if (isFaceCoveredBySibling(boxes, box, axis, direction)) continue;

                    double plane = facePlane(box, axis, direction);
                    if (isOnCellBoundary(plane, direction)) {
                        int neighbourX = cellX + (axis == 0 ? direction : 0);
                        int neighbourY = cellY + (axis == 1 ? direction : 0);
                        int neighbourZ = cellZ + (axis == 2 ? direction : 0);
                        if (isOpaqueForWireframe(world, neighbourX, neighbourY, neighbourZ, opaqueDisplayCells)) {
                            continue; // Face buried in the neighbouring block: nothing to draw.
                        }
                    }

                    double[][] corners = faceCorners(box, axis, plane);
                    double faceCentreX = cellX + axisAverage(corners, 0);
                    double faceCentreY = cellY + axisAverage(corners, 1);
                    double faceCentreZ = cellZ + axisAverage(corners, 2);
                    double facing = (eye.getX() - faceCentreX) * (axis == 0 ? direction : 0)
                            + (eye.getY() - faceCentreY) * (axis == 1 ? direction : 0)
                            + (eye.getZ() - faceCentreZ) * (axis == 2 ? direction : 0);
                    if (facing <= FACE_EPSILON) continue;

                    drawQuadOutline(player, world, buildingId, cellX, cellY, cellZ, corners,
                            color, desiredSegments, opaqueDisplayCells);
                    if (--faceBudget <= 0) return;
                }
            }
        }
    }

    private static double axisAverage(double[][] corners, int axis) {
        double sum = 0.0;
        for (double[] corner : corners) sum += corner[axis];
        return sum / corners.length;
    }

    /**
     * Flowers, grass, saplings and crops are two crossed vertical planes. Their outline is
     * drawn along those planes, so the plant itself glows instead of a box around it.
     */
    private void drawCrossModelOutline(Player player, World world, String buildingId,
                                       int cellX, int cellY, int cellZ, Color color,
                                       Set<String> desiredSegments, Set<String> opaqueDisplayCells) {
        double low = 0.17;
        double high = 0.83;
        double top = 0.85;
        double[][] firstPlane = {
                {low, 0.02, low},
                {high, 0.02, high},
                {high, top, high},
                {low, top, low}
        };
        double[][] secondPlane = {
                {low, 0.02, high},
                {high, 0.02, low},
                {high, top, low},
                {low, top, high}
        };
        drawQuadOutline(player, world, buildingId, cellX, cellY, cellZ, firstPlane,
                color, desiredSegments, opaqueDisplayCells);
        drawQuadOutline(player, world, buildingId, cellX, cellY, cellZ, secondPlane,
                color, desiredSegments, opaqueDisplayCells);
    }

    /**
     * Draws the construction highlight of the current layer.
     *
     * <p>Only blocks that still have to appear (or foreign blocks that must be broken) are
     * highlighted - correctly placed blocks are skipped, so their hint disappears the moment
     * they are built. Blocks that fill their cell keep the classic cube wireframe; blocks
     * whose model only occupies part of the cell (flowers, stairs, slabs, signs, torches,
     * fences, doors) are outlined along their own model volume instead.</p>
     */
    private void renderLayerWireframes(Player player, World world, ActiveBuilding bld, BuildingSchematic schem,
                                       Set<String> desiredWireframeSegments) {
        if (player == null || world == null || bld == null || schem == null) return;

        Location eye = player.getEyeLocation();
        int layerY = bld.getOriginY() + bld.getCurrentLayer();
        Set<String> opaqueDisplayCells = plugin.getHologramDisplayManager() != null
                ? plugin.getHologramDisplayManager().getOpaqueDisplayCellKeys(world)
                : Collections.emptySet();

        int effW = schem.getWidthX();
        int effL = schem.getLengthZ();
        if (bld.getRotationDeg() == 90 || bld.getRotationDeg() == 270) {
            int swap = effW;
            effW = effL;
            effL = swap;
        }

        // Only cells of the building foot print are highlighted: neighbouring terrain
        // must never be painted as an obstacle of this layer.
        int minX = bld.getOriginX();
        int maxX = bld.getOriginX() + effW - 1;
        int minZ = bld.getOriginZ();
        int maxZ = bld.getOriginZ() + effL - 1;

        for (int x = minX; x <= maxX; x++) {
            for (int z = minZ; z <= maxZ; z++) {
                if (!world.isChunkLoaded(x >> 4, z >> 4)) continue;

                byte cellType = getCellType(world, bld, schem, x, layerY, z, opaqueDisplayCells);
                if (isAirCell(cellType)) continue;
                // The block is already placed correctly (or already completed): its hint
                // must disappear, no matter whether the model fills the cell or not.
                if (cellType == TYPE_OTHER_LAYER) continue;

                Color color = cellType == TYPE_OBSTACLE
                        ? HologramDisplayManager.GLOW_RED
                        : HologramDisplayManager.GLOW_BLUE;

                BlockData blockData = getWireframeBlockData(cellType, world, bld, schem, x, layerY, z);
                boolean modelHandled = false;
                if (blockData != null) {
                    try {
                        if (ModelShapeUtil.isCrossModel(blockData.getMaterial())) {
                            drawCrossModelOutline(player, world, bld.getInstanceId(), x, layerY, z,
                                    color, desiredWireframeSegments, opaqueDisplayCells);
                            modelHandled = true;
                        } else {
                            List<BoundingBox> modelShape = ModelShapeUtil.modelBoxes(
                                    blockData, new Location(world, x, layerY, z));
                            if (modelShape.isEmpty()) {
                                // Unknown model geometry: never fake a cube the block does not occupy.
                                modelHandled = true;
                            } else if (!ModelShapeUtil.isSolidBlock(modelShape)) {
                                // Stairs, slabs, signs, torches, fences...: outline the model itself.
                                drawModelOutline(player, world, bld.getInstanceId(), x, layerY, z,
                                        modelShape, eye, color, desiredWireframeSegments, opaqueDisplayCells);
                                modelHandled = true;
                            }
                        }
                    } catch (Throwable failure) {
                        // A single exotic model must never break the whole layer highlight;
                        // the cell falls back to the classic cube outline instead of vanishing.
                        plugin.getLogger().fine("Не удалось построить контур блока " + blockData.getMaterial()
                                + " в " + x + "," + layerY + "," + z + ": " + failure.getMessage());
                    }
                }
                if (modelHandled) continue;

                for (int face = 0; face < 6; face++) {
                    int nx = 0, ny = 0, nz = 0;
                    double[][] vertices;
                    double fx = x + 0.5, fy = layerY + 0.5, fz = z + 0.5;
                    switch (face) {
                        case 0: // +X
                            nx = 1; fx = x + 1.0;
                            vertices = new double[][]{{x+1,layerY,z},{x+1,layerY+1,z},{x+1,layerY+1,z+1},{x+1,layerY,z+1}}; break;
                        case 1: // -X
                            nx = -1; fx = x;
                            vertices = new double[][]{{x,layerY,z},{x,layerY,z+1},{x,layerY+1,z+1},{x,layerY+1,z}}; break;
                        case 2: // +Y
                            ny = 1; fy = layerY + 1.0;
                            vertices = new double[][]{{x,layerY+1,z},{x,layerY+1,z+1},{x+1,layerY+1,z+1},{x+1,layerY+1,z}}; break;
                        case 3: // -Y
                            ny = -1; fy = layerY;
                            vertices = new double[][]{{x,layerY,z},{x+1,layerY,z},{x+1,layerY,z+1},{x,layerY,z+1}}; break;
                        case 4: // +Z
                            nz = 1; fz = z + 1.0;
                            vertices = new double[][]{{x,layerY,z+1},{x+1,layerY,z+1},{x+1,layerY+1,z+1},{x,layerY+1,z+1}}; break;
                        default: // -Z
                            nz = -1; fz = z;
                            vertices = new double[][]{{x,layerY,z},{x,layerY+1,z},{x+1,layerY+1,z},{x+1,layerY,z}}; break;
                    }

                    byte neighborType = getCellType(world, bld, schem, x + nx, layerY + ny, z + nz, opaqueDisplayCells);
                    if (!isAirCell(neighborType)) continue;
                    double facing = (eye.getX() - fx) * nx + (eye.getY() - fy) * ny + (eye.getZ() - fz) * nz;
                    if (facing <= 0.0001) continue;

                    for (int edge = 0; edge < 4; edge++) {
                        drawVisibleEdge(player, world, bld.getInstanceId(), x, layerY, z,
                                vertices[edge], vertices[(edge + 1) % 4], color,
                                desiredWireframeSegments, opaqueDisplayCells);
                    }
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
        clearWireframeDisplays(player);
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
        clearWireframeDisplays();
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
