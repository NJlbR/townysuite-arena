import os

# 1. Update CannonDetector.java
cannon_detector_code = '''package com.towny.explosion.util;

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
 * Strict Mortar & Cannon Artillery Detector with Debris Suppression Tracking.
 * 
 * Rules:
 * 1. Only projectiles explicitly confirmed as Mortars (Мортиры) are permitted
 *    to damage cities during an active siege.
 * 2. All cannon projectiles (SiegeCannons, regular cannons, custom shells) are tracked
 *    to completely neutralize built-in debris/flying block scattering outside of active siege.
 */
public class CannonDetector {

    private final TownyExplosionUnblockerPlugin plugin;
    private final Set<UUID> trackedMortarTnts = ConcurrentHashMap.newKeySet();
    private final Set<UUID> trackedCannonProjectiles = ConcurrentHashMap.newKeySet();
    
    // Recent cannon explosions / impact points (Location -> Timestamp millis)
    private final Map<Location, Long> recentCannonImpacts = new ConcurrentHashMap<>();

    public CannonDetector(TownyExplosionUnblockerPlugin plugin) {
        this.plugin = plugin;
    }

    public void trackSpawnedEntity(Entity entity) {
        if (entity == null) return;
        UUID uuid = entity.getUniqueId();
        
        if (isMortarProjectile(entity)) {
            trackedMortarTnts.add(uuid);
            trackedCannonProjectiles.add(uuid);
            if (plugin.isDebugEnabled()) {
                plugin.getLogger().info("[TRACK] Зарегистрирован снаряд мортиры UUID=" + uuid);
            }
        } else if (isCannonOrSiegeProjectile(entity)) {
            trackedCannonProjectiles.add(uuid);
            if (plugin.isDebugEnabled()) {
                plugin.getLogger().info("[TRACK] Зарегистрирован снаряд пушки SiegeCannon UUID=" + uuid);
            }
        }
    }

    public void untrack(UUID uuid) {
        if (uuid == null) return;
        trackedMortarTnts.remove(uuid);
        trackedCannonProjectiles.remove(uuid);
    }

    /**
     * Strictest Mortar Detection:
     * Returns true ONLY if the entity is an authentic siege mortar projectile.
     */
    public boolean isMortarProjectile(Entity entity) {
        if (entity == null) return false;
        EntityType type = entity.getType();
        if (isBlacklistedVanillaEntity(type)) {
            return false;
        }

        UUID uuid = entity.getUniqueId();
        if (trackedMortarTnts.contains(uuid)) {
            return true;
        }

        // 1. Check Custom Name for mortar keywords (Russian & English)
        String customName = entity.getCustomName();
        if (customName != null) {
            String lower = customName.toLowerCase();
            if (lower.contains("мортир") || lower.contains("mortar")) {
                return true;
            }
        }

        // 2. Check Scoreboard Tags
        Set<String> tags = entity.getScoreboardTags();
        if (tags != null) {
            for (String tag : tags) {
                if (tag != null) {
                    String lower = tag.toLowerCase();
                    if (lower.contains("mortar") || lower.contains("мортир")) {
                        return true;
                    }
                }
            }
        }

        // 3. Check Metadata keys for mortar
        try {
            if (entity.hasMetadata("mortar") || 
                entity.hasMetadata("mortar_shell") || 
                entity.hasMetadata("siege_mortar") ||
                entity.hasMetadata("is_mortar")) {
                return true;
            }

            List<String> metaKeys = plugin.getConfig().getStringList("detection.mortar-metadata-keys");
            for (String key : metaKeys) {
                if (key != null && entity.hasMetadata(key)) {
                    return true;
                }
            }
        } catch (Throwable ignored) {}

        return false;
    }

    /**
     * Comprehensive Cannon & Siege Artillery Detection:
     * Returns true if the entity is ANY cannon projectile (SiegeCannons, regular cannon, mortar).
     */
    public boolean isCannonOrSiegeProjectile(Entity entity) {
        if (entity == null) return false;
        if (isMortarProjectile(entity)) return true;

        UUID uuid = entity.getUniqueId();
        if (trackedCannonProjectiles.contains(uuid)) return true;

        EntityType type = entity.getType();
        if (isBlacklistedVanillaEntity(type)) return false;

        // Custom name check
        String customName = entity.getCustomName();
        if (customName != null) {
            String lower = customName.toLowerCase();
            if (lower.contains("cannon") || lower.contains("пушк") || lower.contains("снаряд") ||
                lower.contains("ядро") || lower.contains("siege") || lower.contains("artillery")) {
                return true;
            }
        }

        // Scoreboard tags check
        Set<String> tags = entity.getScoreboardTags();
        if (tags != null) {
            for (String tag : tags) {
                if (tag != null) {
                    String lower = tag.toLowerCase();
                    if (lower.contains("cannon") || lower.contains("siege") || lower.contains("projectile") ||
                        lower.contains("shot") || lower.contains("shell") || lower.contains("debris")) {
                        return true;
                    }
                }
            }
        }

        // Metadata check
        try {
            if (entity.hasMetadata("cannon") || entity.hasMetadata("cannonball") ||
                entity.hasMetadata("siegecannon") || entity.hasMetadata("siege") ||
                entity.hasMetadata("projectile") || entity.hasMetadata("cannons:projectile")) {
                return true;
            }
        } catch (Throwable ignored) {}

        return false;
    }

    public boolean isCannonProjectile(Entity entity) {
        return isMortarProjectile(entity);
    }

    /**
     * Record a cannon impact or explosion point to suppress flying block debris in radius.
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

    private boolean isBlacklistedVanillaEntity(EntityType type) {
        if (type == null) return true;
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
'''

with open("tmp/towny-explosion-unblocker/src/main/java/com/towny/explosion/util/CannonDetector.java", "w", encoding="utf-8") as f:
    f.write(cannon_detector_code)
print("Updated CannonDetector.java")

# 2. Update CannonExplosionListener.java
cannon_listener_code = '''package com.towny.explosion.listener;

import com.palmergames.bukkit.towny.TownyAPI;
import com.palmergames.bukkit.towny.object.Town;
import com.palmergames.bukkit.towny.object.TownBlock;
import com.towny.explosion.TownyExplosionUnblockerPlugin;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.FallingBlock;
import org.bukkit.entity.Player;
import org.bukkit.entity.TNTPrimed;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.entity.EntityChangeBlockEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.EntitySpawnEvent;
import org.bukkit.event.entity.ProjectileHitEvent;
import org.bukkit.plugin.Plugin;
import org.bukkit.util.Vector;

import java.lang.reflect.Method;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Absolute Cannon Explosion & Block Scattering Controller.
 * 
 * Fundamental Rules:
 * 1. ZERO town damage outside active siege. All explosions in or near non-sieged towns
 *    have their town blocks 100% protected and cleared at EventPriority.LOWEST.
 * 2. Neutralization of SiegeCannons built-in block scattering ("разлет блоков"):
 *    Outside of active siege, all flying block (FallingBlock) debris spawned by cannon
 *    explosions is intercepted, cancelled, removed, and the original block is restored!
 * 3. Flying blocks landing in towns outside active siege (EntityChangeBlockEvent) are cancelled.
 * 4. During an active siege (ACTIVE_SIEGE), ONLY verified mortars (мортиры) are permitted
 *    to damage town blocks. Regular cannons, player TNT, and other weapons CANNOT damage towns.
 */
public class CannonExplosionListener implements Listener {

    private final TownyExplosionUnblockerPlugin plugin;
    private final Map<UUID, List<Block>> capturedBlastBlocks = new ConcurrentHashMap<>();
    private final Map<UUID, Float> capturedYield = new ConcurrentHashMap<>();

    // Set of materials that naturally fall by Minecraft gravity
    private static final Set<Material> NATURAL_GRAVITY_MATERIALS = EnumSet.of(
            Material.SAND, Material.RED_SAND, Material.GRAVEL,
            Material.SUSPICIOUS_SAND, Material.SUSPICIOUS_GRAVEL,
            Material.ANVIL, Material.CHIPPED_ANVIL, Material.DAMAGED_ANVIL,
            Material.DRAGON_EGG, Material.SCAFFOLDING, Material.POINTED_DRIPSTONE,
            Material.WHITE_CONCRETE_POWDER, Material.ORANGE_CONCRETE_POWDER,
            Material.MAGENTA_CONCRETE_POWDER, Material.LIGHT_BLUE_CONCRETE_POWDER,
            Material.YELLOW_CONCRETE_POWDER, Material.LIME_CONCRETE_POWDER,
            Material.PINK_CONCRETE_POWDER, Material.GRAY_CONCRETE_POWDER,
            Material.LIGHT_GRAY_CONCRETE_POWDER, Material.CYAN_CONCRETE_POWDER,
            Material.PURPLE_CONCRETE_POWDER, Material.BLUE_CONCRETE_POWDER,
            Material.BROWN_CONCRETE_POWDER, Material.GREEN_CONCRETE_POWDER,
            Material.RED_CONCRETE_POWDER, Material.BLACK_CONCRETE_POWDER
    );

    public CannonExplosionListener(TownyExplosionUnblockerPlugin plugin) {
        this.plugin = plugin;
    }

    /**
     * Track newly spawned projectiles and intercept flying blocks (разлет блоков) from cannons!
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onEntitySpawnEarly(EntitySpawnEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Entity entity = event.getEntity();
        if (entity == null) return;

        // 1. Track cannon / mortar projectiles
        if (entity instanceof TNTPrimed || plugin.getCannonDetector().isCannonOrSiegeProjectile(entity)) {
            plugin.getCannonDetector().trackSpawnedEntity(entity);
            return;
        }

        // 2. Intercept and neutralize SiegeCannons flying blocks (FallingBlock debris) outside siege!
        if (entity instanceof FallingBlock) {
            handleFallingBlockSpawn(event, (FallingBlock) entity);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onEntitySpawnLate(EntitySpawnEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Entity entity = event.getEntity();
        if (entity instanceof FallingBlock) {
            handleFallingBlockSpawn(event, (FallingBlock) entity);
        }
    }

    /**
     * Intercepts and neutralizes cannon flying blocks / scattered debris outside active siege.
     */
    private void handleFallingBlockSpawn(EntitySpawnEvent event, FallingBlock fb) {
        if (!plugin.getConfig().getBoolean("block-scattering.disable-outside-siege", true)) {
            return;
        }

        Location loc = fb.getLocation();
        Location srcLoc = null;
        try {
            srcLoc = fb.getSourceLoc();
        } catch (Throwable ignored) {}
        if (srcLoc == null) {
            srcLoc = loc;
        }

        boolean locInTown = isLocationInTown(loc);
        boolean srcInTown = isLocationInTown(srcLoc);

        if (!locInTown && !srcInTown) {
            return; // Pure wilderness, outside town boundaries
        }

        String townName = locInTown ? getTownNameAt(loc) : getTownNameAt(srcLoc);
        boolean underSiege = townName != null && isTownUnderActiveSiege(townName);

        // If town is in active siege: mortars are permitted to cause destruction
        if (underSiege) {
            return;
        }

        // TOWN IS NOT IN ACTIVE SIEGE!
        // Determine whether this FallingBlock is cannon debris / artificial flying block:
        Material mat = fb.getBlockData() != null ? fb.getBlockData().getMaterial() : fb.getMaterial();
        Vector vel = fb.getVelocity();
        double hSpeedSq = (vel.getX() * vel.getX()) + (vel.getZ() * vel.getZ());
        boolean hasOutwardVelocity = hSpeedSq > 0.0001 || vel.getY() > 0.01;
        boolean isUnnaturalFallingBlock = mat != null && !NATURAL_GRAVITY_MATERIALS.contains(mat);
        double radius = plugin.getConfig().getDouble("block-scattering.suppression-radius", 35.0);
        boolean nearCannonImpact = plugin.getCannonDetector().isNearRecentCannonImpact(loc, radius) ||
                                   plugin.getCannonDetector().isNearRecentCannonImpact(srcLoc, radius);

        // If it's unnatural block (stone, wood, cobble), or has blast velocity, or is near cannon impact:
        if (isUnnaturalFallingBlock || hasOutwardVelocity || nearCannonImpact) {
            event.setCancelled(true);
            fb.remove();

            if (plugin.isDebugEnabled()) {
                plugin.getLogger().info("[SCATTER-BLOCKED] Подавлен разлет блока " + mat + " в городе '" + townName + "' вне штурма.");
            }

            // RESTORE THE BLOCK if the cannon plugin turned it into AIR when launching it!
            if (plugin.getConfig().getBoolean("block-scattering.restore-scattered-blocks", true)) {
                if (srcLoc.getWorld() != null) {
                    Block srcBlock = srcLoc.getBlock();
                    if (srcBlock.getType().isAir() && fb.getBlockData() != null && !fb.getBlockData().getMaterial().isAir()) {
                        srcBlock.setBlockData(fb.getBlockData(), false);
                    }
                }
                if (loc.getWorld() != null && !loc.equals(srcLoc)) {
                    Block locBlock = loc.getBlock();
                    if (locBlock.getType().isAir() && fb.getBlockData() != null && !fb.getBlockData().getMaterial().isAir()) {
                        locBlock.setBlockData(fb.getBlockData(), false);
                    }
                }
            }
        }
    }

    /**
     * Prevents flying blocks / debris from landing, solidifying, or destroying town blocks outside siege.
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onFallingBlockLand(EntityChangeBlockEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        if (!(event.getEntity() instanceof FallingBlock)) return;

        Block targetBlock = event.getBlock();
        Location targetLoc = targetBlock.getLocation();

        if (isLocationInTown(targetLoc)) {
            String townName = getTownNameAt(targetLoc);
            boolean underSiege = townName != null && isTownUnderActiveSiege(townName);

            if (!underSiege) {
                // Outside siege: NEVER allow falling blocks to replace/break town blocks!
                event.setCancelled(true);
                event.getEntity().remove();
                if (plugin.isDebugEnabled()) {
                    plugin.getLogger().info("[LAND-BLOCKED] Заблокировано приземление FallingBlock в городе '" + townName + "' вне штурма.");
                }
            }
        }
    }

    /**
     * Intercept projectile impact on town blocks outside siege.
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onProjectileHit(ProjectileHitEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Entity projectile = event.getEntity();
        if (projectile == null) return;

        Location hitLoc = event.getHitBlock() != null ? event.getHitBlock().getLocation() : projectile.getLocation();
        if (hitLoc == null) return;

        if (isLocationInTown(hitLoc)) {
            String townName = getTownNameAt(hitLoc);
            boolean underSiege = townName != null && isTownUnderActiveSiege(townName);
            boolean isMortar = plugin.getCannonDetector().isMortarProjectile(projectile);

            if (!underSiege || !isMortar) {
                // Record impact for radius debris suppression
                plugin.getCannonDetector().recordCannonImpact(hitLoc);

                if (plugin.getCannonDetector().isCannonOrSiegeProjectile(projectile)) {
                    event.setCancelled(true);
                    if (projectile instanceof FallingBlock) {
                        projectile.remove();
                    }
                    if (plugin.isDebugEnabled()) {
                        plugin.getLogger().info("[PROJECTILE-HIT-BLOCKED] Попадание пушечного снаряда заблокировано в городе '" + townName + "' вне штурма.");
                    }
                }
            }
        }
    }

    /**
     * Phase 1 (LOWEST Priority):
     * EARLY SUPPRESSION:
     * - Outside active siege, OR if NOT a mortar:
     *   Immediately cancel event, clear blockList, set yield to 0!
     *   This ensures downstream plugins (like SiegeCannons at NORMAL or HIGH) receive
     *   an already-cancelled event with an empty blockList and do NOT launch flying blocks!
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onExplosionEarly(EntityExplodeEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Entity entity = event.getEntity();
        Location loc = event.getLocation();

        boolean isMortar = plugin.getCannonDetector().isMortarProjectile(entity);
        boolean originInTown = isLocationInTown(loc);
        String originTown = originInTown ? getTownNameAt(loc) : null;
        boolean originActiveSiege = originTown != null && isTownUnderActiveSiege(originTown);

        // If this explosion originated in a town:
        if (originInTown) {
            if (!originActiveSiege || !isMortar) {
                // Suppress completely and immediately at LOWEST!
                event.blockList().clear();
                event.setYield(0.0f);
                event.setCancelled(true);
                plugin.getCannonDetector().recordCannonImpact(loc);

                if (plugin.isDebugEnabled()) {
                    plugin.getLogger().info("[EARLY-BLOCKED] Взрыв в городе '" + originTown + "' немедленно заблокирован на стадии LOWEST (штурм=" + originActiveSiege + ", мортира=" + isMortar + ")");
                }
                return;
            }
        }

        // If outside town, or in active siege town:
        // Filter any blocks that belong to non-sieged towns or non-mortars
        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b == null) continue;
            Location bLoc = b.getLocation();
            if (isLocationInTown(bLoc)) {
                String bTown = getTownNameAt(bLoc);
                boolean bSiege = bTown != null && isTownUnderActiveSiege(bTown);
                if (!bSiege || !isMortar) {
                    it.remove();
                }
            }
        }

        if (event.blockList().isEmpty() && originInTown) {
            event.setCancelled(true);
            event.setYield(0.0f);
            plugin.getCannonDetector().recordCannonImpact(loc);
            return;
        }

        // If verified active siege mortar: save blast blocks for unblocking
        if (isMortar && originActiveSiege && entity != null) {
            UUID entityId = entity.getUniqueId();
            if (event.blockList() != null && !event.blockList().isEmpty()) {
                capturedBlastBlocks.put(entityId, new ArrayList<>(event.blockList()));
                capturedYield.put(entityId, event.getYield());
            }
        }
    }

    /**
     * Phase 2 (HIGHEST Priority):
     * ABSOLUTE VERIFICATION & UNBLOCKING:
     * - Only verified mortars during active siege can break town blocks.
     * - Everything else is 100% blocked.
     */
    @EventHandler(priority = EventPriority.HIGHEST)
    public void onExplosionLate(EntityExplodeEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Entity entity = event.getEntity();
        Location loc = event.getLocation();

        boolean isMortar = plugin.getCannonDetector().isMortarProjectile(entity);
        boolean originInTown = isLocationInTown(loc);
        String originTown = originInTown ? getTownNameAt(loc) : null;
        boolean originActiveSiege = originTown != null && isTownUnderActiveSiege(originTown);

        if (originInTown) {
            if (!originActiveSiege || !isMortar) {
                event.blockList().clear();
                event.setYield(0.0f);
                event.setCancelled(true);
                plugin.getCannonDetector().recordCannonImpact(loc);
                return;
            }
        }

        UUID entityId = entity != null ? entity.getUniqueId() : null;
        List<Block> savedBlocks = entityId != null ? capturedBlastBlocks.remove(entityId) : null;
        Float savedYield = entityId != null ? capturedYield.remove(entityId) : null;
        if (entityId != null) {
            plugin.getCannonDetector().untrack(entityId);
        }

        // Restore saved mortar blocks if towny cancelled
        if (isMortar && savedBlocks != null && !savedBlocks.isEmpty()) {
            for (Block b : savedBlocks) {
                if (b != null && !event.blockList().contains(b)) {
                    event.blockList().add(b);
                }
            }
        }

        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b == null) {
                it.remove();
                continue;
            }
            Location bLoc = b.getLocation();
            if (isLocationInTown(bLoc)) {
                String bTown = getTownNameAt(bLoc);
                boolean bUnderSiege = bTown != null && isTownUnderActiveSiege(bTown);
                if (!bUnderSiege || !isMortar) {
                    it.remove();
                    continue;
                }
            }
        }

        if (event.blockList().isEmpty()) {
            if (originInTown) {
                event.setCancelled(true);
            }
            return;
        }

        if (event.isCancelled()) {
            if (isMortar && (originActiveSiege || hasBlocksInActiveSiegeTown(event.blockList()))) {
                event.setCancelled(false);
            } else {
                event.blockList().clear();
                return;
            }
        }

        if (savedYield != null && savedYield > 0f) {
            event.setYield(savedYield);
        }

        if (originActiveSiege && isMortar && plugin.getConfig().getBoolean("explosion.notify-town-residents", true)) {
            alertTownResidents(loc);
        }
    }

    /**
     * Block Explosions (beds, respawn anchors, etc.): Towns 100% immune at all times.
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onBlockExplodeEarly(BlockExplodeEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Location loc = event.getBlock().getLocation();
        if (isLocationInTown(loc)) {
            event.blockList().clear();
            event.setCancelled(true);
            return;
        }
        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b != null && isLocationInTown(b.getLocation())) {
                it.remove();
            }
        }
        if (event.blockList().isEmpty()) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onBlockExplodeLate(BlockExplodeEvent event) {
        onBlockExplodeEarly(event);
    }

    private boolean hasBlocksInActiveSiegeTown(List<Block> blocks) {
        if (blocks == null || blocks.isEmpty()) return false;
        for (Block b : blocks) {
            if (b == null) continue;
            Location loc = b.getLocation();
            if (isLocationInTown(loc)) {
                String town = getTownNameAt(loc);
                if (town != null && isTownUnderActiveSiege(town)) {
                    return true;
                }
            }
        }
        return false;
    }

    public boolean isLocationInTown(Location loc) {
        if (loc == null || loc.getWorld() == null) return false;
        try {
            if (Bukkit.getPluginManager().isPluginEnabled("Towny")) {
                TownyAPI api = TownyAPI.getInstance();
                if (api != null) {
                    if (!api.isWilderness(loc)) {
                        return true;
                    }
                    if (api.getTownName(loc) != null) {
                        return true;
                    }
                    if (api.getTown(loc) != null) {
                        return true;
                    }
                    TownBlock tb = api.getTownBlock(loc);
                    if (tb != null && tb.hasTown()) {
                        return true;
                    }
                }
            }
        } catch (Throwable ignored) {}
        return false;
    }

    public String getTownNameAt(Location loc) {
        if (loc == null || loc.getWorld() == null) return null;
        try {
            if (Bukkit.getPluginManager().isPluginEnabled("Towny")) {
                TownyAPI api = TownyAPI.getInstance();
                if (api != null) {
                    String name = api.getTownName(loc);
                    if (name != null && !name.isEmpty()) return name;
                    Town town = api.getTown(loc);
                    if (town != null) return town.getName();
                    TownBlock tb = api.getTownBlock(loc);
                    if (tb != null) {
                        try {
                            Town t = tb.getTownOrNull();
                            if (t != null) return t.getName();
                        } catch (Throwable ignored) {}
                    }
                }
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public boolean isTownUnderActiveSiege(String townName) {
        if (townName == null) return false;
        try {
            Plugin ts = Bukkit.getPluginManager().getPlugin("TownySieges");
            if (ts != null && ts.isEnabled()) {
                try {
                    Method m = ts.getClass().getMethod("isTownUnderActiveSiege", String.class);
                    Object res = m.invoke(null, townName);
                    if (res instanceof Boolean) {
                        return (Boolean) res;
                    }
                } catch (Throwable ignored) {}
                try {
                    Object sm = ts.getClass().getMethod("getSiegeManager").invoke(ts);
                    if (sm != null) {
                        Method m = sm.getClass().getMethod("isTownUnderActiveSiege", String.class);
                        Object res = m.invoke(sm, townName);
                        if (res instanceof Boolean) {
                            return (Boolean) res;
                        }
                    }
                } catch (Throwable ignored) {}
            }
        } catch (Throwable ignored) {}
        return false;
    }

    public boolean isLocationUnderActiveSiege(Location loc) {
        if (loc == null) return false;
        String townName = getTownNameAt(loc);
        return isTownUnderActiveSiege(townName);
    }

    private void alertTownResidents(Location loc) {
        try {
            String townName = getTownNameAt(loc);
            if (townName == null) return;
            Town town = TownyAPI.getInstance().getTown(townName);
            if (town == null) return;
            String alertMsg = ChatColor.translateAlternateColorCodes('&',
                    plugin.getConfig().getString("explosion.resident-alert-message", "&c[!] &6Осадная мортира пробила укрепления на территории города!"));
            for (Player p : Bukkit.getOnlinePlayers()) {
                if (town.hasResident(p.getName())) {
                    p.sendMessage(alertMsg);
                }
            }
        } catch (Throwable ignored) {}
    }
}
'''

with open("tmp/towny-explosion-unblocker/src/main/java/com/towny/explosion/listener/CannonExplosionListener.java", "w", encoding="utf-8") as f:
    f.write(cannon_listener_code)
print("Updated CannonExplosionListener.java")

# 3. Update SiegeProtectionListener.java
siege_protection_code = '''package com.towny.sieges.listener;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.ChunkCoord;
import com.towny.sieges.model.SiegeCamp;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.FallingBlock;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityChangeBlockEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.EntitySpawnEvent;
import org.bukkit.event.entity.ProjectileHitEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.util.Vector;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SiegeProtectionListener implements Listener {

    private final TownySiegesPlugin plugin;
    private final Map<Location, Long> recentCannonImpacts = new ConcurrentHashMap<>();

    private static final Set<Material> NATURAL_GRAVITY_MATERIALS = EnumSet.of(
            Material.SAND, Material.RED_SAND, Material.GRAVEL,
            Material.SUSPICIOUS_SAND, Material.SUSPICIOUS_GRAVEL,
            Material.ANVIL, Material.CHIPPED_ANVIL, Material.DAMAGED_ANVIL,
            Material.DRAGON_EGG, Material.SCAFFOLDING, Material.POINTED_DRIPSTONE,
            Material.WHITE_CONCRETE_POWDER, Material.ORANGE_CONCRETE_POWDER,
            Material.MAGENTA_CONCRETE_POWDER, Material.LIGHT_BLUE_CONCRETE_POWDER,
            Material.YELLOW_CONCRETE_POWDER, Material.LIME_CONCRETE_POWDER,
            Material.PINK_CONCRETE_POWDER, Material.GRAY_CONCRETE_POWDER,
            Material.LIGHT_GRAY_CONCRETE_POWDER, Material.CYAN_CONCRETE_POWDER,
            Material.PURPLE_CONCRETE_POWDER, Material.BLUE_CONCRETE_POWDER,
            Material.BROWN_CONCRETE_POWDER, Material.GREEN_CONCRETE_POWDER,
            Material.RED_CONCRETE_POWDER, Material.BLACK_CONCRETE_POWDER
    );

    public SiegeProtectionListener(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void onBlockPlace(BlockPlaceEvent event) {
        Player player = event.getPlayer();
        if (player.hasPermission("townysieges.admin")) return;

        ChunkCoord coord = ChunkCoord.fromLocation(event.getBlock().getLocation());
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(coord);
        if (camp != null) {
            String pTown = plugin.getTownyHook().getPlayerTownName(player);
            if (pTown == null || !pTown.equalsIgnoreCase(camp.getAttackingTown())) {
                event.setCancelled(true);
                player.sendMessage(ChatColor.RED + "[TownySieges] Этот чанк является осадным лагерем города «" + 
                        camp.getAttackingTown() + "»! Вы не можете строить здесь.");
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        Player player = event.getPlayer();
        if (player.hasPermission("townysieges.admin")) return;

        ChunkCoord coord = ChunkCoord.fromLocation(event.getBlock().getLocation());
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(coord);
        if (camp != null) {
            String pTown = plugin.getTownyHook().getPlayerTownName(player);
            if (pTown == null || !pTown.equalsIgnoreCase(camp.getAttackingTown())) {
                event.setCancelled(true);
                player.sendMessage(ChatColor.RED + "[TownySieges] Этот чанк является осадным лагерем города «" + 
                        camp.getAttackingTown() + "»! Вы не можете разрушать здесь.");
            }
        }
    }

    /**
     * Phase 1 (LOWEST Priority):
     * Instantly cancel explosions in town outside active siege or if not a mortar,
     * so that SiegeCannons and other plugins do not trigger their built-in block scattering!
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onEntityExplodeEarly(EntityExplodeEvent event) {
        Location loc = event.getLocation();
        Entity entity = event.getEntity();
        boolean isMortar = isMortarProjectile(entity);

        String centerTown = plugin.getTownyHook().getTownNameAt(loc);
        boolean centerInTown = centerTown != null;
        boolean centerUnderSiege = centerInTown && plugin.getSiegeManager().isTownUnderActiveSiege(centerTown);

        if (centerInTown && (!centerUnderSiege || !isMortar)) {
            event.blockList().clear();
            event.setYield(0.0f);
            event.setCancelled(true);
            recordCannonImpact(loc);
            return;
        }

        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b == null) continue;
            String bTown = plugin.getTownyHook().getTownNameAt(b.getLocation());
            if (bTown != null) {
                boolean bUnderSiege = plugin.getSiegeManager().isTownUnderActiveSiege(bTown);
                if (!bUnderSiege || !isMortar) {
                    it.remove();
                }
            }
        }

        if (event.blockList().isEmpty() && centerInTown) {
            event.setCancelled(true);
            event.setYield(0.0f);
            recordCannonImpact(loc);
        }
    }

    /**
     * Phase 2 (HIGHEST Priority):
     * Absolute Explosion Defense:
     * - In a town: Damage permitted ONLY during ACTIVE_SIEGE AND if projectile is a MORTAR!
     * - Outside active assault, or if not a mortar: All town blocks are 100% protected.
     */
    @EventHandler(priority = EventPriority.HIGHEST)
    public void onEntityExplode(EntityExplodeEvent event) {
        Location loc = event.getLocation();
        Entity entity = event.getEntity();
        boolean isMortar = isMortarProjectile(entity);

        String centerTown = plugin.getTownyHook().getTownNameAt(loc);
        boolean centerInTown = centerTown != null;
        boolean centerUnderSiege = centerInTown && plugin.getSiegeManager().isTownUnderActiveSiege(centerTown);

        if (centerInTown && (!centerUnderSiege || !isMortar)) {
            event.blockList().clear();
            event.setYield(0.0f);
            event.setCancelled(true);
            recordCannonImpact(loc);
            return;
        }

        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b == null) continue;
            String bTown = plugin.getTownyHook().getTownNameAt(b.getLocation());
            if (bTown != null) {
                boolean bUnderSiege = plugin.getSiegeManager().isTownUnderActiveSiege(bTown);
                if (!bUnderSiege || !isMortar) {
                    it.remove();
                }
            }
        }

        if (event.blockList().isEmpty()) {
            if (centerInTown) {
                event.setCancelled(true);
                event.setYield(0.0f);
            }
        }
    }

    /**
     * Intercept and suppress SiegeCannons flying block debris (FallingBlock) outside active siege.
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onFallingBlockSpawn(EntitySpawnEvent event) {
        Entity entity = event.getEntity();
        if (!(entity instanceof FallingBlock)) return;

        FallingBlock fb = (FallingBlock) entity;
        Location loc = fb.getLocation();
        Location srcLoc = null;
        try {
            srcLoc = fb.getSourceLoc();
        } catch (Throwable ignored) {}
        if (srcLoc == null) {
            srcLoc = loc;
        }

        String townAtLoc = plugin.getTownyHook().getTownNameAt(loc);
        String townAtSrc = plugin.getTownyHook().getTownNameAt(srcLoc);
        String townName = townAtLoc != null ? townAtLoc : townAtSrc;

        if (townName == null) return; // Wilderness

        boolean underSiege = plugin.getSiegeManager().isTownUnderActiveSiege(townName);
        if (underSiege) return; // Active siege allows mortar destruction

        // Outside active siege: check if this is flying block debris
        Material mat = fb.getBlockData() != null ? fb.getBlockData().getMaterial() : fb.getMaterial();
        Vector vel = fb.getVelocity();
        double hSpeedSq = (vel.getX() * vel.getX()) + (vel.getZ() * vel.getZ());
        boolean hasOutwardVelocity = hSpeedSq > 0.0001 || vel.getY() > 0.01;
        boolean isUnnaturalFallingBlock = mat != null && !NATURAL_GRAVITY_MATERIALS.contains(mat);
        boolean nearCannon = isNearRecentCannonImpact(loc, 35.0) || isNearRecentCannonImpact(srcLoc, 35.0);

        if (isUnnaturalFallingBlock || hasOutwardVelocity || nearCannon) {
            event.setCancelled(true);
            fb.remove();

            // Restore original block if turned to air
            if (srcLoc.getWorld() != null) {
                Block srcBlock = srcLoc.getBlock();
                if (srcBlock.getType().isAir() && fb.getBlockData() != null && !fb.getBlockData().getMaterial().isAir()) {
                    srcBlock.setBlockData(fb.getBlockData(), false);
                }
            }
            if (loc.getWorld() != null && !loc.equals(srcLoc)) {
                Block locBlock = loc.getBlock();
                if (locBlock.getType().isAir() && fb.getBlockData() != null && !fb.getBlockData().getMaterial().isAir()) {
                    locBlock.setBlockData(fb.getBlockData(), false);
                }
            }
        }
    }

    /**
     * Intercept and suppress FallingBlocks landing in town outside siege.
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onFallingBlockLand(EntityChangeBlockEvent event) {
        if (!(event.getEntity() instanceof FallingBlock)) return;

        Location targetLoc = event.getBlock().getLocation();
        String townName = plugin.getTownyHook().getTownNameAt(targetLoc);
        if (townName != null) {
            boolean underSiege = plugin.getSiegeManager().isTownUnderActiveSiege(townName);
            if (!underSiege) {
                event.setCancelled(true);
                event.getEntity().remove();
            }
        }
    }

    /**
     * Intercept projectile impact on town blocks outside siege.
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onProjectileHit(ProjectileHitEvent event) {
        Entity projectile = event.getEntity();
        if (projectile == null) return;

        Location hitLoc = event.getHitBlock() != null ? event.getHitBlock().getLocation() : projectile.getLocation();
        if (hitLoc == null) return;

        String townName = plugin.getTownyHook().getTownNameAt(hitLoc);
        if (townName != null) {
            boolean underSiege = plugin.getSiegeManager().isTownUnderActiveSiege(townName);
            boolean isMortar = isMortarProjectile(projectile);

            if (!underSiege || !isMortar) {
                recordCannonImpact(hitLoc);
                if (isAnyCannonProjectile(projectile)) {
                    event.setCancelled(true);
                    if (projectile instanceof FallingBlock) {
                        projectile.remove();
                    }
                }
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onBlockExplode(BlockExplodeEvent event) {
        Location loc = event.getBlock().getLocation();
        String centerTown = plugin.getTownyHook().getTownNameAt(loc);
        if (centerTown != null) {
            event.blockList().clear();
            event.setCancelled(true);
            return;
        }

        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b != null && plugin.getTownyHook().getTownNameAt(b.getLocation()) != null) {
                it.remove();
            }
        }

        if (event.blockList().isEmpty()) {
            event.setCancelled(true);
        }
    }

    public void recordCannonImpact(Location loc) {
        if (loc == null) return;
        recentCannonImpacts.put(loc.clone(), System.currentTimeMillis());
        cleanOldImpacts();
    }

    private boolean isNearRecentCannonImpact(Location loc, double radius) {
        if (loc == null || loc.getWorld() == null) return false;
        cleanOldImpacts();

        long now = System.currentTimeMillis();
        double radiusSq = radius * radius;
        for (Map.Entry<Location, Long> entry : recentCannonImpacts.entrySet()) {
            Location impactLoc = entry.getKey();
            if (impactLoc.getWorld() != null && impactLoc.getWorld().equals(loc.getWorld())) {
                if (now - entry.getValue() < 6000L) {
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

    private boolean isMortarProjectile(Entity entity) {
        if (entity == null) return false;
        String name = entity.getType().name();
        if (name.equals("CREEPER") || name.equals("ENDER_CRYSTAL") || name.equals("WITHER") || name.equals("WITHER_SKULL")) {
            return false;
        }

        String customName = entity.getCustomName();
        if (customName != null) {
            String lower = customName.toLowerCase();
            if (lower.contains("мортир") || lower.contains("mortar")) return true;
        }

        Set<String> tags = entity.getScoreboardTags();
        if (tags != null) {
            for (String tag : tags) {
                if (tag != null) {
                    String lower = tag.toLowerCase();
                    if (lower.contains("mortar") || lower.contains("мортир")) return true;
                }
            }
        }

        try {
            if (entity.hasMetadata("mortar") || entity.hasMetadata("mortar_shell") || entity.hasMetadata("siege_mortar")) {
                return true;
            }
        } catch (Throwable ignored) {}

        return false;
    }

    private boolean isAnyCannonProjectile(Entity entity) {
        if (entity == null) return false;
        if (isMortarProjectile(entity)) return true;

        String customName = entity.getCustomName();
        if (customName != null) {
            String lower = customName.toLowerCase();
            if (lower.contains("cannon") || lower.contains("пушк") || lower.contains("снаряд") ||
                lower.contains("ядро") || lower.contains("siege")) {
                return true;
            }
        }

        Set<String> tags = entity.getScoreboardTags();
        if (tags != null) {
            for (String tag : tags) {
                if (tag != null) {
                    String lower = tag.toLowerCase();
                    if (lower.contains("cannon") || lower.contains("siege") || lower.contains("projectile")) {
                        return true;
                    }
                }
            }
        }

        try {
            if (entity.hasMetadata("cannon") || entity.hasMetadata("cannonball") || entity.hasMetadata("siegecannon")) {
                return true;
            }
        } catch (Throwable ignored) {}

        return false;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onPlayerMove(PlayerMoveEvent event) {
        if (event.getFrom().getBlockX() >> 4 == event.getTo().getBlockX() >> 4 &&
            event.getFrom().getBlockZ() >> 4 == event.getTo().getBlockZ() >> 4) {
            return;
        }

        ChunkCoord toCoord = ChunkCoord.fromLocation(event.getTo());
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(coordToCamp(toCoord));
        if (camp != null) {
            Player p = event.getPlayer();
            String phaseStr = camp.isActiveSiege() ? "§4[ШТУРМ]" : "§e[Подготовка]";
            try {
                p.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                        new TextComponent("§c⚔ Осадный лагерь города §6" + camp.getAttackingTown() + " §7(Цель: §c" + camp.getDefendingTown() + "§7) " + phaseStr));
            } catch (Exception ignored) {}
        }
    }

    private ChunkCoord coordToCamp(ChunkCoord c) {
        return c;
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        plugin.getBossBarManager().updatePlayerBossBar(event.getPlayer());
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        plugin.getBossBarManager().removePlayerBossBar(event.getPlayer());
    }
}
'''

with open("tmp/towny-sieges/src/main/java/com/towny/sieges/listener/SiegeProtectionListener.java", "w", encoding="utf-8") as f:
    f.write(siege_protection_code)
print("Updated SiegeProtectionListener.java")

print("All sources successfully written!")
