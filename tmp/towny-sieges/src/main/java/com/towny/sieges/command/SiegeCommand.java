package com.towny.sieges.command;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.ChunkCoord;
import com.towny.sieges.model.NationWar;
import com.towny.sieges.model.SiegeCamp;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;

import java.util.*;
import java.util.stream.Collectors;

public class SiegeCommand implements CommandExecutor, TabCompleter {

    private final TownySiegesPlugin plugin;

    public SiegeCommand(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        String cmdName = command.getName().toLowerCase();
        
        // 1. Handle TOP-LEVEL commands from plugin.yml
        if (cmdName.equals("disband") || cmdName.equals("cancel") || cmdName.equals("destroy")) {
            return handleDisband(sender, args);
        }
        
        if (cmdName.equals("skip-prep") || cmdName.equals("skip") || cmdName.equals("assault")) {
            return handleSkipPrep(sender, args);
        }

        // 2. Handle /siege <subcommand>
        if (cmdName.equals("siege") || cmdName.equals("sieges") || cmdName.equals("townysieges") || cmdName.equals("osada")) {
            if (args.length == 0) {
                if (sender instanceof Player) {
                    plugin.getSiegeMenuGui().openMainMenu((Player) sender);
                } else {
                    sendConsoleSystemsOverview(sender);
                }
                return true;
            }
            if (args[0].equalsIgnoreCase("help")) {
                sendHelp(sender);
                return true;
            }

            String sub = args[0].toLowerCase();
            String[] subArgs = args.length > 1 ? Arrays.copyOfRange(args, 1, args.length) : new String[0];

            switch (sub) {
                case "menu":
                case "gui":
                case "меню":
                case "crafts":
                case "recipes":
                case "крафты":
                case "рецепты":
                    if (sender instanceof Player) {
                        plugin.getSiegeMenuGui().openMainMenu((Player) sender);
                    } else {
                        sendConsoleSystemsOverview(sender);
                    }
                    return true;
                case "disband":
                case "cancel":
                case "destroy":
                case "расформировать":
                case "уничтожить":
                    return handleDisband(sender, subArgs);
                case "skip-prep":
                case "skipprep":
                case "skip":
                case "fastforward":
                case "штурм":
                    return handleSkipPrep(sender, subArgs);
                case "admin":
                    return handleAdmin(sender, subArgs);
                case "camp":
                case "lager":
                    return handleCamp(sender, subArgs);
                case "expand":
                case "rasshirit":
                    return handleExpand(sender, subArgs);
                case "unclaim":
                case "udalit":
                    return handleUnclaim(sender, subArgs);
                case "banner":
                case "flag":
                case "флаг":
                    return handleBanner(sender, subArgs);

                case "cannon":
                case "pushka":
                case "mortar":
                    return handleCannon(sender, subArgs);
                case "ammo":
                case "yadra":
                    return handleAmmo(sender, subArgs);
                case "nationwar":
                case "war":
                case "война":
                    return handleNationWar(sender, subArgs);
                case "switch":
                case "toggle":
                    return handleSwitch(sender);
                case "skill":
                case "artillery":
                case "навык":
                case "артиллерист":
                    if (!sender.hasPermission("townysieges.admin")) {
                        sender.sendMessage(ChatColor.RED + "Нет прав!");
                        return true;
                    }
                    return handleSkill(sender, subArgs);
                case "architect":
                case "архитектор":
                    if (!sender.hasPermission("townysieges.admin")) {
                        sender.sendMessage(ChatColor.RED + "Нет прав!");
                        return true;
                    }
                    return handleArchitect(sender, subArgs);
                case "recalculate":
                case "sync":
                case "update":
                case "actualize":
                case "актуализация":
                case "актуализировать":
                case "перерасчет":
                    if (!sender.hasPermission("townysieges.admin")) {
                        sender.sendMessage(ChatColor.RED + "Нет прав!");
                        return true;
                    }
                    return handleRecalculate(sender);
                default:
                    sender.sendMessage(ChatColor.RED + "Неизвестная команда. Введите /siege help");
                    return true;
            }
        }
        return true;
    }

    private boolean handleDisband(CommandSender sender, String[] args) {
        if (args.length >= 1 && sender.hasPermission("townysieges.admin")) {
            plugin.getSiegeManager().endSiegeAdmin(args[0], sender);
            return true;
        }
        if (!(sender instanceof Player)) {
            sender.sendMessage(ChatColor.RED + "Использование: /disband <Город|Нация>");
            return true;
        }
        plugin.getSiegeManager().disbandCampByMayor((Player) sender);
        return true;
    }

    private boolean handleSkipPrep(CommandSender sender, String[] args) {
        if (!sender.hasPermission("townysieges.admin")) {
            sender.sendMessage(ChatColor.RED + "Нет прав!");
            return true;
        }
        String target = args.length >= 1 ? args[0] : null;
        plugin.getSiegeManager().skipPreparation(target, sender);
        return true;
    }

    private boolean handleAdmin(CommandSender sender, String[] args) {
        if (!sender.hasPermission("townysieges.admin")) {
            sender.sendMessage(ChatColor.RED + "Нет прав!");
            return true;
        }
        if (args.length < 1 || args[0].equalsIgnoreCase("help")) {
            sender.sendMessage(ChatColor.GOLD + "══════ Админ-команды ══════");
            sender.sendMessage(ChatColor.AQUA + "/siege admin skill <игрок> <уровень>");
            sender.sendMessage(ChatColor.AQUA + "/siege admin architect <игрок> <уровень>");
            sender.sendMessage(ChatColor.AQUA + "/siege admin skip-prep [цель]");
            sender.sendMessage(ChatColor.AQUA + "/siege admin end [цель]");
            sender.sendMessage(ChatColor.AQUA + "/siege admin recalculate");
            return true;
        }
        String sub = args[0].toLowerCase();
        String target = args.length >= 2 ? args[1] : null;

        if (sub.equals("skill") || sub.equals("artillery") || sub.equals("навык")) {
            return handleSkill(sender, Arrays.copyOfRange(args, 1, args.length));
        } else if (sub.equals("architect") || sub.equals("архитектор")) {
            return handleArchitect(sender, Arrays.copyOfRange(args, 1, args.length));
        } else if (sub.equals("skip-prep") || sub.equals("skip")) {
            plugin.getSiegeManager().skipPreparation(target, sender);
        } else if (sub.equals("end") || sub.equals("stop")) {
            plugin.getSiegeManager().endSiegeAdmin(target, sender);
        } else if (sub.equals("recalculate") || sub.equals("sync")) {
            return handleRecalculate(sender);
        }
        return true;
    }

    private boolean handleArchitect(CommandSender sender, String[] args) {
        org.bukkit.plugin.Plugin archPl = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
        if (archPl == null || !archPl.isEnabled()) {
            sender.sendMessage(ChatColor.RED + "Плагин TownyArchitecture не загружен.");
            return true;
        }

        if (args.length == 0) {
            if (!(sender instanceof Player player)) {
                sender.sendMessage(ChatColor.RED + "Использование: /siege architect <игрок> [уровень]");
                return true;
            }
            try {
                Object aMgr = archPl.getClass().getMethod("getArchitectManager").invoke(archPl);
                int level = (Integer) aMgr.getClass().getMethod("getLevel", Player.class).invoke(aMgr, player);
                Object st = aMgr.getClass().getMethod("getStats", Player.class).invoke(aMgr, player);
                int xp = 0;
                if (st != null) {
                    try { xp = (Integer) st.getClass().getField("xp").get(st); } catch (Exception ignored) {}
                }
                player.sendMessage(ChatColor.GOLD + "══════ Профиль Архитектора: " + ChatColor.YELLOW + player.getName() + ChatColor.GOLD + " ══════");
                player.sendMessage(ChatColor.WHITE + " • Уровень: " + ChatColor.GREEN + level + " ур.");
                player.sendMessage(ChatColor.WHITE + " • Опыт (XP): " + ChatColor.AQUA + xp + " XP");
            } catch (Exception e) {
                sender.sendMessage(ChatColor.RED + "Ошибка получения профиля архитектора: " + e.getMessage());
            }
            return true;
        }

        Player target = Bukkit.getPlayer(args[0]);
        if (target == null) {
            sender.sendMessage(ChatColor.RED + "Игрок '" + args[0] + "' не найден онлайн!");
            return true;
        }

        if (args.length >= 2) {
            try {
                int newLevel = Integer.parseInt(args[1]);
                Object aMgr = archPl.getClass().getMethod("getArchitectManager").invoke(archPl);
                aMgr.getClass().getMethod("setLevel", Player.class, int.class).invoke(aMgr, target, newLevel);
                sender.sendMessage(ChatColor.GREEN + "✔ Уровень Архитектора игрока " + target.getName() + " установлен на " + newLevel + " ур.!");
                target.sendMessage(ChatColor.GOLD + "⚡ [Администрация] Ваш уровень Архитектора установлен на " + newLevel + " ур.!");
            } catch (NumberFormatException e) {
                sender.sendMessage(ChatColor.RED + "Некорректный уровень: " + args[1]);
            } catch (Exception e) {
                sender.sendMessage(ChatColor.RED + "Ошибка установки уровня архитектора: " + e.getMessage());
            }
            return true;
        }

        try {
            Object aMgr = archPl.getClass().getMethod("getArchitectManager").invoke(archPl);
            int level = (Integer) aMgr.getClass().getMethod("getLevel", Player.class).invoke(aMgr, target);
            Object st = aMgr.getClass().getMethod("getStats", Player.class).invoke(aMgr, target);
            int xp = 0;
            if (st != null) {
                try { xp = (Integer) st.getClass().getField("xp").get(st); } catch (Exception ignored) {}
            }
            sender.sendMessage(ChatColor.GOLD + "══════ Профиль Архитектора: " + ChatColor.YELLOW + target.getName() + ChatColor.GOLD + " ══════");
            sender.sendMessage(ChatColor.WHITE + " • Уровень: " + ChatColor.GREEN + level + " ур.");
            sender.sendMessage(ChatColor.WHITE + " • Опыт (XP): " + ChatColor.AQUA + xp + " XP");
        } catch (Exception e) {
            sender.sendMessage(ChatColor.RED + "Ошибка получения профиля архитектора: " + e.getMessage());
        }
        return true;
    }

    private boolean handleSkill(CommandSender sender, String[] args) {
        com.towny.sieges.manager.ArtillerySkillManager mgr = plugin.getArtillerySkillManager();
        if (mgr == null) {
            sender.sendMessage(ChatColor.RED + "Система навыков не инициализирована.");
            return true;
        }

        if (args.length == 0) {
            if (!(sender instanceof Player player)) {
                sender.sendMessage(ChatColor.RED + "Использование: /siege skill <игрок> [уровень]");
                return true;
            }
            int level = mgr.getLevel(player.getUniqueId());
            double xp = mgr.getXP(player.getUniqueId());
            double cd = mgr.getReloadCooldownSeconds(player.getUniqueId());
            double reqXp = mgr.getRequiredXPForLevel(level < 10 ? level + 1 : 10);

            player.sendMessage(ChatColor.GOLD + "══════ Навык «Артиллерист» ══════");
            player.sendMessage(ChatColor.YELLOW + "• Уровень: " + ChatColor.WHITE + level + " / 10 ур.");
            player.sendMessage(ChatColor.YELLOW + "• Скорость перезарядки: " + ChatColor.GREEN + String.format(Locale.US, "%.1f", cd) + " сек. " + ChatColor.GRAY + "(10.0s ➔ 5.0s)");
            player.sendMessage(ChatColor.YELLOW + "• Опыт (XP): " + ChatColor.WHITE + String.format(Locale.US, "%.0f", xp) + 
                    (level < 10 ? " / " + String.format(Locale.US, "%.0f", reqXp) + " XP" : " XP (МАКС)"));
            player.sendMessage(ChatColor.GRAY + "Прокачка: Выстрелы из мортиры (+15 XP), урон и разрушения во время осад.");
            return true;
        }

        Player target = Bukkit.getPlayer(args[0]);
        if (target == null) {
            sender.sendMessage(ChatColor.RED + "Игрок '" + args[0] + "' не найден онлайн!");
            return true;
        }

        if (args.length >= 2) {
            if (!sender.hasPermission("townysieges.admin")) {
                sender.sendMessage(ChatColor.RED + "У вас нет прав администратора для изменения уровня артиллериста!");
                return true;
            }
            try {
                int newLevel = Integer.parseInt(args[1]);
                if (newLevel < 1 || newLevel > com.towny.sieges.manager.ArtillerySkillManager.MAX_LEVEL) {
                    sender.sendMessage(ChatColor.RED + "Уровень должен быть от 1 до " + com.towny.sieges.manager.ArtillerySkillManager.MAX_LEVEL + "!");
                    return true;
                }
                mgr.setLevel(target.getUniqueId(), newLevel);
                double cd = mgr.getReloadCooldownSeconds(target.getUniqueId());

                sender.sendMessage(ChatColor.GREEN + "✔ Уровень навыка «Артиллерист» игрока " + target.getName() + 
                        " установлен на " + newLevel + " ур.! (Перезарядка: " + String.format(Locale.US, "%.1f", cd) + " сек).");
                target.sendMessage(ChatColor.GOLD + "⚡ [Администрация] Ваш уровень навыка «Артиллерист» установлен на " + 
                        newLevel + " ур.! Скорость перезарядки мортиры: " + String.format(Locale.US, "%.1f", cd) + " сек.");
            } catch (NumberFormatException e) {
                sender.sendMessage(ChatColor.RED + "Некорректный числовой уровень: " + args[1]);
            }
            return true;
        }

        int level = mgr.getLevel(target.getUniqueId());
        double xp = mgr.getXP(target.getUniqueId());
        double cd = mgr.getReloadCooldownSeconds(target.getUniqueId());
        sender.sendMessage(ChatColor.GOLD + "══════ Навык «Артиллерист»: " + target.getName() + " ══════");
        sender.sendMessage(ChatColor.YELLOW + "• Уровень: " + ChatColor.WHITE + level + " / 10 ур.");
        sender.sendMessage(ChatColor.YELLOW + "• Перезарядка: " + ChatColor.GREEN + String.format(Locale.US, "%.1f", cd) + " сек.");
        sender.sendMessage(ChatColor.YELLOW + "• Опыт (XP): " + ChatColor.WHITE + String.format(Locale.US, "%.0f", xp));
        return true;
    }



    private boolean handleCamp(CommandSender sender, String[] args) {
        if (!(sender instanceof Player)) return true;
        if (args.length < 1) {
            sender.sendMessage(ChatColor.RED + "/siege camp <Город>");
            return true;
        }
        plugin.getSiegeManager().createSiegeCamp((Player) sender, args[0], ((Player) sender).getLocation());
        return true;
    }

    private boolean handleExpand(CommandSender sender, String[] args) {
        if (sender instanceof Player) plugin.getSiegeManager().expandSiegeCamp((Player) sender, ((Player) sender).getLocation());
        return true;
    }

    private boolean handleUnclaim(CommandSender sender, String[] args) {
        if (sender instanceof Player) plugin.getSiegeManager().unclaimSiegeChunk((Player) sender, ((Player) sender).getLocation());
        return true;
    }

    private boolean handleBanner(CommandSender sender, String[] args) {
        if (!sender.hasPermission("townysieges.admin")) return true;
        Player target = (args.length >= 1) ? Bukkit.getPlayer(args[0]) : (sender instanceof Player ? (Player) sender : null);
        if (target != null) {
            target.getInventory().addItem(plugin.getCaptureManager().getAssaultBannerItem());
            sender.sendMessage(ChatColor.GREEN + "Выдан штурмовой флаг " + target.getName());
        }
        return true;
    }



    private boolean handleCannon(CommandSender sender, String[] args) {
        if (!sender.hasPermission("townysieges.admin")) return true;
        Player target = (args.length >= 1) ? Bukkit.getPlayer(args[0]) : (sender instanceof Player ? (Player) sender : null);
        if (target != null) {
            target.getInventory().addItem(plugin.getCannonManager().getCannonItem());
            sender.sendMessage(ChatColor.GREEN + "Выдана мортира " + target.getName());
        }
        return true;
    }

    private boolean handleAmmo(CommandSender sender, String[] args) {
        if (args.length >= 1 && args[0].equalsIgnoreCase("recipes")) {
            sendAmmoRecipes(sender);
            return true;
        }
        if (args.length >= 2 && args[0].equalsIgnoreCase("give")) {
            if (!sender.hasPermission("townysieges.admin")) return true;
            boolean isAp = args[1].equalsIgnoreCase("ap");
            int count = (args.length >= 3) ? Integer.parseInt(args[2]) : 1;
            Player target = (args.length >= 4) ? Bukkit.getPlayer(args[3]) : (sender instanceof Player ? (Player) sender : null);
            if (target != null) {
                for (int i=0; i<count; i++) target.getInventory().addItem(plugin.getCannonManager().createAmmoItem(isAp));
                sender.sendMessage(ChatColor.GREEN + "Выдано " + count + " ядер " + target.getName());
            }
            return true;
        }
        return true;
    }

    private void sendAmmoRecipes(CommandSender sender) {
        sender.sendMessage(ChatColor.GOLD + "══════ Рецепты Крафта TownySieges (Верстак 3х3) ══════");
        sender.sendMessage(ChatColor.YELLOW + "1. Осадная Мортира:");
        sender.sendMessage(ChatColor.WHITE + "   [Жел.блок]   [Раздатчик] [Жел.блок]");
        sender.sendMessage(ChatColor.WHITE + "   [Камень]     [Котёл]     [Камень]");
        sender.sendMessage(ChatColor.WHITE + "   [Дуб.бревно] [Дуб.бревно][Дуб.бревно]");
        sender.sendMessage(ChatColor.YELLOW + "2. Фугасное Ядро (Чугунное):");
        sender.sendMessage(ChatColor.WHITE + "   [Жел.слиток] [Жел.слиток][Жел.слиток]");
        sender.sendMessage(ChatColor.WHITE + "   [Жел.слиток] [Порох]     [Жел.слиток]");
        sender.sendMessage(ChatColor.WHITE + "   [Уголь]      [Порох]     [Уголь]");
        sender.sendMessage(ChatColor.YELLOW + "3. Бронебойное Ядро (Незерит, пробивает обсидиан):");
        sender.sendMessage(ChatColor.WHITE + "   [Алмаз]      [Обсидиан]  [Алмаз]");
        sender.sendMessage(ChatColor.WHITE + "   [Незерит.обл][TNT]       [Обсидиан]");
        sender.sendMessage(ChatColor.WHITE + "   [Алмаз]      [Порох]     [Алмаз]");
        sender.sendMessage(ChatColor.YELLOW + "4. Штурмовой Флаг (Захват чанка):");
        sender.sendMessage(ChatColor.WHITE + "   [Золото]     [TNT]       [Золото]");
        sender.sendMessage(ChatColor.WHITE + "   [Золото]     [Красн.флаг][Золото]");
        sender.sendMessage(ChatColor.WHITE + "   [Пусто]      [Стерж.ифрита][Пусто]");
        sender.sendMessage(ChatColor.GOLD + "══════════════════════════════════════════════════════");
    }

    private void sendConsoleSystemsOverview(CommandSender sender) {
        sender.sendMessage(ChatColor.GOLD + "═══════════ СИСТЕМЫ И КРАФТЫ TOWNYSIEGES ═══════════");
        sender.sendMessage(ChatColor.YELLOW + "1. Осадные Лагеря: " + ChatColor.WHITE + "/siege camp <Город> | /siege expand | /disband");
        sender.sendMessage(ChatColor.GRAY + "   24ч подготовка -> 2ч активный штурм (взрывы и разрушения).");
        sender.sendMessage(ChatColor.YELLOW + "2. Почанковый Захват: " + ChatColor.WHITE + "Штурмовой флаг, луч маяка, BossBar.");
        sender.sendMessage(ChatColor.GRAY + "   Удержание 5 минут. При успехе чанк переходит атакующим как Аванпост.");
        sender.sendMessage(ChatColor.YELLOW + "3. Осадные Мортиры: " + ChatColor.WHITE + "Установка блоком, перезарядка 10 сек.");
        sender.sendMessage(ChatColor.GRAY + "   ПКМ прицелиться, ЛКМ выстрел, клавиша [F] переключение ядер.");
        sender.sendMessage(ChatColor.YELLOW + "4. Боеприпасы: " + ChatColor.WHITE + "Фугасы (радиус 4.5) и Бронебойные (пробивают обсидиан).");
        sender.sendMessage(ChatColor.YELLOW + "5. Навык «Артиллерист»: " + ChatColor.WHITE + "Прокачка от урона и разрушения блоков.");
        sender.sendMessage(ChatColor.YELLOW + "6. Войны Наций: " + ChatColor.WHITE + "/siege nationwar declare <Нация> - тотальный разгром.");
        sender.sendMessage(ChatColor.YELLOW + "7. Захваченные здания: " + ChatColor.WHITE + "Переходят победителю (лимит: 1 уникальное).");
        sendAmmoRecipes(sender);
    }

    private boolean handleNationWar(CommandSender sender, String[] args) {
        if (args.length < 1 || args[0].equalsIgnoreCase("status")) {
            sender.sendMessage(ChatColor.GOLD + "══════ Войны Наций ══════");
            for (NationWar nw : plugin.getSiegeManager().getAllNationWars()) {
                sender.sendMessage(ChatColor.YELLOW + "• " + nw.getAttackerNation() + " ➔ " + nw.getDefenderNation());
            }
            return true;
        }
        if (args[0].equalsIgnoreCase("declare") && sender instanceof Player && args.length >= 2) {
            plugin.getSiegeManager().declareNationWar((Player) sender, args[1]);
        }
        return true;
    }

    private boolean handleSwitch(CommandSender sender) {
        if (sender instanceof Player) {
            Player p = (Player) sender;
            if (plugin.getCannonManager().isMounted(p)) plugin.getCannonManager().cycleAmmo(p);
        }
        return true;
    }

    private boolean handleRecalculate(CommandSender sender) {
        sender.sendMessage(ChatColor.YELLOW + "[TownySuite] Запуск полного перерасчета и актуализации всех систем...");
        Map<String, Object> siegesStats = plugin.getSiegeManager().performFullRecalculation(sender);

        Map<String, Object> archStats = null;
        try {
            org.bukkit.plugin.Plugin archPl = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
            if (archPl != null && archPl.isEnabled()) {
                Object mgr = archPl.getClass().getMethod("getBuildingManager").invoke(archPl);
                if (mgr != null) {
                    archStats = (Map<String, Object>) mgr.getClass().getMethod("performFullRecalculation", CommandSender.class).invoke(mgr, sender);
                }
            }
        } catch (Throwable ignored) {}

        sendRecalculationReport(sender, archStats, siegesStats);
        return true;
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

    private void sendHelp(CommandSender sender) {
        sender.sendMessage(ChatColor.GOLD + "══════ TownySieges ══════");
        sender.sendMessage(ChatColor.YELLOW + "/siege menu " + ChatColor.GRAY + "- Интерактивное меню систем и крафтов");
        sender.sendMessage(ChatColor.YELLOW + "/siege camp <Город> " + ChatColor.GRAY + "- Разбить осадный лагерь");
        sender.sendMessage(ChatColor.YELLOW + "/siege expand " + ChatColor.GRAY + "- Расширить лагерь на чанк");
        sender.sendMessage(ChatColor.YELLOW + "/disband " + ChatColor.GRAY + "- Расформировать лагерь (Мэр)");
        sender.sendMessage(ChatColor.YELLOW + "/siege switch " + ChatColor.GRAY + "- Сменить ядро (или [F])");
        sender.sendMessage(ChatColor.YELLOW + "/siege recipes " + ChatColor.GRAY + "- Рецепты мортир, ядер и флага");
        sender.sendMessage(ChatColor.YELLOW + "/siege admin skip-prep " + ChatColor.GRAY + "- Начать штурм");
        sender.sendMessage(ChatColor.YELLOW + "/siege recalculate " + ChatColor.GRAY + "- Полный перерасчет мира");
        sender.sendMessage(ChatColor.GOLD + "═════════════════════════");
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        String cmdName = command.getName().toLowerCase();
        
        // Handle /siege tab completion
        if (cmdName.equals("siege")) {
            if (args.length == 1) {
                List<String> list = new ArrayList<>(Arrays.asList("menu", "gui", "recipes", "camp", "expand", "disband", "unclaim", "banner", "cannon", "ammo", "nationwar", "admin", "help", "switch"));
                if (sender.hasPermission("townysieges.admin")) {
                    list.add("recalculate");
                    list.add("sync");
                    list.add("skill");
                    list.add("artillery");
                    list.add("навык");
                }
                return filter(list, args[0]);
            }
            if (args.length == 2) {
                String sub = args[0].toLowerCase();
                if (sub.equals("admin")) return filter(Arrays.asList("skip-prep", "end", "recalculate", "skill"), args[1]);
                if (sub.equals("nationwar")) return filter(Arrays.asList("declare", "status"), args[1]);
                if (sub.equals("ammo")) return filter(Arrays.asList("give", "recipes"), args[1]);
                if (sub.equals("banner") || sub.equals("cannon")) return filter(Arrays.asList("give"), args[1]);
                if (sub.equals("camp") || sub.equals("skill") || sub.equals("artillery") || sub.equals("навык")) return filter(Bukkit.getOnlinePlayers().stream().map(Player::getName).collect(Collectors.toList()), args[1]);
            }
            if (args.length == 3) {
                if (args[0].equalsIgnoreCase("ammo") && args[1].equalsIgnoreCase("give")) return filter(Arrays.asList("regular", "ap"), args[2]);
                if (args[0].equalsIgnoreCase("skill") || args[0].equalsIgnoreCase("artillery") || (args[0].equalsIgnoreCase("admin") && args[1].equalsIgnoreCase("skill"))) {
                    return filter(Arrays.asList("1", "2", "3", "4", "5", "6", "7", "8", "9", "10"), args[2]);
                }
            }
        }

        // Handle /disband, /cancel tab completion
        if (cmdName.equals("disband") || cmdName.equals("cancel")) {
            if (args.length == 1 && sender.hasPermission("townysieges.admin")) {
                return filter(Bukkit.getOnlinePlayers().stream().map(Player::getName).collect(Collectors.toList()), args[0]);
            }
        }
        
        return new ArrayList<>();
    }

    private List<String> filter(List<String> list, String input) {
        String last = input.toLowerCase();
        return list.stream().filter(s -> s.toLowerCase().startsWith(last)).collect(Collectors.toList());
    }
}
