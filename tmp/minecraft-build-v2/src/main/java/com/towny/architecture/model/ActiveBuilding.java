package com.towny.architecture.model;

import org.bukkit.Location;
import org.bukkit.Material;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class ActiveBuilding {
    public enum Status {
        CONSTRUCTING,
        ACTIVE,
        DAMAGED,
        ENTOMBED
    }

    private final String instanceId;
    private final String blueprintId;
    private String townName;
    private final UUID placedBy;
    private final String worldName;
    private final Set<ChunkCoord> assignedChunks;
    private final Map<Material, Integer> requiredMaterials;
    private final Map<Material, Integer> placedMaterials;
    private final Map<Material, Integer> maxPlacedMaterials;

    // v2.0.0 Schematic Anchor Coordinates
    private int originX;
    private int originY;
    private int originZ;
    private int rotationDeg = 0;
    private int currentLayer = 0;
    private final Set<String> completedBlocks = ConcurrentHashMap.newKeySet();

    private double healthPercent;
    private double exteriorExposurePercent = 100.0;
    private Status status;
    private final long createdAt;

    public ActiveBuilding(
            String instanceId,
            String blueprintId,
            String townName,
            UUID placedBy,
            String worldName,
            Set<ChunkCoord> assignedChunks,
            Map<Material, Integer> requiredMaterials,
            int originX,
            int originY,
            int originZ) {
        this.instanceId = instanceId;
        this.blueprintId = blueprintId;
        this.townName = townName;
        this.placedBy = placedBy;
        this.worldName = worldName != null ? worldName : "world";
        this.assignedChunks = new LinkedHashSet<>(assignedChunks);
        this.requiredMaterials = new LinkedHashMap<>(requiredMaterials);
        this.placedMaterials = new LinkedHashMap<>();
        this.maxPlacedMaterials = new LinkedHashMap<>();
        for (Material mat : requiredMaterials.keySet()) {
            this.placedMaterials.put(mat, 0);
            this.maxPlacedMaterials.put(mat, 0);
        }
        this.originX = originX;
        this.originY = originY;
        this.originZ = originZ;
        this.currentLayer = 0;
        this.healthPercent = 100.0;
        this.status = Status.CONSTRUCTING;
        this.createdAt = System.currentTimeMillis();
    }

    public boolean contains(Location loc) {
        if (loc.getWorld() == null || !loc.getWorld().getName().equals(worldName)) {
            return false;
        }
        ChunkCoord cc = ChunkCoord.fromLocation(loc);
        return assignedChunks.contains(cc);
    }

    public boolean occupiesChunk(ChunkCoord cc) {
        if (cc == null || !cc.getWorldName().equals(worldName)) {
            return false;
        }
        return assignedChunks.contains(cc);
    }

    public int getOriginX() { return originX; }
    public int getOriginY() { return originY; }
    public int getOriginZ() { return originZ; }
    public void setOrigin(int x, int y, int z) {
        this.originX = x;
        this.originY = y;
        this.originZ = z;
    }

    public int getRotationDeg() { return rotationDeg; }
    public void setRotationDeg(int rotationDeg) { this.rotationDeg = rotationDeg; }

    public int getCurrentLayer() { return currentLayer; }
    public void setCurrentLayer(int currentLayer) { this.currentLayer = currentLayer; }

    public boolean isBlockCompleted(int dx, int dy, int dz) {
        return completedBlocks.contains(dx + "," + dy + "," + dz);
    }

    public void markBlockCompleted(int dx, int dy, int dz) {
        completedBlocks.add(dx + "," + dy + "," + dz);
    }

    public void markBlockBroken(int dx, int dy, int dz) {
        completedBlocks.remove(dx + "," + dy + "," + dz);
    }

    public Set<String> getCompletedBlocks() {
        return Collections.unmodifiableSet(completedBlocks);
    }

    public int getCompletedBlockCount() {
        return completedBlocks.size();
    }

    public String getInstanceId() { return instanceId; }
    public String getBlueprintId() { return blueprintId; }
    public String getTownName() { return townName; }
    public void setTownName(String townName) { this.townName = townName; }
    public UUID getPlacedBy() { return placedBy; }
    public String getWorldName() { return worldName; }
    public Set<ChunkCoord> getAssignedChunks() { return Collections.unmodifiableSet(assignedChunks); }
    public Map<Material, Integer> getRequiredMaterials() { return Collections.unmodifiableMap(requiredMaterials); }
    public Map<Material, Integer> getPlacedMaterials() { return Collections.unmodifiableMap(placedMaterials); }
    public double getHealthPercent() { return healthPercent; }
    public void setHealthPercent(double healthPercent) { this.healthPercent = healthPercent; }
    public double getExteriorExposurePercent() { return exteriorExposurePercent; }
    public void setExteriorExposurePercent(double exteriorExposurePercent) { this.exteriorExposurePercent = exteriorExposurePercent; }
    public Status getStatus() { return status; }
    public void setStatus(Status status) { this.status = status; }
    public long getCreatedAt() { return createdAt; }

    public int getPlacedCount(Material mat) {
        return placedMaterials.getOrDefault(mat, 0);
    }

    public int getRequiredCount(Material mat) {
        return requiredMaterials.getOrDefault(mat, 0);
    }

    public int getMaxPlacedCount(Material mat) {
        return maxPlacedMaterials.getOrDefault(mat, 0);
    }

    public void setMaxPlacedCount(Material mat, int count) {
        maxPlacedMaterials.put(mat, count);
    }

    public synchronized boolean addPlacedBlock(Material mat) {
        if (!requiredMaterials.containsKey(mat)) {
            return false;
        }
        int current = placedMaterials.getOrDefault(mat, 0);
        int target = requiredMaterials.getOrDefault(mat, 0);
        placedMaterials.put(mat, current + 1);

        int currentMax = maxPlacedMaterials.getOrDefault(mat, 0);
        if (current < target && (current + 1) > currentMax) {
            maxPlacedMaterials.put(mat, Math.min(target, current + 1));
            return true;
        }
        return false;
    }

    public synchronized boolean removePlacedBlock(Material mat) {
        if (!requiredMaterials.containsKey(mat)) {
            return false;
        }
        int current = placedMaterials.getOrDefault(mat, 0);
        if (current <= 0) {
            return false;
        }
        placedMaterials.put(mat, current - 1);
        return true;
    }

    public void setPlacedCount(Material mat, int count) {
        placedMaterials.put(mat, Math.max(0, count));
    }

    public int getTotalRequiredBlocks() {
        int sum = 0;
        for (int v : requiredMaterials.values()) sum += v;
        return sum;
    }

    public int getTotalPlacedBlocks() {
        int sum = 0;
        for (int v : placedMaterials.values()) sum += v;
        return sum;
    }

    public int getEffectivePlacedBlocks() {
        int sum = 0;
        for (Map.Entry<Material, Integer> entry : requiredMaterials.entrySet()) {
            int placed = placedMaterials.getOrDefault(entry.getKey(), 0);
            sum += Math.min(placed, entry.getValue());
        }
        return sum;
    }

    public int getProgressPercent() {
        int req = getTotalRequiredBlocks();
        if (req <= 0) return 100;
        int placed = !completedBlocks.isEmpty() ? completedBlocks.size() : getEffectivePlacedBlocks();
        return Math.min(100, (int) ((placed * 100.0) / req));
    }

    public int getProgressPercent(BuildingSchematic schem) {
        int req = (schem != null) ? schem.getTotalBlockCount() : getTotalRequiredBlocks();
        if (req <= 0) return 100;
        int placed = !completedBlocks.isEmpty() ? completedBlocks.size() : getEffectivePlacedBlocks();
        return Math.min(100, (int) ((placed * 100.0) / req));
    }

    public double calculateHealthPercent() {
        int req = getTotalRequiredBlocks();
        if (req <= 0) return 100.0;
        int placed = !completedBlocks.isEmpty() ? completedBlocks.size() : getEffectivePlacedBlocks();
        return Math.max(0.0, Math.min(100.0, ((double) placed / req) * 100.0));
    }

    public double calculateHealthPercent(BuildingSchematic schem) {
        int req = (schem != null) ? schem.getTotalBlockCount() : getTotalRequiredBlocks();
        if (req <= 0) return 100.0;
        int placed = !completedBlocks.isEmpty() ? completedBlocks.size() : getEffectivePlacedBlocks();
        return Math.max(0.0, Math.min(100.0, ((double) placed / req) * 100.0));
    }

    public synchronized void syncPlacedMaterialsFromCompleted(BuildingSchematic schem) {
        if (schem == null) return;
        Map<Material, Integer> counts = new HashMap<>();
        for (SchematicBlock sb : schem.getBlocks()) {
            if (isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                counts.put(sb.getMaterial(), counts.getOrDefault(sb.getMaterial(), 0) + 1);
            }
        }
        for (Map.Entry<Material, Integer> entry : requiredMaterials.entrySet()) {
            int c = counts.getOrDefault(entry.getKey(), 0);
            placedMaterials.put(entry.getKey(), c);
            int maxC = maxPlacedMaterials.getOrDefault(entry.getKey(), 0);
            if (c > maxC) {
                maxPlacedMaterials.put(entry.getKey(), Math.min(entry.getValue(), c));
            }
        }
    }

    public boolean isFullyBuilt() {
        int reqBlocks = getTotalRequiredBlocks();
        if (reqBlocks <= 0) return false;
        if (completedBlocks.size() < reqBlocks) {
            return false;
        }
        if (!requiredMaterials.isEmpty()) {
            for (Map.Entry<Material, Integer> entry : requiredMaterials.entrySet()) {
                int placed = placedMaterials.getOrDefault(entry.getKey(), 0);
                if (placed < entry.getValue()) {
                    return false;
                }
            }
        }
        return true;
    }

    public boolean isFullyBuilt(BuildingSchematic schem) {
        if (schem != null) {
            int total = schem.getTotalBlockCount();
            if (total <= 0) return false;
            if (completedBlocks.size() < total) {
                return false;
            }
            for (SchematicBlock sb : schem.getBlocks()) {
                if (!isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                    return false;
                }
            }
            return true;
        }
        return isFullyBuilt();
    }
}
