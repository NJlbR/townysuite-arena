package com.towny.respawn.listener;

import com.towny.respawn.TownyRespawnPlugin;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.*;

import java.util.UUID;

public class DeathRespawnListener implements Listener {

    private final TownyRespawnPlugin plugin;

    public DeathRespawnListener(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerDeath(PlayerDeathEvent event) {
        Player player = event.getEntity();
        plugin.getRespawnManager().markPendingRespawn(player.getUniqueId());

        // Мгновенный перевод в Limbo и меню без задержки на экране смерти
        Bukkit.getScheduler().runTaskLater(plugin, () -> {
            if (player.isOnline() && player.isDead()) {
                try {
                    player.spigot().respawn();
                } catch (Throwable ignored) {}
            }
        }, 1L);
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerRespawn(PlayerRespawnEvent event) {
        Player player = event.getPlayer();

        // Направляем точку респавна в безопасное Limbo высоко в небе под лимитом мира,
        // чтобы игрок ВООБЩЕ не появлялся в игровом мире и не мешал другим игрокам!
        Location limboLoc = plugin.getRespawnManager().getLimboLocation(player);
        event.setRespawnLocation(limboLoc);

        // Помещаем игрока в Limbo (скрыт от всех, невидим, без коллизии, режим ADVENTURE)
        plugin.getRespawnManager().enterLimbo(player);

        long delay = plugin.getConfig().getLong("respawn.gui-open-delay-ticks", 1L);
        Bukkit.getScheduler().runTaskLater(plugin, () -> {
            if (player.isOnline() && plugin.getRespawnManager().isLimbo(player.getUniqueId())) {
                // Повторно скрываем игрока для всех игроков, так как Bukkit мог завершить спавн-трекер
                for (Player other : Bukkit.getOnlinePlayers()) {
                    if (!other.equals(player)) {
                        try {
                            other.hidePlayer(plugin, player);
                        } catch (Throwable ignored) {}
                    }
                }
                plugin.getGuiManager().openDeathRespawnGui(player);
            }
        }, Math.max(1L, delay));
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player joined = event.getPlayer();
        UUID uuid = joined.getUniqueId();

        // Если сам зашедший игрок ранее находился в Limbo или ожидает респавна
        if (plugin.getRespawnManager().isLimbo(uuid) || plugin.getRespawnManager().isPendingRespawn(uuid)) {
            joined.teleport(plugin.getRespawnManager().getLimboLocation(joined));
            plugin.getRespawnManager().enterLimbo(joined);
            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                if (joined.isOnline()) {
                    plugin.getGuiManager().openDeathRespawnGui(joined);
                }
            }, 5L);
        }

        // Скрываем от вновь зашедшего игрока всех тех, кто сейчас находится в Limbo
        for (UUID limboUuid : plugin.getRespawnManager().getLimboPlayers()) {
            Player limboPlayer = Bukkit.getPlayer(limboUuid);
            if (limboPlayer != null && limboPlayer.isOnline() && !limboPlayer.equals(joined)) {
                try {
                    joined.hidePlayer(plugin, limboPlayer);
                } catch (Throwable ignored) {}
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onPlayerMove(PlayerMoveEvent event) {
        Player player = event.getPlayer();
        if (plugin.getRespawnManager().isLimbo(player.getUniqueId())) {
            Location from = event.getFrom();
            Location to = event.getTo();
            if (to != null && (from.getBlockX() != to.getBlockX() || from.getBlockY() != to.getBlockY() || from.getBlockZ() != to.getBlockZ())) {
                // Фиксируем координаты в Limbo, позволяя только поворачивать камеру
                event.setTo(new Location(from.getWorld(), from.getX(), from.getY(), from.getZ(), to.getYaw(), to.getPitch()));
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onEntityDamage(EntityDamageEvent event) {
        if (event.getEntity() instanceof Player) {
            Player player = (Player) event.getEntity();
            if (plugin.getRespawnManager().isLimbo(player.getUniqueId())) {
                event.setCancelled(true);
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onEntityDamageByEntity(EntityDamageByEntityEvent event) {
        if (event.getDamager() instanceof Player) {
            Player damager = (Player) event.getDamager();
            if (plugin.getRespawnManager().isLimbo(damager.getUniqueId())) {
                event.setCancelled(true);
            }
        }
        if (event.getEntity() instanceof Player) {
            Player victim = (Player) event.getEntity();
            if (plugin.getRespawnManager().isLimbo(victim.getUniqueId())) {
                event.setCancelled(true);
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onPlayerInteract(PlayerInteractEvent event) {
        if (plugin.getRespawnManager().isLimbo(event.getPlayer().getUniqueId())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onPlayerInteractEntity(PlayerInteractEntityEvent event) {
        if (plugin.getRespawnManager().isLimbo(event.getPlayer().getUniqueId())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onPlayerInteractAtEntity(PlayerInteractAtEntityEvent event) {
        if (plugin.getRespawnManager().isLimbo(event.getPlayer().getUniqueId())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        if (plugin.getRespawnManager().isLimbo(event.getPlayer().getUniqueId())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onBlockPlace(BlockPlaceEvent event) {
        if (plugin.getRespawnManager().isLimbo(event.getPlayer().getUniqueId())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onDropItem(PlayerDropItemEvent event) {
        if (plugin.getRespawnManager().isLimbo(event.getPlayer().getUniqueId())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onPickupItem(EntityPickupItemEvent event) {
        if (event.getEntity() instanceof Player) {
            Player p = (Player) event.getEntity();
            if (plugin.getRespawnManager().isLimbo(p.getUniqueId())) {
                event.setCancelled(true);
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onSwapHandItems(PlayerSwapHandItemsEvent event) {
        if (plugin.getRespawnManager().isLimbo(event.getPlayer().getUniqueId())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onPlayerCommand(PlayerCommandPreprocessEvent event) {
        Player player = event.getPlayer();
        if (plugin.getRespawnManager().isLimbo(player.getUniqueId())) {
            if (!player.hasPermission("townyrespawn.admin") && !player.isOp()) {
                event.setCancelled(true);
                player.sendMessage(ChatColor.RED + "Вы не можете использовать команды во время выбора точки возрождения!");
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onEntityTarget(EntityTargetLivingEntityEvent event) {
        if (event.getTarget() instanceof Player) {
            Player target = (Player) event.getTarget();
            if (plugin.getRespawnManager().isLimbo(target.getUniqueId())) {
                event.setCancelled(true);
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onProjectileHit(ProjectileHitEvent event) {
        if (event.getHitEntity() instanceof Player) {
            Player hit = (Player) event.getHitEntity();
            if (plugin.getRespawnManager().isLimbo(hit.getUniqueId())) {
                event.setCancelled(true);
            }
        }
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        UUID uuid = event.getPlayer().getUniqueId();
        plugin.getRespawnManager().cancelLimboTicker(uuid);
    }
}
