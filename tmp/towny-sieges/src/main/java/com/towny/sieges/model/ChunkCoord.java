package com.towny.sieges.model;

import org.bukkit.Chunk;
import org.bukkit.Location;
import org.bukkit.World;

import java.util.Objects;

public class ChunkCoord {
    private final String world;
    private final int x;
    private final int z;

    public ChunkCoord(String world, int x, int z) {
        this.world = world;
        this.x = x;
        this.z = z;
    }

    public static ChunkCoord fromLocation(Location loc) {
        if (loc == null || loc.getWorld() == null) return null;
        return new ChunkCoord(loc.getWorld().getName(), loc.getBlockX() >> 4, loc.getBlockZ() >> 4);
    }

    public static ChunkCoord fromChunk(Chunk chunk) {
        if (chunk == null) return null;
        return new ChunkCoord(chunk.getWorld().getName(), chunk.getX(), chunk.getZ());
    }

    public String getWorld() {
        return world;
    }

    public int getX() {
        return x;
    }

    public int getZ() {
        return z;
    }

    public boolean isAdjacent(ChunkCoord other) {
        if (other == null || !Objects.equals(this.world, other.world)) return false;
        int dx = Math.abs(this.x - other.x);
        int dz = Math.abs(this.z - other.z);
        return (dx == 1 && dz == 0) || (dx == 0 && dz == 1);
    }

    public double distance(ChunkCoord other) {
        if (other == null || !Objects.equals(this.world, other.world)) return Double.MAX_VALUE;
        double dx = this.x - other.x;
        double dz = this.z - other.z;
        return Math.sqrt(dx * dx + dz * dz);
    }

    public String serialize() {
        return world + ";" + x + ";" + z;
    }

    public static ChunkCoord deserialize(String str) {
        if (str == null || str.isEmpty()) return null;
        String[] parts = str.split(";");
        if (parts.length < 3) return null;
        try {
            return new ChunkCoord(parts[0], Integer.parseInt(parts[1]), Integer.parseInt(parts[2]));
        } catch (NumberFormatException e) {
            return null;
        }
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ChunkCoord that = (ChunkCoord) o;
        return x == that.x && z == that.z && Objects.equals(world, that.world);
    }

    @Override
    public int hashCode() {
        return Objects.hash(world, x, z);
    }

    @Override
    public String toString() {
        return "[" + world + " (" + x + ", " + z + ")]";
    }
}
