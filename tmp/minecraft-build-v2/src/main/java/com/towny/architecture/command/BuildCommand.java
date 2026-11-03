package com.towny.architecture.command;

import com.towny.architecture.model.SchematicBlock;
import com.towny.architecture.manager.BuildingManager;
import org.bukkit.World;
import org.bukkit.Particle;
import org.bukkit.Color;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.BuildingSchematic;
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
            if (args.length > 0 && args[0].equalsIgnoreCase("reload")) {
                plugin.reloadPluginConfig();
                sender.sendMessage("Конфигурация TownyArchitecture успешно перезагружена!");
                return true;
            }
            if (args.length > 0 && (args[0].equalsIgnoreCase("recalculate") || args[0].equalsIgnoreCase("sync") || args[0].equalsIgnoreCase("actualize") || args[0].equalsIgnoreCase("актуализация") || args[0].equalsIgnoreCase("актуализировать") || args[0].equalsIgnoreCase("перерасчет"))) {
                executeFullRecalculationAndReport(sender);
                return true;
            }
            sender.sendMessage("Команда доступна только игрокам в игре! (Консоль поддерживает: /build reload, /build recalculate)");
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

            case "forge":
            case "кузница": {
                ChunkCoord cc = ChunkCoord.fromLocation(player.getLocation());
                ActiveBuilding bld = plugin.getBuildingManager().getBuildingOccupyingChunk(cc);
                if (bld == null || !bld.getBlueprintId().equalsIgnoreCase("forge") || bld.getStatus() != ActiveBuilding.Status.ACTIVE) {
                    player.sendMessage(ChatColor.RED + "❌ Для доступа к функциям кузницы вы должны находиться на чанке со своей построенной и активной Городской Кузницей!");
                    player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
                    return true;
                }

                if (args.length >= 2 && (args[1].equalsIgnoreCase("anvil") || args[1].equalsIgnoreCase("наковальня"))) {
                    player.openAnvil(player.getLocation(), true);
                    player.playSound(player.getLocation(), Sound.BLOCK_ANVIL_USE, 0.8f, 1.2f);
                } else if (args.length >= 2 && (args[1].equalsIgnoreCase("super") || args[1].equalsIgnoreCase("супер"))) {
                    plugin.getForgeManager().openSuperAnvil(player);
                } else {
                    plugin.getForgeManager().openForgeHub(player);
                }
                break;
            }

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

            case "check":
            case "remaining":
            case "layer":
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
                double wallExp = plugin.getBuildingManager().calculateWallExposurePercent(building);
                String expColor = wallExp >= 50.0 ? ChatColor.GREEN.toString() : ChatColor.RED.toString();
                player.sendMessage(ChatColor.YELLOW + "Открытость стен и крыши: " + expColor + String.format("%.1f", wallExp) + "% " + 
                        ChatColor.GRAY + "(Мин. 50% " + (wallExp >= 50.0 ? "✔ норма" : "✖ заблокировано") + ")");
                BuildingSchematic schem = plugin.getSchematicManager().getSchematic(building.getBlueprintId());
                int totalBlocks = (schem != null) ? schem.getTotalBlockCount() : building.getTotalRequiredBlocks();
                player.sendMessage(ChatColor.DARK_AQUA + "Общий прогресс: " + ChatColor.GREEN + building.getProgressPercent() + "% " +
                        ChatColor.GRAY + "(" + building.getCompletedBlockCount() + "/" + totalBlocks + " блоков на своих местах)");

                if (schem != null && building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                    int cLayer = building.getCurrentLayer();
                    List<SchematicBlock> missing = plugin.getBuildingManager().getMissingBlocksInLayer(building, schem, cLayer);
                    int layerTotal = schem.getBlocksAtLayer(cLayer).size();
                    int layerPlaced = layerTotal - missing.size();

                    player.sendMessage(ChatColor.AQUA + "Текущий этап: " + ChatColor.YELLOW + "Слой " + (cLayer + 1) + 
                            ChatColor.WHITE + " (" + layerPlaced + "/" + layerTotal + " блоков установлено)");

                    if (!missing.isEmpty()) {
                        player.sendMessage(ChatColor.GOLD + "Осталось установить на Слое " + (cLayer + 1) + ":");
                        Map<Material, Integer> missingMatCounts = new LinkedHashMap<>();
                        for (SchematicBlock sb : missing) {
                            missingMatCounts.put(sb.getMaterial(), missingMatCounts.getOrDefault(sb.getMaterial(), 0) + 1);
                        }
                        for (Map.Entry<Material, Integer> me : missingMatCounts.entrySet()) {
                            player.sendMessage(ChatColor.YELLOW + " • " + ChatColor.WHITE + RussianTranslator.getMaterialRu(me.getKey()) + 
                                    ": " + ChatColor.RED + me.getValue() + " шт.");
                        }
                    }
                }
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
                if (!player.isOp() && !player.hasPermission("townyarchitecture.admin") && !player.hasPermission("*")) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав! (Требуется townyarchitecture.admin)");
                    return true;
                }
                if (args.length < 2) {
                    player.sendMessage(ChatColor.RED + "Использование: /build setlevel [игрок] <уровень>");
                    return true;
                }
                if (args.length >= 3) {
                    String targetName = args[1];
                    org.bukkit.OfflinePlayer target = org.bukkit.Bukkit.getOfflinePlayer(targetName);
                    if (target == null || target.getUniqueId() == null) {
                        player.sendMessage(ChatColor.RED + "Игрок '" + targetName + "' не найден!");
                        return true;
                    }
                    try {
                        int level = Integer.parseInt(args[2]);
                        plugin.getArchitectManager().setLevel(target.getUniqueId(), level);
                        String displayName = target.getName() != null ? target.getName() : targetName;
                        player.sendMessage(ChatColor.GREEN + "✔ Уровень Архитектора игрока " + displayName + " успешно установлен на " + level);
                        if (target.isOnline() && target.getPlayer() != null) {
                            target.getPlayer().sendMessage(ChatColor.GOLD + "⚡ [Администрация] Ваш уровень Архитектора установлен на " + level);
                        }
                    } catch (NumberFormatException e) {
                        player.sendMessage(ChatColor.RED + "Неверный уровень: " + args[2]);
                    }
                } else {
                    try {
                        int level = Integer.parseInt(args[1]);
                        plugin.getArchitectManager().setLevel(player.getUniqueId(), level);
                        player.sendMessage(ChatColor.GREEN + "✔ Ваш уровень Архитектора установлен на " + level);
                    } catch (NumberFormatException e) {
                        org.bukkit.OfflinePlayer target = org.bukkit.Bukkit.getOfflinePlayer(args[1]);
                        if (target != null && target.getUniqueId() != null) {
                            player.sendMessage(ChatColor.YELLOW + "Использование: /build setlevel " + (target.getName() != null ? target.getName() : args[1]) + " <уровень>");
                        } else {
                            player.sendMessage(ChatColor.RED + "Неверный уровень или игрок не найден: " + args[1]);
                        }
                    }
                }
                break;
            }
            case "tnt": {
                if (player.hasPermission("townyarchitecture.admin") || player.isOp()) {
                    int count = 4;
                    if (args.length >= 2) {
                        try { count = Integer.parseInt(args[1]); } catch (Exception ignored) {}
                    }
                    player.getInventory().addItem(plugin.getSiegeDamageManager().createSiegeTnt(count));
                    player.sendMessage(ChatColor.GREEN + "[TownyArchitecture v2] Вы получили " + count + " шт. Осадного TNT!");
                } else {
                    player.sendMessage(ChatColor.GOLD + "══════ Осадный Динамит (Siege TNT) ══════");
                    player.sendMessage(ChatColor.WHITE + "Используется для пробития обсидиановых коробок и бункеров!");
                    player.sendMessage(ChatColor.YELLOW + "Рецепт крафта в верстаке: " + ChatColor.WHITE + "TNT в центре, 4 железа по бокам, 4 пороха по углам.");
                    player.sendMessage(ChatColor.GOLD + "══════════════════════════════════════════");
                }
                break;
            }

            case "hologram":
            case "holograms": {
                ActiveBuilding building = plugin.getBuildingManager().getBuildingAt(player.getLocation());
                if (building == null) {
                    player.sendMessage(ChatColor.RED + "Вы не стоите на территории активного строительного проекта!");
                    return true;
                }
                plugin.getHologramDisplayManager().initHologramsForBuilding(building);
                player.sendMessage(ChatColor.GREEN + "✦ 3D-Голограммы чертежа (Слой " + (building.getCurrentLayer() + 1) + ") перезапущены!");
                player.playSound(player.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.5f);
                break;
            }

            case "facade":
            case "inspect":
            case "walls": {
                ActiveBuilding building = plugin.getBuildingManager().getBuildingAt(player.getLocation());
                if (building == null) {
                    player.sendMessage(ChatColor.RED + "Вы не стоите внутри какого-либо городского здания!");
                    return true;
                }
                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(building.getBlueprintId());
                String bpName = bp != null ? bp.getNameRu() : building.getBlueprintId();
                double exp = plugin.getBuildingManager().calculateWallExposurePercent(building);

                player.sendMessage(ChatColor.GOLD + "══════ Анализ Фасадов: " + ChatColor.YELLOW + bpName + ChatColor.GOLD + " ══════");
                player.sendMessage(ChatColor.WHITE + " • Открытость стен внешней среде: " + (exp >= 50.0 ? ChatColor.GREEN : ChatColor.RED) + 
                        String.format("%.1f", exp) + "% " + (exp >= 50.0 ? "✔ [НОРМА]" : "✖ [ЗАБЛОКИРОВАНО]"));
                player.sendMessage(ChatColor.WHITE + " • Требуемый минимум: " + ChatColor.YELLOW + "50.0% открытых блоков стен");
                player.sendMessage(ChatColor.GRAY + " • Разрешенные контактные блоки: " + ChatColor.AQUA + "Воздух, трава, листва, дорожки, цветы, вода");
                player.sendMessage(ChatColor.GRAY + " • Запрещено: " + ChatColor.RED + "Прятать постройки в бункеры или возводить глухие двойные стены");
                if (exp < 50.0) {
                    player.sendMessage(ChatColor.RED + "⚠ ВНИМАНИЕ: Баффы города приостановлены! Расчистите блоки вокруг стен здания.");
                } else {
                    player.sendMessage(ChatColor.GREEN + "✔ Фасад соответствует стандартам градостроительства.");
                }
                player.sendMessage(ChatColor.GOLD + "══════════════════════════════════════════");
                break;
            }

            case "rotate":
            case "turn":
            case "rot": {
                ActiveBuilding bld = plugin.getBuildingManager().getBuildingAt(player.getLocation());
                if (bld == null) {
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&c[!] Вы должны стоять на строительном участке постройки для ее поворота!"));
                    return true;
                }
                boolean success = plugin.getBuildingManager().rotateActiveBuilding(player, bld);
                if (success) {
                    BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                    String name = (bp != null) ? bp.getNameRu() : bld.getBlueprintId();
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&a[!] Голограмма постройки «&6" + name + 
                            "&a» успешно повернута на &e" + bld.getRotationDeg() + "°&a!"));
                    player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BELL, 1.0f, 1.2f);
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

            case "recalculate":
            case "sync":
            case "update":
            case "actualize":
            case "актуализация":
            case "актуализировать":
            case "перерасчет": {
                if (!player.hasPermission("townyarchitecture.admin") && !player.isOp()) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                executeFullRecalculationAndReport(player);
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
                player.sendMessage(ChatColor.YELLOW + "Команды: /builds (меню), /build rotate (поворот голограммы), /build stats, /plot set build, /build info, /build repair");
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








    public void executeFullRecalculationAndReport(CommandSender sender) {
        sender.sendMessage(ChatColor.YELLOW + "[TownySuite] Запуск полного перерасчета и актуализации всех систем...");
        Map<String, Object> archStats = plugin.getBuildingManager().performFullRecalculation(sender);
        
        Map<String, Object> siegesStats = null;
        try {
            org.bukkit.plugin.Plugin siegesPl = org.bukkit.Bukkit.getPluginManager().getPlugin("TownySieges");
            if (siegesPl != null && siegesPl.isEnabled()) {
                Object mgr = siegesPl.getClass().getMethod("getSiegeManager").invoke(siegesPl);
                if (mgr != null) {
                    siegesStats = (Map<String, Object>) mgr.getClass().getMethod("performFullRecalculation", CommandSender.class).invoke(mgr, sender);
                }
            }
        } catch (Throwable ignored) {}

        sendRecalculationReport(sender, archStats, siegesStats);
    }

    public static void sendRecalculationReport(CommandSender sender, Map<String, Object> archStats, Map<String, Object> siegesStats) {
        sender.sendMessage(ChatColor.GOLD + "═══════════ " + ChatColor.YELLOW + "[TownySuite] ПОЛНЫЙ ПЕРЕРАСЧЕТ И АКТУАЛИЗАЦИЯ " + ChatColor.GOLD + "═══════════");
        
        if (archStats != null) {
            sender.sendMessage(ChatColor.GREEN + "✔ TownyArchitecture (Городские постройки и территории):");
            sender.sendMessage(ChatColor.WHITE + "  • Всего построек в реестре: " + ChatColor.YELLOW + archStats.get("totalBuildings") +
                    ChatColor.GRAY + " (Затронуто городов: " + ChatColor.WHITE + archStats.get("affectedTownsCount") + ChatColor.GRAY + ")");
            sender.sendMessage(ChatColor.WHITE + "  • Статусы в реальном мире: " +
                    ChatColor.GREEN + "Активных: " + archStats.get("activeCount") + ChatColor.GRAY + " | " +
                    ChatColor.YELLOW + "Строятся: " + archStats.get("constructingCount") + ChatColor.GRAY + " | " +
                    ChatColor.RED + "Повреждены: " + archStats.get("damagedCount") + ChatColor.GRAY + " | " +
                    ChatColor.DARK_GRAY + "Замурованы: " + archStats.get("entombedCount"));
            sender.sendMessage(ChatColor.WHITE + "  • Физическая прочность: " + ChatColor.AQUA + "100% пересчитана по реальным блокам schematics");
            sender.sendMessage(ChatColor.WHITE + "  • Завершено строек по факту блоков: " + ChatColor.GREEN + "+" + archStats.get("completedConstructing") +
                    ChatColor.GRAY + " | Восстановлено после починки: " + ChatColor.GREEN + "+" + archStats.get("restoredToActive"));
            sender.sendMessage(ChatColor.WHITE + "  • Передано построек победителям/новым владельцам: " + ChatColor.GOLD + archStats.get("transferredCount"));
            sender.sendMessage(ChatColor.WHITE + "  • Отвязано от уничтоженных городов: " + ChatColor.RED + archStats.get("unlinkedFromDeletedTown"));
            sender.sendMessage(ChatColor.WHITE + "  • Чанков подгружено для сканирования: " + ChatColor.LIGHT_PURPLE + archStats.get("chunksForceLoaded"));
            sender.sendMessage(ChatColor.GRAY + "  • Лимиты (1 на 2 чанка / уникальные здания) и городские баффы обновлены.");
        } else {
            sender.sendMessage(ChatColor.GRAY + "• TownyArchitecture: плагин не загружен.");
        }

        if (siegesStats != null) {
            sender.sendMessage(ChatColor.GREEN + "✔ TownySieges (Войны наций, осадные лагеря и артиллерия):");
            sender.sendMessage(ChatColor.WHITE + "  • Активных войн наций: " + ChatColor.YELLOW + siegesStats.get("warsActive") +
                    ChatColor.GRAY + " (Всего: " + siegesStats.get("warsTotal") + ", удалено неактуальных: " + siegesStats.get("warsEnded") + ")");
            int totalActiveCamps = ((Number) siegesStats.getOrDefault("campsActive", 0)).intValue() + ((Number) siegesStats.getOrDefault("campsPrep", 0)).intValue();
            sender.sendMessage(ChatColor.WHITE + "  • Действующих осадных лагерей: " + ChatColor.YELLOW + totalActiveCamps +
                    ChatColor.GRAY + " (Штурм: " + ChatColor.RED + siegesStats.get("campsActive") + ChatColor.GRAY +
                    ", Подготовка: " + ChatColor.GOLD + siegesStats.get("campsPrep") + ChatColor.GRAY + ")");
            sender.sendMessage(ChatColor.WHITE + "  • Лагерей очищено/завершено (удаленные города/истекшие): " + ChatColor.RED + siegesStats.get("campsCleaned"));
            sender.sendMessage(ChatColor.WHITE + "  • Переведено из подготовки в штурм по таймеру: " + ChatColor.GOLD + "+" + siegesStats.get("prepAdvancedToAssault"));
            sender.sendMessage(ChatColor.WHITE + "  • Активных захватов штурмовых знамен: " + ChatColor.AQUA + siegesStats.get("bannerCapturesActive"));
            sender.sendMessage(ChatColor.GRAY + "  • Осадные боссбары и территориальные привязки синхронизированы.");
        } else {
            sender.sendMessage(ChatColor.GRAY + "• TownySieges: плагин не загружен.");
        }

        sender.sendMessage(ChatColor.GOLD + "══════════════════════════════════════════════════════════════════");
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
            List<String> list = new ArrayList<>(Arrays.asList("gui", "stats", "info", "check", "forge", "plot", "rotate", "turn", "repair", "highlight", "borders", "effects"));
            if (sender instanceof Player && plugin.getTownyHook().isPlayerMayorOrAssistant((Player) sender)) {
                list.add("demolish");
            }
            if (sender.hasPermission("townyarchitecture.admin") || sender.isOp()) {
                list.add("reload");
                list.add("recalculate");
                list.add("sync");
                list.add("wonder");
                list.add("resetxp");
                list.add("setlevel");
            }
            return list;
        } else if (args.length == 2 && (args[0].equalsIgnoreCase("forge") || args[0].equalsIgnoreCase("кузница"))) {
            return Arrays.asList("anvil", "super", "наковальня", "супер");
        } else if (args.length == 2 && args[0].equalsIgnoreCase("setlevel") && (sender.hasPermission("townyarchitecture.admin") || sender.isOp())) {
            List<String> suggestions = new ArrayList<>();
            for (org.bukkit.entity.Player p : org.bukkit.Bukkit.getOnlinePlayers()) {
                suggestions.add(p.getName());
            }
            suggestions.addAll(Arrays.asList("1", "5", "10", "15", "20", "25", "30", "50"));
            return suggestions;
        } else if (args.length == 3 && args[0].equalsIgnoreCase("setlevel") && (sender.hasPermission("townyarchitecture.admin") || sender.isOp())) {
            return Arrays.asList("1", "5", "10", "15", "20", "25", "30", "50");
        } else if (args.length == 2 && args[0].equalsIgnoreCase("plot")) {
            return Arrays.asList("set", "list", "remove");
        } else if (args.length == 3 && args[0].equalsIgnoreCase("plot") && args[1].equalsIgnoreCase("set")) {
            return Collections.singletonList("build");
        }
        return Collections.emptyList();
    }
}
