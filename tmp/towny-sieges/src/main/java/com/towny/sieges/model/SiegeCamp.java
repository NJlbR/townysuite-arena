package com.towny.sieges.model;

import java.util.*;

public class SiegeCamp {

    public enum Status {
        PREPARATION,    // 24 hours countdown
        ACTIVE_SIEGE,   // 2 hours active assault (cannons/explosions enabled)
        COMPLETED,      // Siege concluded
        CANCELLED       // Dismantled by mayor or cancelled by admin
    }

    private final String siegeId;
    private final String attackingTown;
    private final String defendingTown;
    private final String mayorName;
    private final String worldName;
    private final Set<ChunkCoord> claimedChunks = new LinkedHashSet<>();
    private final Map<ChunkCoord, PreviousChunkStatus> initialChunkStatuses = new LinkedHashMap<>();
    private final ChunkCoord initialCampChunk;
    private final long createdAtMillis;
    private long preparationEndsAtMillis;
    private long activeEndsAtMillis;
    private Status status;

    public SiegeCamp(String siegeId, String attackingTown, String defendingTown, String mayorName,
                     String worldName, ChunkCoord initialCampChunk,
                     long preparationDurationSeconds, long activeDurationSeconds) {
        this.siegeId = siegeId;
        this.attackingTown = attackingTown;
        this.defendingTown = defendingTown;
        this.mayorName = mayorName;
        this.worldName = worldName;
        this.initialCampChunk = initialCampChunk;
        this.claimedChunks.add(initialCampChunk);
        this.createdAtMillis = System.currentTimeMillis();
        this.preparationEndsAtMillis = this.createdAtMillis + (preparationDurationSeconds * 1000L);
        this.activeEndsAtMillis = this.preparationEndsAtMillis + (activeDurationSeconds * 1000L);
        this.status = Status.PREPARATION;
    }

    // Constructor for loading from data.yml
    public SiegeCamp(String siegeId, String attackingTown, String defendingTown, String mayorName,
                     String worldName, ChunkCoord initialCampChunk, Set<ChunkCoord> claimedChunks,
                     Map<ChunkCoord, PreviousChunkStatus> initialStatuses,
                     long createdAtMillis, long preparationEndsAtMillis, long activeEndsAtMillis, Status status) {
        this.siegeId = siegeId;
        this.attackingTown = attackingTown;
        this.defendingTown = defendingTown;
        this.mayorName = mayorName;
        this.worldName = worldName;
        this.initialCampChunk = initialCampChunk;
        this.claimedChunks.addAll(claimedChunks);
        if (initialStatuses != null) {
            this.initialChunkStatuses.putAll(initialStatuses);
        }
        this.createdAtMillis = createdAtMillis;
        this.preparationEndsAtMillis = preparationEndsAtMillis;
        this.activeEndsAtMillis = activeEndsAtMillis;
        this.status = status;
    }

    public String getSiegeId() {
        return siegeId;
    }

    public String getAttackingTown() {
        return attackingTown;
    }

    public String getDefendingTown() {
        return defendingTown;
    }

    public String getMayorName() {
        return mayorName;
    }

    public String getWorldName() {
        return worldName;
    }

    public ChunkCoord getInitialCampChunk() {
        return initialCampChunk;
    }

    public Set<ChunkCoord> getClaimedChunks() {
        return Collections.unmodifiableSet(claimedChunks);
    }

    public boolean addClaimedChunk(ChunkCoord coord) {
        if (coord != null) {
            return claimedChunks.add(coord);
        }
        return false;
    }

    public boolean addClaimedChunk(ChunkCoord coord, PreviousChunkStatus initialStatus) {
        if (coord != null) {
            boolean added = claimedChunks.add(coord);
            initialChunkStatuses.put(coord, initialStatus != null ? initialStatus : PreviousChunkStatus.WILDERNESS);
            return added;
        }
        return false;
    }

    public PreviousChunkStatus getInitialStatus(ChunkCoord coord) {
        return initialChunkStatuses.getOrDefault(coord, PreviousChunkStatus.WILDERNESS);
    }

    public void setInitialStatus(ChunkCoord coord, PreviousChunkStatus status) {
        if (coord != null && status != null) {
            initialChunkStatuses.put(coord, status);
        }
    }

    public Map<ChunkCoord, PreviousChunkStatus> getInitialChunkStatuses() {
        return Collections.unmodifiableMap(initialChunkStatuses);
    }

    public boolean removeClaimedChunk(ChunkCoord coord) {
        if (coord != null && !coord.equals(initialCampChunk)) {
            claimedChunks.remove(coord);
            initialChunkStatuses.remove(coord);
            return true;
        }
        return false;
    }

    public boolean containsChunk(ChunkCoord coord) {
        return coord != null && claimedChunks.contains(coord);
    }

    public boolean isAdjacentToCamp(ChunkCoord coord) {
        if (coord == null) return false;
        for (ChunkCoord existing : claimedChunks) {
            if (existing.isAdjacent(coord)) {
                return true;
            }
        }
        return false;
    }

    public long getCreatedAtMillis() {
        return createdAtMillis;
    }

    public long getPreparationEndsAtMillis() {
        return preparationEndsAtMillis;
    }

    public void setPreparationEndsAtMillis(long millis) {
        this.preparationEndsAtMillis = millis;
    }

    public long getActiveEndsAtMillis() {
        return activeEndsAtMillis;
    }

    public void setActiveEndsAtMillis(long millis) {
        this.activeEndsAtMillis = millis;
    }

    public Status getStatus() {
        return status;
    }

    public void setStatus(Status status) {
        this.status = status;
    }

    public boolean isPreparationPhase() {
        return status == Status.PREPARATION && System.currentTimeMillis() < preparationEndsAtMillis;
    }

    public boolean isActiveSiege() {
        return status == Status.ACTIVE_SIEGE && System.currentTimeMillis() < activeEndsAtMillis;
    }

    public long getRemainingPreparationSeconds() {
        long rem = (preparationEndsAtMillis - System.currentTimeMillis()) / 1000L;
        return Math.max(0, rem);
    }

    public long getRemainingActiveSeconds() {
        long rem = (activeEndsAtMillis - System.currentTimeMillis()) / 1000L;
        return Math.max(0, rem);
    }

    public String getFormattedRemainingTime() {
        long sec = isPreparationPhase() ? getRemainingPreparationSeconds() : getRemainingActiveSeconds();
        long hours = sec / 3600;
        long minutes = (sec % 3600) / 60;
        long seconds = sec % 60;
        if (hours > 0) {
            return String.format("%02d:%02d:%02d", hours, minutes, seconds);
        } else {
            return String.format("%02d:%02d", minutes, seconds);
        }
    }
}
