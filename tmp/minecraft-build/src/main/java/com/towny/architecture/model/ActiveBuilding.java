package com.towny.architecture.model;

import org.bukkit.Location;
import org.bukkit.Material;

import java.util.*;

public class ActiveBuilding {
    public enum Status {
        CONSTRUCTING,
        ACTIVE,
        DAMAGED
    }

    private final String instanceId;
    private final String blueprintId;
    private final String townName;
    private final UUID placedBy;
    private final String worldName;
    private final Set<ChunkCoord> assignedChunks;
    private final Map<Material, Integer> requiredMaterials;
    private final Map<Material, Integer> placedMaterials;
    private final Map<Material, Integer> maxPlacedMaterials; // TRACKS historical max for XP

    private double healthPercent;
    private Status status;
    private final long createdAt;

    public ActiveBuilding(
            String instanceId,
            String blueprintId,
            String townName,
            UUID placedBy,
            String worldName,
            Set<ChunkCoord> assignedChunks,
            Map<Material, Integer> requiredMaterials) {
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

    public String getInstanceId() { return instanceId; }
    public String getBlueprintId() { return blueprintId; }
    public String getTownName() { return townName; }
    public UUID getPlacedBy() { return placedBy; }
    public String getWorldName() { return worldName; }
    public Set<ChunkCoord> getAssignedChunks() { return Collections.unmodifiableSet(assignedChunks); }
    public Map<Material, Integer> getRequiredMaterials() { return Collections.unmodifiableMap(requiredMaterials); }
    public Map<Material, Integer> getPlacedMaterials() { return Collections.unmodifiableMap(placedMaterials); }
    public double getHealthPercent() { return healthPercent; }
    public void setHealthPercent(double healthPercent) { this.healthPercent = healthPercent; }
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
            return true; // Indicates new max was reached within required quota (XP should be awarded)
        }
        return false; // Not a new max or beyond required quota
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

    /**
     * Total placed blocks capped at required count per material.
     * Prevents surplus of one material from artificially inflating progress/health for missing materials.
     */
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
        int placed = getEffectivePlacedBlocks();
        return Math.min(100, (int) ((placed * 100.0) / req));
    }

    public double calculateHealthPercent() {
        int req = getTotalRequiredBlocks();
        if (req <= 0) return 100.0;
        int placed = getEffectivePlacedBlocks();
        return Math.max(0.0, Math.min(100.0, ((double) placed / req) * 100.0));
    }

    public boolean isFullyBuilt() {
        for (Map.Entry<Material, Integer> entry : requiredMaterials.entrySet()) {
            int placed = placedMaterials.getOrDefault(entry.getKey(), 0);
            if (placed < entry.getValue()) {
                return false;
            }
        }
        return true;
    }
}
