package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import org.bukkit.*;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryCloseEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemFlag;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;

import java.util.*;

public class ForgeManager implements Listener {

    private final TownyArchitecturePlugin plugin;
    private final NamespacedKey superPickaxeKey;
    private final NamespacedKey capturedSpawnerKey;

    public ForgeManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
        this.superPickaxeKey = new NamespacedKey(plugin, "super_pickaxe");
        this.capturedSpawnerKey = new NamespacedKey(plugin, "spawner_mob_type");
    }

    public void openForgeHub(Player player) {
        Inventory inv = Bukkit.createInventory(null, 27, ChatColor.DARK_RED + "" + ChatColor.BOLD + "⚒ Городская Кузница");

        ItemStack grayGlass = createGlassPane(Material.GRAY_STAINED_GLASS_PANE, " ");
        for (int i = 0; i < 27; i++) {
            inv.setItem(i, grayGlass);
        }

        // Option 1: Virtual Anvil
        ItemStack anvilBtn = new ItemStack(Material.ANVIL);
        ItemMeta anvilMeta = anvilBtn.getItemMeta();
        if (anvilMeta != null) {
            anvilMeta.setDisplayName(ChatColor.GOLD + "" + ChatColor.BOLD + "1. Виртуальная Наковальня");
            anvilMeta.setLore(Arrays.asList(
                    ChatColor.GRAY + "Полнофункциональная виртуальная копия наковальни.",
                    ChatColor.YELLOW + "Ремонтируйте предметы, переименовывайте и объединяйте",
                    ChatColor.YELLOW + "зачарования без необходимости ставить блок наковальни!",
                    "",
                    ChatColor.GREEN + "» Нажмите, чтобы открыть Наковальню!"
            ));
            anvilBtn.setItemMeta(anvilMeta);
        }
        inv.setItem(11, anvilBtn);

        // Option 2: Super Anvil
        ItemStack superAnvilBtn = new ItemStack(Material.SMITHING_TABLE);
        ItemMeta superMeta = superAnvilBtn.getItemMeta();
        if (superMeta != null) {
            superMeta.setDisplayName(ChatColor.LIGHT_PURPLE + "" + ChatColor.BOLD + "2. Супер-Наковальня (Супер-Кирка)");
            superMeta.setLore(Arrays.asList(
                    ChatColor.GRAY + "Специальный горн для создания легендарного инструмента.",
                    ChatColor.LIGHT_PURPLE + "Объедините 2 Незеритовые Кирки любой прочности,",
                    ChatColor.LIGHT_PURPLE + "чтобы ковать ⚡ Супер-Кирку [Добыча Спавнера]!",
                    "",
                    ChatColor.GOLD + "✦ Особое свойство Супер-Кирки:",
                    ChatColor.YELLOW + "• Позволяет 1 раз сломать спавнер мобов.",
                    ChatColor.YELLOW + "• Спавнер выпадет в инвентарь с сохраненным мобом!",
                    "",
                    ChatColor.GREEN + "» Нажмите, чтобы открыть Супер-Наковальню!"
            ));
            superAnvilBtn.setItemMeta(superMeta);
        }
        inv.setItem(15, superAnvilBtn);

        // Info item
        ItemStack infoBtn = new ItemStack(Material.BOOK);
        ItemMeta infoMeta = infoBtn.getItemMeta();
        if (infoMeta != null) {
            infoMeta.setDisplayName(ChatColor.AQUA + "" + ChatColor.BOLD + "ℹ Информация о Кузнице");
            infoMeta.setLore(Arrays.asList(
                    ChatColor.GRAY + "Вы находитесь на территории активной Городской Кузницы.",
                    ChatColor.WHITE + " • Доступ к командам: " + ChatColor.YELLOW + "/build forge",
                    ChatColor.WHITE + " • Виртуальная наковальня: " + ChatColor.GREEN + "Доступна 24/7",
                    ChatColor.WHITE + " • Ковка Супер-Кирок: " + ChatColor.LIGHT_PURPLE + "Доступна"
            ));
            infoBtn.setItemMeta(infoMeta);
        }
        inv.setItem(13, infoBtn);

        // Close button
        ItemStack closeBtn = new ItemStack(Material.BARRIER);
        ItemMeta closeMeta = closeBtn.getItemMeta();
        if (closeMeta != null) {
            closeMeta.setDisplayName(ChatColor.RED + "Закрыть");
            closeBtn.setItemMeta(closeMeta);
        }
        inv.setItem(22, closeBtn);

        player.openInventory(inv);
        player.playSound(player.getLocation(), Sound.BLOCK_ANVIL_USE, 0.7f, 1.2f);
    }

    public void openSuperAnvil(Player player) {
        SuperAnvilHolder holder = new SuperAnvilHolder();
        Inventory inv = Bukkit.createInventory(holder, 27, ChatColor.DARK_RED + "" + ChatColor.BOLD + "⚒ Супер-Наковальня");
        holder.setInventory(inv);

        ItemStack grayGlass = createGlassPane(Material.GRAY_STAINED_GLASS_PANE, " ");

        for (int i = 0; i < 27; i++) {
            inv.setItem(i, grayGlass);
        }

        // Input slots 11 and 15 empty
        inv.setItem(11, null);
        inv.setItem(15, null);

        // Result / Craft button at slot 13
        ItemStack craftBtn = new ItemStack(Material.ANVIL);
        ItemMeta craftMeta = craftBtn.getItemMeta();
        if (craftMeta != null) {
            craftMeta.setDisplayName(ChatColor.LIGHT_PURPLE + "" + ChatColor.BOLD + "⚡ Сковать Супер-Кирку");
            craftMeta.setLore(Arrays.asList(
                    ChatColor.GRAY + "Поместите 2 Незеритовые Кирки в левый и правый слоты.",
                    ChatColor.GRAY + "Прочность и зачарования кирки могут быть любыми.",
                    "",
                    ChatColor.GOLD + "Результат: " + ChatColor.LIGHT_PURPLE + "⚡ Супер-Кирка (1 использование)",
                    ChatColor.YELLOW + "Добывает 1 спавнер с сохранением яйца моба!",
                    "",
                    ChatColor.GREEN + "» Нажмите, чтобы объединить кирки!"
            ));
            craftBtn.setItemMeta(craftMeta);
        }
        inv.setItem(13, craftBtn);

        // Guidance arrows
        ItemStack arrow = createGlassPane(Material.LIGHT_BLUE_STAINED_GLASS_PANE, ChatColor.AQUA + "➔ Поместите Незеритовые Кирки ➔");
        inv.setItem(10, arrow);
        inv.setItem(12, arrow);
        inv.setItem(14, arrow);
        inv.setItem(16, arrow);

        // Info card at slot 22
        ItemStack infoCard = new ItemStack(Material.KNOWLEDGE_BOOK);
        ItemMeta infoMeta = infoCard.getItemMeta();
        if (infoMeta != null) {
            infoMeta.setDisplayName(ChatColor.YELLOW + "Рецепт Кузницы:");
            infoMeta.setLore(Arrays.asList(
                    ChatColor.WHITE + " • Ингредиент 1: " + ChatColor.DARK_PURPLE + "1 Незеритовая кирка",
                    ChatColor.WHITE + " • Ингредиент 2: " + ChatColor.DARK_PURPLE + "1 Незеритовая кирка",
                    ChatColor.GRAY + " (Кирки расходуются безвозвратно)",
                    "",
                    ChatColor.GOLD + "✦ Входные кирки возвращаются в инвентарь при закрытии меню!"
            ));
            infoCard.setItemMeta(infoMeta);
        }
        inv.setItem(22, infoCard);

        // Back button at slot 26
        ItemStack backBtn = new ItemStack(Material.SPECTRAL_ARROW);
        ItemMeta backMeta = backBtn.getItemMeta();
        if (backMeta != null) {
            backMeta.setDisplayName(ChatColor.YELLOW + "« Назад в Кузницу");
            backBtn.setItemMeta(backMeta);
        }
        inv.setItem(26, backBtn);

        player.openInventory(inv);
        player.playSound(player.getLocation(), Sound.BLOCK_SMITHING_TABLE_USE, 1.0f, 1.0f);
    }

    @EventHandler
    public void onInventoryClick(InventoryClickEvent event) {
        String title = event.getView().getTitle();
        if (!(event.getWhoClicked() instanceof Player player)) return;

        if (title.contains("Городская Кузница")) {
            event.setCancelled(true);
            int slot = event.getRawSlot();
            if (slot == 11) {
                player.closeInventory();
                player.openAnvil(player.getLocation(), true);
                player.playSound(player.getLocation(), Sound.BLOCK_ANVIL_USE, 0.8f, 1.2f);
            } else if (slot == 15) {
                openSuperAnvil(player);
            } else if (slot == 22) {
                player.closeInventory();
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.5f, 1.0f);
            }
            return;
        }

        if (event.getInventory().getHolder() instanceof SuperAnvilHolder holder) {
            int rawSlot = event.getRawSlot();
            int topSize = event.getInventory().getSize();

            if (rawSlot >= 0 && rawSlot < topSize) {
                if (rawSlot == 11 || rawSlot == 15) {
                    event.setCancelled(false);
                    return;
                }
                event.setCancelled(true);

                if (rawSlot == 13) {
                    handleSuperAnvilCraft(player, event.getInventory());
                } else if (rawSlot == 26) {
                    openForgeHub(player);
                }
            }
        }
    }

    @EventHandler
    public void onInventoryClose(InventoryCloseEvent event) {
        if (event.getInventory().getHolder() instanceof SuperAnvilHolder holder) {
            if (event.getPlayer() instanceof Player player) {
                Inventory inv = event.getInventory();
                ItemStack item1 = inv.getItem(11);
                ItemStack item2 = inv.getItem(15);
                inv.setItem(11, null);
                inv.setItem(15, null);

                if (item1 != null && item1.getType() != Material.AIR) {
                    HashMap<Integer, ItemStack> leftover = player.getInventory().addItem(item1);
                    for (ItemStack lo : leftover.values()) {
                        player.getWorld().dropItemNaturally(player.getLocation(), lo);
                    }
                }
                if (item2 != null && item2.getType() != Material.AIR) {
                    HashMap<Integer, ItemStack> leftover = player.getInventory().addItem(item2);
                    for (ItemStack lo : leftover.values()) {
                        player.getWorld().dropItemNaturally(player.getLocation(), lo);
                    }
                }
            }
        }
    }

    private void handleSuperAnvilCraft(Player player, Inventory inv) {
        ItemStack item1 = inv.getItem(11);
        ItemStack item2 = inv.getItem(15);

        if (item1 == null || item2 == null ||
            item1.getType() != Material.NETHERITE_PICKAXE ||
            item2.getType() != Material.NETHERITE_PICKAXE) {

            player.sendMessage(ChatColor.RED + "❌ Для ковки требуются ДВЕ Незеритовые Кирки (по одной в каждом слоте)!");
            player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
            return;
        }

        inv.setItem(11, null);
        inv.setItem(15, null);

        ItemStack superPick = createSuperPickaxe();
        HashMap<Integer, ItemStack> leftover = player.getInventory().addItem(superPick);
        for (ItemStack lo : leftover.values()) {
            player.getWorld().dropItemNaturally(player.getLocation(), lo);
        }

        player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");
        player.sendMessage(ChatColor.GOLD + "⚡ [Кузница] Вы успешно объединили 2 Незеритовые кирки!");
        player.sendMessage(ChatColor.LIGHT_PURPLE + "⚡ Скована «Супер-Кирка» для добычи Спавнера мобов!");
        player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");

        player.playSound(player.getLocation(), Sound.BLOCK_ANVIL_USE, 1.0f, 0.8f);
        player.playSound(player.getLocation(), Sound.ITEM_TOTEM_USE, 0.8f, 1.2f);
        player.getWorld().spawnParticle(Particle.FIREWORKS_SPARK, player.getLocation().add(0, 1, 0), 40, 0.5, 0.5, 0.5, 0.1);
    }

    public ItemStack createSuperPickaxe() {
        ItemStack item = new ItemStack(Material.NETHERITE_PICKAXE, 1);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.LIGHT_PURPLE + "" + ChatColor.BOLD + "⚡ Супер-Кирка [Добыча Спавнера]");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Легендарное орудие, выкованное в Городской Кузнице.");
            lore.add(ChatColor.GOLD + "✦ Особое свойство: Позволяет 1 раз сломать спавнер мобов.");
            lore.add(ChatColor.YELLOW + "✦ Выпавший спавнер сохраняет яйцо и тип вложенного моба.");
            lore.add(ChatColor.RED + "✦ Кирка полностью разрушается после 1 использования.");
            meta.setLore(lore);

            meta.setCustomModelData(7005);
            meta.getPersistentDataContainer().set(superPickaxeKey, PersistentDataType.STRING, "true");
            meta.addEnchant(Enchantment.DURABILITY, 1, true);
            meta.addItemFlags(ItemFlag.HIDE_ENCHANTS, ItemFlag.HIDE_ATTRIBUTES);
            item.setItemMeta(meta);
        }
        return item;
    }

    public boolean isSuperPickaxe(ItemStack item) {
        if (item == null || !item.hasItemMeta()) return false;
        ItemMeta meta = item.getItemMeta();
        if (meta.getPersistentDataContainer().has(superPickaxeKey, PersistentDataType.STRING)) {
            return true;
        }
        if (meta.hasDisplayName() && meta.getDisplayName().contains("Супер-Кирка")) {
            return true;
        }
        return meta.hasCustomModelData() && meta.getCustomModelData() == 7005;
    }

    public ItemStack createCapturedSpawnerItem(EntityType mobType) {
        ItemStack item = new ItemStack(Material.SPAWNER, 1);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            String mobNameRu = getRussianEntityName(mobType);
            meta.setDisplayName(ChatColor.GOLD + "" + ChatColor.BOLD + "📦 Спавнер Мобов [" + mobNameRu + "]");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Добыт с помощью Супер-Кирки.");
            lore.add(ChatColor.YELLOW + "• Содержит яйцо моба: " + ChatColor.LIGHT_PURPLE + mobNameRu);
            lore.add(ChatColor.GREEN + "• Разместите блок в любом месте для работы спавнера!");
            meta.setLore(lore);

            meta.getPersistentDataContainer().set(capturedSpawnerKey, PersistentDataType.STRING, mobType.name());
            item.setItemMeta(meta);
        }
        return item;
    }

    public boolean isCapturedSpawner(ItemStack item) {
        if (item == null || item.getType() != Material.SPAWNER || !item.hasItemMeta()) return false;
        return item.getItemMeta().getPersistentDataContainer().has(capturedSpawnerKey, PersistentDataType.STRING);
    }

    public EntityType getCapturedSpawnerType(ItemStack item) {
        if (!isCapturedSpawner(item)) return EntityType.PIG;
        try {
            String name = item.getItemMeta().getPersistentDataContainer().get(capturedSpawnerKey, PersistentDataType.STRING);
            return EntityType.valueOf(name);
        } catch (Throwable t) {
            return EntityType.PIG;
        }
    }

    public static String getRussianEntityName(EntityType type) {
        if (type == null) return "Свинья";
        switch (type) {
            case ZOMBIE: return "Зомби";
            case SKELETON: return "Скелет";
            case SPIDER: return "Паук";
            case CAVE_SPIDER: return "Пещерный паук";
            case CREEPER: return "Крипер";
            case BLAZE: return "Ифрит";
            case ENDERMAN: return "Эндермен";
            case WITHER_SKELETON: return "Визер-скелет";
            case PIG: return "Свинья";
            case COW: return "Корова";
            case SHEEP: return "Овца";
            case CHICKEN: return "Курица";
            case ZOMBIFIED_PIGLIN: return "Зомби-пиглин";
            case MAGMA_CUBE: return "Магмовый куб";
            case SLIME: return "Слизень";
            case WITCH: return "Ведьма";
            case DROWNED: return "Утопленник";
            case PHANTOM: return "Фантом";
            case PILLAGER: return "Разбойник";
            case VINDICATOR: return "Поборник";
            case EVOKER: return "Вызыватель";
            case GUARDIAN: return "Страж";
            case ELDER_GUARDIAN: return "Древний страж";
            case SILVERFISH: return "Чешуйница";
            default:
                String raw = type.name().toLowerCase().replace('_', ' ');
                return Character.toUpperCase(raw.charAt(0)) + raw.substring(1);
        }
    }

    private ItemStack createGlassPane(Material mat, String name) {
        ItemStack item = new ItemStack(mat);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(name);
            item.setItemMeta(meta);
        }
        return item;
    }

    public static class SuperAnvilHolder implements org.bukkit.inventory.InventoryHolder {
        private Inventory inventory;
        public void setInventory(Inventory inventory) { this.inventory = inventory; }
        @Override public Inventory getInventory() { return inventory; }
    }
}
