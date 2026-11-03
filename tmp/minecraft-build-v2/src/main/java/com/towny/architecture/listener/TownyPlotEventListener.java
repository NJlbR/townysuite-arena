package com.towny.architecture.listener;

import com.palmergames.bukkit.towny.event.ChunkNotificationEvent;
import com.palmergames.bukkit.towny.event.PlayerChangePlotEvent;
import com.palmergames.bukkit.towny.event.PlotChangeTypeEvent;
import com.palmergames.bukkit.towny.event.TitleNotificationEvent;
import com.palmergames.bukkit.towny.object.TownBlock;
import com.palmergames.bukkit.towny.object.TownBlockType;
import com.palmergames.bukkit.towny.object.WorldCoord;
import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.ChunkCoord;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.ChatColor;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerMoveEvent;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

import com.palmergames.bukkit.towny.event.PlotClearEvent;

public class TownyPlotEventListener implements Listener {

    private final TownyArchitecturePlugin plugin;
    private final Map<UUID, Long> lastActionBarSent = new ConcurrentHashMap<>();

    public TownyPlotEventListener(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
    }

    private String getPlotBuildingTitle(ChunkCoord cc, Player player) {
        ActiveBuilding bld = plugin.getBuildingManager().getBuildingOccupyingChunk(cc);
        if (bld != null) {
            BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
            String bpName = bp != null ? bp.getNameRu() : bld.getBlueprintId();
            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                return "В процессе постройки: " + bpName;
            } else if (bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                return bpName + " [Повреждено]";
            } else {
                return bpName;
            }
        }

        String playerTown = plugin.getTownyHook().getPlayerTownName(player);
        if (playerTown != null && plugin.getBuildingManager().getTownBuildPlots(playerTown).contains(cc)) {
            return "Стройплощадка";
        }

        for (String town : plugin.getBuildingManager().getAllTownsWithPlots()) {
            if (plugin.getBuildingManager().getTownBuildPlots(town).contains(cc)) {
                return "Стройплощадка (" + town + ")";
            }
        }

        return null;
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onChunkNotification(ChunkNotificationEvent event) {
        if (event.getToCoord() == null) return;
        String wName = event.getPlayer() != null ? event.getPlayer().getWorld().getName() : "world";
        ChunkCoord cc = new ChunkCoord(wName, event.getToCoord().getX(), event.getToCoord().getZ());
        String customTitle = getPlotBuildingTitle(cc, event.getPlayer());
        if (customTitle == null) return;

        String msg = event.getMessage();
        if (msg == null) return;

        // Replace any "ничейное", "Ничейное", "unclaimed" with building title
        if (msg.matches("(?i).*?(ничейное|unclaimed).*?")) {
            msg = msg.replaceAll("(?i)ничейное|unclaimed", ChatColor.GOLD + customTitle + ChatColor.RESET);
        } else if (!msg.contains(customTitle)) {
            msg = msg + " " + ChatColor.GOLD + "«" + customTitle + "»";
        }
        event.setMessage(msg);
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onTitleNotification(TitleNotificationEvent event) {
        if (event.getTitleNotification() == null || event.getTitleNotification().getWorldCoord() == null) return;
        WorldCoord wc = event.getTitleNotification().getWorldCoord();
        ChunkCoord cc = new ChunkCoord(wc.getWorldName(), wc.getX(), wc.getZ());
        String customTitle = getPlotBuildingTitle(cc, event.getPlayer());
        if (customTitle == null) return;

        var tn = event.getTitleNotification();
        String sub = tn.getSubtitleNotification();
        if (sub == null || sub.isEmpty() || sub.matches("(?i).*?(ничейное|unclaimed).*?")) {
            tn.setSubtitleNotification(ChatColor.GOLD + customTitle);
        }
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onPlayerChangePlot(PlayerChangePlotEvent event) {
        if (event.getTo() == null) return;
        ChunkCoord cc = new ChunkCoord(event.getTo().getWorldName(), event.getTo().getX(), event.getTo().getZ());
        sendPlotEntryActionBar(event.getPlayer(), cc);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onPlayerMove(PlayerMoveEvent event) {
        if (event.getTo() == null) return;
        if (event.getFrom().getBlockX() >> 4 == event.getTo().getBlockX() >> 4 &&
            event.getFrom().getBlockZ() >> 4 == event.getTo().getBlockZ() >> 4) {
            return;
        }

        ChunkCoord cc = ChunkCoord.fromLocation(event.getTo());
        sendPlotEntryActionBar(event.getPlayer(), cc);
    }

    private void sendPlotEntryActionBar(Player player, ChunkCoord cc) {
        if (player == null || !player.isOnline()) return;

        long now = System.currentTimeMillis();
        Long last = lastActionBarSent.get(player.getUniqueId());
        if (last != null && (now - last) < 1500) {
            return;
        }

        ActiveBuilding bld = plugin.getBuildingManager().getBuildingOccupyingChunk(cc);
        if (bld != null) {
            BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
            String bpName = bp != null ? bp.getNameRu() : bld.getBlueprintId();
            String barText;
            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                barText = ChatColor.GOLD + "🏗 В процессе постройки: " + ChatColor.YELLOW + bpName + 
                        ChatColor.GRAY + " (" + bld.getProgressPercent() + "%)";
            } else if (bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
                barText = ChatColor.GOLD + "🏛 Постройка: " + ChatColor.YELLOW + bpName + 
                        ChatColor.GREEN + " [Активно 100%]";
            } else {
                barText = ChatColor.GOLD + "🏛 Постройка: " + ChatColor.YELLOW + bpName + 
                        ChatColor.RED + " [Повреждено: " + ((int) bld.getHealthPercent()) + "%]";
            }

            player.spigot().sendMessage(ChatMessageType.ACTION_BAR, TextComponent.fromLegacyText(barText));
            lastActionBarSent.put(player.getUniqueId(), now);
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onPlotChangeType(PlotChangeTypeEvent event) {
        TownBlock tb = event.getTownBlock();
        if (tb == null || !tb.hasTown()) return;
        try {
            ChunkCoord cc = new ChunkCoord(tb.getWorld().getName(), tb.getX(), tb.getZ());
            String town = tb.getTown().getName();
            if (plugin.getBuildingManager().getTownBuildPlots(town).contains(cc)) {
                // If the plugin sets the type to RESIDENTIAL during /plot set build, we should ignore it.
                // We only want to clear the build plot if a player manually changes it to something like FARM, ARENA, etc.
                if (event.getNewType() == TownBlockType.RESIDENTIAL) {
                    return;
                }
                
                plugin.getBuildingManager().removeTownBuildPlot(town, cc);
                tb.setName("");
                tb.save();
            }
        } catch (Exception ignored) {}
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onPlotClear(PlotClearEvent event) {
        TownBlock tb = event.getTownBlock();
        if (tb == null || !tb.hasTown()) return;
        try {
            ChunkCoord cc = new ChunkCoord(tb.getWorld().getName(), tb.getX(), tb.getZ());
            String town = tb.getTown().getName();
            if (plugin.getBuildingManager().getTownBuildPlots(town).contains(cc)) {
                plugin.getBuildingManager().removeTownBuildPlot(town, cc);
                // Towny's plot clear will natively clear the name anyway, but just in case:
                tb.setName("");
                tb.save();
            }
        } catch (Exception ignored) {}
    }
}
