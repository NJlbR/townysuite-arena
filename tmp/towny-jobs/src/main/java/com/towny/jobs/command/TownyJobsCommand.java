package com.towny.jobs.command;

import com.towny.jobs.TownyJobsPlugin;
import org.bukkit.ChatColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;

import java.util.Collections;
import java.util.List;

public final class TownyJobsCommand implements CommandExecutor, TabCompleter {
    private final TownyJobsPlugin plugin;

    public TownyJobsCommand(TownyJobsPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length > 0 && args[0].equalsIgnoreCase("reload")) {
            if (!sender.hasPermission("townyjobs.admin")) {
                sender.sendMessage(ChatColor.RED + "У вас нет права перезагружать TownyJobs.");
                return true;
            }
            plugin.reloadConfig();
            plugin.getManager().syncOnlinePlayers();
            sender.sendMessage(ChatColor.GREEN + "Конфигурация TownyJobs перезагружена.");
            return true;
        }
        if (!(sender instanceof Player)) {
            sender.sendMessage(ChatColor.RED + "Открыть меню работ может только игрок.");
            return true;
        }
        if (!sender.hasPermission("townyjobs.use")) {
            sender.sendMessage(ChatColor.RED + "У вас нет права использовать TownyJobs.");
            return true;
        }
        plugin.getMenu().open((Player) sender);
        return true;
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (args.length == 1 && sender.hasPermission("townyjobs.admin")
                && "reload".startsWith(args[0].toLowerCase())) return Collections.singletonList("reload");
        return Collections.emptyList();
    }
}
