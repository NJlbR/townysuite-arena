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

    /** Updates edge displays independently and more frequently than ambient particles. */
    public void renderWireframes() {
        if (!plugin.getConfig().getBoolean("settings.hologram.wireframe.enabled", true)) {
            clearWireframeDisplays();
            return;
        }

        Collection<ActiveBuilding> activeBuildings = plugin.getBuildingManager().getActiveBuildings();
        Map<World, Set<String>> opaqueCellsByWorld = new IdentityHashMap<>();
        for (Player player : Bukkit.getOnlinePlayers()) {
            if (!hasParticlesEnabled(player)) {
                clearWireframeDisplays(player);
                continue;
            }
            World world = player.getWorld();
            if (world == null) {
                clearWireframeDisplays(player);
                continue;
            }

            Location playerLocation = player.getLocation();
            double playerX = playerLocation.getX();
            double playerZ = playerLocation.getZ();
            Set<String> desiredSegments = new HashSet<>();
            Set<String> opaqueDisplayCells = null;

            for (ActiveBuilding building : activeBuildings) {
                if (building.getStatus() != ActiveBuilding.Status.CONSTRUCTING
                        || !world.getName().equals(building.getWorldName())
                        || building.getAssignedChunks().isEmpty()
                        || plugin.getBuildingManager().getBlueprint(building.getBlueprintId()) == null) continue;

                int minChunkX = Integer.MAX_VALUE, maxChunkX = Integer.MIN_VALUE;
                int minChunkZ = Integer.MAX_VALUE, maxChunkZ = Integer.MIN_VALUE;
                for (ChunkCoord chunk : building.getAssignedChunks()) {
                    minChunkX = Math.min(minChunkX, chunk.getX());
                    maxChunkX = Math.max(maxChunkX, chunk.getX());
                    minChunkZ = Math.min(minChunkZ, chunk.getZ());
                    maxChunkZ = Math.max(maxChunkZ, chunk.getZ());
                }
                double minX = (minChunkX << 4) - 48.0;
                double maxX = ((maxChunkX + 1) << 4) + 48.0;
                double minZ = (minChunkZ << 4) - 48.0;
                double maxZ = ((maxChunkZ + 1) << 4) + 48.0;
                if (playerX < minX || playerX > maxX || playerZ < minZ || playerZ > maxZ) continue;

                BuildingSchematic schematic = plugin.getSchematicManager().getSchematic(building.getBlueprintId());
                if (schematic == null) continue;
                if (opaqueDisplayCells == null) {
                    opaqueDisplayCells = opaqueCellsByWorld.computeIfAbsent(world,
                            plugin.getHologramDisplayManager()::getOpaqueDisplayCellKeys);
                }
                renderLayerWireframes(player, world, building, schematic, desiredSegments, opaqueDisplayCells);
            }
            syncWireframeDisplays(player, desiredSegments);
        }
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
                if (bld.isBlockCompleted(dx, dy, dz)) return TYPE_OTHER_LAYER;
                // A correct physical block that has not yet been reconciled as
                // completed still belongs to the active layer and needs its edge.
                if (BuildingManager.isMaterialMatch(mat, sb.getMaterial())) return TYPE_HOLOGRAM;
                return TYPE_OBSTACLE;
            }
        }
        return TYPE_OBSTACLE;
    }

    private BlockData getBlockDataAtCell(World world, ActiveBuilding bld, BuildingSchematic schem,
                                         int x, int y, int z, Set<String> opaqueDisplayCells) {
        if (y < world.getMinHeight() || y >= world.getMaxHeight()) return null;
        org.bukkit.block.Block block = world.getBlockAt(x, y, z);
        Material material = block.getType();
        if (!material.isAir() && material != Material.WATER && material != Material.LAVA) {
            return block.getBlockData();
        }
        int[] local = BuildingManager.unrotateRelativeCoords(
                x - bld.getOriginX(), z - bld.getOriginZ(), bld.getRotationDeg(),
                schem.getWidthX(), schem.getLengthZ());
        SchematicBlock target = schem.getBlock(local[0], y - bld.getOriginY(), local[1]);
        if (target != null && !bld.isBlockCompleted(local[0], y - bld.getOriginY(), local[1])) {
            return plugin.getHologramDisplayManager().getRotatedSchematicBlockData(target, bld.getRotationDeg());
        }
        // A stale/non-schematic display has no model metadata available here.
        return null;
    }

    private Collection<BoundingBox> getCellCollisionBoxes(World world, ActiveBuilding bld,
                                                           BuildingSchematic schem, int x, int y, int z,
                                                           Set<String> opaqueDisplayCells,
                                                           Map<String, Collection<BoundingBox>> shapeCache) {
        String key = cellKey(x, y, z);
        Collection<BoundingBox> cached = shapeCache.get(key);
        if (cached != null) return cached;
        if (y < world.getMinHeight() || y >= world.getMaxHeight()) return Collections.emptyList();
        if (!world.isChunkLoaded(x >> 4, z >> 4)) {
            return Collections.singletonList(new BoundingBox(0, 0, 0, 1, 1, 1));
        }
        org.bukkit.block.Block block = world.getBlockAt(x, y, z);
        Material material = block.getType();
        boolean physicalOccupancy = !material.isAir() && material != Material.WATER && material != Material.LAVA;
        boolean displayOccupancy = opaqueDisplayCells.contains(key);
        Collection<BoundingBox> boxes;
        if (!physicalOccupancy && !displayOccupancy) {
            // A schematic block in a future/unspawned layer is not an occluder.
            boxes = Collections.emptyList();
        } else {
            BlockData data = physicalOccupancy
                    ? block.getBlockData()
                    : getBlockDataAtCell(world, bld, schem, x, y, z, opaqueDisplayCells);
            if (data == null) {
                boxes = displayOccupancy
                        ? Collections.singletonList(new BoundingBox(0, 0, 0, 1, 1, 1))
                        : Collections.emptyList();
            } else {
                try {
                    boxes = data.getCollisionShape(new Location(world, x, y, z)).getBoundingBoxes();
                } catch (Exception ignored) {
                    boxes = Collections.singletonList(new BoundingBox(0, 0, 0, 1, 1, 1));
                }
            }
        }
        shapeCache.put(key, boxes);
        return boxes;
    }

    private boolean isFullCubeShape(Collection<BoundingBox> boxes) {
        if (boxes.size() != 1) return false;
        BoundingBox box = boxes.iterator().next();
        double epsilon = 1.0e-5;
        return box.getMinX() <= epsilon && box.getMinY() <= epsilon && box.getMinZ() <= epsilon
                && box.getMaxX() >= 1.0 - epsilon && box.getMaxY() >= 1.0 - epsilon
                && box.getMaxZ() >= 1.0 - epsilon;
    }

    private boolean isFullCubeCell(World world, ActiveBuilding bld, BuildingSchematic schem,
                                   int x, int y, int z, Set<String> opaqueDisplayCells,
                                   Map<String, Collection<BoundingBox>> shapeCache) {
        if (y < world.getMinHeight() || y >= world.getMaxHeight()) return false;
        // Unknown cells must not suppress an otherwise visible face.
        if (!world.isChunkLoaded(x >> 4, z >> 4)) return false;
        return isFullCubeShape(getCellCollisionBoxes(world, bld, schem, x, y, z,
                opaqueDisplayCells, shapeCache));
    }

    private boolean rayIntersectsBox(double ox, double oy, double oz,
                                     double dx, double dy, double dz,
                                     double startT, double endT,
                                     int cellX, int cellY, int cellZ, BoundingBox box) {
        double minX = cellX + box.getMinX(), maxX = cellX + box.getMaxX();
        double minY = cellY + box.getMinY(), maxY = cellY + box.getMaxY();
        double minZ = cellZ + box.getMinZ(), maxZ = cellZ + box.getMaxZ();
        double enter = startT, exit = endT;
        double epsilon = 1.0e-9;

        if (Math.abs(dx) < epsilon) {
            if (ox <= minX + epsilon || ox >= maxX - epsilon) return false;
        } else {
            double a = (minX - ox) / dx, b = (maxX - ox) / dx;
            if (a > b) { double swap = a; a = b; b = swap; }
            enter = Math.max(enter, a); exit = Math.min(exit, b);
            if (exit - enter <= epsilon) return false;
        }
        if (Math.abs(dy) < epsilon) {
            if (oy <= minY + epsilon || oy >= maxY - epsilon) return false;
        } else {
            double a = (minY - oy) / dy, b = (maxY - oy) / dy;
            if (a > b) { double swap = a; a = b; b = swap; }
            enter = Math.max(enter, a); exit = Math.min(exit, b);
            if (exit - enter <= epsilon) return false;
        }
        if (Math.abs(dz) < epsilon) {
            if (oz <= minZ + epsilon || oz >= maxZ - epsilon) return false;
        } else {
            double a = (minZ - oz) / dz, b = (maxZ - oz) / dz;
            if (a > b) { double swap = a; a = b; b = swap; }
            enter = Math.max(enter, a); exit = Math.min(exit, b);
            if (exit - enter <= epsilon) return false;
        }
        return exit - enter > epsilon;
    }

    /** Tests actual block collision boxes along the ray, not whole voxel cells. */
    private boolean isOpaqueForWireframe(World world, int x, int y, int z,
                                         double ox, double oy, double oz,
                                         double dx, double dy, double dz,
                                         double startT, double endT,
                                         ActiveBuilding bld, BuildingSchematic schem,
                                         Set<String> opaqueDisplayCells,
                                         Map<String, Collection<BoundingBox>> shapeCache) {
        if (y < world.getMinHeight() || y >= world.getMaxHeight()) return false;
        if (!world.isChunkLoaded(x >> 4, z >> 4)) return true;
        Collection<BoundingBox> boxes = getCellCollisionBoxes(world, bld, schem, x, y, z,
                opaqueDisplayCells, shapeCache);
        for (BoundingBox box : boxes) {
            if (rayIntersectsBox(ox, oy, oz, dx, dy, dz, startT, endT, x, y, z, box)) return true;
        }
        return false;
    }

    /** True only when no collision shape lies between the eye and this point. */
    private boolean hasWireframeLineOfSight(Player player, World world, double x, double y, double z,
                                            int sourceX, int sourceY, int sourceZ,
                                            ActiveBuilding bld, BuildingSchematic schem,
                                            Set<String> opaqueDisplayCells,
                                            Map<String, Collection<BoundingBox>> shapeCache) {
        Location eye = player.getEyeLocation();
        double ox = eye.getX(), oy = eye.getY(), oz = eye.getZ();
        double dx = x - ox, dy = y - oy, dz = z - oz;
        double distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
        // Keep model glow available throughout the active building area. The
        // renderer already bounds buildings spatially, so a short arbitrary
        // ray-distance cutoff made valid previews vanish while backing away.
        if (distance < 0.001) return true;
        int bx = (int) Math.floor(ox), by = (int) Math.floor(oy), bz = (int) Math.floor(oz);
        double invX = dx == 0.0 ? Double.POSITIVE_INFINITY : Math.abs(1.0 / dx);
        double invY = dy == 0.0 ? Double.POSITIVE_INFINITY : Math.abs(1.0 / dy);
        double invZ = dz == 0.0 ? Double.POSITIVE_INFINITY : Math.abs(1.0 / dz);
        int stepX = Double.compare(dx, 0.0), stepY = Double.compare(dy, 0.0), stepZ = Double.compare(dz, 0.0);
        double maxX = dx == 0.0 ? Double.POSITIVE_INFINITY : ((stepX > 0 ? bx + 1.0 - ox : ox - bx) * invX);
        double maxY = dy == 0.0 ? Double.POSITIVE_INFINITY : ((stepY > 0 ? by + 1.0 - oy : oy - by) * invY);
        double maxZ = dz == 0.0 ? Double.POSITIVE_INFINITY : ((stepZ > 0 ? bz + 1.0 - oz : oz - bz) * invZ);

        // Amanatides-Woo cell traversal bounds the work, while each cell is
        // occluding only where its actual VoxelShape intersects the ray.
        final double tieEpsilon = 1.0e-10;
        double cellEnter = 0.0;
        boolean firstCell = true;
        for (int traversed = 0; traversed < 512; traversed++) {
            double nextT = Math.min(maxX, Math.min(maxY, maxZ));
            double cellExit = Math.min(1.0, nextT);
            if (!firstCell && !(bx == sourceX && by == sourceY && bz == sourceZ)
                    && isOpaqueForWireframe(world, bx, by, bz, ox, oy, oz, dx, dy, dz,
                    cellEnter, cellExit, bld, schem, opaqueDisplayCells, shapeCache)) return false;
            if (nextT >= 1.0) return true;

            if (Math.abs(maxX - nextT) <= tieEpsilon) { bx += stepX; maxX += invX; }
            if (Math.abs(maxY - nextT) <= tieEpsilon) { by += stepY; maxY += invY; }
            if (Math.abs(maxZ - nextT) <= tieEpsilon) { bz += stepZ; maxZ += invZ; }
            cellEnter = nextT;
            firstCell = false;
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
        double edgeX = b[0] - a[0], edgeY = b[1] - a[1], edgeZ = b[2] - a[2];
        double midX = (a[0] + b[0]) * 0.5;
        double midY = (a[1] + b[1]) * 0.5;
        double midZ = (a[2] + b[2]) * 0.5;
        Location eye = player.getEyeLocation();
        double viewX = eye.getX() - midX;
        double viewY = eye.getY() - midY;
        double viewZ = eye.getZ() - midZ;

        // Choose the face-normal axis most directly toward the viewer while
        // keeping the rod on the same geometric edge.
        int normalX = 0, normalY = 0, normalZ = 0;
        if (Math.abs(edgeX) >= Math.abs(edgeY) && Math.abs(edgeX) >= Math.abs(edgeZ)) {
            if (Math.abs(viewY) >= Math.abs(viewZ)) normalY = viewY >= 0.0 ? 1 : -1;
            else normalZ = viewZ >= 0.0 ? 1 : -1;
        } else if (Math.abs(edgeY) >= Math.abs(edgeZ)) {
            if (Math.abs(viewX) >= Math.abs(viewZ)) normalX = viewX >= 0.0 ? 1 : -1;
            else normalZ = viewZ >= 0.0 ? 1 : -1;
        } else {
            if (Math.abs(viewX) >= Math.abs(viewY)) normalX = viewX >= 0.0 ? 1 : -1;
            else normalY = viewY >= 0.0 ? 1 : -1;
        }
        String key = wireframeSegmentKey(buildingId, a, b, color)
                + "|view:" + normalX + "," + normalY + "," + normalZ;
        if (!desiredSegments.add(key)) return;

        Map<String, BlockDisplay> playerDisplays = playerWireframeDisplays.computeIfAbsent(
                player.getUniqueId(), ignored -> new HashMap<>());
        BlockDisplay existing = playerDisplays.get(key);
        if (existing != null && existing.isValid() && !existing.isDead()) return;

        float thickness = getWireframeThickness();
        // Lift the solid rod just beyond its source face. Without this tiny
        // offset, depth testing lets the hologram BlockDisplay itself cover
        // parts of its matching edge (most noticeably on selected full cubes).
        double surfaceOffset = thickness / 2.0 + 0.002;
        double offsetX = normalX * surfaceOffset;
        double offsetY = normalY * surfaceOffset;
        double offsetZ = normalZ * surfaceOffset;
        double ax = a[0] + offsetX, ay = a[1] + offsetY, az = a[2] + offsetZ;
        double bx = b[0] + offsetX, by = b[1] + offsetY, bz = b[2] + offsetZ;
        double dx = bx - ax, dy = by - ay, dz = bz - az;
        double length = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (length < 0.005) return;

        Vector3f direction = new Vector3f((float) dx, (float) dy, (float) dz).normalize();
        Quaternionf rotation = new Quaternionf().rotationTo(new Vector3f(1.0f, 0.0f, 0.0f), direction);
        Vector3f translation = rotation.transform(new Vector3f(
                (float) length / 2.0f, thickness / 2.0f, thickness / 2.0f)).negate();
        Vector3f scale = new Vector3f((float) length, thickness, thickness);
        Location spawnLocation = new Location(world,
                (ax + bx) / 2.0, (ay + by) / 2.0, (az + bz) / 2.0);

        try {
            BlockDisplay display = world.spawn(spawnLocation, BlockDisplay.class, entity -> {
                // Solid concrete avoids patterned pixels on diagonal rod edges.
                // Full-block edge markers are real, depth-tested geometry. Do not use the
                // entity glow outline here: Minecraft intentionally renders that through walls.
                Material lineMaterial = color.getRed() > color.getBlue()
                        ? Material.RED_CONCRETE
                        : Material.LIGHT_BLUE_CONCRETE;
                entity.setBlock(lineMaterial.createBlockData());
                entity.setBrightness(new Display.Brightness(15, 15));
                entity.setViewRange(2.0f);
                entity.setShadowRadius(0.0f);
                entity.setShadowStrength(0.0f);
                entity.setInterpolationDuration(0);
                entity.setTeleportDuration(0);
                entity.setTransformation(new Transformation(
                        translation,
                        new AxisAngle4f(rotation),
                        scale,
                        new AxisAngle4f()));
                // Intentionally no glowing outline: it is x-ray rendered by Minecraft.
                entity.setGlowing(false);
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

    /**
     * Glowing entities are outlined through walls by Minecraft. Only create/show a
     * model display when at least one point on that actual block shape is visible.
     */
    private boolean isBlockModelVisible(Player player, World world, int blockX, int blockY, int blockZ,
                                        Collection<BoundingBox> shape, ActiveBuilding bld,
                                        BuildingSchematic schem, Set<String> opaqueDisplayCells,
                                        Map<String, Collection<BoundingBox>> shapeCache) {
        List<double[]> samples = new ArrayList<>();
        if (shape != null && !shape.isEmpty()) {
            for (BoundingBox box : shape) {
                double minX = Math.min(box.getMaxX(), box.getMinX() + 0.002);
                double maxX = Math.max(box.getMinX(), box.getMaxX() - 0.002);
                double minY = Math.min(box.getMaxY(), box.getMinY() + 0.002);
                double maxY = Math.max(box.getMinY(), box.getMaxY() - 0.002);
                double minZ = Math.min(box.getMaxZ(), box.getMinZ() + 0.002);
                double maxZ = Math.max(box.getMinZ(), box.getMaxZ() - 0.002);
                double cx = (minX + maxX) * 0.5;
                double cy = (minY + maxY) * 0.5;
                double cz = (minZ + maxZ) * 0.5;
                double[] xs = {minX, cx, maxX};
                double[] ys = {minY, cy, maxY};
                double[] zs = {minZ, cz, maxZ};
                // Test box corners as well as face centers. Narrow visible
                // corners are common on stairs, fences and ladder models.
                for (int ix = 0; ix < 3; ix++) {
                    for (int iy = 0; iy < 3; iy++) {
                        for (int iz = 0; iz < 3; iz++) {
                            int centerAxes = (ix == 1 ? 1 : 0) + (iy == 1 ? 1 : 0) + (iz == 1 ? 1 : 0);
                            // Keep the eight corners and six face centers; edge
                            // centers add cost but little extra coverage.
                            if (centerAxes == 1 || centerAxes == 3) continue;
                            samples.add(new double[]{xs[ix], ys[iy], zs[iz]});
                        }
                    }
                }
                samples.add(new double[]{cx, cy, cz});
            }
        }
        if (samples.isEmpty()) {
            // Plants and other zero-collision models still have a real rendered
            // model. Their crossed planes meet around the cell's central axis.
            samples.add(new double[]{0.5, 0.5, 0.5});
            samples.add(new double[]{0.5, 0.2, 0.5});
            samples.add(new double[]{0.5, 0.8, 0.5});
            samples.add(new double[]{0.2, 0.35, 0.2});
            samples.add(new double[]{0.8, 0.65, 0.8});
            samples.add(new double[]{0.2, 0.35, 0.8});
            samples.add(new double[]{0.8, 0.65, 0.2});
        }

        for (double[] sample : samples) {
            if (hasWireframeLineOfSight(player, world,
                    blockX + sample[0], blockY + sample[1], blockZ + sample[2],
                    blockX, blockY, blockZ, bld, schem, opaqueDisplayCells, shapeCache)) return true;
        }
        return false;
    }

    /** Shows the real Minecraft block model with a player-only glow outline. */
    private void showBlockModelGlow(Player player, World world, String buildingId,
                                    int blockX, int blockY, int blockZ,
                                    BlockData blockData, Color color, Set<String> desiredDisplays) {
        String key = "model:" + buildingId + ":" + cellKey(blockX, blockY, blockZ)
                + ":" + blockData.getAsString() + ":" + color.getRed() + ","
                + color.getGreen() + "," + color.getBlue();
        if (!desiredDisplays.add(key)) return;

        Map<String, BlockDisplay> playerDisplays = playerWireframeDisplays.computeIfAbsent(
                player.getUniqueId(), ignored -> new HashMap<>());
        BlockDisplay existing = playerDisplays.get(key);
        if (existing != null && existing.isValid() && !existing.isDead()) return;

        try {
            Location location = new Location(world, blockX, blockY, blockZ);
            BlockDisplay display = world.spawn(location, BlockDisplay.class, entity -> {
                entity.setBlock(blockData);
                entity.setBrightness(new Display.Brightness(15, 15));
                entity.setViewRange(2.0f);
                entity.setShadowRadius(0.0f);
                entity.setShadowStrength(0.0f);
                entity.setInterpolationDuration(0);
                entity.setTeleportDuration(0);
                // Match the schematic hologram's exact transform so plant model
                // offsets and directional geometry overlay the same prototype.
                entity.setTransformation(plugin.getHologramDisplayManager().createBlockTransformation());
                entity.setGlowColorOverride(color);
                entity.setGlowing(true);
                entity.setInvulnerable(true);
                entity.setPersistent(false);
                entity.setVisibleByDefault(false);
            });
            player.showEntity(plugin, display);
            playerDisplays.put(key, display);
        } catch (Exception e) {
            plugin.getLogger().fine("Не удалось подсветить модель блока игроку " + player.getName() + ": " + e.getMessage());
        }
    }

    /**
     * Renders only edges belonging to exposed, camera-facing faces. This is a
     * geometric face/visibility calculation, not a fixed top-plane wireframe.
     */
    private void renderLayerWireframes(Player player, World world, ActiveBuilding bld,
                                       BuildingSchematic schem, Set<String> desiredSegments,
                                       Set<String> opaqueDisplayCells) {
        if (bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) return;

        int effectiveWidth = schem.getWidthX();
        int effectiveLength = schem.getLengthZ();
        if (bld.getRotationDeg() == 90 || bld.getRotationDeg() == 270) {
            effectiveWidth = schem.getLengthZ();
            effectiveLength = schem.getWidthX();
        }

        int minX = bld.getOriginX();
        int maxX = minX + effectiveWidth - 1;
        int minZ = bld.getOriginZ();
        int maxZ = minZ + effectiveLength - 1;
        int layerY = bld.getOriginY() + bld.getCurrentLayer();
        Map<String, Collection<BoundingBox>> shapeCache = new HashMap<>();
        Location eye = player.getEyeLocation();

        for (int x = minX; x <= maxX; x++) {
            for (int z = minZ; z <= maxZ; z++) {
                byte cellType = getCellType(world, bld, schem, x, layerY, z, opaqueDisplayCells);
                if (cellType != TYPE_HOLOGRAM && cellType != TYPE_OBSTACLE) continue;
                Color color = cellType == TYPE_OBSTACLE
                        ? HologramDisplayManager.GLOW_RED
                        : HologramDisplayManager.GLOW_BLUE;

                BlockData blockData = getBlockDataAtCell(world, bld, schem, x, layerY, z, opaqueDisplayCells);
                if (blockData == null) continue;
                Collection<BoundingBox> shape;
                try {
                    shape = blockData.getCollisionShape(new Location(world, x, layerY, z)).getBoundingBoxes();
                } catch (Exception ignored) {
                    // Unknown shapes are treated as non-cubic; only show their actual model if visible.
                    shape = Collections.emptyList();
                }
                if (shape.isEmpty() || !isFullCubeShape(shape)) {
                    if (isBlockModelVisible(player, world, x, layerY, z, shape,
                            bld, schem, opaqueDisplayCells, shapeCache)) {
                        showBlockModelGlow(player, world, bld.getInstanceId(),
                                x, layerY, z, blockData, color, desiredSegments);
                    }
                    continue;
                }

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

                    if (isFullCubeCell(world, bld, schem, x + nx, layerY + ny, z + nz,
                            opaqueDisplayCells, shapeCache)) continue;
                    double facing = (eye.getX() - fx) * nx + (eye.getY() - fy) * ny + (eye.getZ() - fz) * nz;
                    if (facing <= 0.0001) continue;

                    for (int edge = 0; edge < 4; edge++) {
                        // Keep full-block edges at their exact block-space endpoints.
                        // The display's depth-tested body handles occlusion naturally.
                        showWireframeSegment(player, world, bld.getInstanceId(),
                                vertices[edge], vertices[(edge + 1) % 4], color, desiredSegments);
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
