package com.towny.sieges.listener;

import com.palmergames.bukkit.towny.event.ChunkNotificationEvent;
import com.palmergames.bukkit.towny.event.PlayerChangePlotEvent;
import com.palmergames.bukkit.towny.event.TitleNotificationEvent;
import com.palmergames.bukkit.towny.object.WorldCoord;
import com.palmergames.bukkit.towny.object.notification.TitleNotification;
import com.palmergames.bukkit.towny.utils.ChunkNotificationUtil;
import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.ChunkCoord;
import com.towny.sieges.model.SiegeCamp;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;

/**
 * TownyNotificationListener intercepts Towny's plot transition and chunk notification events:
 * 1. PlayerChangePlotEvent: sets setShowingPlotNotifications(false) when entering a Siege Camp
 *    to prevent Towny from scheduling its 1-tick delayed '~ Wilderness' action bar task.
 * 2. ChunkNotificationEvent: overrides event.setMessage() so that if Towny ever creates
 *    a notification for a Siege Camp chunk, it broadcasts the Siege Camp info instead of Wilderness.
 * 3. TitleNotificationEvent: overrides Title / Subtitle notifications for Siege Camp chunks.
 * 4. Cancels any stale Towny player notification tasks via ChunkNotificationUtil.cancelPlayerTasks(player).
 */
public class TownyNotificationListener implements Listener {

    private final TownySiegesPlugin plugin;

    public TownyNotificationListener(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onPlayerChangePlot(PlayerChangePlotEvent event) {
        if (event == null) return;
        WorldCoord to = event.getTo();
        if (to == null) return;

        ChunkCoord coord = new ChunkCoord(to.getWorldName(), to.getX(), to.getZ());
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(coord);
        if (camp != null) {
            // CRITICAL FIX: Suppress Towny's default Wilderness notification task!
            // When false, Towny skips scheduling ChunkNotificationUtil.showChunkNotification completely.
            event.setShowingPlotNotifications(false);

            Player player = event.getPlayer();
            if (player != null && player.isOnline()) {
                // Cancel any pending Towny actionbar tasks
                try {
                    ChunkNotificationUtil.cancelPlayerTasks(player);
                } catch (Throwable ignored) {}

                String phaseStr = camp.isActiveSiege() ? "§4[АКТИВНЫЙ ШТУРМ 2Ч]" : "§e[Подготовка 24ч]";
                String siegeMsg = "§c⚔ Осадный лагерь города §6" + camp.getAttackingTown() +
                        " §7(Цель: §c" + camp.getDefendingTown() + "§7) " + phaseStr;

                sendActionBar(player, siegeMsg);

                // Re-assert at tick 2 and 6 to defeat any other external HUD tasks
                Bukkit.getScheduler().runTaskLater(plugin, () -> {
                    if (player.isOnline() && isPlayerInCamp(player, camp)) {
                        sendActionBar(player, siegeMsg);
                    }
                }, 2L);
                Bukkit.getScheduler().runTaskLater(plugin, () -> {
                    if (player.isOnline() && isPlayerInCamp(player, camp)) {
                        sendActionBar(player, siegeMsg);
                    }
                }, 6L);
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void onChunkNotification(ChunkNotificationEvent event) {
        if (event == null) return;
        WorldCoord to = event.getToCoord();
        if (to == null) return;

        ChunkCoord coord = new ChunkCoord(to.getWorldName(), to.getX(), to.getZ());
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(coord);
        if (camp != null) {
            Player player = event.getPlayer();
            if (player != null && player.isOnline()) {
                try {
                    ChunkNotificationUtil.cancelPlayerTasks(player);
                } catch (Throwable ignored) {}
            }

            String phaseStr = camp.isActiveSiege() ? "§4[АКТИВНЫЙ ШТУРМ 2Ч]" : "§e[Подготовка 24ч]";
            String siegeMsg = "§c⚔ Осадный лагерь города §6" + camp.getAttackingTown() +
                    " §7(Цель: §c" + camp.getDefendingTown() + "§7) " + phaseStr;

            // Replace Towny's "~ Wilderness" string with our Siege Camp message!
            event.setMessage(siegeMsg);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void onTitleNotification(TitleNotificationEvent event) {
        if (event == null) return;
        TitleNotification tn = event.getTitleNotification();
        if (tn == null) return;
        WorldCoord to = tn.getWorldCoord();
        if (to == null) return;

        ChunkCoord coord = new ChunkCoord(to.getWorldName(), to.getX(), to.getZ());
        SiegeCamp camp = plugin.getSiegeManager().getSiegeCampAt(coord);
        if (camp != null) {
            String phaseStr = camp.isActiveSiege() ? "§4[ШТУРМ 2Ч]" : "§e[Подготовка 24ч]";
            tn.setTitleNotification("§c⚔ Осадный лагерь §6" + camp.getAttackingTown());
            tn.setSubtitleNotification("§eЦель: §c" + camp.getDefendingTown() + " §7| " + phaseStr);
        }
    }

    private boolean isPlayerInCamp(Player p, SiegeCamp camp) {
        if (p == null || camp == null || !p.isOnline()) return false;
        ChunkCoord c = ChunkCoord.fromLocation(p.getLocation());
        return camp.containsChunk(c);
    }

    private void sendActionBar(Player p, String message) {
        try {
            p.spigot().sendMessage(ChatMessageType.ACTION_BAR, new TextComponent(message));
        } catch (Throwable ignored) {}
    }
}
