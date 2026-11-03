package com.towny.respawn.model;

import com.towny.respawn.manager.BedManager;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.configuration.serialization.ConfigurationSerializable;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Represents a registered player bed respawn point.
 * Accurately tracks BOTH blocks of the 2-block bed (HEAD and FOOT)
 * so clicking either block refers to the exact same bed, preventing duplicates
 * and ensuring strictly 1 player can claim a bed.
 */
public class PlayerBed implements ConfigurationSerializable {

    private final UUID id;
    private final UUID ownerUuid;
    private String name;
    private final String worldName;

    // Canonical Head Block coordinates
    private final int headX;
    private final int headY;
    private final int headZ;

    // Connected Foot Block coordinates
    private final int footX;
    private final int footY;
    private final int footZ;

    private final float yaw;
    private final float pitch;
    private final long createdAt;

    public PlayerBed(UUID ownerUuid, String name, Block headBlock, Block footBlock, float yaw, float pitch) {
        this.id = UUID.randomUUID();
        this.ownerUuid = ownerUuid;
        this.name = name;
        this.worldName = headBlock.getWorld() != null ? headBlock.getWorld().getName() : "world";
        this.headX = headBlock.getX();
        this.headY = headBlock.getY();
        this.headZ = headBlock.getZ();

        if (footBlock != null) {
            this.footX = footBlock.getX();
            this.footY = footBlock.getY();
            this.footZ = footBlock.getZ();
        } else {
            this.footX = headX;
            this.footY = headY;
            this.footZ = headZ;
        }

        this.yaw = yaw;
        this.pitch = pitch;
        this.createdAt = System.currentTimeMillis();
    }

    public PlayerBed(UUID id, UUID ownerUuid, String name, String worldName,
                     int headX, int headY, int headZ,
                     int footX, int footY, int footZ,
                     float yaw, float pitch, long createdAt) {
        this.id = id;
        this.ownerUuid = ownerUuid;
        this.name = name;
        this.worldName = worldName;
        this.headX = headX;
        this.headY = headY;
        this.headZ = headZ;
        this.footX = footX;
        this.footY = footY;
        this.footZ = footZ;
        this.yaw = yaw;
        this.pitch = pitch;
        this.createdAt = createdAt;
    }

    public UUID getId() {
        return id;
    }

    public UUID getOwnerUuid() {
        return ownerUuid;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getWorldName() {
        return worldName;
    }

    public int getHeadX() {
        return headX;
    }

    public int getHeadY() {
        return headY;
    }

    public int getHeadZ() {
        return headZ;
    }

    public int getFootX() {
        return footX;
    }

    public int getFootY() {
        return footY;
    }

    public int getFootZ() {
        return footZ;
    }

    public int getBlockX() {
        return headX;
    }

    public int getBlockY() {
        return headY;
    }

    public int getBlockZ() {
        return headZ;
    }

    public float getYaw() {
        return yaw;
    }

    public float getPitch() {
        return pitch;
    }

    public long getCreatedAt() {
        return createdAt;
    }

    public Location getLocation() {
        World world = Bukkit.getWorld(worldName);
        if (world == null) return null;
        return new Location(world, headX + 0.5, headY + 0.1, headZ + 0.5, yaw, pitch);
    }

    /**
     * Checks if this bed matches a given block in the world.
     * Matches if the block is EITHER the HEAD block OR the FOOT block of this bed,
     * or if its canonical head resolves to this bed's head.
     */
    public boolean matchesBlock(Block block) {
        if (block == null || block.getWorld() == null) return false;
        if (!block.getWorld().getName().equalsIgnoreCase(worldName)) return false;

        int bx = block.getX();
        int by = block.getY();
        int bz = block.getZ();

        // 1. Matches HEAD block coordinates directly
        if (bx == headX && by == headY && bz == headZ) {
            return true;
        }

        // 2. Matches FOOT block coordinates directly
        if (bx == footX && by == footY && bz == footZ) {
            return true;
        }

        // 3. Resolve canonical head of the tested block
        Block canonicalHead = BedManager.getCanonicalBedHead(block);
        if (canonicalHead != null) {
            if (canonicalHead.getX() == headX && canonicalHead.getY() == headY && canonicalHead.getZ() == headZ) {
                return true;
            }
        }

        return false;
    }

    public boolean matchesLocation(Location loc) {
        if (loc == null || loc.getWorld() == null) return false;
        return matchesBlock(loc.getBlock());
    }

    @Override
    public Map<String, Object> serialize() {
        Map<String, Object> map = new HashMap<>();
        map.put("id", id.toString());
        map.put("ownerUuid", ownerUuid.toString());
        map.put("name", name);
        map.put("worldName", worldName);
        map.put("headX", headX);
        map.put("headY", headY);
        map.put("headZ", headZ);
        map.put("footX", footX);
        map.put("footY", footY);
        map.put("footZ", footZ);
        map.put("yaw", (double) yaw);
        map.put("pitch", (double) pitch);
        map.put("createdAt", createdAt);
        return map;
    }

    public static PlayerBed deserialize(Map<String, Object> map) {
        UUID id = UUID.fromString((String) map.get("id"));
        UUID ownerUuid = UUID.fromString((String) map.get("ownerUuid"));
        String name = (String) map.get("name");
        String worldName = (String) map.get("worldName");

        int headX;
        int headY;
        int headZ;
        int footX;
        int footY;
        int footZ;

        if (map.containsKey("headX")) {
            headX = ((Number) map.get("headX")).intValue();
            headY = ((Number) map.get("headY")).intValue();
            headZ = ((Number) map.get("headZ")).intValue();
            footX = map.containsKey("footX") ? ((Number) map.get("footX")).intValue() : headX;
            footY = map.containsKey("footY") ? ((Number) map.get("footY")).intValue() : headY;
            footZ = map.containsKey("footZ") ? ((Number) map.get("footZ")).intValue() : headZ;
        } else {
            // Backward compatibility with older serialized format (x, y, z)
            double x = ((Number) map.get("x")).doubleValue();
            double y = ((Number) map.get("y")).doubleValue();
            double z = ((Number) map.get("z")).doubleValue();
            headX = (int) Math.floor(x);
            headY = (int) Math.floor(y);
            headZ = (int) Math.floor(z);
            footX = headX;
            footY = headY;
            footZ = headZ;
        }

        float yaw = map.containsKey("yaw") ? ((Number) map.get("yaw")).floatValue() : 0.0f;
        float pitch = map.containsKey("pitch") ? ((Number) map.get("pitch")).floatValue() : 0.0f;
        long createdAt = ((Number) map.getOrDefault("createdAt", System.currentTimeMillis())).longValue();

        return new PlayerBed(id, ownerUuid, name, worldName, headX, headY, headZ, footX, footY, footZ, yaw, pitch, createdAt);
    }
}
