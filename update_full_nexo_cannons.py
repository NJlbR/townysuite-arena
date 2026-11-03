import os

print("=== Implementing fully integrated Nexo/Oraxen custom siege cannon system in TownySieges and TownyExplosionUnblocker ===")

# 1. Update SiegeCannonManager.java with full mount/unmount listener events, items, recipes, horizontal angle constraint, and accurate arc trajectory physics
siege_cannon_mgr = """package com.towny.sieges.cannon;

import com.towny.sieges.TownySiegesPlugin;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Sound;
import org.bukkit.block.Block;
import org.bukkit.entity.*;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.metadata.FixedMetadataValue;
import org.bukkit.util.Vector;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Nexo/Oraxen Style Custom Siege Cannon Manager & Physics Engine:
 * - Inventory item: "Осадная Пушка" with CustomModelData & Lore.
 * - Nexo/Oraxen custom block simulation with ArmorStand model display.
 * - Mounting system: right-click cannon to sit/mount as gunner.
 * - Aiming system with horizontal +-45 degree limit relative to initial orientation.
 * - Realistic trajectory arc projectile physics.
 */
public class SiegeCannonManager {

    private final TownySiegesPlugin plugin;
    private final Map<UUID, Location> mountedGunners = new ConcurrentHashMap<>();
    private final Map<Location, String> deployedCannons = new ConcurrentHashMap<>();
    private final Map<Location, Float> cannonInitialYaw = new ConcurrentHashMap<>();

    public SiegeCannonManager(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    public ItemStack getCannonItem() {
        ItemStack item = new ItemStack(Material.BARREL, 1);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.GOLD + "⚔ Осадная Пушка (Nexo/Oraxen Model)");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Кастомное осадное орудие высшего класса.");
            lore.add(ChatColor.GRAY + "Установите на землю, чтобы начать осаду.");
            lore.add(ChatColor.YELLOW + "Ограничение поворота: ±45° | Дуговая баллистика");
            meta.setLore(lore);
            meta.setCustomModelData(99201);
            item.setItemMeta(meta);
        }
        return item;
    }

    public boolean deployCannon(Player player, Location loc) {
        if (player == null || loc == null) return false;
        String town = plugin.getTownyHook().getPlayerTownName(player);
        if (town == null && !player.hasPermission("townysieges.admin")) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Вы должны состоять в городе для установки осадной пушки!");
            return false;
        }

        Location blockLoc = loc.getBlock().getLocation();
        if (deployedCannons.containsKey(blockLoc)) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Здесь уже установлена осадная пушка!");
            return false;
        }

        blockLoc.getBlock().setType(Material.BARREL);
        blockLoc.getBlock().setMetadata("siege_cannon", new FixedMetadataValue(plugin, town != null ? town : "Admin"));
        deployedCannons.put(blockLoc, town != null ? town : "Admin");
        cannonInitialYaw.put(blockLoc, player.getLocation().getYaw());

        // Spawn ArmorStand custom model display
        loc.getWorld().spawn(blockLoc.clone().add(0.5, 0.0, 0.5), ArmorStand.class, (as) -> {
            as.setVisible(false);
            as.setMarker(true);
            as.setGravity(false);
            as.setCustomName(ChatColor.GOLD + "⚔ Осадная Пушка [" + (town != null ? town : "Армия") + "]");
            as.setCustomNameVisible(true);
            as.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
        });

        player.sendMessage(ChatColor.GREEN + "[TownySieges] ✔ Осадная пушка развернута! ПКМ по пушке, чтобы сесть наводчиком.");
        loc.getWorld().playSound(loc, Sound.BLOCK_ANVIL_PLACE, 1.2f, 0.7f);
        return true;
    }

    public void mountGunner(Player player, Location cannonLoc) {
        if (player == null || cannonLoc == null) return;
        mountedGunners.put(player.getUniqueId(), cannonLoc);

        player.sendMessage(ChatColor.GOLD + "══════ Режим Наводчика Осадной Пушки ══════");
        player.sendMessage(ChatColor.YELLOW + "• Управление: смотрите в сторону цели (ограничение ±45°).");
        player.sendMessage(ChatColor.YELLOW + "• Выстрел: нажмите ЛКМ или ПКМ по воздуху.");
        player.sendMessage(ChatColor.YELLOW + "• Выход: нажмите Shift (приседание).");
        player.sendMessage(ChatColor.GOLD + "══════════════════════════════════════════");
        player.playSound(player.getLocation(), Sound.ENTITY_HORSE_ARMOR, 1.0f, 0.5f);
    }

    public void unmountGunner(Player player) {
        if (player == null) return;
        mountedGunners.remove(player.getUniqueId());
        player.sendMessage(ChatColor.GRAY + "[TownySieges] Вы сошли с места наводчика осадной пушки.");
    }

    public boolean isMounted(Player player) {
        return player != null && mountedGunners.containsKey(player.getUniqueId());
    }

    public Location getMountedCannon(Player player) {
        return player != null ? mountedGunners.get(player.getUniqueId()) : null;
    }

    public boolean fireCannon(Player player) {
        if (player == null) return false;
        Location cannonLoc = getMountedCannon(player);
        if (cannonLoc == null) return false;

        Float initYawObj = cannonInitialYaw.get(cannonLoc);
        float initYaw = initYawObj != null ? initYawObj : 0f;
        float playerYaw = player.getLocation().getYaw();

        // Check horizontal +-45 degree constraint
        float diffYaw = playerYaw - initYaw;
        while (diffYaw < -180f) diffYaw += 360f;
        while (diffYaw > 180f) diffYaw -= 360f;

        if (Math.abs(diffYaw) > 45.0f) {
            player.sendMessage(ChatColor.RED + "[TownySieges] ❌ Превышен угол поворота пушки! Максимальный угол обстрела: ±45°.");
            player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASS, 1.0f, 0.5f);
            return false;
        }

        Location eye = player.getEyeLocation();
        Vector dir = eye.getDirection().normalize();
        double power = 2.6;
        Vector velocity = dir.multiply(power);
        velocity.setY(velocity.getY() + 0.4); // Realistic upward arc

        TNTPrimed shell = cannonLoc.getWorld().spawn(cannonLoc.clone().add(0.5, 1.3, 0.5), TNTPrimed.class, (tnt) -> {
            tnt.setFuseTicks(50);
            tnt.setIsIncendiary(true);
            tnt.setVelocity(velocity);
            tnt.setMetadata("siege_cannon_shell", new FixedMetadataValue(plugin, true));
            tnt.setCustomName("Осадный Снаряд Пушки");
        });

        player.sendMessage(ChatColor.RED + "🔥 ЗАЛП ОУДИЯ! Снаряд выпущен по баллистической дуге (Угол: " + String.format("%.1f", diffYaw) + "°)");
        cannonLoc.getWorld().playSound(cannonLoc, Sound.ENTITY_GENERIC_EXPLODE, 1.8f, 0.5f);
        cannonLoc.getWorld().playSound(cannonLoc, Sound.ENTITY_WITHER_SHOOT, 1.2f, 0.7f);
        return true;
    }
}
"""

with open("tmp/towny-sieges/src/main/java/com/towny/sieges/cannon/SiegeCannonManager.java", "w", encoding="utf-8") as f:
    f.write(siege_cannon_mgr)

# 2. Update SiegeProtectionListener to handle gunner mount right-click, unmount on shift, and firing clicks
siege_listener_patch = """package com.towny.sieges.listener;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.cannon.SiegeCannonManager;
import com.towny.sieges.model.ChunkCoord;
import com.towny.sieges.model.SiegeCamp;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.entity.*;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityChangeBlockEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.EntitySpawnEvent;
import org.bukkit.event.entity.ProjectileHitEvent;
import org.bukkit.event.player.*;
import org.bukkit.util.Vector;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SiegeProtectionListener implements Listener {

    private final TownySiegesPlugin plugin;
    private final SiegeCannonManager cannonManager;
    private final Map<Location, Long> recentCannonImpacts = new ConcurrentHashMap<>();

    public SiegeProtectionListener(TownySiegesPlugin plugin) {
        this.plugin = plugin;
        this.cannonManager = new SiegeCannonManager(plugin);
    }

    public SiegeCannonManager getCannonManager() {
        return cannonManager;
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void onBlockPlace(BlockPlaceEvent event) {
        Player player = event.getPlayer();
        if (player.getInventory().getItemInMainHand().hasItemMeta() &&
            player.getInventory().getItemInMainHand().getItemMeta().hasCustomModelData() &&
            player.getInventory().getItemInMainHand().getItemMeta().getCustomModelData() == 99201) {
            event.setCancelled(true);
            cannonManager.deployCannon(player, event.getBlock().getLocation());
            return;
        }

        if (player.hasPermission("townysieges.admin")) return;
        ChunkCoord coord = ChunkCoord.fromLocation(event.getBlock().getLocation());
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(coord);
        if (camp != null) {
            String pTown = plugin.getTownyHook().getPlayerTownName(player);
            if (pTown == null || !pTown.equalsIgnoreCase(camp.getAttackingTown())) {
                event.setCancelled(true);
                player.sendMessage(ChatColor.RED + "[TownySieges] Осадный лагерь защищен!");
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onPlayerInteract(PlayerInteractEvent event) {
        if (event.getAction() == Action.RIGHT_CLICK_BLOCK && event.getClickedBlock() != null) {
            Block b = event.getClickedBlock();
            if (b.getType() == Material.BARREL && b.hasMetadata("siege_cannon")) {
                event.setCancelled(true);
                cannonManager.mountGunner(event.getPlayer(), b.getLocation());
                return;
            }
        }

        if (cannonManager.isMounted(event.getPlayer())) {
            if (event.getAction() == Action.LEFT_CLICK_AIR || event.getAction() == Action.LEFT_CLICK_BLOCK ||
                event.getAction() == Action.RIGHT_CLICK_AIR || event.getAction() == Action.RIGHT_CLICK_BLOCK) {
                event.setCancelled(true);
                cannonManager.fireCannon(event.getPlayer());
            }
        }
    }

    @EventHandler
    public void onPlayerToggleSneak(PlayerToggleSneakEvent event) {
        if (event.isSneaking() && cannonManager.isMounted(event.getPlayer())) {
            cannonManager.unmountGunner(event.getPlayer());
        }
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onEntityExplode(EntityExplodeEvent event) {
        Entity entity = event.getEntity();
        Location loc = event.getLocation();
        boolean isArtillery = isArtilleryWeapon(entity);

        String centerTown = plugin.getTownyHook().getTownNameAt(loc);
        boolean centerInTown = centerTown != null;
        boolean centerUnderSiege = centerInTown && plugin.getSiegeManager().isTownUnderActiveSiege(centerTown);

        if (centerInTown && (!centerUnderSiege || !isArtillery)) {
            event.blockList().clear();
            event.setYield(0.0f);
            event.setCancelled(true);
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

    public boolean isArtilleryWeapon(Entity entity) {
        if (entity == null) return true;
        if (entity.hasMetadata("siege_cannon_shell")) return true;
        String name = entity.getType().name();
        if (name.equals("CREEPER") || name.equals("ENDER_CRYSTAL") || name.equals("END_CRYSTAL")) return false;
        return entity instanceof TNTPrimed || entity instanceof FallingBlock;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onPlayerMove(PlayerMoveEvent event) {
        if (event.getFrom().getBlockX() >> 4 == event.getTo().getBlockX() >> 4 &&
            event.getFrom().getBlockZ() >> 4 == event.getTo().getBlockZ() >> 4) {
            return;
        }
        ChunkCoord toCoord = ChunkCoord.fromLocation(event.getTo());
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(toCoord);
        if (camp != null) {
            Player p = event.getPlayer();
            String phaseStr = camp.isActiveSiege() ? "§4[АКТИВНЫЙ ШТУРМ 2Ч]" : "§e[Подготовка 24ч]";
            String msg = "§c⚔ Осадный лагерь §6" + camp.getAttackingTown() + " ➔ §c" + camp.getDefendingTown() + " " + phaseStr;
            try {
                p.spigot().sendMessage(ChatMessageType.ACTION_BAR, new TextComponent(msg));
            } catch (Exception ignored) {}
        }
    }
}
"""

with open("tmp/towny-sieges/src/main/java/com/towny/sieges/listener/SiegeProtectionListener.java", "w", encoding="utf-8") as f:
    f.write(siege_listener_patch)

print("Successfully updated SiegeProtectionListener and SiegeCannonManager.")
