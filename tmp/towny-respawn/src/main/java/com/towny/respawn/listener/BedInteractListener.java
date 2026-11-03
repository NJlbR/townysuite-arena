package com.towny.respawn.listener;

import com.towny.respawn.TownyRespawnPlugin;
import com.towny.respawn.model.PlayerBed;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.player.PlayerBedEnterEvent;
import org.bukkit.event.player.PlayerInteractEvent;

import java.util.List;

public class BedInteractListener implements Listener {

    private final TownyRespawnPlugin plugin;

    public BedInteractListener(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBedEnter(PlayerBedEnterEvent event) {
        if (!plugin.getConfig().getBoolean("beds.enabled", true)) return;
        Player player = event.getPlayer();
        handleBedRegistration(player, event.getBed());
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onPlayerInteract(PlayerInteractEvent event) {
        if (!plugin.getConfig().getBoolean("beds.enabled", true)) return;
        if (event.getAction() != Action.RIGHT_CLICK_BLOCK) return;

        Block block = event.getClickedBlock();
        if (block == null) return;

        Material mat = block.getType();
        if (mat.name().endsWith("_BED")) {
            Player player = event.getPlayer();
            if (plugin.getConfig().getBoolean("beds.auto-register-on-interact", true)) {
                handleBedRegistration(player, block);
            }
        }
    }

    private void handleBedRegistration(Player player, Block clickedBlock) {
        if (player == null || clickedBlock == null) return;

        boolean success = plugin.getBedManager().registerBed(player, clickedBlock);
        if (success) {
            List<PlayerBed> beds = plugin.getBedManager().getBeds(player);
            int current = beds.size();
            int max = plugin.getBedManager().getMaxBeds(player);
            PlayerBed registeredBed = beds.get(beds.size() - 1);

            String prefix = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.prefix", "&b&l[TownyRespawn]&r "));
            String msg = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.bed-registered", "&a✔ Кровать «{name}» успешно привязана! ({current}/{max})"))
                    .replace("{name}", registeredBed.getName())
                    .replace("{current}", String.valueOf(current))
                    .replace("{max}", String.valueOf(max));
            player.sendMessage(prefix + msg);
            player.sendMessage(ChatColor.YELLOW + "[TownyRespawn] Переименовать кровать: " + ChatColor.WHITE + "/respawn rename " + current + " <новое имя>" + ChatColor.GRAY + " или через " + ChatColor.AQUA + "/respawn (ПКМ)");
        }
    }

    /* -------------------------------------------------------------
     * Automatic destruction listeners: remove broken bed instantly!
     * ------------------------------------------------------------- */

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        Block block = event.getBlock();
        if (block.getType().name().endsWith("_BED")) {
            plugin.getBedManager().cleanupDestroyedBedsAt(block);
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockExplode(BlockExplodeEvent event) {
        for (Block b : event.blockList()) {
            if (b.getType().name().endsWith("_BED")) {
                plugin.getBedManager().cleanupDestroyedBedsAt(b);
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onEntityExplode(EntityExplodeEvent event) {
        for (Block b : event.blockList()) {
            if (b.getType().name().endsWith("_BED")) {
                plugin.getBedManager().cleanupDestroyedBedsAt(b);
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockBurn(BlockBurnEvent event) {
        Block b = event.getBlock();
        if (b.getType().name().endsWith("_BED")) {
            plugin.getBedManager().cleanupDestroyedBedsAt(b);
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onPistonExtend(BlockPistonExtendEvent event) {
        for (Block b : event.getBlocks()) {
            if (b.getType().name().endsWith("_BED")) {
                plugin.getBedManager().cleanupDestroyedBedsAt(b);
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onPistonRetract(BlockPistonRetractEvent event) {
        for (Block b : event.getBlocks()) {
            if (b.getType().name().endsWith("_BED")) {
                plugin.getBedManager().cleanupDestroyedBedsAt(b);
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockPhysics(BlockPhysicsEvent event) {
        Block b = event.getBlock();
        if (b.getType().name().endsWith("_BED")) {
            // If the bed is being popped off due to missing block beneath
            Bukkit.getScheduler().runTask(plugin, () -> {
                if (!b.getType().name().endsWith("_BED")) {
                    plugin.getBedManager().cleanupDestroyedBedsAt(b);
                }
            });
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockFromTo(BlockFromToEvent event) {
        Block to = event.getToBlock();
        if (to.getType().name().endsWith("_BED")) {
            // If liquid flows into bed
            Bukkit.getScheduler().runTask(plugin, () -> {
                if (!to.getType().name().endsWith("_BED")) {
                    plugin.getBedManager().cleanupDestroyedBedsAt(to);
                }
            });
        }
    }
}
