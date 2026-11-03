package com.towny.respawn.listener;

import com.towny.respawn.TownyRespawnPlugin;
import com.towny.respawn.gui.RespawnMenuHolder;
import com.towny.respawn.model.PlayerBed;
import com.towny.respawn.model.RespawnPoint;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryCloseEvent;

import java.util.List;

public class GuiListener implements Listener {

    private final TownyRespawnPlugin plugin;

    public GuiListener(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler
    public void onInventoryClick(InventoryClickEvent event) {
        if (!(event.getInventory().getHolder() instanceof RespawnMenuHolder)) {
            return;
        }

        event.setCancelled(true);

        if (!(event.getWhoClicked() instanceof Player)) {
            return;
        }

        Player player = (Player) event.getWhoClicked();
        RespawnMenuHolder holder = (RespawnMenuHolder) event.getInventory().getHolder();
        int slot = event.getRawSlot();

        if (slot < 0 || slot >= 54) {
            return;
        }

        // Close button (slot 49)
        if (slot == 49) {
            if (holder.getMode() == RespawnMenuHolder.Mode.RESPAWN_SELECTION) {
                player.closeInventory();
            } else {
                player.sendMessage(ChatColor.RED + "Выберите точку возрождения!");
            }
            return;
        }

        // Bed Slots Check
        int[] bedSlots = {
                10, 11, 12, 13, 14, 15, 16,
                19, 20, 21, 22, 23, 24, 25
        };

        for (int i = 0; i < bedSlots.length; i++) {
            if (slot == bedSlots[i]) {
                List<PlayerBed> beds = plugin.getBedManager().getBeds(player);
                if (i < beds.size()) {
                    PlayerBed bed = beds.get(i);

                    // Check Right Click for Renaming
                    if (event.isRightClick()) {
                        if (!player.hasPermission("townyrespawn.beds.rename")) {
                            player.sendMessage(ChatColor.RED + "У вас нет прав на переименование кроватей.");
                            return;
                        }
                        plugin.getBedManager().setPendingRename(player.getUniqueId(), bed.getId());
                        player.closeInventory();
                        player.sendMessage(" ");
                        player.sendMessage(ChatColor.GOLD + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
                        player.sendMessage(ChatColor.AQUA + "✍ Введите новое название для кровати в чат:");
                        player.sendMessage(ChatColor.GRAY + "Текущее название: " + ChatColor.WHITE + bed.getName());
                        player.sendMessage(ChatColor.GRAY + "(Напишите " + ChatColor.RED + "отмена" + ChatColor.GRAY + " или " + ChatColor.RED + "cancel" + ChatColor.GRAY + " для отмены)");
                        player.sendMessage(ChatColor.GOLD + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
                        player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_PLING, 1.0f, 1.5f);
                        return;
                    }

                    // Left Click: Teleport / Respawn
                    if (!plugin.getBedManager().isBedPhysicallyValid(bed)) {
                        plugin.getBedManager().removeBed(player, bed);
                        player.sendMessage(ChatColor.RED + "Эта кровать была разрушена и автоматически удалена из меню!");
                        player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
                        plugin.getGuiManager().renderGui(holder);
                        return;
                    }

                    RespawnPoint point = new RespawnPoint(
                            RespawnPoint.Type.BED,
                            "bed_" + bed.getId(),
                            "§b🛏 " + bed.getName(),
                            null,
                            null,
                            bed.getLocation(),
                            true,
                            null
                    );
                    triggerRespawn(player, holder, point);
                }
                return;
            }
        }

        // Town Spawn Click (slot 28)
        if (slot == 28) {
            if (plugin.getTownyHook().isTownyAvailable()) {
                String townName = plugin.getTownyHook().getPlayerTownName(player);
                Object townObj = plugin.getTownyHook().getPlayerTown(player);
                if (townName != null && townObj != null) {
                    boolean underSiege = plugin.getTownySiegesHook().isTownUnderActiveSiege(townName);
                    boolean blocked = underSiege && (plugin.getConfig().getBoolean("respawn.block-spawn-if-under-siege", false) || plugin.getConfig().getBoolean("limbo.block-spawn-if-under-siege", false));
                    if (blocked) {
                        player.sendMessage(ChatColor.RED + "Возрождение в городе заблокировано осадным положением!");
                        player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
                        return;
                    }
                    Location tLoc = plugin.getTownyHook().getTownSpawn(townObj);
                    if (tLoc != null) {
                        RespawnPoint point = new RespawnPoint(RespawnPoint.Type.TOWN_SPAWN, "town_spawn", "§6Спавн города «" + townName + "»", null, null, tLoc, true, null);
                        triggerRespawn(player, holder, point);
                        return;
                    }
                }
            }
            player.sendMessage(ChatColor.RED + "Спавн города недоступен.");
            return;
        }

        // Nation Spawn Click (slot 30)
        if (slot == 30) {
            if (plugin.getTownyHook().isTownyAvailable()) {
                String nationName = plugin.getTownyHook().getPlayerNationName(player);
                Object nationObj = plugin.getTownyHook().getPlayerNation(player);
                if (nationName != null && nationObj != null) {
                    Location nLoc = plugin.getTownyHook().getNationSpawn(nationObj);
                    if (nLoc != null) {
                        RespawnPoint point = new RespawnPoint(RespawnPoint.Type.NATION_SPAWN, "nation_spawn", "§eСпавн столицы «" + nationName + "»", null, null, nLoc, true, null);
                        triggerRespawn(player, holder, point);
                        return;
                    }
                }
            }
            player.sendMessage(ChatColor.RED + "Спавн столицы нации недоступен.");
            return;
        }

        // Vanilla Wild Respawn Click (slot 32)
        if (slot == 32) {
            var wildLoc = plugin.getRespawnManager().findSafeVanillaWildSpawn(player);
            RespawnPoint point = new RespawnPoint(RespawnPoint.Type.VANILLA, "vanilla", "§aВанильный респавн", null, null, wildLoc, true, null);
            triggerRespawn(player, holder, point);
            return;
        }

        // Server Spawn Click (slot 34)
        if (slot == 34) {
            var sLoc = plugin.getRespawnManager().getServerSpawnLocation(player);
            RespawnPoint point = new RespawnPoint(RespawnPoint.Type.SERVER_SPAWN, "server_spawn", "§6Спавн сервера", null, null, sLoc, true, null);
            triggerRespawn(player, holder, point);
            return;
        }
    }

    private void triggerRespawn(Player player, RespawnMenuHolder holder, RespawnPoint point) {
        // Администратор в тестовом режиме через /respawn
        if (holder.getMode() == RespawnMenuHolder.Mode.RESPAWN_SELECTION) {
            player.closeInventory();
            Location target = point.getTargetLocation();
            if (target == null) target = plugin.getRespawnManager().getServerSpawnLocation(player);
            player.teleport(target);
            player.sendMessage(ChatColor.GREEN + "[TownyRespawn] [Тестовый режим] Вы перемещены на: " + point.getDisplayName());
            player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 1.0f, 1.8f);
            return;
        }

        // Для обычных игроков в DEATH_RESPAWN:
        // Проверяем КД на возрождение в 30 секунд от предыдущего возрождения!
        long remainingCd = plugin.getRespawnManager().getRemainingCooldownSeconds(player.getUniqueId());
        if (remainingCd > 0) {
            String warnMsg = ChatColor.translateAlternateColorCodes('&',
                    plugin.getConfig().getString("messages.cooldown-warning",
                            "&cВозрождение недоступно! До окончания КД осталось: &e{seconds} &cсек."))
                    .replace("{seconds}", String.valueOf(remainingCd));
            player.sendMessage(plugin.getConfig().getString("messages.prefix", "&b&l[TownyRespawn]&r ") + warnMsg);
            player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASS, 1.0f, 0.7f);
            return;
        }

        // КД завершен (или это первое возрождение) -> Мгновенно возрождаем без каких-либо задержек и блокировок!
        plugin.getRespawnManager().exitLimboAndRespawn(player, point);
    }

    @EventHandler
    public void onInventoryClose(InventoryCloseEvent event) {
        if (!(event.getInventory().getHolder() instanceof RespawnMenuHolder)) {
            return;
        }
        if (!(event.getPlayer() instanceof Player)) {
            return;
        }

        Player player = (Player) event.getPlayer();
        RespawnMenuHolder holder = (RespawnMenuHolder) event.getInventory().getHolder();

        // Если игрок умер и находится в Limbo, не позволяем ему закрыть меню и бегать по миру
        if (holder.getMode() == RespawnMenuHolder.Mode.DEATH_RESPAWN && plugin.getRespawnManager().isLimbo(player.getUniqueId())) {
            if (plugin.getBedManager().isAwaitingRename(player.getUniqueId())) {
                return; // Игрок переименовывает кровать в чате
            }
            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                if (player.isOnline() && plugin.getRespawnManager().isLimbo(player.getUniqueId())) {
                    plugin.getGuiManager().openDeathRespawnGui(player);
                }
            }, 2L);
        }
    }
}
