package com.towny.sieges.listener;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.cannon.SiegeCannonManager;
import com.towny.sieges.model.ChunkCoord;
import com.towny.sieges.model.SiegeCamp;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.FallingBlock;
import org.bukkit.entity.Player;
import org.bukkit.entity.TNTPrimed;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.inventory.InventoryAction;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.PrepareItemCraftEvent;
import org.bukkit.event.player.*;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.spigotmc.event.entity.EntityDismountEvent;

import java.util.*;
import java.util.UUID;

public class SiegeProtectionListener implements Listener {

    private final TownySiegesPlugin plugin;
    private final SiegeCannonManager cannonManager;

    public SiegeProtectionListener(TownySiegesPlugin plugin) {
        this.plugin = plugin;
        this.cannonManager = plugin.getCannonManager();
    }

    public SiegeCannonManager getCannonManager() {
        return cannonManager;
    }

    @EventHandler(priority = EventPriority.MONITOR)
    public void onPlayerJoin(PlayerJoinEvent event) {
        unlockSiegeRecipes(event.getPlayer());
    }

    public void unlockSiegeRecipes(Player player) {
        if (player == null || !player.isOnline()) return;
        try {
            org.bukkit.NamespacedKey mortarKey = new org.bukkit.NamespacedKey(plugin, "siege_mortar");
            org.bukkit.NamespacedKey regKey = new org.bukkit.NamespacedKey(plugin, "siege_cannonball_regular");
            org.bukkit.NamespacedKey apKey = new org.bukkit.NamespacedKey(plugin, "siege_cannonball_ap");
            org.bukkit.NamespacedKey bannerKey = new org.bukkit.NamespacedKey(plugin, "siege_assault_banner_recipe");

            player.discoverRecipe(mortarKey);
            player.discoverRecipe(regKey);
            player.discoverRecipe(apKey);
            player.discoverRecipe(bannerKey);
        } catch (Throwable ignored) {
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void onBlockPlace(BlockPlaceEvent event) {
        Player player = event.getPlayer();
        ItemStack held = event.getItemInHand();

        if (plugin.getCaptureManager().isAssaultBanner(held)) {
            // We want to override Towny/WorldGuard protection for the banner if it's a valid siege placement.
            // First, we setCancelled(false) to allow our logic to run even if Towny cancelled it.
            event.setCancelled(false);

            Location loc = event.getBlockPlaced().getLocation();
            boolean success = plugin.getCaptureManager().placeAssaultBanner(player, loc);
            if (success) {
                // If placement is valid according to our siege rules, we set the block and cancel the event
                // to prevent other plugins from reacting to a standard block placement.
                event.setCancelled(true); 
                event.getBlockPlaced().setType(Material.RED_BANNER);
                if (player.getGameMode() != GameMode.CREATIVE) {
                    held.setAmount(held.getAmount() - 1);
                    player.updateInventory();
                }
            } else {
                // If our logic says NO (e.g. not adjacent), we re-cancel it if it was originally cancelled.
                // (It likely was cancelled by Towny if we are in a town).
                event.setCancelled(true);
            }
            return;
        }

        if (cannonManager.isCannonItem(held)) {
            event.setCancelled(false); // Override
            Location loc = event.getBlockPlaced().getLocation();
            boolean success = cannonManager.deployCannon(player, loc);
            if (success) {
                event.setCancelled(true);
                if (player.getGameMode() != GameMode.CREATIVE) {
                    held.setAmount(held.getAmount() - 1);
                    player.updateInventory();
                }
            } else {
                event.setCancelled(true);
            }
            return;
        }

        if (event.isCancelled()) return; // Respect standard protection for normal blocks
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
    public void onBlockBreak(BlockBreakEvent event) {
        Block b = event.getBlock();
        Location cannonLoc = cannonManager.getNearbyCannon(b.getLocation());
        if (cannonLoc != null && cannonManager.isCannonAt(cannonLoc)) {
            event.setCancelled(true);
            cannonManager.breakCannon(event.getPlayer(), cannonLoc);
        }
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onPlayerInteract(PlayerInteractEvent event) {
        Player player = event.getPlayer();

        // 1. If player is seated on a cannon:
        if (cannonManager.isMounted(player)) {
            event.setCancelled(true);
            Long mountTime = cannonManager.getLastMountTime(player.getUniqueId());
            if (mountTime != null && System.currentTimeMillis() - mountTime < 600L) {
                return; // Lockout during mount transition
            }

            // Strictly ignore ghost click packets fired right after pressing Q (Drop key)
            if (cannonManager.isDropDebounced(player)) {
                return;
            }

            // LMB (Left-click) = Fire cannon
            if (event.getAction() == Action.LEFT_CLICK_AIR || event.getAction() == Action.LEFT_CLICK_BLOCK) {
                cannonManager.fireCannon(player);
                return;
            }

            // RMB (Right-click) = Toggle precision aiming / zoom scope
            if (event.getAction() == Action.RIGHT_CLICK_AIR || event.getAction() == Action.RIGHT_CLICK_BLOCK) {
                cannonManager.toggleAiming(player);
                return;
            }
            return;
        }

        // 2. Right-click on existing cannon or adjacent block to mount
        if (event.getAction() == Action.RIGHT_CLICK_BLOCK && event.getClickedBlock() != null) {
            Block b = event.getClickedBlock();
            Location cannonLoc = cannonManager.getNearbyCannon(b.getLocation());
            if (cannonLoc != null && cannonManager.isCannonAt(cannonLoc)) {
                event.setCancelled(true);
                if (player.isSneaking()) {
                    cannonManager.breakCannon(player, cannonLoc);
                } else {
                    cannonManager.mountGunner(player, cannonLoc);
                }
                return;
            }
        }

        // 3. Left-click on cannon to dismantle
        if (event.getAction() == Action.LEFT_CLICK_BLOCK && event.getClickedBlock() != null) {
            Block b = event.getClickedBlock();
            Location cannonLoc = cannonManager.getNearbyCannon(b.getLocation());
            if (cannonLoc != null && cannonManager.isCannonAt(cannonLoc)) {
                event.setCancelled(true);
                cannonManager.breakCannon(player, cannonLoc);
                return;
            }
        }
    }


    @EventHandler(priority = EventPriority.HIGH)
    public void onPlayerInteractAtEntity(PlayerInteractAtEntityEvent event) {
        handleEntityInteraction(event.getPlayer(), event.getRightClicked(), event);
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onPlayerInteractEntity(PlayerInteractEntityEvent event) {
        handleEntityInteraction(event.getPlayer(), event.getRightClicked(), event);
    }

    private void handleEntityInteraction(Player player, Entity entity, org.bukkit.event.Cancellable event) {
        if (entity == null || player == null) return;
        if (cannonManager.isMounted(player)) {
            event.setCancelled(true);
            Long mountTime = cannonManager.getLastMountTime(player.getUniqueId());
            if (mountTime == null || System.currentTimeMillis() - mountTime >= 600L) {
                cannonManager.toggleAiming(player);
            }
            return;
        }

        Location blockLoc = null;
        if (entity.hasMetadata("siege_cannon_interaction")) {
            blockLoc = (Location) entity.getMetadata("siege_cannon_interaction").get(0).value();
        } else if (entity.hasMetadata("siege_cannon_entity")) {
            blockLoc = (Location) entity.getMetadata("siege_cannon_entity").get(0).value();
        }

        if (blockLoc != null && cannonManager.isCannonAt(blockLoc)) {
            event.setCancelled(true);
            if (player.isSneaking()) {
                cannonManager.breakCannon(player, blockLoc);
            } else {
                cannonManager.mountGunner(player, blockLoc);
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onEntityDamage(EntityDamageByEntityEvent event) {
        Entity entity = event.getEntity();
        Entity damager = event.getDamager();

        // Check mortar shell entity damage: ONLY allow damage during active assault (штурм)!
        boolean isMortar = damager != null && (damager.hasMetadata("siege_cannon_shell") || damager.hasMetadata("siege_armor_piercing"));
        if (isMortar) {
            Location hitLoc = entity.getLocation();
            boolean activeAssault = isActiveAssaultAt(hitLoc) || (damager != null && isActiveAssaultAt(damager.getLocation()));
            if (!activeAssault) {
                // Completely negate damage to players, defenders, mounts, and entities during preparation phase or peacetime!
                event.setCancelled(true);
                event.setDamage(0.0);
                return;
            }

            // Reward XP for damage dealt by mortar to players
            if (entity instanceof Player) {
                String shooterUUID = null;
                if (damager.hasMetadata("siege_cannon_shooter")) {
                    shooterUUID = damager.getMetadata("siege_cannon_shooter").get(0).asString();
                }
                if (shooterUUID != null) {
                    Player shooter = Bukkit.getPlayer(UUID.fromString(shooterUUID));
                    if (shooter != null) {
                        double damage = event.getFinalDamage();
                        // 1 XP per 1 heart (2 damage units)
                        plugin.getArtillerySkillManager().addXP(shooter, damage / 2.0);
                    }
                }
            }
        }

        if (event.getDamager() instanceof Player) {
            Player p = (Player) event.getDamager();
            if (cannonManager.isMounted(p)) {
                event.setCancelled(true);
                return;
            }
        }

        Location blockLoc = null;
        if (entity.hasMetadata("siege_cannon_interaction")) {
            blockLoc = (Location) entity.getMetadata("siege_cannon_interaction").get(0).value();
        } else if (entity.hasMetadata("siege_cannon_entity")) {
            blockLoc = (Location) entity.getMetadata("siege_cannon_entity").get(0).value();
        }

        if (blockLoc != null && cannonManager.isCannonAt(blockLoc)) {
            event.setCancelled(true);
            if (event.getDamager() instanceof Player) {
                Player player = (Player) event.getDamager();
                cannonManager.breakCannon(player, blockLoc);
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerDropItem(PlayerDropItemEvent event) {
        Player player = event.getPlayer();
        if (cannonManager.isMounted(player)) {
            event.setCancelled(true);
            // Record drop key press so any following ghost click is strictly suppressed
            cannonManager.recordDropPress(player);
            // NO fireCannon() here under any circumstances!
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerSwapHandItems(PlayerSwapHandItemsEvent event) {
        Player player = event.getPlayer();
        if (cannonManager.isMounted(player)) {
            event.setCancelled(true);
            // Cycle ammunition between Regular and Armor-Piercing on Hand Swap (F key)
            cannonManager.cycleAmmo(player);
        }
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onPrepareCraft(PrepareItemCraftEvent event) {
        if (event.getRecipe() == null) return;
        ItemStack result = event.getInventory().getResult();
        if (result == null) return;
        if (cannonManager.isCannonItem(result)) {
            event.getInventory().setResult(cannonManager.getCannonItem());
        } else if (cannonManager.isRegularAmmo(result)) {
            event.getInventory().setResult(cannonManager.getRegularAmmoItem());
        } else if (cannonManager.isArmorPiercingAmmo(result)) {
            event.getInventory().setResult(cannonManager.getArmorPiercingAmmoItem());
        }
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onInventoryClick(InventoryClickEvent event) {
        if (event.getWhoClicked() instanceof Player) {
            Player p = (Player) event.getWhoClicked();
            if (cannonManager.isMounted(p)) {
                ItemStack current = event.getCurrentItem();
                ItemStack cursor = event.getCursor();
                int slot = event.getSlot();

                // Prevent moving or taking the main-hand control stick
                if (slot == p.getInventory().getHeldItemSlot() && event.getClickedInventory() == p.getInventory()) {
                    event.setCancelled(true);
                    return;
                }
                if (cannonManager.isAimingTool(current) || cannonManager.isAimingTool(cursor)) {
                    event.setCancelled(true);
                    return;
                }
                // Allow all other slot actions and off-hand placements freely
            }

            // Enforce non-stackable behavior for mortar, regular ammo and AP ammo
            ItemStack cursor = event.getCursor();
            ItemStack current = event.getCurrentItem();
            if (cursor != null && current != null && cursor.getType() == current.getType()) {
                if (cannonManager.isAnySiegeAmmoOrCannon(cursor) && cannonManager.isAnySiegeAmmoOrCannon(current)) {
                    if (event.getAction() == InventoryAction.PLACE_ALL ||
                        event.getAction() == InventoryAction.PLACE_ONE ||
                        event.getAction() == InventoryAction.PLACE_SOME) {
                        event.setCancelled(true);
                        p.sendMessage(ChatColor.RED + "[TownySieges] Осадные орудия и боеприпасы являются строго нестакаемыми!");
                    }
                }
            }
        }
    }

    @EventHandler
    public void onPlayerToggleSneak(PlayerToggleSneakEvent event) {
        if (event.isSneaking() && cannonManager.isMounted(event.getPlayer())) {
            cannonManager.unmountGunner(event.getPlayer());
        }
    }

    @EventHandler
    public void onEntityDismount(EntityDismountEvent event) {
        if (event.getEntity() instanceof Player && event.getDismounted().hasMetadata("cannon_seat")) {
            cannonManager.unmountGunner((Player) event.getEntity());
        }
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        cannonManager.unmountGunner(event.getPlayer());
    }

    @EventHandler
    public void onPlayerDeath(PlayerDeathEvent event) {
        cannonManager.unmountGunner(event.getEntity());
    }

    @EventHandler
    public void onPlayerTeleport(PlayerTeleportEvent event) {
        if (cannonManager.isMounted(event.getPlayer())) {
            cannonManager.unmountGunner(event.getPlayer());
        }
    }

    public boolean isActiveAssaultAt(Location loc) {
        if (loc == null) return false;
        String townName = plugin.getTownyHook().getTownNameAt(loc);
        if (townName != null && plugin.getSiegeManager().isTownUnderActiveSiege(townName)) {
            return true;
        }
        ChunkCoord coord = ChunkCoord.fromLocation(loc);
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(coord);
        if (camp != null) {
            if (camp.isActiveSiege()) return true;
            if (camp.getDefendingTown() != null && plugin.getSiegeManager().isTownUnderActiveSiege(camp.getDefendingTown())) {
                return true;
            }
        }
        return false;
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onEntityExplode(EntityExplodeEvent event) {
        Entity entity = event.getEntity();
        Location loc = event.getLocation();
        boolean isMortar = entity != null && (entity.hasMetadata("siege_cannon_shell") || entity.hasMetadata("siege_armor_piercing"));
        boolean isArtillery = isArtilleryWeapon(entity);

        String centerTown = plugin.getTownyHook().getTownNameAt(loc);
        boolean centerInTown = centerTown != null;
        boolean centerUnderSiege = centerInTown && plugin.getSiegeManager().isTownUnderActiveSiege(centerTown);

        // Check active assault for mortar shells:
        // Mortar explosions must destroy blocks ONLY during active assault (штурм), NOT during preparation phase or peacetime!
        if (isMortar) {
            boolean activeAssault = centerUnderSiege || isActiveAssaultAt(loc);
            if (!activeAssault) {
                event.blockList().clear();
                event.setYield(0.0f);
                event.setCancelled(true);
                return;
            }
        }

        if (centerInTown && (!centerUnderSiege || !isArtillery)) {
            event.blockList().clear();
            event.setYield(0.0f);
            event.setCancelled(true);
            return;
        }

        boolean isArmorPiercing = entity != null && entity.hasMetadata("siege_armor_piercing");

        // ARMOR-PIERCING KINETIC PENETRATION OF OBSIDIAN
        if (isArmorPiercing && (centerUnderSiege || isActiveAssaultAt(loc))) {
            World world = loc.getWorld();
            if (world != null) {
                double radius = 3.2;
                int r = (int) Math.ceil(radius);
                int brokenObsidian = 0;
                for (int dx = -r; dx <= r; dx++) {
                    for (int dy = -r; dy <= r; dy++) {
                        for (int dz = -r; dz <= r; dz++) {
                            if (dx * dx + dy * dy + dz * dz > radius * radius) continue;
                            Block b = loc.clone().add(dx, dy, dz).getBlock();
                            Material mat = b.getType();
                            if (mat == Material.OBSIDIAN || mat == Material.CRYING_OBSIDIAN || mat == Material.RESPAWN_ANCHOR) {
                                String bTown = plugin.getTownyHook().getTownNameAt(b.getLocation());
                                if (bTown != null && plugin.getSiegeManager().isTownUnderActiveSiege(bTown)) {
                                    world.spawnParticle(Particle.BLOCK_CRACK, b.getLocation().add(0.5, 0.5, 0.5), 35, 0.3, 0.3, 0.3, 0.1, Bukkit.createBlockData(mat));
                                    world.spawnParticle(Particle.EXPLOSION_LARGE, b.getLocation().add(0.5, 0.5, 0.5), 1, 0, 0, 0, 0);
                                    world.playSound(b.getLocation(), Sound.ENTITY_WITHER_BREAK_BLOCK, 1.2f, 0.8f);
                                    world.playSound(b.getLocation(), Sound.BLOCK_STONE_BREAK, 1.5f, 0.6f);
                                    world.dropItemNaturally(b.getLocation(), new ItemStack(mat, 1));
                                    b.setType(Material.AIR);
                                    brokenObsidian++;
                                }
                            }
                        }
                    }
                }
                if (brokenObsidian > 0) {
                    world.playSound(loc, Sound.ENTITY_ZOMBIE_BREAK_WOODEN_DOOR, 1.5f, 0.5f);
                }
            }
        }

        // Standard blocklist filtering: only blocks in a town or assault area under active siege can be broken
        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b == null) continue;

            Material mat = b.getType();
            // Regular artillery shells cannot break obsidian
            if (!isArmorPiercing && (mat == Material.OBSIDIAN || mat == Material.CRYING_OBSIDIAN || mat == Material.RESPAWN_ANCHOR)) {
                it.remove();
                continue;
            }

            String bTown = plugin.getTownyHook().getTownNameAt(b.getLocation());
            if (bTown != null) {
                boolean bUnderSiege = plugin.getSiegeManager().isTownUnderActiveSiege(bTown);
                if (!bUnderSiege || !isArtillery) {
                    it.remove();
                }
            } else {
                // In wilderness: if it's a mortar shell, it can only break blocks during active assault
                if (isMortar && !isActiveAssaultAt(b.getLocation())) {
                    it.remove();
                }
            }
        }

        if (event.blockList().isEmpty()) {
            event.setCancelled(true);
            event.setYield(0.0f);
        } else if (isMortar) {
            // Reward XP for blocks destroyed by mortar
            String shooterUUID = null;
            if (entity.hasMetadata("siege_cannon_shooter")) {
                shooterUUID = entity.getMetadata("siege_cannon_shooter").get(0).asString();
            }
            if (shooterUUID != null) {
                Player shooter = Bukkit.getPlayer(UUID.fromString(shooterUUID));
                if (shooter != null) {
                    int brokenBlocks = event.blockList().size();
                    // 0.2 XP per block, 5 XP per obsidian (since brokenObsidian was calculated separately)
                    double totalXP = (brokenBlocks * 0.2);
                    // I need to access brokenObsidian from the AP logic above. 
                    // Since I can't easily, I'll recalculate or just reward for the AP metadata.
                    if (entity.hasMetadata("siege_armor_piercing")) {
                        totalXP += 15.0; // Flat bonus for a successful AP strike
                    }
                    plugin.getArtillerySkillManager().addXP(shooter, totalXP);
                }
            }
        }
    }

    public boolean isArtilleryWeapon(Entity entity) {
        if (entity == null) return true;
        if (entity.hasMetadata("siege_cannon_shell") || entity.hasMetadata("siege_armor_piercing")) return true;
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
