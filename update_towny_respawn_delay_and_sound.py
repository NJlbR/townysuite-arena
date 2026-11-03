import os

# 1. Update config.yml
config_yml = '''# ========================================================
# TownyRespawn Configuration v1.1.0
# ========================================================
enabled: true
debug-logging: false

# --------------------------------------------------------
# 1. Настройки системы мульти-кроватей (Multiple Beds)
# --------------------------------------------------------
beds:
  enabled: true
  max-beds-default: 3
  use-permission-limits: true
  allow-rename: true
  auto-register-on-interact: true
  verify-bed-block-exists: true
  exclusive-one-player-per-bed: true
  auto-cleanup-destroyed-beds: true
  default-bed-name-format: "Кровать #{number}"

# --------------------------------------------------------
# 2. Настройки точек возрождения и задержки
# --------------------------------------------------------
respawn:
  # Задержка на респавн в секундах (30 секунд)
  delay-seconds: 30
  # Команда /respawn доступна только администраторам для тестов (игрокам меню открывается при смерти)
  admin-only-command: true
  allow-town-spawn: true
  allow-nation-spawn: true
  block-spawn-if-under-siege: false

  vanilla-respawn:
    enabled: true
    label: "&a&l🌲 Ванильный респавн"
    description:
      - "&7Возрождение в дикой природе мира"
      - "&7(как при стандартном случайном спавне)"
      - "&e▸ Нажмите для быстрого возрождения"
    wild-radius-min: 200
    wild-radius-max: 1500

  server-spawn:
    enabled: true
    label: "&6&l🏛 На спавн сервера"
    description:
      - "&7Возрождение на главном спавне сервера"
      - "&7Безопасная мирная зона"
      - "&e▸ Нажмите для телепортации на спавн"
    use-world-spawn: true
    custom-coords:
      enabled: false
      world: "world"
      x: 0.5
      y: 70.0
      z: 0.5
      yaw: 0.0
      pitch: 0.0

  gui-open-delay-ticks: 1

  # Негромкий звук при возрождении для оповещения окружающих игроков (БЕЗ ТОТЕМОВ И ЭФФЕКТОВ!)
  sound:
    enabled: true
    name: "BLOCK_BEACON_ACTIVATE"
    volume: 0.5
    pitch: 1.4

# --------------------------------------------------------
# 3. Сообщения плагина
# --------------------------------------------------------
messages:
  prefix: "&b&l[TownyRespawn]&r "
  menu-title-death: "&8Выбор точки возрождения"
  menu-title-respawn: "&8Выбор точки возрождения"
  command-admin-only: "&cКоманда /respawn доступна только администраторам для тестирования. Меню выбора точки возрождения открывается автоматически при вашей смерти."
  countdown-actionbar: "&e⏳ Возрождение на точке &b«{location}» &eчерез &c{seconds} &eсек..."
  countdown-title: "&eВозрождение"
  countdown-subtitle: "&7До появления: &c{seconds} &7сек..."
  respawn-selected: "&aВы успешно возродились: &f{location}&a!"
  bed-registered: "&a✔ Кровать «{name}» успешно привязана! ({current}/{max})"
  bed-limit-reached: "&cУ вас достигнут лимит кроватей ({max})! Удалите старую через /respawn delete."
  bed-renamed: "&a✔ Кровать успешно переименована в: &b«{name}»&a!"
'''

with open("tmp/towny-respawn/src/main/resources/config.yml", "w", encoding="utf-8") as f:
    f.write(config_yml)
print("Updated config.yml")

# 2. Update RespawnCommand.java
respawn_command_java = '''package com.towny.respawn.command;

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

        // Меню /respawn открывается только для админов для тестов!
        // Для обычных игроков меню открывается ТОЛЬКО при смерти игрока.
        if (plugin.getConfig().getBoolean("respawn.admin-only-command", true)) {
            if (!player.hasPermission("townyrespawn.admin") && !player.isOp()) {
                String adminMsg = ChatColor.translateAlternateColorCodes('&',
                        plugin.getConfig().getString("messages.command-admin-only",
                                "&cКоманда /respawn доступна только администраторам для тестирования. Меню выбора точки возрождения открывается автоматически при вашей смерти."));
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
'''

with open("tmp/towny-respawn/src/main/java/com/towny/respawn/command/RespawnCommand.java", "w", encoding="utf-8") as f:
    f.write(respawn_command_java)
print("Updated RespawnCommand.java")

# 3. Update GuiManager.java (short title "Выбор точки возрождения")
gui_manager_java = '''package com.towny.respawn.manager;

import com.palmergames.bukkit.towny.object.Nation;
import com.palmergames.bukkit.towny.object.Town;
import com.towny.respawn.TownyRespawnPlugin;
import com.towny.respawn.gui.RespawnMenuHolder;
import com.towny.respawn.model.PlayerBed;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class GuiManager {

    private final TownyRespawnPlugin plugin;

    public GuiManager(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    public void openRespawnGui(Player player) {
        openGui(player, RespawnMenuHolder.Mode.RESPAWN_SELECTION);
    }

    public void openDeathRespawnGui(Player player) {
        openGui(player, RespawnMenuHolder.Mode.DEATH_RESPAWN);
    }

    public void openGui(Player player, RespawnMenuHolder.Mode mode) {
        if (player == null) return;
        RespawnMenuHolder holder = new RespawnMenuHolder(mode, player);

        // Короткий заголовок меню, чтобы он гарантированно влезал в рамку интерфейса
        String titleRaw = plugin.getConfig().getString("messages.menu-title-respawn", "&8Выбор точки возрождения");
        if (mode == RespawnMenuHolder.Mode.DEATH_RESPAWN) {
            titleRaw = plugin.getConfig().getString("messages.menu-title-death", "&8Выбор точки возрождения");
        }

        String title = ChatColor.translateAlternateColorCodes('&', titleRaw);
        if (title.length() > 32) {
            title = title.substring(0, 32);
        }

        Inventory inv = Bukkit.createInventory(holder, 54, title);
        holder.setInventory(inv);

        renderGui(holder);
        player.openInventory(inv);
    }

    public void renderGui(RespawnMenuHolder holder) {
        Inventory inv = holder.getInventory();
        inv.clear();
        Player player = holder.getPlayer();

        plugin.getBedManager().cleanupDestroyedBeds(player);

        // 1. Fill background border with dark glass
        ItemStack border = createItem(Material.GRAY_STAINED_GLASS_PANE, " ");
        for (int i = 0; i < 54; i++) {
            if (i < 9 || i >= 45 || i % 9 == 0 || i % 9 == 8) {
                inv.setItem(i, border);
            }
        }

        // 2. Header banner info
        if (holder.getMode() == RespawnMenuHolder.Mode.DEATH_RESPAWN) {
            int delaySec = plugin.getConfig().getInt("respawn.delay-seconds", 30);
            inv.setItem(4, createItem(Material.COMPASS, "§c§lВЫБОР ТОЧКИ ВОЗРОЖДЕНИЯ",
                    "§7Выберите безопасное место для появления.",
                    "§e⏳ Задержка возрождения: §c" + delaySec + " §eсек.",
                    "§a▸ Без слепоты и замедления"));
        } else {
            inv.setItem(4, createItem(Material.COMPASS, "§b§lТОЧКИ ВОЗРОЖДЕНИЯ (ТЕСТОВЫЙ РЕЖИМ)",
                    "§7Администраторский просмотр точек появления.",
                    "§7ЛКМ: Выбрать для телепортации / привязки",
                    "§6▸ ПКМ по кровати: Переименовать её ✍"));
        }

        // 3. Display Player's Registered Beds (Automatically removes destroyed beds!)
        List<PlayerBed> beds = plugin.getBedManager().getBeds(player);
        List<PlayerBed> validBeds = new ArrayList<>();
        Iterator<PlayerBed> it = beds.iterator();
        while (it.hasNext()) {
            PlayerBed b = it.next();
            if (plugin.getBedManager().isBedPhysicallyValid(b)) {
                validBeds.add(b);
            } else {
                it.remove();
                plugin.getBedManager().removeBed(player, b);
            }
        }

        int[] bedSlots = {
                10, 11, 12, 13, 14, 15, 16,
                19, 20, 21, 22, 23, 24, 25
        };

        if (validBeds.isEmpty()) {
            inv.setItem(13, createItem(Material.BARRIER, "§7У вас нет активных кроватей",
                    "§8Разрушенные кровати удалены автоматически.",
                    "§8Поспите на любой кровати в безопасном месте,",
                    "§8чтобы зарегистрировать её как персональную точку!"));
        } else {
            for (int i = 0; i < validBeds.size() && i < bedSlots.length; i++) {
                PlayerBed bed = validBeds.get(i);
                List<String> lore = new ArrayList<>();
                lore.add("§8Порядковый номер: §f#" + (i + 1));
                lore.add("§7Мир: §e" + bed.getWorldName());
                lore.add("§7Координаты: §fX: " + bed.getHeadX() +
                        " Y: " + bed.getHeadY() +
                        " Z: " + bed.getHeadZ());
                lore.add("§a✔ Кровать цела и готова к использованию");
                lore.add(" ");
                lore.add("§e▸ ЛКМ: Возродиться на этой точке");
                lore.add("§6▸ ПКМ: Переименовать кровать ✍");

                inv.setItem(bedSlots[i], createItem(Material.RED_BED, "§b🛏 " + bed.getName(), lore));
            }
        }

        // 4. Secondary Action Row (Town, Nation, Vanilla, Server Spawn)
        if (plugin.getConfig().getBoolean("respawn.allow-town-spawn", true) && plugin.getTownyHook().isTownyAvailable()) {
            Town town = plugin.getTownyHook().getPlayerTown(player);
            if (town != null) {
                boolean underSiege = plugin.getTownySiegesHook().isTownUnderActiveSiege(town.getName());
                boolean blocked = underSiege && plugin.getConfig().getBoolean("respawn.block-spawn-if-under-siege", false);

                List<String> townLore = new ArrayList<>();
                townLore.add("§7Город: §6" + town.getName());
                townLore.add("§7Мэр: §e" + (town.getMayor() != null ? town.getMayor().getName() : "Неизвестно"));
                if (underSiege) {
                    townLore.add("§4⚔ ГОРОД ПОД АКТИВНЫМ ШТУРМОМ!");
                }
                if (blocked) {
                    townLore.add("§c✖ Спавн заблокирован осадным положением!");
                } else {
                    townLore.add("§a✔ Ратуша открыта для жителей");
                    townLore.add("§e▸ Нажмите ЛКМ для возрождения");
                }
                inv.setItem(28, createItem(blocked ? Material.COPPER_BLOCK : Material.GOLD_BLOCK,
                        "§6🏛 Спавн Города («" + town.getName() + "»)", townLore));
            } else {
                inv.setItem(28, createItem(Material.IRON_BARS, "§7Спавн города недоступен", "§8Вы не состоите ни в одном городе Towny"));
            }
        }

        if (plugin.getConfig().getBoolean("respawn.allow-nation-spawn", true) && plugin.getTownyHook().isTownyAvailable()) {
            Nation nation = plugin.getTownyHook().getPlayerNation(player);
            if (nation != null) {
                List<String> nationLore = new ArrayList<>();
                nationLore.add("§7Нация: §e" + nation.getName());
                if (nation.getCapital() != null) {
                    nationLore.add("§7Столица: §f" + nation.getCapital().getName());
                }
                nationLore.add("§a✔ Столица нации готова принять союзников");
                nationLore.add("§e▸ Нажмите ЛКМ для возрождения");
                inv.setItem(30, createItem(Material.EMERALD_BLOCK, "§e👑 Спавн Столицы Нации", nationLore));
            } else {
                inv.setItem(30, createItem(Material.IRON_BARS, "§7Спавн нации недоступен", "§8Ваш город не входит в состав нации"));
            }
        }

        // Vanilla Random Respawn Button
        if (plugin.getConfig().getBoolean("respawn.vanilla-respawn.enabled", true)) {
            List<String> vLore = new ArrayList<>();
            vLore.add("§7Случайное безопасное появление");
            vLore.add("§7в дикой природе мира (дистанция 200-1500 блоков).");
            vLore.add("§e▸ Нажмите для быстрого возрождения");
            inv.setItem(32, createItem(Material.COMPASS, "§a§l🌲 Ванильный респавн", vLore));
        }

        // Server World Spawn Button
        if (plugin.getConfig().getBoolean("respawn.server-spawn.enabled", true)) {
            List<String> sLore = new ArrayList<>();
            sLore.add("§7Центральный спавн сервера.");
            sLore.add("§7Безопасная охраняемая зона без PvP.");
            sLore.add("§e▸ Нажмите для возрождения");
            inv.setItem(34, createItem(Material.BEACON, "§6§l🏛 На спавн сервера", sLore));
        }

        // 5. Bottom Info & Controls
        inv.setItem(45, createItem(Material.BOOK, "§eℹ Справка по кроватям",
                "§7• 1 кровать = ровно 1 игрок (эксклюзивно)",
                "§7• Разрушенные кровати удаляются автоматически",
                "§7• Чтобы переименовать: нажмите §6ПКМ §7по кровати",
                "§7• Задержка на респавн: §c30 секунд"));

        if (holder.getMode() != RespawnMenuHolder.Mode.DEATH_RESPAWN) {
            inv.setItem(49, createItem(Material.BARRIER, "§cЗакрыть меню", "§7Нажмите для выхода из интерфейса"));
        }

        int maxBeds = plugin.getBedManager().getMaxBeds(player);
        inv.setItem(53, createItem(Material.PAPER, "§bВаш лимит кроватей",
                "§7Использовано: §e" + validBeds.size() + " §7из §a" + maxBeds,
                "§8(Дополнительные слоты выдаются правами)"));
    }

    private ItemStack createItem(Material mat, String name, String... loreLines) {
        List<String> lore = new ArrayList<>();
        if (loreLines != null) {
            for (String l : loreLines) {
                lore.add(l);
            }
        }
        return createItem(mat, name, lore);
    }

    private ItemStack createItem(Material mat, String name, List<String> lore) {
        ItemStack item = new ItemStack(mat);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(name);
            meta.setLore(lore);
            item.setItemMeta(meta);
        }
        return item;
    }
}
'''

with open("tmp/towny-respawn/src/main/java/com/towny/respawn/manager/GuiManager.java", "w", encoding="utf-8") as f:
    f.write(gui_manager_java)
print("Updated GuiManager.java")

# 4. Update RespawnManager.java (30s delay countdown, subtle quiet sound, no effects, no totem)
respawn_manager_java = '''package com.towny.respawn.manager;

import com.palmergames.bukkit.towny.object.Nation;
import com.palmergames.bukkit.towny.object.Town;
import com.towny.respawn.TownyRespawnPlugin;
import com.towny.respawn.model.PlayerBed;
import com.towny.respawn.model.RespawnPoint;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.scheduler.BukkitTask;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

public class RespawnManager {

    private final TownyRespawnPlugin plugin;
    private final Set<UUID> pendingRespawnPlayers = ConcurrentHashMap.newKeySet();
    private final Map<UUID, BukkitTask> activeCountdowns = new ConcurrentHashMap<>();

    public RespawnManager(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    public void addPendingRespawn(UUID uuid) {
        pendingRespawnPlayers.add(uuid);
    }

    public void markPendingRespawn(UUID uuid) {
        pendingRespawnPlayers.add(uuid);
    }

    public void removePendingRespawn(UUID uuid) {
        pendingRespawnPlayers.remove(uuid);
    }

    public void clearPendingRespawn(UUID uuid) {
        pendingRespawnPlayers.remove(uuid);
    }

    public boolean isPendingRespawn(UUID uuid) {
        return pendingRespawnPlayers.contains(uuid);
    }

    public void cancelCountdown(UUID uuid) {
        BukkitTask task = activeCountdowns.remove(uuid);
        if (task != null) {
            task.cancel();
        }
    }

    /**
     * Запускает 30-секундный таймер обратного отсчета перед появлением игрока на выбранной точке.
     */
    public void startRespawnCountdown(Player player, RespawnPoint point, int totalSeconds) {
        if (player == null || point == null) return;
        UUID uuid = player.getUniqueId();
        cancelCountdown(uuid);

        if (totalSeconds <= 0) {
            executeRespawn(player, point);
            return;
        }

        // Защита игрока во время ожидания респавна
        player.setInvulnerable(true);
        player.removePotionEffect(PotionEffectType.BLINDNESS);
        player.removePotionEffect(PotionEffectType.SLOW);

        BukkitTask task = Bukkit.getScheduler().runTaskTimer(plugin, new Runnable() {
            int remaining = totalSeconds;

            @Override
            public void run() {
                if (!player.isOnline()) {
                    cancelCountdown(uuid);
                    return;
                }

                if (remaining <= 0) {
                    cancelCountdown(uuid);
                    executeRespawn(player, point);
                    return;
                }

                // Отображение обратного отсчета в Action Bar и Title
                String actionbarMsg = ChatColor.translateAlternateColorCodes('&',
                        plugin.getConfig().getString("messages.countdown-actionbar",
                                "&e⏳ Возрождение на точке &b«{location}» &eчерез &c{seconds} &eсек..."))
                        .replace("{location}", point.getDisplayName())
                        .replace("{seconds}", String.valueOf(remaining));

                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, new TextComponent(actionbarMsg));
                } catch (Throwable ignored) {}

                // Мягкий Title
                String title = ChatColor.translateAlternateColorCodes('&',
                        plugin.getConfig().getString("messages.countdown-title", "&eВозрождение"));
                String subtitle = ChatColor.translateAlternateColorCodes('&',
                        plugin.getConfig().getString("messages.countdown-subtitle", "&7До появления: &c{seconds} &7сек..."))
                        .replace("{seconds}", String.valueOf(remaining));

                player.sendTitle(title, subtitle, 0, 25, 5);

                // Едва слышный клик таймера игроку
                if (remaining <= 5 || remaining % 10 == 0) {
                    player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.3f, 1.5f);
                }

                remaining--;
            }
        }, 0L, 20L); // Каждую секунду (20 тиков)

        activeCountdowns.put(uuid, task);
    }

    /**
     * Окончательное возрождение:
     * - БЕЗ ВСЕХ ЭФФЕКТОВ (слепота, замедление, сопротивление удалены)
     * - БЕЗ ТОТЕМА (никаких звуков тотема и частиц тотема)
     * - НЕГРОМКИЙ ЗВУК для оповещения окружающих игроков в мире
     */
    public void executeRespawn(Player player, RespawnPoint point) {
        if (player == null || point == null) return;
        UUID uuid = player.getUniqueId();
        cancelCountdown(uuid);
        clearPendingRespawn(uuid);

        Location target = point.getTargetLocation();
        if (target == null) {
            target = getServerSpawnLocation(player);
        }

        // Очищаем абсолютно все эффекты
        player.removePotionEffect(PotionEffectType.BLINDNESS);
        player.removePotionEffect(PotionEffectType.SLOW);
        player.removePotionEffect(PotionEffectType.DAMAGE_RESISTANCE);
        player.removePotionEffect(PotionEffectType.FIRE_RESISTANCE);
        player.removePotionEffect(PotionEffectType.REGENERATION);

        // Снимаем временную неуязвимость
        player.setInvulnerable(false);

        // Телепортируем на целевую точку
        player.teleport(target);

        // НЕГРОМКИЙ ЗВУК В МИРЕ ДЛЯ ОПОВЕЩЕНИЯ ДРУГИХ ИГРОКОВ (в радиусе точки появления)
        if (plugin.getConfig().getBoolean("respawn.sound.enabled", true) && target.getWorld() != null) {
            String soundName = plugin.getConfig().getString("respawn.sound.name", "BLOCK_BEACON_ACTIVATE");
            float volume = (float) plugin.getConfig().getDouble("respawn.sound.volume", 0.5);
            float pitch = (float) plugin.getConfig().getDouble("respawn.sound.pitch", 1.4);
            try {
                Sound sound = Sound.valueOf(soundName);
                target.getWorld().playSound(target, sound, SoundCategory.BLOCKS, volume, pitch);
            } catch (Throwable ignored) {
                target.getWorld().playSound(target, Sound.BLOCK_BEACON_ACTIVATE, SoundCategory.BLOCKS, 0.5f, 1.4f);
            }
        }

        // Сообщение игроку
        String prefix = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.prefix", "&b&l[TownyRespawn]&r "));
        String msg = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.respawn-selected", "&aВы успешно возродились: &f{location}&a!"))
                .replace("{location}", point.getDisplayName());
        player.sendMessage(prefix + msg);

        // Снимаем Title
        player.sendTitle("§a✔ Возрождение", "§f" + point.getDisplayName(), 5, 20, 10);
    }

    public Location getServerSpawnLocation(Player player) {
        World world = player != null ? player.getWorld() : Bukkit.getWorlds().get(0);
        if (plugin.getConfig().getBoolean("respawn.server-spawn.custom-coords.enabled", false)) {
            String wName = plugin.getConfig().getString("respawn.server-spawn.custom-coords.world", world.getName());
            World w = Bukkit.getWorld(wName);
            if (w != null) {
                double x = plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.x", 0.5);
                double y = plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.y", 70.0);
                double z = plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.z", 0.5);
                float yaw = (float) plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.yaw", 0.0);
                float pitch = (float) plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.pitch", 0.0);
                return new Location(w, x, y, z, yaw, pitch);
            }
        }
        return world.getSpawnLocation().add(0.5, 0.1, 0.5);
    }

    public Location findSafeVanillaWildSpawn(Player player) {
        World world = player != null ? player.getWorld() : Bukkit.getWorlds().get(0);
        int min = plugin.getConfig().getInt("respawn.vanilla-respawn.wild-radius-min", 200);
        int max = plugin.getConfig().getInt("respawn.vanilla-respawn.wild-radius-max", 1500);
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        int angle = rnd.nextInt(360);
        int dist = min + rnd.nextInt(Math.max(1, max - min));
        int x = (int) (Math.cos(Math.toRadians(angle)) * dist);
        int z = (int) (Math.sin(Math.toRadians(angle)) * dist);
        int y = world.getHighestBlockYAt(x, z);
        if (y < world.getMinHeight() + 5) y = 70;
        return new Location(world, x + 0.5, y + 1.0, z + 0.5);
    }
}
'''

with open("tmp/towny-respawn/src/main/java/com/towny/respawn/manager/RespawnManager.java", "w", encoding="utf-8") as f:
    f.write(respawn_manager_java)
print("Updated RespawnManager.java")

# 5. Update GuiListener.java
gui_listener_java = '''package com.towny.respawn.listener;

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
import org.bukkit.inventory.ItemStack;

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

        ItemStack clicked = event.getCurrentItem();
        if (clicked == null || clicked.getType().isAir()) {
            return;
        }

        // Close button (slot 49)
        if (slot == 49 && holder.getMode() != RespawnMenuHolder.Mode.DEATH_RESPAWN) {
            player.closeInventory();
            return;
        }

        // Bed Slots: 10..16, 19..25
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
                    player.closeInventory();
                    triggerRespawn(player, holder, point);
                }
                return;
            }
        }

        // Town Spawn Click (slot 28)
        if (slot == 28) {
            if (plugin.getTownyHook().isTownyAvailable()) {
                var town = plugin.getTownyHook().getPlayerTown(player);
                if (town != null) {
                    boolean underSiege = plugin.getTownySiegesHook().isTownUnderActiveSiege(town.getName());
                    boolean blocked = underSiege && plugin.getConfig().getBoolean("respawn.block-spawn-if-under-siege", false);
                    if (blocked) {
                        player.sendMessage(ChatColor.RED + "Возрождение в городе заблокировано осадным положением!");
                        player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
                        return;
                    }

                    var tLoc = plugin.getTownyHook().getTownSpawn(town);
                    if (tLoc != null) {
                        RespawnPoint point = new RespawnPoint(RespawnPoint.Type.TOWN_SPAWN, "town_spawn", "§6Спавн города «" + town.getName() + "»", null, null, tLoc, true, null);
                        player.closeInventory();
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
                var nation = plugin.getTownyHook().getPlayerNation(player);
                if (nation != null) {
                    var nLoc = plugin.getTownyHook().getNationSpawn(nation);
                    if (nLoc != null) {
                        RespawnPoint point = new RespawnPoint(RespawnPoint.Type.NATION_SPAWN, "nation_spawn", "§eСпавн столицы «" + nation.getName() + "»", null, null, nLoc, true, null);
                        player.closeInventory();
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
            player.closeInventory();
            triggerRespawn(player, holder, point);
            return;
        }

        // Server Spawn Click (slot 34)
        if (slot == 34) {
            var sLoc = plugin.getRespawnManager().getServerSpawnLocation(player);
            RespawnPoint point = new RespawnPoint(RespawnPoint.Type.SERVER_SPAWN, "server_spawn", "§6Спавн сервера", null, null, sLoc, true, null);
            player.closeInventory();
            triggerRespawn(player, holder, point);
            return;
        }
    }

    private void triggerRespawn(Player player, RespawnMenuHolder holder, RespawnPoint point) {
        boolean isTestAdmin = (holder.getMode() == RespawnMenuHolder.Mode.RESPAWN_SELECTION)
                && (player.hasPermission("townyrespawn.admin") || player.isOp());

        int delay = plugin.getConfig().getInt("respawn.delay-seconds", 30);
        if (isTestAdmin || delay <= 0) {
            plugin.getRespawnManager().executeRespawn(player, point);
        } else {
            plugin.getRespawnManager().startRespawnCountdown(player, point, delay);
        }
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

        // If player is in DEATH_RESPAWN and closed without picking, force server spawn with countdown
        if (holder.getMode() == RespawnMenuHolder.Mode.DEATH_RESPAWN && plugin.getRespawnManager().isPendingRespawn(player.getUniqueId())) {
            if (plugin.getBedManager().isAwaitingRename(player.getUniqueId())) {
                return;
            }

            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                if (player.isOnline() && plugin.getRespawnManager().isPendingRespawn(player.getUniqueId())) {
                    var sLoc = plugin.getRespawnManager().getServerSpawnLocation(player);
                    RespawnPoint point = new RespawnPoint(RespawnPoint.Type.SERVER_SPAWN, "fallback_spawn", "§6Спавн сервера", null, null, sLoc, true, null);
                    int delay = plugin.getConfig().getInt("respawn.delay-seconds", 30);
                    plugin.getRespawnManager().startRespawnCountdown(player, point, delay);
                }
            }, 10L);
        }
    }
}
'''

with open("tmp/towny-respawn/src/main/java/com/towny/respawn/listener/GuiListener.java", "w", encoding="utf-8") as f:
    f.write(gui_listener_java)
print("Updated GuiListener.java")

# 6. Update DeathRespawnListener.java (cleanup on quit)
death_listener_java = '''package com.towny.respawn.listener;

import com.towny.respawn.TownyRespawnPlugin;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.player.PlayerRespawnEvent;

public class DeathRespawnListener implements Listener {

    private final TownyRespawnPlugin plugin;

    public DeathRespawnListener(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerDeath(PlayerDeathEvent event) {
        Player player = event.getEntity();
        plugin.getRespawnManager().markPendingRespawn(player.getUniqueId());
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerRespawn(PlayerRespawnEvent event) {
        Player player = event.getPlayer();
        plugin.getRespawnManager().markPendingRespawn(player.getUniqueId());

        long delay = plugin.getConfig().getLong("respawn.gui-open-delay-ticks", 1L);
        Bukkit.getScheduler().runTaskLater(plugin, () -> {
            if (player.isOnline() && plugin.getRespawnManager().isPendingRespawn(player.getUniqueId())) {
                player.setInvulnerable(true);
                // Открывает меню выбора точек возрождения автоматически при смерти
                plugin.getGuiManager().openDeathRespawnGui(player);
            }
        }, delay);
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        plugin.getRespawnManager().cancelCountdown(event.getPlayer().getUniqueId());
        plugin.getRespawnManager().clearPendingRespawn(event.getPlayer().getUniqueId());
    }
}
'''

with open("tmp/towny-respawn/src/main/java/com/towny/respawn/listener/DeathRespawnListener.java", "w", encoding="utf-8") as f:
    f.write(death_listener_java)
print("Updated DeathRespawnListener.java")

print("All TownyRespawn sources updated!")
