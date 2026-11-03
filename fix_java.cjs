const fs = require('fs');
const content = fs.readFileSync('./src/data/javaSources.ts', 'utf8');
const newHologramManager = `package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingSchematic;
import com.towny.architecture.model.SchematicBlock;
import com.towny.architecture.model.ChunkCoord;
import org.bukkit.*;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.entity.Entity;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.util.Transformation;
import org.joml.AxisAngle4f;
import org.joml.Vector3f;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class HologramDisplayManager {
    public static final Color GLOW_BLUE = Color.fromRGB(0, 229, 255);
    public static final Color GLOW_RED = Color.fromRGB(255, 30, 30);

    private final TownyArchitecturePlugin plugin;
    private final NamespacedKey hologramKey;
    private final NamespacedKey blockCoordKey;

    private final Map<String, Map<String, BlockDisplay>> activeDisplays = new ConcurrentHashMap<>();

    public HologramDisplayManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
        this.hologramKey = new NamespacedKey(plugin, "hologram_instance");
        this.blockCoordKey = new NamespacedKey(plugin, "hologram_coord");
    }

    private Display.Brightness getConfiguredBrightness() {
        return new Display.Brightness(15, 15);
    }

    public Transformation createBlockTransformation() {
        return new Transformation(
                new Vector3f(0f, 0f, 0f),
                new AxisAngle4f(),
                new Vector3f(1.0f, 1.0f, 1.0f),
                new AxisAngle4f()
        );
    }

    public void initHologramsForBuilding(ActiveBuilding bld) {
        clearHologramsForBuilding(bld.getInstanceId());
        if (bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING && bld.getStatus() != ActiveBuilding.Status.DAMAGED) return;
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return;
        World world = Bukkit.getWorld(bld.getWorldName());
        if (world == null) return;
        int targetLayer = bld.getCurrentLayer();
        if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
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
                    if (hasUncompleted) break;
                }
                targetLayer++;
            }
            if (targetLayer > schem.getMaxLayer()) return;
            bld.setCurrentLayer(targetLayer);
        }
        spawnLayerHolograms(bld, schem, world, targetLayer);
    }

    public void spawnLayerHolograms(ActiveBuilding bld, BuildingSchematic schem, World world, int layerY) {
        int minX = Integer.MAX_VALUE, maxX = -Integer.MAX_VALUE;
        int minZ = Integer.MAX_VALUE, maxZ = -Integer.MAX_VALUE;
        for (ChunkCoord cc : bld.getAssignedChunks()) {
            minX = Math.min(minX, cc.getX() << 4);
            maxX = Math.max(maxX, (cc.getX() + 1) << 4);
            minZ = Math.min(minZ, cc.getZ() << 4);
            maxZ = Math.max(maxZ, (cc.getZ() + 1) << 4);
        }
        for (int x = minX; x < maxX; x++) {
            for (int z = minZ; z < maxZ; z++) {
                Location loc = new Location(world, x, bld.getOriginY() + layerY, z);
                org.bukkit.block.Block b = world.getBlockAt(loc);
                if (b.getType().isAir() || b.getType() == Material.WATER || b.getType() == Material.LAVA) continue;
                int rx = x - bld.getOriginX();
                int rz = z - bld.getOriginZ();
                int[] unrot = com.towny.architecture.manager.BuildingManager.unrotateRelativeCoords(rx, rz, bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
                if (schem.getBlock(unrot[0], layerY, unrot[1]) == null) {
                    respawnHologramForMissingBlock(bld, -999, layerY, -999, b.getType(), loc, "extra_" + x + "_" + layerY + "_" + z);
                }
            }
        }
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(layerY);
        if (layerBlocks == null) return;
        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) continue;
            int[] rPos = com.towny.architecture.manager.BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            Location spawnLoc = new Location(world, bld.getOriginX() + rPos[0], bld.getOriginY() + sb.getDy(), bld.getOriginZ() + rPos[1]);
            if (com.towny.architecture.manager.BuildingManager.isMaterialMatch(world.getBlockAt(spawnLoc).getType(), sb.getMaterial())) {
                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                continue;
            }
            respawnHologramForMissingBlock(bld, sb.getDx(), sb.getDy(), sb.getDz(), sb.getMaterial(), spawnLoc, sb.getKey());
        }
    }

    public void respawnHologramForMissingBlock(ActiveBuilding bld, int dx, int dy, int dz, Material mat, Location loc, String coordKey) {
        Map<String, BlockDisplay> buildingMap = activeDisplays.computeIfAbsent(bld.getInstanceId(), k -> new java.util.concurrent.ConcurrentHashMap<>());
        World world = loc.getWorld();
        if (world == null) return;
        org.bukkit.block.Block worldBlock = world.getBlockAt(loc);
        Material worldMat = worldBlock.getType();
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        boolean isObstacle = !worldMat.isAir() && (schem == null || !com.towny.architecture.manager.BuildingManager.isMaterialMatch(worldMat, mat));
        BlockDisplay existing = buildingMap.get(coordKey);
        if (existing != null && existing.isValid() && !existing.isDead()) {
            if (isObstacle) { existing.setBlock(worldBlock.getBlockData()); existing.setGlowColorOverride(GLOW_RED); }
            else { existing.setBlock(mat.createBlockData()); existing.setGlowColorOverride(GLOW_BLUE); }
            existing.setTransformation(createBlockTransformation());
            return;
        }
        try {
            BlockDisplay display = world.spawn(loc, BlockDisplay.class, entity -> {
                if (isObstacle) { entity.setBlock(worldBlock.getBlockData()); entity.setGlowColorOverride(GLOW_RED); }
                else { entity.setBlock(mat.createBlockData()); entity.setGlowColorOverride(GLOW_BLUE); }
                entity.setBrightness(getConfiguredBrightness());
                entity.setTransformation(createBlockTransformation());
                entity.setGlowing(true);
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
        if (map != null) { for (BlockDisplay d : map.values()) { if (d != null && d.isValid()) d.remove(); } }
    }

    public void clearAll() {
        for (Map<String, BlockDisplay> map : activeDisplays.values()) { for (BlockDisplay d : map.values()) { if (d != null && d.isValid()) d.remove(); } }
        activeDisplays.clear();
        for (World world : Bukkit.getWorlds()) { for (Entity entity : world.getEntitiesByClass(BlockDisplay.class)) { if (entity.getPersistentDataContainer().has(hologramKey, PersistentDataType.STRING)) entity.remove(); } }
    }

    public boolean checkAndAdvanceLayer(ActiveBuilding bld, BuildingSchematic schem, World world) {
        if (bld == null || schem == null || world == null) return false;
        int currentLayer = bld.getCurrentLayer();
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(currentLayer);
        if (layerBlocks == null) return true;
        boolean layerDone = true;
        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) continue;
            int[] rPos = com.towny.architecture.manager.BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            if (com.towny.architecture.manager.BuildingManager.isMaterialMatch(world.getBlockAt(bld.getOriginX() + rPos[0], bld.getOriginY() + sb.getDy(), bld.getOriginZ() + rPos[1]).getType(), sb.getMaterial())) {
                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                continue;
            }
            layerDone = false;
            break;
        }
        if (!layerDone) return false;
        clearHologramsForBuilding(bld.getInstanceId());
        if (currentLayer < schem.getMaxLayer()) {
            bld.setCurrentLayer(currentLayer + 1);
            spawnLayerHolograms(bld, schem, world, currentLayer + 1);
            return true;
        }
        return true;
    }
}`;
const escaped = newHologramManager.replace(/\\/g, '\\\\').replace(/\"/g, '\\"').replace(/\n/g, '\\n');
const managerRegex = /\{\s*"path":\s*"[^"]*HologramDisplayManager\.java",\s*"name":\s*"HologramDisplayManager\.java",\s*"content":\s*"[\s\S]*?",\s*"category":\s*"core"\s*\}/;
const newManagerObj = '{\n    "path": "src/main/java/com/towny/architecture/manager/HologramDisplayManager.java",\n    "name": "HologramDisplayManager.java",\n    "content": "' + escaped + '",\n    "category": "core"\n  }';
let fixedContent = content.replace(managerRegex, newManagerObj);
fixedContent = fixedContent.replace(/TownyArchitecture v" \+ getDescription\(\)\.getVersion\(\) \+ " успешно активирован!/g, 'TownyArchitecture v2.8.9 успешно активирован!');
fs.writeFileSync('./src/data/javaSources.ts', fixedContent);
console.log('Done');
