package com.towny.respawn.listener;

import com.towny.respawn.TownyRespawnPlugin;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.AsyncPlayerChatEvent;

import java.util.UUID;

public class ChatRenameListener implements Listener {

    private final TownyRespawnPlugin plugin;

    public ChatRenameListener(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onPlayerChat(AsyncPlayerChatEvent event) {
        Player player = event.getPlayer();
        if (!plugin.getBedManager().isAwaitingRename(player.getUniqueId())) {
            return;
        }

        event.setCancelled(true);
        UUID bedId = plugin.getBedManager().getPendingRenameBedId(player.getUniqueId());
        plugin.getBedManager().clearPendingRename(player.getUniqueId());

        String message = event.getMessage().trim();
        if (message.equalsIgnoreCase("отмена") || message.equalsIgnoreCase("cancel") || message.equalsIgnoreCase("quit")) {
            player.sendMessage(ChatColor.YELLOW + "[TownyRespawn] Переименование кровати отменено.");
            player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASS, 1.0f, 0.8f);
            Bukkit.getScheduler().runTask(plugin, () -> {
                if (plugin.getRespawnManager().isPendingRespawn(player.getUniqueId())) {
                    plugin.getGuiManager().openDeathRespawnGui(player);
                } else {
                    plugin.getGuiManager().openRespawnGui(player);
                }
            });
            return;
        }

        String cleanName;
        if (player.hasPermission("townyrespawn.beds.color")) {
            cleanName = ChatColor.translateAlternateColorCodes('&', message);
        } else {
            cleanName = ChatColor.stripColor(ChatColor.translateAlternateColorCodes('&', message));
        }

        if (cleanName.isEmpty() || cleanName.length() > 32) {
            player.sendMessage(ChatColor.RED + "[TownyRespawn] Ошибка! Название должно быть длиной от 1 до 32 символов.");
            Bukkit.getScheduler().runTask(plugin, () -> plugin.getGuiManager().openRespawnGui(player));
            return;
        }

        boolean renamed = plugin.getBedManager().renameBed(player, bedId, cleanName);
        if (renamed) {
            player.sendMessage(ChatColor.GREEN + "[TownyRespawn] ✔ Кровать успешно переименована в: «" + ChatColor.AQUA + cleanName + ChatColor.GREEN + "»!");
            player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 1.0f, 1.5f);
        } else {
            player.sendMessage(ChatColor.RED + "[TownyRespawn] Не удалось найти кровать для переименования.");
        }

        Bukkit.getScheduler().runTask(plugin, () -> {
            if (plugin.getRespawnManager().isPendingRespawn(player.getUniqueId())) {
                plugin.getGuiManager().openDeathRespawnGui(player);
            } else {
                plugin.getGuiManager().openRespawnGui(player);
            }
        });
    }
}
