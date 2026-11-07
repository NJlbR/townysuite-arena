package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingSchematic;
import com.towny.architecture.model.SchematicBlock;
import org.bukkit.*;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.entity.Entity;
import org.bukkit.block.data.BlockData;
import org.bukkit.block.structure.StructureRotation;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.util.Transformation;
import org.joml.AxisAngle4f;
import org.joml.Vector3f;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class HologramDisplayManager {
    // Saturated colors stay legible against bright terrain and under shader lighting.
    public static final Color GLOW_BLUE = Color.fromRGB(0, 235, 255);
    public static final Color GLOW_RED = Color.fromRGB(255, 35, 45);

    private final TownyArchitecturePlugin plugin;
    private final NamespacedKey hologramKey;
    private final NamespacedKey blockCoordKey;

    // Map: instanceId -> Map<"dx,dy,dz", BlockDisplay>
    private final Map<String, Map<String, BlockDisplay>> activeDisplays = new ConcurrentHashMap<>();

    public HologramDisplayManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
        this.hologramKey = new NamespacedKey(plugin, "hologram_instance");
        this.blockCoordKey = new NamespacedKey(plugin, "hologram_coord");
    }

    private Display.Brightness getConfiguredBrightness() {
        int b = plugin.getConfig().getInt("settings.hologram.brightness-block", 15);
        int s = plugin.getConfig().getInt("settings.hologram.brightness-sky", 15);
        b = Math.max(0, Math.min(15, b));
        s = Math.max(0, Math.min(15, s));
        return new Display.Brightness(b, s);
    }

    /**
     * Creates transformation with exact offset and scale (1.008) for full-size seamless blocks.
     */
    public Transformation createBlockTransformation() {
        return createBlockTransformation(null, 0, 0);
    }

    /**
     * Matches vanilla's coordinate-seeded XZ model offset for small and tall flowers.
     * BlockDisplay does not inherit the offset of the real world block automatically,
     * so apply it to the display pose using the block's world X/Z coordinates.
     */
    public Transformation createBlockTransformation(BlockData data, int blockX, int blockZ) {
        float scale = (float) plugin.getConfig().getDouble("settings.hologram.scale", 1.008);
        if (scale <= 0.5f || scale > 1.2f) {
            scale = 1.008f;
        }
        double flowerOffsetX = 0.0;
        double flowerOffsetZ = 0.0;
        if (data != null && (Tag.SMALL_FLOWERS.isTagged(data.getMaterial())
                || Tag.TALL_FLOWERS.isTagged(data.getMaterial()))) {
            // Mirrors Mth.getSeed(x, 0, z), including Java long overflow.
            long seed = (long) (blockX * 3129871) ^ (long) blockZ * 116129781L;
            seed = seed * seed * 42317861L + seed * 11L;
            float xFraction = (float) (seed >> 16 & 15L) / 15.0F;
            float zFraction = (float) (seed >> 24 & 15L) / 15.0F;
            flowerOffsetX = ((double) xFraction - 0.5D) * 0.5D;
            flowerOffsetZ = ((double) zFraction - 0.5D) * 0.5D;
        }
        float scaleOffset = (1.0f - scale) / 2.0f;
        return new Transformation(
                new Vector3f(scaleOffset + (float) flowerOffsetX, scaleOffset,
                        scaleOffset + (float) flowerOffsetZ),
                new AxisAngle4f(),
                new Vector3f(scale, scale, scale),
                new AxisAngle4f()
        );
    }

    private void applyBlockTransformation(BlockDisplay display) {
        Location location = display.getLocation();
        display.setTransformation(createBlockTransformation(
                display.getBlock(), location.getBlockX(), location.getBlockZ()));
    }

    /** Applies the same structure orientation to preview data and HUD model overlays. */
    public BlockData getRotatedSchematicBlockData(SchematicBlock schematicBlock, int rotationDeg) {
        BlockData data = schematicBlock.getMaterial().createBlockData();
        switch (Math.floorMod(rotationDeg, 360)) {
            case 90:
                data.rotate(StructureRotation.COUNTERCLOCKWISE_90);
                break;
            case 180:
                data.rotate(StructureRotation.CLOCKWISE_180);
                break;
            case 270:
                data.rotate(StructureRotation.CLOCKWISE_90);
                break;
            default:
                break;
        }
        return data;
    }

    /**
     * Initializes holograms for an active building (spawns the current active layer)
     */
    public void initHologramsForBuilding(ActiveBuilding bld) {
        clearHologramsForBuilding(bld.getInstanceId());
        if (bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
            return; // Never show holograms for completed or non-constructing buildings!
        }
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return;

        World world = Bukkit.getWorld(bld.getWorldName());
        if (world == null) return;

        int targetLayer = bld.getCurrentLayer();
        while (targetLayer <= schem.getMaxLayer()) {
            List<SchematicBlock> lBlocks = schem.getBlocksAtLayer(targetLayer);
            if (lBlocks != null && !lBlocks.isEmpty()) {
                boolean hasUncompleted = false;
                for (SchematicBlock sb : lBlocks) {
                    if (!bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                        hasUncompleted = true;
                        break;
                    }
                }
                if (hasUncompleted) {
                    break;
                }
            }
            targetLayer++;
        }

        if (targetLayer > schem.getMaxLayer()) {
            return;
        }
        bld.setCurrentLayer(targetLayer);
        spawnLayerHolograms(bld, schem, world, targetLayer);
    }

    /**
     * Spawns holograms for a specific layer that haven't been completed yet
     */
    public void spawnLayerHolograms(ActiveBuilding bld, BuildingSchematic schem, World world, int layerY) {
        Map<String, BlockDisplay> buildingMap = activeDisplays.computeIfAbsent(bld.getInstanceId(), k -> new ConcurrentHashMap<>());

        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(layerY);
        for (SchematicBlock sb : layerBlocks) {
            String coordKey = sb.getKey();
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                continue; // Already placed in world!
            }
            if (buildingMap.containsKey(coordKey)) {
                BlockDisplay old = buildingMap.get(coordKey);
                if (old != null && old.isValid() && !old.isDead()) {
                    continue; // Already has valid display entity
                }
            }

            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            Location spawnLoc = new Location(world, 
                    bld.getOriginX() + rPos[0],
                    bld.getOriginY() + sb.getDy(),
                    bld.getOriginZ() + rPos[1]);

            // If block is already completed or already physically placed in world, mark and skip
            if (BuildingManager.isMaterialMatch(world.getBlockAt(spawnLoc).getType(), sb.getMaterial())) {
                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                bld.addPlacedBlock(sb.getMaterial());
                continue;
            }

            try {
                org.bukkit.block.Block worldBlock = world.getBlockAt(spawnLoc);
                Material worldMat = worldBlock.getType();
                boolean isObstacle = !worldMat.isAir() && !(worldMat == Material.WATER || worldMat == Material.LAVA) && !BuildingManager.isMaterialMatch(worldMat, sb.getMaterial());

                BlockDisplay display = world.spawn(spawnLoc, BlockDisplay.class, entity -> {
                    if (isObstacle) {
                        entity.setBlock(worldBlock.getBlockData());
                        entity.setGlowColorOverride(GLOW_RED);
                    } else {
                        entity.setBlock(getRotatedSchematicBlockData(sb, bld.getRotationDeg()));
                        entity.setGlowColorOverride(GLOW_BLUE);
                    }
                    entity.setBrightness(getConfiguredBrightness());
                    entity.setShadowRadius(0f);
                    entity.setShadowStrength(0f);
                    entity.setInterpolationDuration(0);
                    entity.setTeleportDuration(0);
                    
                    applyBlockTransformation(entity);
                    entity.setGlowing(false);
                    entity.setInvulnerable(true);
                    
                    entity.getPersistentDataContainer().set(hologramKey, PersistentDataType.STRING, bld.getInstanceId());
                    entity.getPersistentDataContainer().set(blockCoordKey, PersistentDataType.STRING, coordKey);
                    entity.setPersistent(false);
                });
                buildingMap.put(coordKey, display);
            } catch (Exception e) {
                plugin.getLogger().warning("Ошибка спавна BlockDisplay в " + spawnLoc + ": " + e.getMessage());
            }
        }

        // Spawn red obstacle glowing displays for foreign blocks inside building footprint at layerY
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
        int layerWorldY = bld.getOriginY() + layerY;

        Set<String> schematicBlockWorldCoords = new HashSet<>();
        for (SchematicBlock sb : layerBlocks) {
            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            schematicBlockWorldCoords.add((bld.getOriginX() + rPos[0]) + "," + (bld.getOriginZ() + rPos[1]));
        }

        for (int bx = minX; bx <= maxX; bx++) {
            for (int bz = minZ; bz <= maxZ; bz++) {
                if (schematicBlockWorldCoords.contains(bx + "," + bz)) continue;
                org.bukkit.block.Block worldBlock = world.getBlockAt(bx, layerWorldY, bz);
                Material worldMat = worldBlock.getType();
                if (!worldMat.isAir() && !(worldMat == Material.WATER || worldMat == Material.LAVA)) {
                    String obsKey = "obs_" + bx + "_" + layerWorldY + "_" + bz;
                    if (buildingMap.containsKey(obsKey)) {
                        BlockDisplay old = buildingMap.get(obsKey);
                        if (old != null && old.isValid() && !old.isDead()) continue;
                    }
                    Location obsLoc = new Location(world, bx, layerWorldY, bz);
                    try {
                        BlockDisplay display = world.spawn(obsLoc, BlockDisplay.class, entity -> {
                            entity.setBlock(worldBlock.getBlockData());
                            entity.setGlowColorOverride(GLOW_RED);
                            entity.setBrightness(getConfiguredBrightness());
                            entity.setShadowRadius(0f);
                            entity.setShadowStrength(0f);
                            entity.setInterpolationDuration(0);
                            entity.setTeleportDuration(0);
                            applyBlockTransformation(entity);
                            entity.setGlowing(false);
                            entity.setInvulnerable(true);
                            entity.getPersistentDataContainer().set(hologramKey, PersistentDataType.STRING, bld.getInstanceId());
                            entity.getPersistentDataContainer().set(blockCoordKey, PersistentDataType.STRING, obsKey);
                            entity.setPersistent(false);
                        });
                        buildingMap.put(obsKey, display);
                    } catch (Exception ignored) {}
                }
            }
        }
    }

    /**
     * Checks if all blocks of the current layer are finished (both in memory and in the physical world)
     * and advances the building to subsequent layers if complete.
     */
    public boolean checkAndAdvanceLayer(ActiveBuilding bld, BuildingSchematic schem, World world) {
        if (bld == null || schem == null || world == null) return false;

        int currentLayer = bld.getCurrentLayer();
        boolean layerDone = true;
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(currentLayer);

        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                continue;
            }
            // Verify physical world block at calculated coordinate
            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            int wx = bld.getOriginX() + rPos[0];
            int wy = bld.getOriginY() + sb.getDy();
            int wz = bld.getOriginZ() + rPos[1];

            if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                Material wm = world.getBlockAt(wx, wy, wz).getType();
                if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                    bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                    bld.addPlacedBlock(sb.getMaterial());
                    continue;
                }
            }
            layerDone = false;
            break;
        }

        if (!layerDone) {
            return false;
        }

        // Layer is complete! Advance forward!
        clearHologramsForBuilding(bld.getInstanceId());

        while (layerDone && currentLayer < schem.getMaxLayer()) {
            currentLayer++;
            bld.setCurrentLayer(currentLayer);

            layerDone = true;
            for (SchematicBlock sb : schem.getBlocksAtLayer(currentLayer)) {
                if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                    continue;
                }
                int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
                int wx = bld.getOriginX() + rPos[0];
                int wy = bld.getOriginY() + sb.getDy();
                int wz = bld.getOriginZ() + rPos[1];
                if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                    Material wm = world.getBlockAt(wx, wy, wz).getType();
                    if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                        bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                        bld.addPlacedBlock(sb.getMaterial());
                        continue;
                    }
                }
                layerDone = false;
                break;
            }

            if (!layerDone) {
                spawnLayerHolograms(bld, schem, world, currentLayer);
                Location loc = new Location(world,
                        bld.getOriginX() + (schem.getWidthX() / 2),
                        bld.getOriginY() + currentLayer,
                        bld.getOriginZ() + (schem.getLengthZ() / 2));
                world.playSound(loc, Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.3f);
                return true; // Successfully advanced to next layer!
            }
        }

        if (layerDone && currentLayer >= schem.getMaxLayer()) {
            clearHologramsForBuilding(bld.getInstanceId());
            return true;
        }
        return false;
    }

    /**
     * Handles when a correct block was placed: removes the single hologram and checks layer progression
     */
    public boolean handleBlockPlaced(ActiveBuilding bld, int dx, int dy, int dz) {
        String coordKey = dx + "," + dy + "," + dz;
        Map<String, BlockDisplay> map = activeDisplays.get(bld.getInstanceId());
        if (map != null) {
            BlockDisplay display = map.remove(coordKey);
            if (display != null && display.isValid()) {
                display.remove();
            }
        }

        if (bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
            // When repairing damaged/active building, placing the block only removes that single hologram.
            // Do NOT call checkAndAdvanceLayer which would wipe holograms of other layers!
            return false;
        }

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return false;

        World world = Bukkit.getWorld(bld.getWorldName());
        // The placed display was removed above and checkAndAdvanceLayer handles
        // spawning the next layer. Avoid rescanning every cell on each placement;
        // the periodic watchdog remains responsible for repairing stale displays.
        return checkAndAdvanceLayer(bld, schem, world);
    }

    /**
     * Called when a block is placed or broken anywhere within an active building plot:
     * instantly updates hologram glow color (Red <-> Blue) or respawns if missing.
     */
    public void onWorldBlockChanged(ActiveBuilding bld, Location loc) {
        if (bld == null || loc == null) return;
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return;

        int rx = loc.getBlockX() - bld.getOriginX();
        int dy = loc.getBlockY() - bld.getOriginY();
        int rz = loc.getBlockZ() - bld.getOriginZ();

        int[] unrot = BuildingManager.unrotateRelativeCoords(rx, rz, bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
        int dx = unrot[0];
        int dz = unrot[1];

        if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING && dy > bld.getCurrentLayer()) return; // only unlocked layers (dy <= currentLayer) have active holograms in construction

        Map<String, BlockDisplay> map = activeDisplays.get(bld.getInstanceId());
        World world = loc.getWorld();
        if (world == null) return;

        org.bukkit.block.Block worldBlock = world.getBlockAt(loc);
        Material wm = worldBlock.getType();

        SchematicBlock sb = schem.getBlock(dx, dy, dz);
        if (sb == null) {
            // Check if this position is inside the active layer footprint (e.g. foreign block obstacle)
            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING && dy == bld.getCurrentLayer()) {
                String obsKey = "obs_" + loc.getBlockX() + "_" + loc.getBlockY() + "_" + loc.getBlockZ();
                if (map == null) {
                    map = activeDisplays.computeIfAbsent(bld.getInstanceId(), k -> new ConcurrentHashMap<>());
                }
                if (map != null) {
                    if (wm.isAir() || wm == Material.WATER || wm == Material.LAVA) {
                        BlockDisplay disp = map.remove(obsKey);
                        if (disp != null && disp.isValid()) {
                            disp.remove();
                        }
                    } else if (map.containsKey(obsKey)) {
                        BlockDisplay disp = map.get(obsKey);
                        if (disp != null && disp.isValid()) {
                            disp.setBlock(worldBlock.getBlockData());
                            disp.setGlowColorOverride(GLOW_RED);
                            applyBlockTransformation(disp);
                        }
                    } else {
                        // Newly placed foreign block in footprint: spawn glowing red obstacle
                        Location obsLoc = new Location(world, loc.getBlockX(), loc.getBlockY(), loc.getBlockZ());
                        try {
                            BlockDisplay display = world.spawn(obsLoc, BlockDisplay.class, entity -> {
                                entity.setBlock(worldBlock.getBlockData());
                                entity.setGlowColorOverride(GLOW_RED);
                                entity.setBrightness(getConfiguredBrightness());
                                entity.setShadowRadius(0f);
                                entity.setShadowStrength(0f);
                                entity.setInterpolationDuration(0);
                                entity.setTeleportDuration(0);
                                applyBlockTransformation(entity);
                                entity.setGlowing(false);
                                entity.setInvulnerable(true);
                                entity.getPersistentDataContainer().set(hologramKey, PersistentDataType.STRING, bld.getInstanceId());
                                entity.getPersistentDataContainer().set(blockCoordKey, PersistentDataType.STRING, obsKey);
                                entity.setPersistent(false);
                            });
                            map.put(obsKey, display);
                        } catch (Exception ignored) {}
                    }
                }
            }
            return;
        }
        if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
            // Block was placed correctly and matches schematic!
            bld.markBlockCompleted(dx, dy, dz);
            bld.addPlacedBlock(sb.getMaterial());
            if (map != null) {
                BlockDisplay display = map.remove(sb.getKey());
                if (display != null && display.isValid()) {
                    display.remove();
                }
            }
            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                checkAndAdvanceLayer(bld, schem, world);
            } else if (bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                double health = bld.calculateHealthPercent(schem);
                bld.setHealthPercent(health);
                if (health >= 100.0) {
                    bld.setStatus(ActiveBuilding.Status.ACTIVE);
                    clearHologramsForBuilding(bld.getInstanceId());
                }
            }
            return;
        }

        // Block is broken or missing: switch status to DAMAGED if it was ACTIVE!
        bld.markBlockBroken(dx, dy, dz);
        if (bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
            bld.setStatus(ActiveBuilding.Status.DAMAGED);
        }

        // Not completed: determine if obstacle exists
        boolean isObstacle = !wm.isAir() && !(wm == Material.WATER || wm == Material.LAVA);
        if (map != null && map.containsKey(sb.getKey())) {
            BlockDisplay disp = map.get(sb.getKey());
            if (disp != null && disp.isValid() && !disp.isDead()) {
                try {
                    if (isObstacle) {
                        disp.setBlock(worldBlock.getBlockData());
                        disp.setGlowColorOverride(GLOW_RED);
                    } else {
                        disp.setBlock(getRotatedSchematicBlockData(sb, bld.getRotationDeg()));
                        disp.setGlowColorOverride(GLOW_BLUE);
                    }
                    applyBlockTransformation(disp);
                } catch (Throwable ignored) {}
                return;
            }
        }

        // If display was missing, respawn it
        respawnHologramForMissingBlock(bld, dx, dy, dz, sb.getMaterial());
    }

    /**
     * Self-healing watchdog: checks if any holograms for the current layer of a constructing building
     * have been destroyed, despawned, or unloaded, dynamically updates their Red/Blue glowing outlines,
     * and safely respawns them if the chunk is loaded.
     */
    public int healOrRefreshLayerHolograms(ActiveBuilding bld) {
        if (bld == null || bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) return 0;
        World world = Bukkit.getWorld(bld.getWorldName());
        if (world == null) return 0;

        // Ensure chunks are currently loaded in world so we do not force-load distant chunks
        boolean chunkLoaded = false;
        if (bld.getAssignedChunks() != null && !bld.getAssignedChunks().isEmpty()) {
            for (com.towny.architecture.model.ChunkCoord cc : bld.getAssignedChunks()) {
                if (world.isChunkLoaded(cc.getX(), cc.getZ())) {
                    chunkLoaded = true;
                    break;
                }
            }
        } else {
            chunkLoaded = world.isChunkLoaded(bld.getOriginX() >> 4, bld.getOriginZ() >> 4);
        }
        if (!chunkLoaded) return 0;

        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return 0;

        int targetLayer = bld.getCurrentLayer();
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(targetLayer);
        if (layerBlocks == null || layerBlocks.isEmpty()) return 0;

        Map<String, BlockDisplay> buildingMap = activeDisplays.computeIfAbsent(bld.getInstanceId(), k -> new ConcurrentHashMap<>());
        buildingMap.entrySet().removeIf(e -> e.getValue() == null || !e.getValue().isValid() || e.getValue().isDead());

        int healed = 0;
        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                continue;
            }

            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            int wx = bld.getOriginX() + rPos[0];
            int wy = bld.getOriginY() + sb.getDy();
            int wz = bld.getOriginZ() + rPos[1];

            // If block is already physically placed in world, mark and skip
            org.bukkit.block.Block worldBlock = world.getBlockAt(wx, wy, wz);
            Material wm = worldBlock.getType();
            if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                bld.addPlacedBlock(sb.getMaterial());
                BlockDisplay oldDisp = buildingMap.remove(sb.getKey());
                if (oldDisp != null && oldDisp.isValid()) {
                    oldDisp.remove();
                }
                continue;
            }

            boolean isObstacle = !wm.isAir() && !(wm == Material.WATER || wm == Material.LAVA);
            String coordKey = sb.getKey();
            BlockDisplay existing = buildingMap.get(coordKey);
            if (existing == null || !existing.isValid() || existing.isDead()) {
                respawnHologramForMissingBlock(bld, sb.getDx(), sb.getDy(), sb.getDz(), sb.getMaterial());
                healed++;
            } else {
                // Dynamically ensure exact block data & glow color (Red with obstacle block data for Obstacle, Blue with schematic block data for Clean Ghost)
                try {
                    if (isObstacle) {
                        existing.setBlock(worldBlock.getBlockData());
                        existing.setGlowColorOverride(GLOW_RED);
                    } else {
                        existing.setBlock(getRotatedSchematicBlockData(sb, bld.getRotationDeg()));
                        existing.setGlowColorOverride(GLOW_BLUE);
                    }
                    applyBlockTransformation(existing);
                } catch (Throwable ignored) {}
            }
        }

        // Also refresh foreign footprint obstacle displays
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
        int layerWorldY = bld.getOriginY() + targetLayer;

        Set<String> schematicBlockWorldCoords = new HashSet<>();
        for (SchematicBlock sb : layerBlocks) {
            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            schematicBlockWorldCoords.add((bld.getOriginX() + rPos[0]) + "," + (bld.getOriginZ() + rPos[1]));
        }

        for (int bx = minX; bx <= maxX; bx++) {
            for (int bz = minZ; bz <= maxZ; bz++) {
                if (schematicBlockWorldCoords.contains(bx + "," + bz)) continue;
                org.bukkit.block.Block worldBlock = world.getBlockAt(bx, layerWorldY, bz);
                Material worldMat = worldBlock.getType();
                String obsKey = "obs_" + bx + "_" + layerWorldY + "_" + bz;
                if (worldMat.isAir() || worldMat == Material.WATER || worldMat == Material.LAVA) {
                    BlockDisplay old = buildingMap.remove(obsKey);
                    if (old != null && old.isValid()) {
                        old.remove();
                    }
                } else {
                    BlockDisplay existing = buildingMap.get(obsKey);
                    if (existing == null || !existing.isValid() || existing.isDead()) {
                        Location obsLoc = new Location(world, bx, layerWorldY, bz);
                        try {
                            BlockDisplay display = world.spawn(obsLoc, BlockDisplay.class, entity -> {
                                entity.setBlock(worldBlock.getBlockData());
                                entity.setGlowColorOverride(GLOW_RED);
                                entity.setBrightness(getConfiguredBrightness());
                                entity.setShadowRadius(0f);
                                entity.setShadowStrength(0f);
                                entity.setInterpolationDuration(0);
                                entity.setTeleportDuration(0);
                                applyBlockTransformation(entity);
                                entity.setGlowing(false);
                                entity.setInvulnerable(true);
                                entity.getPersistentDataContainer().set(hologramKey, PersistentDataType.STRING, bld.getInstanceId());
                                entity.getPersistentDataContainer().set(blockCoordKey, PersistentDataType.STRING, obsKey);
                                entity.setPersistent(false);
                            });
                            buildingMap.put(obsKey, display);
                        } catch (Exception ignored) {}
                    } else {
                        try {
                            existing.setBlock(worldBlock.getBlockData());
                            existing.setGlowColorOverride(GLOW_RED);
                            applyBlockTransformation(existing);
                        } catch (Throwable ignored) {}
                    }
                }
            }
        }

        return healed;
    }

    public void respawnHologramForMissingBlock(ActiveBuilding bld, int dx, int dy, int dz, Material mat) {
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return;

        SchematicBlock sb = schem.getBlock(dx, dy, dz);
        if (sb == null) return; // Not part of blueprint!

        // If building is still constructing, NEVER spawn holograms for future layers!
        if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING && sb.getDy() > bld.getCurrentLayer()) {
            return;
        }

        World world = Bukkit.getWorld(bld.getWorldName());
        if (world == null) return;

        String coordKey = dx + "," + dy + "," + dz;
        Map<String, BlockDisplay> buildingMap = activeDisplays.computeIfAbsent(bld.getInstanceId(), k -> new ConcurrentHashMap<>());

        int[] rPos = BuildingManager.rotateRelativeCoords(dx, dz, bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
        Location spawnLoc = new Location(world, bld.getOriginX() + rPos[0], bld.getOriginY() + dy, bld.getOriginZ() + rPos[1]);

        org.bukkit.block.Block worldBlock = world.getBlockAt(spawnLoc);
        Material worldMat = worldBlock.getType();

        // If the block is physically present, matches the blueprint, AND was not just marked broken:
        // remove any ghost hologram and keep it completed.
        if (BuildingManager.isMaterialMatch(worldMat, sb.getMaterial())) {
            if (bld.isBlockCompleted(dx, dy, dz)) {
                BlockDisplay existing = buildingMap.remove(coordKey);
                if (existing != null && existing.isValid()) {
                    existing.remove();
                }
                return;
            }
        }

        if (buildingMap.containsKey(coordKey)) {
            BlockDisplay existing = buildingMap.get(coordKey);
            if (existing != null && existing.isValid() && !existing.isDead()) {
                try {
                    boolean isObstacle = !worldMat.isAir() && !(worldMat == Material.WATER || worldMat == Material.LAVA) && !BuildingManager.isMaterialMatch(worldMat, sb.getMaterial());
                    if (isObstacle) {
                        existing.setBlock(worldBlock.getBlockData());
                        existing.setGlowColorOverride(GLOW_RED);
                    } else {
                        existing.setBlock(getRotatedSchematicBlockData(sb, bld.getRotationDeg()));
                        existing.setGlowColorOverride(GLOW_BLUE);
                    }
                    applyBlockTransformation(existing);
                } catch (Throwable ignored) {}
                return;
            } else {
                buildingMap.remove(coordKey);
            }
        }
        
        try {
            boolean isObstacle = !worldMat.isAir() && !(worldMat == Material.WATER || worldMat == Material.LAVA) && !BuildingManager.isMaterialMatch(worldMat, sb.getMaterial());

            BlockDisplay display = world.spawn(spawnLoc, BlockDisplay.class, entity -> {
                if (isObstacle) {
                    entity.setBlock(worldBlock.getBlockData());
                    entity.setGlowColorOverride(GLOW_RED);
                } else {
                    entity.setBlock(getRotatedSchematicBlockData(sb, bld.getRotationDeg()));
                    entity.setGlowColorOverride(GLOW_BLUE);
                }
                entity.setBrightness(getConfiguredBrightness());
                entity.setShadowRadius(0f);
                entity.setShadowStrength(0f);
                entity.setInterpolationDuration(0);
                entity.setTeleportDuration(0);
                
                applyBlockTransformation(entity);
                entity.setGlowing(false);
                entity.setInvulnerable(true);
                
                entity.getPersistentDataContainer().set(hologramKey, PersistentDataType.STRING, bld.getInstanceId());
                entity.getPersistentDataContainer().set(blockCoordKey, PersistentDataType.STRING, coordKey);
                entity.setPersistent(false);
            });
            buildingMap.put(coordKey, display);
        } catch (Exception ignored) {}
    }

    public void clearHologramsForBuilding(String instanceId) {
        Map<String, BlockDisplay> map = activeDisplays.remove(instanceId);
        if (map != null) {
            for (BlockDisplay d : map.values()) {
                if (d != null && d.isValid()) {
                    d.remove();
                }
            }
            map.clear();
        }
    }

    public void clearAll() {
        for (Map<String, BlockDisplay> map : activeDisplays.values()) {
            for (BlockDisplay d : map.values()) {
                if (d != null && d.isValid()) {
                    d.remove();
                }
            }
            map.clear();
        }
        activeDisplays.clear();

        // Also sweep loaded worlds to purge any leftover tagged BlockDisplays
        for (World world : Bukkit.getWorlds()) {
            for (Entity entity : world.getEntitiesByClass(BlockDisplay.class)) {
                if (entity.getPersistentDataContainer().has(hologramKey, PersistentDataType.STRING)) {
                    entity.remove();
                }
            }
        }
    }

    /**
     * Returns the occupied block cells of all active display entities in a world.
     * BlockDisplay entities are not blocks in Bukkit's block map, so rendering and
     * visibility checks must explicitly treat their cells as opaque.
     */
    public Set<String> getOpaqueDisplayCellKeys(World world) {
        if (world == null) return Collections.emptySet();
        Set<String> cells = new HashSet<>();
        for (Map<String, BlockDisplay> buildingDisplays : activeDisplays.values()) {
            for (BlockDisplay display : buildingDisplays.values()) {
                if (display == null || !display.isValid() || display.isDead() || display.getWorld() != world) continue;
                Location location = display.getLocation();
                cells.add(cellKey(location.getBlockX(), location.getBlockY(), location.getBlockZ()));
            }
        }
        return cells;
    }

    private static String cellKey(int x, int y, int z) {
        return x + "," + y + "," + z;
    }

    public NamespacedKey getHologramKey() { return hologramKey; }
    public NamespacedKey getBlockCoordKey() { return blockCoordKey; }
}
