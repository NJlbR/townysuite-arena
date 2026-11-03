package com.towny.architecture.command;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.ChunkCoord;
import com.towny.architecture.manager.ArchitectManager;
import com.towny.architecture.util.RussianTranslator;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Sound;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;

import java.util.*;

public class BuildCommand implements CommandExecutor, TabCompleter {
    private final TownyArchitecturePlugin plugin;

    public BuildCommand(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player)) {
            sender.sendMessage("Команда доступна только игрокам в игре!");
            return true;
        }

        Player player = (Player) sender;

        if (args.length == 0) {
            // Open GUI by default
            plugin.getBuildsMenuGui().open(player);
            return true;
        }

        String sub = args[0].toLowerCase();

        switch (sub) {
            case "gui":
            case "menu":
            case "list":
                plugin.getBuildsMenuGui().open(player);
                break;

            case "highlight":
            case "particles":
            case "borders":
            case "border": {
                boolean enabled = plugin.getBuildingHudManager().toggleParticles(player);
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.2f);
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + (enabled ? "&aПодсветка границ построек &2ВКЛЮЧЕНА&a (видна только вам)!" : "&cПодсветка границ построек &4ВЫКЛЮЧЕНА&c.")));
                break;
            }

            case "effects":
            case "effect": {
                boolean enabled = plugin.getBuildingHudManager().toggleEffectParticles(player);
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.2f);
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + (enabled ? "&aПодсветка зон эффектов &2ВКЛЮЧЕНА&a (видна только вам)!" : "&cПодсветка зон эффектов &4ВЫКЛЮЧЕНА&c.")));
                break;
            }

            case "stats":
            case "level":
            case "xp":
            case "skill": {
                ArchitectManager.ArchitectStats st = plugin.getArchitectManager().getStats(player);
                int lvl = plugin.getArchitectManager().getLevel(player);
                int currentLevelBaseXp = ArchitectManager.getXpForLevel(lvl);
                int nextLevelXp = ArchitectManager.getXpForLevel(lvl + 1);
                int curInLevel = st.xp - currentLevelBaseXp;
                int reqInLevel = nextLevelXp - currentLevelBaseXp;
                if (reqInLevel <= 0) reqInLevel = 100;
                int pct = Math.min(100, Math.max(0, (curInLevel * 100) / reqInLevel));

                player.sendMessage(ChatColor.GOLD + "══════ Профиль Архитектора: " + ChatColor.YELLOW + player.getName() + ChatColor.GOLD + " ══════");
                player.sendMessage(ChatColor.WHITE + " • Текущий уровень: " + ChatColor.GREEN + "" + ChatColor.BOLD + lvl + " ур.");
                player.sendMessage(ChatColor.WHITE + " • Всего опыта (XP): " + ChatColor.AQUA + st.xp + " XP");
                player.sendMessage(ChatColor.WHITE + " • Прогресс до " + (lvl + 1) + " ур: " + ChatColor.YELLOW + Math.max(0, curInLevel) + ChatColor.GRAY + "/" + ChatColor.WHITE + reqInLevel + " XP " +
                        ChatColor.DARK_GRAY + "[" + renderProgressBar(Math.max(0, curInLevel), reqInLevel, 10) + ChatColor.DARK_GRAY + "] " + ChatColor.GREEN + pct + "%");
                player.sendMessage(ChatColor.DARK_GRAY + "───────────────────────────────────");
                player.sendMessage(ChatColor.GRAY + " • Размещено стройматериалов: " + ChatColor.WHITE + st.placed + " шт.");
                player.sendMessage(ChatColor.GRAY + " • Сломано блоков: " + ChatColor.WHITE + st.broken + " шт.");
                player.sendMessage(ChatColor.GRAY + " • Чистый рекорд (High-Water Mark): " + ChatColor.WHITE + st.maxNet + " шт.");
                player.sendMessage(ChatColor.DARK_GRAY + "───────────────────────────────────");
                player.sendMessage(ChatColor.YELLOW + "Подсказка: " + ChatColor.GRAY + "Ставьте блоки по чертежам (" + ChatColor.AQUA + "+15 XP" + ChatColor.GRAY + ") или стройте в городе (" + ChatColor.AQUA + "+1 XP" + ChatColor.GRAY + ")!");
                player.sendMessage(ChatColor.GOLD + "════════════════════════════════════════");
                break;
            }

            case "plot": {
                handlePlotCommand(player, args);
                break;
            }

            case "info":
            case "progress":
            case "status": {
                ActiveBuilding building = plugin.getBuildingManager().getBuildingAt(player.getLocation());
                if (building == null) {
                    player.sendMessage(ChatColor.RED + "Вы не стоите внутри чанка активного городского здания!");
                    return true;
                }

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(building.getBlueprintId());
                String bpName = bp != null ? bp.getNameRu() : building.getBlueprintId();

                player.sendMessage(ChatColor.GOLD + "══════ Прогресс постройки: " + ChatColor.YELLOW + bpName + ChatColor.GOLD + " ══════");
                player.sendMessage(ChatColor.GRAY + "Город: " + ChatColor.WHITE + building.getTownName() + 
                                   ChatColor.GRAY + " | Статус: " + ChatColor.WHITE + RussianTranslator.getStatusRu(building.getStatus()));
                player.sendMessage(ChatColor.DARK_AQUA + "Общий прогресс: " + ChatColor.GREEN + building.getProgressPercent() + "%");
                player.sendMessage(ChatColor.YELLOW + "Требуемые ресурсы:");

                for (Map.Entry<Material, Integer> entry : building.getRequiredMaterials().entrySet()) {
                    int placed = building.getPlacedCount(entry.getKey());
                    int need = entry.getValue();
                    int pct = need > 0 ? Math.min(100, (placed * 100) / need) : 100;
                    String bar = renderProgressBar(placed, need, 10);
                    String check = placed >= need ? ChatColor.GREEN + "✔" : ChatColor.YELLOW + "■";

                    player.sendMessage(" " + check + " " + ChatColor.WHITE + RussianTranslator.getMaterialRu(entry.getKey()) + ": " +
                            ChatColor.GREEN + placed + ChatColor.GRAY + "/" + ChatColor.WHITE + need + " " +
                            ChatColor.DARK_GRAY + "[" + bar + ChatColor.DARK_GRAY + "] " +
                            ChatColor.AQUA + pct + "%");
                }
                player.sendMessage(ChatColor.GOLD + "════════════════════════════════════════");
                break;
            }

            case "demolish": {
                if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player)) {
                    player.sendMessage(ChatColor.RED + "Только мэр или помощник могут сносить здания!");
                    return true;
                }
                String town = plugin.getTownyHook().getPlayerTownName(player);
                if (town == null) return true;
                
                ChunkCoord cc = ChunkCoord.fromLocation(player.getLocation());
                ActiveBuilding bld = plugin.getBuildingManager().getBuildingOccupyingChunk(cc);
                if (bld == null || !bld.getTownName().equalsIgnoreCase(town)) {
                    player.sendMessage(ChatColor.RED + "Вы не стоите на территории здания вашего города.");
                    return true;
                }

                if (args.length >= 2 && args[1].equalsIgnoreCase("confirm")) {
                    plugin.getBuildingManager().demolishBuilding(bld);
                    player.sendMessage(ChatColor.GREEN + "Здание успешно снесено из базы данных. Физические блоки остались нетронутыми.");
                } else {
                    player.sendMessage(ChatColor.YELLOW + "Вы уверены, что хотите снести постройку «" + bld.getBlueprintId() + "»?");
                    player.sendMessage(ChatColor.YELLOW + "Она будет удалена из системы (лимиты обновятся), но физические блоки останутся.");
                    player.sendMessage(ChatColor.RED + "Для подтверждения введите: " + ChatColor.WHITE + "/build demolish confirm");
                }
                break;
            }
            case "repair": {
                ActiveBuilding building = plugin.getBuildingManager().getBuildingAt(player.getLocation());
                if (building == null) {
                    player.sendMessage(ChatColor.RED + "Вы не стоите внутри какого-либо городского здания!");
                    return true;
                }
                plugin.getSiegeDamageManager().showRepairInstructions(player, building);
                break;
            }

            case "resetxp": {
                if (!player.hasPermission("townyarchitecture.admin") && !player.isOp()) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                plugin.getArchitectManager().resetStats(player);
                break;
            }
            case "setlevel": {
                if (!player.hasPermission("townyarchitecture.admin") && !player.isOp()) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                if (args.length < 2) {
                    player.sendMessage(ChatColor.RED + "Использование: /build setlevel <уровень>");
                    return true;
                }
                try {
                    int level = Integer.parseInt(args[1]);
                    plugin.getArchitectManager().setLevel(player, level);
                    player.sendMessage(ChatColor.GREEN + "Ваш уровень Архитектора установлен на " + level);
                } catch (NumberFormatException e) {
                    player.sendMessage(ChatColor.RED + "Неверный уровень!");
                }
                break;
            }
            case "reload": {
                if (!player.hasPermission("townyarchitecture.admin")) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                plugin.reloadPluginConfig();
                player.sendMessage(ChatColor.GREEN + "Конфигурация TownyArchitecture успешно перезагружена!");
                break;
            }

            case "wonder": {
                if (!player.hasPermission("townyarchitecture.admin")) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                if (args.length >= 3 && args[1].equalsIgnoreCase("reset")) {
                    String wonderId = args[2];
                    BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(wonderId);
                    if (bp != null) {
                        bp.setWonderCompletedByTown(null);
                        plugin.getBuildingManager().saveData();
                        player.sendMessage(ChatColor.GREEN + "Блокировка Чуда Света «" + bp.getNameRu() + "» сброшена!");
                    } else {
                        player.sendMessage(ChatColor.RED + "Чертеж не найден: " + wonderId);
                    }
                } else {
                    player.sendMessage(ChatColor.YELLOW + "Использование: /build wonder reset <id>");
                }
                break;
            }

            default:
                player.sendMessage(ChatColor.YELLOW + "Команды: /builds (меню), /build stats (уровень), /plot set build, /build info, /build plot list, /build repair");
                break;
        }

        return true;
    }

    private void handlePlotCommand(Player player, String[] args) {
        String town = plugin.getTownyHook().getPlayerTownName(player);
        if (town == null) {
            player.sendMessage(ChatColor.RED + "Вы должны состоять в городе!");
            return;
        }

        if (args.length >= 3 && args[1].equalsIgnoreCase("set") && args[2].equalsIgnoreCase("build")) {
            processPlotSetBuild(player);
            return;
        }

        if (args.length >= 2 && args[1].equalsIgnoreCase("remove")) {
            if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player)) {
                player.sendMessage(ChatColor.RED + "Только мэр или помощник могут снимать статус строительного участка!");
                return;
            }
            ChunkCoord cc = ChunkCoord.fromLocation(player.getLocation());
            if (plugin.getBuildingManager().isChunkOccupiedByBuilding(cc)) {
                player.sendMessage(ChatColor.RED + "Этот участок сейчас занят постройкой! Сначала завершите или удалите проект.");
                return;
            }
            boolean removed = plugin.getBuildingManager().removeTownBuildPlot(town, cc);
            if (removed) {
                plugin.getTownyHook().clearPlotTag(player.getLocation());
                player.sendMessage(ChatColor.YELLOW + "Чанк " + cc + " исключен из списка строительных участков города.");
            } else {
                player.sendMessage(ChatColor.RED + "Этот чанк не был назначен строительным участком.");
            }
            return;
        }

        if (args.length >= 2 && args[1].equalsIgnoreCase("list")) {
            Set<ChunkCoord> plots = plugin.getBuildingManager().getTownBuildPlots(town);
            player.sendMessage(ChatColor.GOLD + "=== Строительные участки города " + town + " (" + plots.size() + ") ===");
            if (plots.isEmpty()) {
                player.sendMessage(ChatColor.GRAY + "Нет назначенных участков. Используйте /plot set build");
            } else {
                for (ChunkCoord c : plots) {
                    ActiveBuilding bld = plugin.getBuildingManager().getBuildingOccupyingChunk(c);
                    String status = bld != null ? ChatColor.YELLOW + "[Занят: " + bld.getBlueprintId() + "]" : 
                                                  ChatColor.GREEN + "[Свободен]";
                    player.sendMessage(ChatColor.WHITE + " • Чанк " + c + " " + status);
                }
            }
            return;
        }

        player.sendMessage(ChatColor.YELLOW + "Использование: /plot set build или /build plot list / remove");
    }

    public void processPlotSetBuild(Player player) {
        String town = plugin.getTownyHook().getPlayerTownName(player);
        if (town == null) {
            player.sendMessage(ChatColor.RED + "Вы должны состоять в городе!");
            return;
        }

        if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player)) {
            player.sendMessage(ChatColor.RED + "Только мэр или помощник города могут назначать строительные участки!");
            player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
            return;
        }

        Location loc = player.getLocation();
        if (!plugin.getTownyHook().isLocationInPlayerTown(loc, player)) {
            player.sendMessage(ChatColor.RED + "Этот участок находится за пределами вашего города (или в диких землях)!");
            return;
        }

        ChunkCoord cc = ChunkCoord.fromLocation(loc);

        if (plugin.getBuildingManager().isChunkOccupiedByBuilding(cc)) {
            ActiveBuilding bld = plugin.getBuildingManager().getBuildingOccupyingChunk(cc);
            player.sendMessage(ChatColor.RED + "Этот чанк уже занят постройкой («" + 
                    (bld != null ? bld.getBlueprintId() : "проект") + "»)! Назначьте другой участок.");
            return;
        }

        plugin.getBuildingManager().addTownBuildPlot(town, cc);
        plugin.getTownyHook().tagPlotAsBuild(loc, "Стройплощадка");

        player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                plugin.getMsg("prefix") + "&a✔ Участок чанка &f" + cc + " &aуспешно назначен строительной площадкой!"));
        player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                plugin.getMsg("prefix") + "&7Размер: 1 чанк (16x16). Назначьте смежные чанки для больших построек (1x2 или 2x2 для Чудес Света)."));
        player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                plugin.getMsg("prefix") + "&eТеперь откройте &f/builds &eчтобы утвердить чертеж."));

        player.playSound(loc, Sound.BLOCK_ANVIL_USE, 0.8f, 1.3f);
    }

    private String renderProgressBar(int current, int max, int totalBars) {
        if (max <= 0) return ChatColor.GREEN + "██████████";
        int filled = (int) Math.round(((double) current / max) * totalBars);
        filled = Math.max(0, Math.min(totalBars, filled));
        StringBuilder sb = new StringBuilder();
        sb.append(ChatColor.GREEN);
        for (int i = 0; i < filled; i++) sb.append("█");
        sb.append(ChatColor.DARK_GRAY);
        for (int i = filled; i < totalBars; i++) sb.append("░");
        return sb.toString();
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (args.length == 1) {
            List<String> list = new ArrayList<>(Arrays.asList("gui", "stats", "info", "plot", "repair", "highlight", "borders", "effects"));
            if (plugin.getTownyHook().isPlayerMayorOrAssistant((Player) sender)) {
                list.add("demolish");
            }
            if (sender.hasPermission("townyarchitecture.admin") || sender.isOp()) {
                list.add("reload");
                list.add("wonder");
                list.add("resetxp");
                list.add("setlevel");
            }
            return list;
        } else if (args.length == 2 && args[0].equalsIgnoreCase("setlevel")) {
            return Arrays.asList("1", "5", "10", "15", "20", "25", "30", "50");
        } else if (args.length == 2 && args[0].equalsIgnoreCase("plot")) {
            return Arrays.asList("set", "list", "remove");
        } else if (args.length == 3 && args[0].equalsIgnoreCase("plot") && args[1].equalsIgnoreCase("set")) {
            return Collections.singletonList("build");
        }
        return Collections.emptyList();
    }
}
