package com.towny.jobs.listener;

import com.palmergames.bukkit.towny.object.Resident;
import com.palmergames.bukkit.towny.object.Town;
import com.towny.jobs.TownyJobsPlugin;
import com.towny.jobs.gui.JobsMenu;
import com.towny.jobs.gui.JobsMenuHolder;
import com.towny.jobs.manager.TownyJobsManager;
import com.towny.jobs.manager.TownyJobsManager.JobRole;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryDragEvent;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.block.BlockPlaceEvent;

import java.util.List;

public final class JobsListener implements Listener {
    private final TownyJobsPlugin plugin;
    private final JobsMenu menu;
    private final TownyJobsManager manager;

    public JobsListener(TownyJobsPlugin plugin, JobsMenu menu, TownyJobsManager manager) {
        this.plugin = plugin;
        this.menu = menu;
        this.manager = manager;
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent event) {
        Bukkit.getScheduler().runTask(plugin, () -> manager.syncPlayerPermissions(event.getPlayer()));
    }

    @EventHandler
    public void onQuit(PlayerQuitEvent event) {
        menu.clearInput(event.getPlayer());
        manager.clearPlayerPermissions(event.getPlayer());
    }

    @EventHandler
    public void onChatInput(AsyncPlayerChatEvent event) {
        Player player = event.getPlayer();
        if (!menu.hasPendingInput(player)) return;
        event.setCancelled(true);
        menu.handleInput(player, event.getMessage());
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockPlace(BlockPlaceEvent event) {
        manager.recordBlueprintPlacement(event.getPlayer(), event);
    }

    @EventHandler
    public void onInventoryClick(InventoryClickEvent event) {
        if (!(event.getView().getTopInventory().getHolder() instanceof JobsMenuHolder)) return;
        event.setCancelled(true);
        if (!(event.getWhoClicked() instanceof Player)) return;
        Player player = (Player) event.getWhoClicked();
        JobsMenuHolder holder = (JobsMenuHolder) event.getView().getTopInventory().getHolder();
        Town town = manager.findTown(holder.townId);
        if (town == null) {
            player.closeInventory();
            player.sendMessage("§cThis town no longer exists.");
            return;
        }

        if (holder.mode == JobsMenuHolder.Mode.MAIN) {
            menu.handleMainClick(player, town, event.getRawSlot(), event.getClick());
            return;
        }
        handleMembersClick(player, town, holder, event.getRawSlot());
    }

    @EventHandler
    public void onInventoryDrag(InventoryDragEvent event) {
        if (event.getView().getTopInventory().getHolder() instanceof JobsMenuHolder) event.setCancelled(true);
    }

    private void handleMembersClick(Player player, Town town, JobsMenuHolder holder, int slot) {
        if (slot < 0 || slot >= 54) return;
        if (slot == 45) {
            menu.openMembers(player, town, holder.roleId, holder.page - 1);
            return;
        }
        if (slot == 49) {
            menu.openMain(player, town);
            return;
        }
        if (slot == 53) {
            menu.openMembers(player, town, holder.roleId, holder.page + 1);
            return;
        }
        if (slot >= 45 || !manager.mayManage(player, town)) return;
        JobRole role = manager.getRole(holder.roleId);
        if (role == null) return;
        List<Resident> residents = manager.getResidents(town);
        int index = holder.page * 45 + slot;
        if (index < 0 || index >= residents.size()) return;
        Resident resident = residents.get(index);
        boolean assigned = manager.toggleRole(town, resident, role.id);
        player.sendMessage("§a" + resident.getName() + (assigned ? " assigned to " : " removed from ") + role.displayName + ".");
        menu.openMembers(player, town, role.id, holder.page);
    }
}
