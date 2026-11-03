package com.towny.respawn.command;

import com.towny.respawn.TownyRespawnPlugin;
import com.towny.respawn.model.PlayerBed;
import org.bukkit.ChatColor;
import org.bukkit.Sound;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class RespawnCommand implements CommandExecutor, TabCompleter {

    private final TownyRespawnPlugin plugin;

    public RespawnCommand(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        String cmdName = command.getName().toLowerCase();

        // Admin command: /townyrespawn reload
        if (cmdName.equals("townyrespawn") || (args.length > 0 && args[0].equalsIgnoreCase("reload"))) {
            if (!sender.hasPermission("townyrespawn.admin")) {
                sender.sendMessage(ChatColor.RED + "У вас нет прав на использование этой команды.");
                return true;
            }
            plugin.reloadConfig();
            plugin.getBedManager().load();
            sender.sendMessage(ChatColor.GREEN + "[TownyRespawn] Конфигурация и база кроватей успешно перезагружены!");
            return true;
        }

        if (!(sender instanceof Player)) {
            sender.sendMessage(ChatColor.RED + "Команда доступна только игрокам в игре.");
            return true;
        }

        Player player = (Player) sender;

        // Subcommand: /respawn rename <номер> <новое имя>
        if (args.length >= 2 && args[0].equalsIgnoreCase("rename")) {
            if (!player.hasPermission("townyrespawn.beds.rename")) {
                player.sendMessage(ChatColor.RED + "У вас нет прав на переименование кроватей.");
                return true;
            }
            try {
                int index = Integer.parseInt(args[1]) - 1;
                StringBuilder sb = new StringBuilder();
                for (int i = 2; i < args.length; i++) {
                    if (sb.length() > 0) sb.append(" ");
                    sb.append(args[i]);
                }
                String newName = sb.toString().trim();
                if (newName.isEmpty()) {
                    player.sendMessage(ChatColor.RED + "Использование: /respawn rename <номер кровати> <новое название>");
                    return true;
                }

                String cleanName = player.hasPermission("townyrespawn.beds.color")
                        ? ChatColor.translateAlternateColorCodes('&', newName)
                        : ChatColor.stripColor(ChatColor.translateAlternateColorCodes('&', newName));

                boolean success = plugin.getBedManager().renameBedByIndex(player, index, cleanName);
                if (success) {
                    player.sendMessage(ChatColor.GREEN + "[TownyRespawn] Кровать #" + (index + 1) + " успешно переименована в: «" + ChatColor.AQUA + cleanName + ChatColor.GREEN + "»!");
                    player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 1.0f, 1.5f);
                } else {
                    player.sendMessage(ChatColor.RED + "[TownyRespawn] Кровать с номером #" + (index + 1) + " не найдена. Проверьте /respawn list.");
                }
            } catch (NumberFormatException e) {
                player.sendMessage(ChatColor.RED + "Номер кровати должен быть числом! Пример: /respawn rename 1 База в горах");
            }
            return true;
        }

        // Subcommand: /respawn list
        if (args.length > 0 && args[0].equalsIgnoreCase("list")) {
            List<PlayerBed> beds = plugin.getBedManager().getBeds(player);
            player.sendMessage(ChatColor.GOLD + "=== Ваши привязанные кровати (" + beds.size() + "/" + plugin.getBedManager().getMaxBeds(player) + ") ===");
            if (beds.isEmpty()) {
                player.sendMessage(ChatColor.GRAY + "У вас пока нет сохранённых кроватей. Поспите на кровати!");
            } else {
                for (int i = 0; i < beds.size(); i++) {
                    PlayerBed b = beds.get(i);
                    player.sendMessage(ChatColor.YELLOW + "#" + (i + 1) + " " + ChatColor.AQUA + b.getName() + " " + ChatColor.GREEN + "[Цела]" +
                            ChatColor.GRAY + " (" + b.getWorldName() + ", X:" + b.getHeadX() + " Y:" + b.getHeadY() + " Z:" + b.getHeadZ() + ")");
                }
            }
            player.sendMessage(ChatColor.GRAY + "Чтобы переименовать: /respawn rename <номер> <новое имя>");
            return true;
        }

        // Subcommand: /respawn delete <номер>
        if (args.length >= 2 && (args[0].equalsIgnoreCase("delete") || args[0].equalsIgnoreCase("remove"))) {
            try {
                int index = Integer.parseInt(args[1]) - 1;
                boolean removed = plugin.getBedManager().removeBedByIndex(player, index);
                if (removed) {
                    player.sendMessage(ChatColor.GREEN + "[TownyRespawn] Кровать #" + (index + 1) + " удалена.");
                } else {
                    player.sendMessage(ChatColor.RED + "[TownyRespawn] Кровать с номером #" + (index + 1) + " не найдена.");
                }
            } catch (NumberFormatException e) {
                player.sendMessage(ChatColor.RED + "Номер кровати должен быть числом!");
            }
            return true;
        }

        // Меню /respawn открывается ТОЛЬКО для админов для тестов!
        // Для обычных игроков меню открывается ТОЛЬКО при смерти игрока!
        if (plugin.getConfig().getBoolean("respawn.admin-only-command", true)) {
            if (!player.hasPermission("townyrespawn.admin") && !player.isOp()) {
                String adminMsg = ChatColor.translateAlternateColorCodes('&',
                        plugin.getConfig().getString("messages.command-admin-only",
                                "&cКоманда /respawn доступна только администраторам для тестов. Для обычных игроков меню открывается только при смерти игрока."));
                player.sendMessage(adminMsg);
                return true;
            }
        }

        // Админ в тестовом режиме открывает GUI
        plugin.getGuiManager().openRespawnGui(player);
        return true;
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        List<String> list = new ArrayList<>();
        if (args.length == 1) {
            for (String sub : Arrays.asList("rename", "list", "delete", "reload")) {
                if (sub.startsWith(args[0].toLowerCase())) {
                    list.add(sub);
                }
            }
        } else if (args.length == 2 && (args[0].equalsIgnoreCase("rename") || args[0].equalsIgnoreCase("delete"))) {
            if (sender instanceof Player) {
                Player p = (Player) sender;
                int count = plugin.getBedManager().getBeds(p).size();
                for (int i = 1; i <= count; i++) {
                    list.add(String.valueOf(i));
                }
            }
        }
        return list;
    }
}
