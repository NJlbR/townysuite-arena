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
            if (plugin.isDebugEnabled()) {
                plugin.getLogger().info("[TRACK] Зарегистрировано орудие / снаряд артиллерии UUID=" + uuid + " (" + entity.getType() + ")");
            }
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
            if (entity.hasMetadata("cannon") || entity.hasMetadata("cannonball") ||
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
 * Universal Artillery & Siege Cannons Controller:
 * 
 * Fundamental Rules:
 * 1. ВО ВРЕМЯ ШТУРМА (ACTIVE_SIEGE):
 *    - ВСЕ орудийные орудия (пушки, мортиры, осадные орудия, SiegeCannons, Cannons) ПОЛНОСТЬЮ РАБОТАЮТ!
 *    - Блоки разрушаются без блокировки!
 *    - Разлет блоков и летящие осколки (FallingBlock) работают по ВСЕМУ оригинальному функционалу SiegeCannons!
 * 
 * 2. ВНЕ ШТУРМА (мирное время и подготовка):
 *    - 100% защита городов: орудия не ломают блоки.
 *    - Разлет блоков (FallingBlock debris) полностью подавляется и нейтрализуется, а затронутые блоки восстанавливаются!
 */
public class CannonExplosionListener implements Listener {

    private final TownyExplosionUnblockerPlugin plugin;
    private final Map<UUID, List<Block>> capturedBlastBlocks = new ConcurrentHashMap<>();
    private final Map<UUID, Float> capturedYield = new ConcurrentHashMap<>();

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

    @EventHandler(priority = EventPriority.LOWEST)
    public void onEntitySpawnEarly(EntitySpawnEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Entity entity = event.getEntity();
        if (entity == null) return;

        if (entity instanceof TNTPrimed || plugin.getCannonDetector().isArtilleryWeapon(entity)) {
            plugin.getCannonDetector().trackSpawnedEntity(entity);
            return;
        }

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
     * Controls FallingBlock debris:
     * - DURING ACTIVE SIEGE: Allowed to fly and scatter with full SiegeCannons functionality!
     * - OUTSIDE SIEGE: Suppressed and blocks restored!
     */
    private void handleFallingBlockSpawn(EntitySpawnEvent event, FallingBlock fb) {
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
            return; // Wilderness: full vanilla physics
        }

        String townName = locInTown ? getTownNameAt(loc) : getTownNameAt(srcLoc);
        boolean underSiege = townName != null && isTownUnderActiveSiege(townName);

        // ВО ВРЕМЯ ШТУРМА: РАЗЛЕТ БЛОКОВ ПОЛНОСТЬЮ РАЗРЕШЕН ПО ВСЕМУ ФУНКЦИОНАЛУ SIEGECANNONS!
        if (underSiege) {
            return;
        }

        // ВНЕ ШТУРМА: ПОЛНОЕ ПОДАВЛЕНИЕ РАЗЛЕТА И ВОССТАНОВЛЕНИЕ БЛОКОВ
        if (!plugin.getConfig().getBoolean("block-scattering.disable-outside-siege", true)) {
            return;
        }

        Material mat = fb.getBlockData() != null ? fb.getBlockData().getMaterial() : fb.getMaterial();
        Vector vel = fb.getVelocity();
        double hSpeedSq = (vel.getX() * vel.getX()) + (vel.getZ() * vel.getZ());
        boolean hasOutwardVelocity = hSpeedSq > 0.0001 || vel.getY() > 0.01;
        boolean isUnnaturalFallingBlock = mat != null && !NATURAL_GRAVITY_MATERIALS.contains(mat);
        double radius = plugin.getConfig().getDouble("block-scattering.suppression-radius", 35.0);
        boolean nearCannonImpact = plugin.getCannonDetector().isNearRecentCannonImpact(loc, radius) ||
                                   plugin.getCannonDetector().isNearRecentCannonImpact(srcLoc, radius);

        if (isUnnaturalFallingBlock || hasOutwardVelocity || nearCannonImpact) {
            event.setCancelled(true);
            fb.remove();

            if (plugin.isDebugEnabled()) {
                plugin.getLogger().info("[SCATTER-BLOCKED] Подавлен разлет блока " + mat + " в городе '" + townName + "' вне штурма.");
            }

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
     * Falling blocks landing:
     * - During active siege: Allowed to land and interact freely.
     * - Outside active siege: Cancelled.
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

            // ВО ВРЕМЯ ШТУРМА: Разрешено полное оседание и разлет блоков SiegeCannons!
            if (underSiege) {
                return;
            }

            // Вне штурма: отмена приземления
            event.setCancelled(true);
            event.getEntity().remove();
            if (plugin.isDebugEnabled()) {
                plugin.getLogger().info("[LAND-BLOCKED] Заблокировано приземление FallingBlock в городе '" + townName + "' вне штурма.");
            }
        }
    }

    /**
     * Projectile Hit Event:
     * - During active siege: All cannon projectile hits process freely!
     * - Outside active siege: Cancelled to suppress secondary triggers.
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

            // ВО ВРЕМЯ ШТУРМА: Попадания орудийных снарядов РАЗРЕШЕНЫ!
            if (underSiege) {
                return;
            }

            // Вне штурма: блокируем попадание
            plugin.getCannonDetector().recordCannonImpact(hitLoc);
            if (plugin.getCannonDetector().isArtilleryWeapon(projectile)) {
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

    /**
     * Phase 1 (LOWEST Priority):
     * - ВО ВРЕМЯ ШТУРМА: Все орудия (пушки, мортиры, SiegeCannons) разрешены, блоки сохраняются для разрушения!
     * - ВНЕ ШТУРМА: Немедленная отмена и очистка списка блоков.
     */
    @EventHandler(priority = EventPriority.LOWEST)
    public void onExplosionEarly(EntityExplodeEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Entity entity = event.getEntity();
        Location loc = event.getLocation();

        boolean isArtillery = plugin.getCannonDetector().isArtilleryWeapon(entity);
        boolean originInTown = isLocationInTown(loc);
        String originTown = originInTown ? getTownNameAt(loc) : null;
        boolean originActiveSiege = originTown != null && isTownUnderActiveSiege(originTown);

        // В ГОРОДЕ ВО ВРЕМЯ АКТИВНОГО ШТУРМА:
        if (originInTown && originActiveSiege) {
            // Если это орудие (пушка, мортира, SiegeCannons, TNT) - РАЗРЕШАЕМ ПОЛНОСТЬЮ!
            if (isArtillery) {
                if (entity != null) {
                    UUID entityId = entity.getUniqueId();
                    if (event.blockList() != null && !event.blockList().isEmpty()) {
                        capturedBlastBlocks.put(entityId, new ArrayList<>(event.blockList()));
                        capturedYield.put(entityId, event.getYield());
                    }
                }
                if (plugin.isDebugEnabled()) {
                    plugin.getLogger().info("[SIEGE-ACTIVE] Орудийный взрыв активен в осажденном городе '" + originTown + "' (блоков: " + event.blockList().size() + ")");
                }
                return;
            }
        }

        // В ГОРОДЕ ВНЕ ШТУРМА (или ванильный крипер/кристалл):
        if (originInTown) {
            event.blockList().clear();
            event.setYield(0.0f);
            event.setCancelled(true);
            plugin.getCannonDetector().recordCannonImpact(loc);
            return;
        }

        // ВЗРЫВ ИЗ ДИКИХ ЗЕМЕЛЬ (снаружи города):
        // Очищаем только те блоки, которые принадлежат городам НЕ под штурмом
        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b == null) continue;
            Location bLoc = b.getLocation();
            if (isLocationInTown(bLoc)) {
                String bTown = getTownNameAt(bLoc);
                boolean bSiege = bTown != null && isTownUnderActiveSiege(bTown);
                // Если город под штурмом и стреляет орудие — БЛОК РАЗРУШАЕТСЯ!
                if (!bSiege || !isArtillery) {
                    it.remove(); // Защищен вне штурма
                }
            }
        }

        if (event.blockList().isEmpty() && originInTown) {
            event.setCancelled(true);
            event.setYield(0.0f);
            plugin.getCannonDetector().recordCannonImpact(loc);
        }
    }

    /**
     * Phase 2 (HIGHEST Priority):
     * - ВО ВРЕМЯ ШТУРМА: Разблокирует взрыв (uncancel), если Towny его отменил!
     * - ВНЕ ШТУРМА: Гарантирует 100% отмену.
     */
    @EventHandler(priority = EventPriority.HIGHEST)
    public void onExplosionLate(EntityExplodeEvent event) {
        if (!plugin.isUnblockerEnabled()) return;
        Entity entity = event.getEntity();
        Location loc = event.getLocation();

        boolean isArtillery = plugin.getCannonDetector().isArtilleryWeapon(entity);
        boolean originInTown = isLocationInTown(loc);
        String originTown = originInTown ? getTownNameAt(loc) : null;
        boolean originActiveSiege = originTown != null && isTownUnderActiveSiege(originTown);

        // Вне штурма: гарантированная блокировка
        if (originInTown && (!originActiveSiege || !isArtillery)) {
            event.blockList().clear();
            event.setYield(0.0f);
            event.setCancelled(true);
            plugin.getCannonDetector().recordCannonImpact(loc);
            return;
        }

        UUID entityId = entity != null ? entity.getUniqueId() : null;
        List<Block> savedBlocks = entityId != null ? capturedBlastBlocks.remove(entityId) : null;
        Float savedYield = entityId != null ? capturedYield.remove(entityId) : null;
        if (entityId != null) {
            plugin.getCannonDetector().untrack(entityId);
        }

        // Во время штурма: восстанавливаем сохраненные блоки взрыва, если Towny их обрезал
        if (isArtillery && originActiveSiege && savedBlocks != null && !savedBlocks.isEmpty()) {
            for (Block b : savedBlocks) {
                if (b != null && !event.blockList().contains(b)) {
                    event.blockList().add(b);
                }
            }
        }

        // Фильтруем блоки: в осажденном городе блоки ломаются, в неосажденном — защищены
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
                if (!bUnderSiege || !isArtillery) {
                    it.remove();
                    continue;
                }
                // Защита городской стены чертежа (двойная стойкость City Wall)
                if (isProperCityWallBlock(bLoc)) {
                    // Обрабатывается TownyArchitecture
                }
            }
        }

        if (event.blockList().isEmpty()) {
            if (originInTown) {
                event.setCancelled(true);
            }
            return;
        }

        // РАЗБЛОКИРОВКА ВЗРЫВА ВО ВРЕМЯ ШТУРМА:
        // Если событие было отменено стандартным Towny, мы снимаем отмену (uncancel)!
        if (event.isCancelled()) {
            if (isArtillery && (originActiveSiege || hasBlocksInActiveSiegeTown(event.blockList()))) {
                event.setCancelled(false);
            } else {
                event.blockList().clear();
                return;
            }
        }

        if (savedYield != null && savedYield > 0f) {
            event.setYield(savedYield);
        }

        if (originActiveSiege && isArtillery && plugin.getConfig().getBoolean("explosion.notify-town-residents", true)) {
            alertTownResidents(loc);
        }
    }

    /**
     * Block Explosions (beds, respawn anchors): Towns 100% immune at all times.
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

    private boolean isProperCityWallBlock(Location loc) {
        if (loc == null) return false;
        try {
            Plugin ta = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
            if (ta != null && ta.isEnabled()) {
                Object bm = ta.getClass().getMethod("getBuildingManager").invoke(ta);
                if (bm != null) {
                    Object res = bm.getClass().getMethod("isProperCityWallBlock", Location.class).invoke(bm, loc);
                    if (res instanceof Boolean) {
                        return (Boolean) res;
                    }
                }
            }
        } catch (Throwable ignored) {}
        return false;
    }

    private void alertTownResidents(Location loc) {
        try {
            String townName = getTownNameAt(loc);
            if (townName == null) return;
            Town town = TownyAPI.getInstance().getTown(townName);
            if (town == null) return;
            String alertMsg = ChatColor.translateAlternateColorCodes('&',
                    plugin.getConfig().getString("explosion.resident-alert-message", "&c[!] &6Орудийный снаряд пробил укрепления на территории города!"));
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

# 3. Update SiegeProtectionListener.java in TownySieges
siege_listener_code = '''package com.towny.sieges.listener;

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
import org.bukkit.entity.TNTPrimed;
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

/**
 * TownySieges Protection Listener:
 * - During active siege (2h active phase): ALL artillery (пушки, мортиры, SiegeCannons, осадный TNT)
 *   can break town blocks and scatter blocks freely across the full functionality of SiegeCannons!
 * - Outside active siege: Towns 100% protected.
 */
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

    @EventHandler(priority = EventPriority.LOWEST)
    public void onEntityExplodeEarly(EntityExplodeEvent event) {
        Location loc = event.getLocation();
        Entity entity = event.getEntity();
        boolean isArtillery = isArtilleryWeapon(entity);

        String centerTown = plugin.getTownyHook().getTownNameAt(loc);
        boolean centerInTown = centerTown != null;
        boolean centerUnderSiege = centerInTown && plugin.getSiegeManager().isTownUnderActiveSiege(centerTown);

        // ВО ВРЕМЯ ШТУРМА: ВСЕ ОРУДИЯ РАЗРЕШЕНЫ ДЛЯ РАЗРУШЕНИЯ БЛОКОВ!
        if (centerInTown && centerUnderSiege && isArtillery) {
            return; // Let explosion destroy blocks!
        }

        // Вне штурма: отмена взрыва
        if (centerInTown && (!centerUnderSiege || !isArtillery)) {
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
                if (!bUnderSiege || !isArtillery) {
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

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onEntityExplode(EntityExplodeEvent event) {
        Location loc = event.getLocation();
        Entity entity = event.getEntity();
        boolean isArtillery = isArtilleryWeapon(entity);

        String centerTown = plugin.getTownyHook().getTownNameAt(loc);
        boolean centerInTown = centerTown != null;
        boolean centerUnderSiege = centerInTown && plugin.getSiegeManager().isTownUnderActiveSiege(centerTown);

        if (centerInTown && (!centerUnderSiege || !isArtillery)) {
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
                if (!bUnderSiege || !isArtillery) {
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
     * Flying block debris:
     * - DURING ACTIVE SIEGE: Allowed to scatter freely across the full functionality of SiegeCannons!
     * - Outside siege: Blocked.
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
        // ВО ВРЕМЯ ШТУРМА: РАЗЛЕТ БЛОКОВ РАЗРЕШЕН ПОЛНОСТЬЮ!
        if (underSiege) return;

        // Вне штурма: блокируем разлет и восстанавливаем блоки
        Material mat = fb.getBlockData() != null ? fb.getBlockData().getMaterial() : fb.getMaterial();
        Vector vel = fb.getVelocity();
        double hSpeedSq = (vel.getX() * vel.getX()) + (vel.getZ() * vel.getZ());
        boolean hasOutwardVelocity = hSpeedSq > 0.0001 || vel.getY() > 0.01;
        boolean isUnnaturalFallingBlock = mat != null && !NATURAL_GRAVITY_MATERIALS.contains(mat);
        boolean nearCannon = isNearRecentCannonImpact(loc, 35.0) || isNearRecentCannonImpact(srcLoc, 35.0);

        if (isUnnaturalFallingBlock || hasOutwardVelocity || nearCannon) {
            event.setCancelled(true);
            fb.remove();

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

    @EventHandler(priority = EventPriority.LOWEST)
    public void onFallingBlockLand(EntityChangeBlockEvent event) {
        if (!(event.getEntity() instanceof FallingBlock)) return;

        Location targetLoc = event.getBlock().getLocation();
        String townName = plugin.getTownyHook().getTownNameAt(targetLoc);
        if (townName != null) {
            boolean underSiege = plugin.getSiegeManager().isTownUnderActiveSiege(townName);
            // ВО ВРЕМЯ ШТУРМА: Разрешено приземление блоков SiegeCannons!
            if (underSiege) return;

            event.setCancelled(true);
            event.getEntity().remove();
        }
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onProjectileHit(ProjectileHitEvent event) {
        Entity projectile = event.getEntity();
        if (projectile == null) return;

        Location hitLoc = event.getHitBlock() != null ? event.getHitBlock().getLocation() : projectile.getLocation();
        if (hitLoc == null) return;

        String townName = plugin.getTownyHook().getTownNameAt(hitLoc);
        if (townName != null) {
            boolean underSiege = plugin.getSiegeManager().isTownUnderActiveSiege(townName);
            // ВО ВРЕМЯ ШТУРМА: Попадания орудий разрешены!
            if (underSiege) return;

            recordCannonImpact(hitLoc);
            if (isArtilleryWeapon(projectile)) {
                event.setCancelled(true);
                if (projectile instanceof FallingBlock) {
                    projectile.remove();
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

    public boolean isArtilleryWeapon(Entity entity) {
        if (entity == null) return true; // Plugin createExplosion
        String typeName = entity.getType().name();
        if (typeName.equals("CREEPER") || typeName.equals("ENDER_CRYSTAL") || 
            typeName.equals("END_CRYSTAL") || typeName.equals("WITHER") || 
            typeName.equals("WITHER_SKULL") || typeName.equals("WIND_CHARGE") ||
            typeName.equals("BREEZE_WIND_CHARGE")) {
            return false;
        }

        String customName = entity.getCustomName();
        if (customName != null) {
            String lower = customName.toLowerCase();
            if (lower.contains("мортир") || lower.contains("mortar") ||
                lower.contains("cannon") || lower.contains("пушк") ||
                lower.contains("снаряд") || lower.contains("ядро") ||
                lower.contains("осад") || lower.contains("siege") ||
                lower.contains("артиллер") || lower.contains("artillery")) {
                return true;
            }
        }

        Set<String> tags = entity.getScoreboardTags();
        if (tags != null) {
            for (String tag : tags) {
                if (tag != null) {
                    String lower = tag.toLowerCase();
                    if (lower.contains("mortar") || lower.contains("cannon") ||
                        lower.contains("siege") || lower.contains("artillery") ||
                        lower.contains("projectile") || lower.contains("shot") ||
                        lower.contains("shell")) {
                        return true;
                    }
                }
            }
        }

        try {
            if (entity.hasMetadata("mortar") || entity.hasMetadata("mortar_shell") || 
                entity.hasMetadata("siege_mortar") || entity.hasMetadata("cannon") ||
                entity.hasMetadata("cannonball") || entity.hasMetadata("siegecannon") ||
                entity.hasMetadata("projectile")) {
                return true;
            }
        } catch (Throwable ignored) {}

        if (entity instanceof TNTPrimed || entity instanceof FallingBlock) {
            return true;
        }

        return false;
    }

    public boolean isMortarProjectile(Entity entity) {
        return isArtilleryWeapon(entity);
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
    f.write(siege_listener_code)
print("Updated SiegeProtectionListener.java")

print("All sources successfully updated for full artillery & SiegeCannons scattering during active siege!")
