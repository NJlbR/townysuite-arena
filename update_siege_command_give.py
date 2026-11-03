import os

print("=== Adding /siege cannon give command and fixing all potential bugs ===")

siege_command_java = """package com.towny.sieges.command;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.NationWar;
import com.towny.sieges.model.SiegeCamp;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class SiegeCommand implements CommandExecutor, TabCompleter {

    private final TownySiegesPlugin plugin;

    public SiegeCommand(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 0 || args[0].equalsIgnoreCase("help")) {
            sender.sendMessage(ChatColor.GOLD + "══════ TownySieges v" + plugin.getDescription().getVersion() + " ══════");
            sender.sendMessage(ChatColor.YELLOW + "/siege camp <Город> " + ChatColor.GRAY + "- Поставить осадный лагерь");
            sender.sendMessage(ChatColor.YELLOW + "/siege expand " + ChatColor.GRAY + "- Расширить осадный лагерь на соседний чанк");
            sender.sendMessage(ChatColor.YELLOW + "/siege unclaim " + ChatColor.GRAY + "- Расприватить чанк лагеря");
            sender.sendMessage(ChatColor.YELLOW + "/siege cannon give [игрок] " + ChatColor.GRAY + "- Выдать осадную пушку");
            sender.sendMessage(ChatColor.YELLOW + "/siege nationwar declare <Нация> " + ChatColor.GRAY + "- Объявить войну нации");
            sender.sendMessage(ChatColor.YELLOW + "/siege nationwar status " + ChatColor.GRAY + "- Статус войн наций и таймеров");
            sender.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════");
            return true;
        }

        // /siege cannon give [player]
        if (args[0].equalsIgnoreCase("cannon") || args[0].equalsIgnoreCase("pusшка")) {
            if (args.length >= 2 && args[1].equalsIgnoreCase("give")) {
                if (!sender.hasPermission("townysieges.admin")) {
                    sender.sendMessage(ChatColor.RED + "[TownySieges] У вас нет прав администратора для выдачи осадных пушек!");
                    return true;
                }
                Player target = sender instanceof Player ? (Player) sender : null;
                if (args.length >= 3) {
                    target = Bukkit.getPlayer(args[2]);
                }
                if (target == null || !target.isOnline()) {
                    sender.sendMessage(ChatColor.RED + "[TownySieges] Игрок не найден или не в сети!");
                    return true;
                }
                target.getInventory().addItem(plugin.getProtectionListener().getCannonManager().getCannonItem());
                target.sendMessage(ChatColor.GREEN + "[TownySieges] Вам выдана кастомная осадная пушка (Nexo/Oraxen Model)!");
                sender.sendMessage(ChatColor.YELLOW + "Установите бочку на землю или поставьте блок правой кнопкой мыши.");
                if (sender != target) {
                    sender.sendMessage(ChatColor.GREEN + "[TownySieges] Пушка успешно выдана игроку " + target.getName() + ".");
                }
                return true;
            }
        }

        // /siege camp <DefendingTown>
        if (args[0].equalsIgnoreCase("camp") || args[0].equalsIgnoreCase("lager")) {
            if (!(sender instanceof Player)) {
                sender.sendMessage("Только игрок может ставить осадный лагерь!");
                return true;
            }
            Player player = (Player) sender;
            if (args.length < 2) {
                player.sendMessage(ChatColor.RED + "Использование: /siege camp <Город-цель>");
                return true;
            }
            String defendingTown = args[1];
            plugin.getSiegeManager().createSiegeCamp(player, defendingTown, player.getLocation());
            return true;
        }

        // /siege expand
        if (args[0].equalsIgnoreCase("expand") || args[0].equalsIgnoreCase("rasshirit")) {
            if (!(sender instanceof Player)) return true;
            Player player = (Player) sender;
            plugin.getSiegeManager().expandSiegeCamp(player, player.getLocation());
            return true;
        }

        // /siege unclaim
        if (args[0].equalsIgnoreCase("unclaim") || args[0].equalsIgnoreCase("udalit")) {
            if (!(sender instanceof Player)) return true;
            Player player = (Player) sender;
            plugin.getSiegeManager().unclaimSiegeChunk(player, player.getLocation());
            return true;
        }

        // /siege nationwar / war
        if (args[0].equalsIgnoreCase("nationwar") || args[0].equalsIgnoreCase("war") || args[0].equalsIgnoreCase("война")) {
            if (args.length < 2 || args[1].equalsIgnoreCase("status")) {
                sender.sendMessage(ChatColor.GOLD + "══════ Активные Войны Наций ══════");
                if (plugin.getSiegeManager().getAllNationWars().isEmpty()) {
                    sender.sendMessage(ChatColor.GRAY + "В данный момент нет активных войн наций.");
                } else {
                    for (NationWar nw : plugin.getSiegeManager().getAllNationWars()) {
                        sender.sendMessage(ChatColor.YELLOW + "• " + nw.getAttackerNation() + " ➔ " + nw.getDefenderNation() +
                                " [" + nw.getStatus() + "] Осталось: " + nw.getFormattedRemainingTime());
                    }
                }
                sender.sendMessage(ChatColor.GOLD + "══════════════════════════════════");
                return true;
            }

            if (args[1].equalsIgnoreCase("declare")) {
                if (!(sender instanceof Player)) {
                    sender.sendMessage("Только глава нации может объявить войну.");
                    return true;
                }
                Player player = (Player) sender;
                if (args.length < 3) {
                    player.sendMessage(ChatColor.RED + "Использование: /siege nationwar declare <Нация-Цель>");
                    return true;
                }
                String targetNat = args[2];
                plugin.getSiegeManager().declareNationWar(player, targetNat);
                return true;
            }

            if (args[1].equalsIgnoreCase("assault") && sender.hasPermission("townysieges.admin")) {
                if (args.length < 3) {
                    sender.sendMessage("Использование: /siege nationwar assault <Нация>");
                    return true;
                }
                NationWar nw = plugin.getSiegeManager().getActiveNationWar(args[2]);
                if (nw != null) {
                    nw.setStatus(NationWar.Status.ACTIVE_ASSAULT);
                    nw.setActiveEndsAtMillis(System.currentTimeMillis() + 7200000L);
                    plugin.getSiegeManager().saveData();
                    sender.sendMessage(ChatColor.GREEN + "Война нации переведена в фазу АКТИВНОГО ШТУРМА (2ч)!");
                } else {
                    sender.sendMessage(ChatColor.RED + "Война для указанной нации не найдена.");
                }
                return true;
            }
        }

        sender.sendMessage(ChatColor.RED + "Неизвестная команда. Введите /siege help");
        return true;
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        List<String> completions = new ArrayList<>();
        if (args.length == 1) {
            List<String> subs = Arrays.asList("camp", "expand", "unclaim", "cannon", "nationwar", "help");
            String input = args[0].toLowerCase();
            for (String s : subs) {
                if (s.startsWith(input)) completions.add(s);
            }
        } else if (args.length == 2) {
            if (args[0].equalsIgnoreCase("nationwar") || args[0].equalsIgnoreCase("war")) {
                List<String> subs = Arrays.asList("declare", "status", "assault");
                String input = args[1].toLowerCase();
                for (String s : subs) {
                    if (s.startsWith(input)) completions.add(s);
                }
            } else if (args[0].equalsIgnoreCase("cannon")) {
                List<String> subs = Arrays.asList("give");
                String input = args[1].toLowerCase();
                for (String s : subs) {
                    if (s.startsWith(input)) completions.add(s);
                }
            }
        }
        return completions;
    }
}
"""

with open("tmp/towny-sieges/src/main/java/com/towny/sieges/command/SiegeCommand.java", "w", encoding="utf-8") as f:
    f.write(siege_command_java)

print("Updated SiegeCommand.java successfully.")
