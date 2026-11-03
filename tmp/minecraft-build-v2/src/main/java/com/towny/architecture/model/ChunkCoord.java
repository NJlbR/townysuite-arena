package com.towny.architecture.model;

import org.bukkit.Chunk;
import org.bukkit.Location;
import org.bukkit.World;

import java.util.Objects;

public class ChunkCoord {
    private final String worldName;
    private final int x;
    private final int z;

    public ChunkCoord(String worldName, int x, int z) {
        this.worldName = worldName != null ? worldName : "world";
        this.x = x;
        this.z = z;
    }

    public ChunkCoord(int x, int z) {
        this("world", x, z);
    }

    public static ChunkCoord fromChunk(Chunk chunk) {
        return new ChunkCoord(chunk.getWorld().getName(), chunk.getX(), chunk.getZ());
    }

    public static ChunkCoord fromLocation(Location loc) {
        String w = loc.getWorld() != null ? loc.getWorld().getName() : "world";
        return new ChunkCoord(w, loc.getBlockX() >> 4, loc.getBlockZ() >> 4);
    }

    public String getWorldName() {
        return worldName;
    }

    public int getX() {
        return x;
    }

    public int getZ() {
        return z;
    }

    public int getMinBlockX() {
        return x << 4;
    }

    public int getMaxBlockX() {
        return (x << 4) + 15;
    }

    public int getMinBlockZ() {
        return z << 4;
    }

    public int getMaxBlockZ() {
        return (z << 4) + 15;
    }

    public boolean contains(Location loc) {
        if (loc.getWorld() == null || !loc.getWorld().getName().equals(worldName)) {
            return false;
        }
        int cx = loc.getBlockX() >> 4;
        int cz = loc.getBlockZ() >> 4;
        return this.x == cx && this.z == cz;
    }

    public String serialize() {
        return worldName + ":" + x + ":" + z;
    }

    public static ChunkCoord deserialize(String str) {
        if (str == null || !str.contains(":")) return null;
        String[] parts = str.split(":");
        if (parts.length >= 3) {
            try {
                return new ChunkCoord(parts[0], Integer.parseInt(parts[1]), Integer.parseInt(parts[2]));
            } catch (NumberFormatException ignored) {}
        }
        return null;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ChunkCoord that = (ChunkCoord) o;
        return x == that.x && z == that.z && Objects.equals(worldName, that.worldName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(worldName, x, z);
    }

    @Override
    public String toString() {
        return "[" + x + "," + z + "]";
    }
}
