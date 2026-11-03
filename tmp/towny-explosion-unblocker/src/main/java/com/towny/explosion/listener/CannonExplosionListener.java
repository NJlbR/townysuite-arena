package com.towny.explosion.listener;

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
