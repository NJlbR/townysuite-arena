package com.towny.explosion.command;

import com.towny.explosion.TownyExplosionUnblockerPlugin;
import org.bukkit.ChatColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ExplosionUnblockerCommand implements CommandExecutor, TabCompleter {

    private final TownyExplosionUnblockerPlugin plugin;

    public ExplosionUnblockerCommand(TownyExplosionUnblockerPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("townyexplosionunblocker.admin")) {
            sender.sendMessage(ChatColor.RED + "У вас нет прав для выполнения этой команды.");
            return true;
        }

        if (args.length == 0 || args[0].equalsIgnoreCase("help")) {
            sender.sendMessage(ChatColor.GOLD + "══════ TownyExplosionUnblocker v" + plugin.getDescription().getVersion() + " ══════");
            sender.sendMessage(ChatColor.YELLOW + "/teu reload " + ChatColor.GRAY + "- Перезагрузить конфигурацию плагина");
            sender.sendMessage(ChatColor.YELLOW + "/teu status " + ChatColor.GRAY + "- Проверить текущий статус и режим работы");
            sender.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════");
            return true;
        }

        if (args[0].equalsIgnoreCase("reload")) {
            plugin.reloadPluginConfig();
            sender.sendMessage(ChatColor.GREEN + "[TownyExplosionUnblocker] Конфигурация успешно перезагружена!");
            return true;
        }

        if (args[0].equalsIgnoreCase("status")) {
            sender.sendMessage(ChatColor.GOLD + "══════ Статус TownyExplosionUnblocker ══════");
            sender.sendMessage(ChatColor.YELLOW + "Работа плагина: " + (plugin.isUnblockerEnabled() ? ChatColor.GREEN + "АКТИВЕН" : ChatColor.RED + "ОТКЛЮЧЕН"));
            sender.sendMessage(ChatColor.YELLOW + "Радиус по умолчанию: " + ChatColor.WHITE + plugin.getConfig().getDouble("explosion.default-cannon-power", 4.0));
            sender.sendMessage(ChatColor.GRAY + "Разблокирует взрывы: ТОЛЬКО снаряды пушек (SiegeCannon / Cannons).");
            sender.sendMessage(ChatColor.GRAY + "Ванильный TNT, криперы, кристаллы, визеры — блокируются Towny.");
            sender.sendMessage(ChatColor.GOLD + "════════════════════════════════════════════");
            return true;
        }

        sender.sendMessage(ChatColor.RED + "Неизвестная подкоманда. Используйте /teu help");
        return true;
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (!sender.hasPermission("townyexplosionunblocker.admin")) return new ArrayList<>();
        if (args.length == 1) {
            List<String> list = Arrays.asList("reload", "status", "help");
            List<String> result = new ArrayList<>();
            for (String s : list) {
                if (s.startsWith(args[0].toLowerCase())) result.add(s);
            }
            return result;
        }
        return new ArrayList<>();
    }
}
