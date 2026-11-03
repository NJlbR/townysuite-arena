package com.towny.explosion.util;

import com.towny.explosion.TownyExplosionUnblockerPlugin;
import org.bukkit.Location;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.FallingBlock;
import org.bukkit.entity.TNTPrimed;

import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Universal Artillery & Cannon Weapon Detector.
 * 
 * Rules:
 * 1. During an ACTIVE SIEGE (ШТУРМ), ALL artillery weapons (мортиры, пушки, осадные орудия,
 *    снаряды SiegeCannons, Cannons, осадный TNT) are fully unlocked to break blocks
 *    and scatter blocks across the complete feature set of SiegeCannons.
 * 2. Outside an active siege, all artillery damage and flying block scattering are 100% blocked.
 */
public class CannonDetector {

    private final TownyExplosionUnblockerPlugin plugin;
    private final Set<UUID> trackedArtilleryProjectiles = ConcurrentHashMap.newKeySet();
    private final Map<Location, Long> recentCannonImpacts = new ConcurrentHashMap<>();

    public CannonDetector(TownyExplosionUnblockerPlugin plugin) {
        this.plugin = plugin;
    }

    public void trackSpawnedEntity(Entity entity) {
        if (entity == null) return;
        UUID uuid = entity.getUniqueId();
        
        if (isArtilleryWeapon(entity)) {
            trackedArtilleryProjectiles.add(uuid);
        }
    }

    public void untrack(UUID uuid) {
        if (uuid == null) return;
        trackedArtilleryProjectiles.remove(uuid);
    }

    /**
     * Universal Artillery Weapon Check:
     * Returns true for ANY artillery/cannon weapon:
     * - Mortars (мортиры)
     * - SiegeCannons & Cannons (пушки, ядра, снаряды)
     * - Siege artillery & custom shells
     * - TNT / FallingBlocks launched as projectiles
     * 
     * Returns false strictly for non-artillery vanilla griefing (Creepers, End Crystals, Withers, Beds, Anchors).
     */
    public boolean isArtilleryWeapon(Entity entity) {
        if (entity == null) return true; // Plugin custom explosion (world.createExplosion)

        EntityType type = entity.getType();
        if (isBlacklistedVanillaEntity(type)) {
            return false;
        }

        UUID uuid = entity.getUniqueId();
        if (trackedArtilleryProjectiles.contains(uuid)) {
            return true;
        }

        // 1. Custom Name check
        String customName = entity.getCustomName();
        if (customName != null) {
            String lower = customName.toLowerCase();
            if (lower.contains("пушк") || lower.contains("cannon") ||
                lower.contains("мортир") || lower.contains("mortar") ||
                lower.contains("снаряд") || lower.contains("ядро") ||
                lower.contains("осад") || lower.contains("siege") ||
                lower.contains("артиллер") || lower.contains("artillery")) {
                return true;
            }
        }

        // 2. Scoreboard tags check
        Set<String> tags = entity.getScoreboardTags();
        if (tags != null) {
            for (String tag : tags) {
                if (tag != null) {
                    String lower = tag.toLowerCase();
                    if (lower.contains("cannon") || lower.contains("mortar") ||
                        lower.contains("siege") || lower.contains("artillery") ||
                        lower.contains("projectile") || lower.contains("shot") ||
                        lower.contains("shell") || lower.contains("debris")) {
                        return true;
                    }
                }
            }
        }

        // 3. Metadata check
        try {
            if (entity.hasMetadata("siege_cannon_shell") || entity.hasMetadata("siege_armor_piercing") ||
                entity.hasMetadata("cannon") || entity.hasMetadata("cannonball") ||
                entity.hasMetadata("siegecannon") || entity.hasMetadata("siege") ||
                entity.hasMetadata("mortar") || entity.hasMetadata("mortar_shell") ||
                entity.hasMetadata("siege_mortar") || entity.hasMetadata("is_mortar") ||
                entity.hasMetadata("projectile") || entity.hasMetadata("cannons:projectile")) {
                return true;
            }

            List<String> metaKeys = plugin.getConfig().getStringList("detection.mortar-metadata-keys");
            for (String key : metaKeys) {
                if (key != null && entity.hasMetadata(key)) {
                    return true;
                }
            }
        } catch (Throwable ignored) {}

        // 4. TNT or FallingBlock (cannon projectiles and launched blocks)
        if (entity instanceof TNTPrimed || entity instanceof FallingBlock) {
            return true;
        }

        return false;
    }

    public boolean isMortarProjectile(Entity entity) {
        return isArtilleryWeapon(entity);
    }

    public boolean isCannonOrSiegeProjectile(Entity entity) {
        return isArtilleryWeapon(entity);
    }

    public boolean isCannonProjectile(Entity entity) {
        return isArtilleryWeapon(entity);
    }

    /**
     * Record a cannon impact or explosion point to suppress flying block debris in radius outside siege.
     */
    public void recordCannonImpact(Location loc) {
        if (loc == null) return;
        recentCannonImpacts.put(loc.clone(), System.currentTimeMillis());
        cleanOldImpacts();
    }

    /**
     * Checks if a location is within suppression distance of a recent cannon impact.
     */
    public boolean isNearRecentCannonImpact(Location loc, double radius) {
        if (loc == null || loc.getWorld() == null) return false;
        cleanOldImpacts();

        long now = System.currentTimeMillis();
        double radiusSq = radius * radius;

        for (Map.Entry<Location, Long> entry : recentCannonImpacts.entrySet()) {
            Location impactLoc = entry.getKey();
            if (impactLoc.getWorld() != null && impactLoc.getWorld().equals(loc.getWorld())) {
                if (now - entry.getValue() < 6000L) { // within 6 seconds
                    if (impactLoc.distanceSquared(loc) <= radiusSq) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    private void cleanOldImpacts() {
        long now = System.currentTimeMillis();
        Iterator<Map.Entry<Location, Long>> it = recentCannonImpacts.entrySet().iterator();
        while (it.hasNext()) {
            if (now - it.next().getValue() > 8000L) {
                it.remove();
            }
        }
    }

    public boolean isBlacklistedVanillaEntity(EntityType type) {
        if (type == null) return false;
        String name = type.name();
        return name.equals("CREEPER") ||
               name.equals("ENDER_CRYSTAL") ||
               name.equals("END_CRYSTAL") ||
               name.equals("WITHER") ||
               name.equals("WITHER_SKULL") ||
               name.equals("WIND_CHARGE") ||
               name.equals("BREEZE_WIND_CHARGE");
    }
}
