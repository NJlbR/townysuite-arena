package com.towny.respawn.manager;

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

    public void updateCooldownHeader(Player player) {
        if (player == null || !player.isOnline()) return;
        if (player.getOpenInventory() != null && player.getOpenInventory().getTopInventory() != null) {
            if (player.getOpenInventory().getTopInventory().getHolder() instanceof RespawnMenuHolder) {
                RespawnMenuHolder holder = (RespawnMenuHolder) player.getOpenInventory().getTopInventory().getHolder();
                if (holder.getMode() == RespawnMenuHolder.Mode.DEATH_RESPAWN) {
                    long remainingCd = plugin.getRespawnManager().getRemainingCooldownSeconds(player.getUniqueId());
                    Inventory inv = player.getOpenInventory().getTopInventory();
                    if (remainingCd > 0) {
                        inv.setItem(4, createItem(Material.CLOCK, "§c§l⏳ КД НА ВОЗРОЖДЕНИЕ: " + remainingCd + " СЕК.",
                                "§7По правилам сервера между возрождениями",
                                "§7должно пройти не менее 30 секунд.",
                                "§c▸ До возможности выбора: §e" + remainingCd + " §cсек.",
                                "§8(Вы скрыты от всех игроков в мире пока в меню)"));
                    } else {
                        inv.setItem(4, createItem(Material.COMPASS, "§a§l✔ ВОЗРОЖДЕНИЕ ДОСТУПНО",
                                "§7Выберите любую доступную точку появления ниже.",
                                "§a▸ Нажмите ЛКМ для мгновенного возрождения",
                                "§8(После выбора вы сразу появитесь на точке)"));
                    }
                }
            }
        }
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

        // 2. Header banner info with Cooldown display
        if (holder.getMode() == RespawnMenuHolder.Mode.DEATH_RESPAWN) {
            long remainingCd = plugin.getRespawnManager().getRemainingCooldownSeconds(player.getUniqueId());
            if (remainingCd > 0) {
                inv.setItem(4, createItem(Material.CLOCK, "§c§l⏳ КД НА ВОЗРОЖДЕНИЕ: " + remainingCd + " СЕК.",
                        "§7По правилам сервера между возрождениями",
                        "§7должно пройти не менее 30 секунд.",
                        "§c▸ До возможности выбора: §e" + remainingCd + " §cсек.",
                        "§8(Вы скрыты от всех игроков в мире пока в меню)"));
            } else {
                inv.setItem(4, createItem(Material.COMPASS, "§a§l✔ ВОЗРОЖДЕНИЕ ДОСТУПНО",
                        "§7Выберите любую доступную точку появления ниже.",
                        "§a▸ Нажмите ЛКМ для мгновенного возрождения",
                        "§8(После выбора вы сразу появитесь на точке)"));
            }
        } else {
            inv.setItem(4, createItem(Material.COMPASS, "§b§lТОЧКИ ВОЗРОЖДЕНИЯ (ТЕСТОВЫЙ РЕЖИМ)",
                    "§7Администраторский просмотр точек появления.",
                    "§7ЛКМ: Выбрать для телепортации / привязки",
                    "§6▸ ПКМ по кровати: Переименовать её ✍"));
        }

        // 3. Display Player's Registered Beds
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
        boolean allowTown = plugin.getConfig().getBoolean("respawn.allow-town-spawn", plugin.getConfig().getBoolean("limbo.allow-town-spawn", true));
        if (allowTown && plugin.getTownyHook().isTownyAvailable()) {
            String townName = plugin.getTownyHook().getPlayerTownName(player);
            if (townName != null) {
                boolean underSiege = plugin.getTownySiegesHook().isTownUnderActiveSiege(townName);
                boolean blocked = underSiege && (plugin.getConfig().getBoolean("respawn.block-spawn-if-under-siege", false) || plugin.getConfig().getBoolean("limbo.block-spawn-if-under-siege", false));

                List<String> townLore = new ArrayList<>();
                townLore.add("§7Город: §6" + townName);
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
                        "§6🏛 Спавн Города («" + townName + "»)", townLore));
            } else {
                inv.setItem(28, createItem(Material.IRON_BARS, "§7Спавн города недоступен", "§8Вы не состоите ни в одном городе Towny"));
            }
        }

        boolean allowNation = plugin.getConfig().getBoolean("respawn.allow-nation-spawn", plugin.getConfig().getBoolean("limbo.allow-nation-spawn", true));
        if (allowNation && plugin.getTownyHook().isTownyAvailable()) {
            String nationName = plugin.getTownyHook().getPlayerNationName(player);
            if (nationName != null) {
                List<String> nationLore = new ArrayList<>();
                nationLore.add("§7Нация: §e" + nationName);
                nationLore.add("§a✔ Доступно для граждан нации");
                nationLore.add("§e▸ Нажмите ЛКМ для возрождения");
                inv.setItem(30, createItem(Material.EMERALD_BLOCK,
                        "§e👑 Спавн Нации («" + nationName + "»)", nationLore));
            } else {
                inv.setItem(30, createItem(Material.IRON_BARS, "§7Спавн нации недоступен", "§8Ваш город не состоит в нации"));
            }
        }

        if (plugin.getConfig().getBoolean("respawn.vanilla-respawn.enabled", true)) {
            String label = ChatColor.translateAlternateColorCodes('&',
                    plugin.getConfig().getString("respawn.vanilla-respawn.label", "&a&l🌲 Ванильный респавн"));
            List<String> rawDesc = plugin.getConfig().getStringList("respawn.vanilla-respawn.description");
            List<String> desc = new ArrayList<>();
            for (String s : rawDesc) desc.add(ChatColor.translateAlternateColorCodes('&', s));
            inv.setItem(32, createItem(Material.OAK_SAPLING, label, desc));
        }

        if (plugin.getConfig().getBoolean("respawn.server-spawn.enabled", true)) {
            String label = ChatColor.translateAlternateColorCodes('&',
                    plugin.getConfig().getString("respawn.server-spawn.label", "&6&l🏛 На спавн сервера"));
            List<String> rawDesc = plugin.getConfig().getStringList("respawn.server-spawn.description");
            List<String> desc = new ArrayList<>();
            for (String s : rawDesc) desc.add(ChatColor.translateAlternateColorCodes('&', s));
            inv.setItem(34, createItem(Material.BEACON, label, desc));
        }

        // Close / Help button
        inv.setItem(49, createItem(Material.BARRIER, "§cЗакрыть меню"));
    }

    private ItemStack createItem(Material mat, String name, String... loreLines) {
        List<String> list = new ArrayList<>();
        if (loreLines != null) {
            for (String s : loreLines) {
                list.add(ChatColor.translateAlternateColorCodes('&', s));
            }
        }
        return createItem(mat, name, list);
    }

    private ItemStack createItem(Material mat, String name, List<String> lore) {
        ItemStack item = new ItemStack(mat);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.translateAlternateColorCodes('&', name));
            if (lore != null && !lore.isEmpty()) {
                meta.setLore(lore);
            }
            item.setItemMeta(meta);
        }
        return item;
    }
}
