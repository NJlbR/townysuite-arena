package com.towny.sieges.gui;

import com.towny.sieges.TownySiegesPlugin;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemFlag;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

import java.util.*;

public class SiegeMenuGui implements Listener {

    private final TownySiegesPlugin plugin;

    public SiegeMenuGui(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    public void openMainMenu(Player player) {
        SiegeMenuHolder holder = new SiegeMenuHolder(SiegeMenuHolder.Type.MAIN);
        String title = ChatColor.GOLD + "" + ChatColor.BOLD + "TownySieges " + ChatColor.DARK_GRAY + "» " + ChatColor.DARK_RED + "Осады и Крафты";
        Inventory inv = Bukkit.createInventory(holder, 54, title);
        holder.setInventory(inv);

        try {
            player.discoverRecipe(new NamespacedKey(plugin, "siege_mortar"));
            player.discoverRecipe(new NamespacedKey(plugin, "siege_cannonball_regular"));
            player.discoverRecipe(new NamespacedKey(plugin, "siege_cannonball_ap"));
            player.discoverRecipe(new NamespacedKey(plugin, "siege_assault_banner_recipe"));
        } catch (Throwable ignored) {}

        // Background frame
        ItemStack grayGlass = createGlassPane(Material.GRAY_STAINED_GLASS_PANE, " ");
        ItemStack redGlass = createGlassPane(Material.RED_STAINED_GLASS_PANE, " ");
        ItemStack orangeGlass = createGlassPane(Material.ORANGE_STAINED_GLASS_PANE, " ");

        for (int i = 0; i < 54; i++) {
            if (i < 9 || i >= 45 || i % 9 == 0 || i % 9 == 8) {
                inv.setItem(i, grayGlass);
            }
        }
        inv.setItem(0, redGlass);
        inv.setItem(8, redGlass);
        inv.setItem(45, redGlass);
        inv.setItem(53, redGlass);

        String playerTown = plugin.getTownyHook().getPlayerTownName(player);
        int artLevel = plugin.getArtillerySkillManager().getLevel(player.getUniqueId());
        double artXp = plugin.getArtillerySkillManager().getXP(player.getUniqueId());

        // Header: Profile & Plugin Overview
        inv.setItem(4, createItem(Material.NETHER_STAR,
                ChatColor.GOLD + "" + ChatColor.BOLD + "⚔ TownySieges: Военная Система",
                Arrays.asList(
                        ChatColor.GRAY + "Полная тактическая система осад городов,",
                        ChatColor.GRAY + "штурмовых лагерей, артиллерии и флагов.",
                        "",
                        ChatColor.WHITE + " • Игрок: " + ChatColor.YELLOW + player.getName(),
                        ChatColor.WHITE + " • Город: " + ChatColor.YELLOW + (playerTown != null ? playerTown : "Без города"),
                        ChatColor.WHITE + " • Навык «Артиллерист»: " + ChatColor.GREEN + artLevel + " ур. " + ChatColor.DARK_GRAY + "(" + String.format("%.0f", artXp) + " XP)",
                        "",
                        ChatColor.YELLOW + "✦ Нажимайте на иконки для просмотра крафтов и описаний!"
                )));

        // Row 1: The Core Pillars of TownySieges
        // 1. Осадные лагеря
        inv.setItem(10, createItem(Material.CAMPFIRE,
                ChatColor.RED + "" + ChatColor.BOLD + "1. Осадные Лагеря (Siege Camps)",
                Arrays.asList(
                        ChatColor.GRAY + "Форпост атакующих для штурма вражеского города.",
                        "",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Создание: " + ChatColor.WHITE + "/siege camp <Город>",
                        ChatColor.GRAY + "   Мэр или помощник атакующего города разбивает",
                        ChatColor.GRAY + "   лагерь на границе с защитниками.",
                        ChatColor.WHITE + " • " + ChatColor.GOLD + "Фаза 1: Подготовка (24 часа):",
                        ChatColor.GRAY + "   Строительство фортификаций, подвоз мортир.",
                        ChatColor.WHITE + " • " + ChatColor.DARK_RED + "Фаза 2: Активный Штурм (2 часа):",
                        ChatColor.GRAY + "   Стрельба мортир, взрывы и разрушение блоков!",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Расширение: " + ChatColor.WHITE + "/siege expand",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Роспуск лагеря: " + ChatColor.WHITE + "/disband"
                )));

        // 2. Почанковый захват
        inv.setItem(12, createItem(Material.RED_BANNER,
                ChatColor.GOLD + "" + ChatColor.BOLD + "2. Почанковый Захват (Chunk Capture)",
                Arrays.asList(
                        ChatColor.GRAY + "Захват вражеской территории флаг за флагом.",
                        "",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Штурмовой Флаг: " + ChatColor.WHITE + "ставится на чанке города",
                        ChatColor.WHITE + " • " + ChatColor.AQUA + "Луч Маяка: " + ChatColor.GRAY + "указывает координаты штурма",
                        ChatColor.WHITE + " • " + ChatColor.LIGHT_PURPLE + "BossBar захвата: " + ChatColor.GRAY + "отображает прогресс",
                        ChatColor.WHITE + " • " + ChatColor.GREEN + "Время удержания: " + ChatColor.GRAY + "базовое 5 минут",
                        ChatColor.WHITE + " • " + ChatColor.RED + "Перевес сил: " + ChatColor.GRAY + "атакующие ускоряют захват,",
                        ChatColor.GRAY + "   а защитники откатывают прогресс назад!",
                        ChatColor.WHITE + " • " + ChatColor.GOLD + "Победа на чанке: " + ChatColor.WHITE + "становится Аванпостом атакующих!",
                        "",
                        ChatColor.YELLOW + "» Нажмите, чтобы открыть крафт Штурмового Флага!"
                )));

        double currentCd = plugin.getArtillerySkillManager().getReloadCooldownSeconds(player.getUniqueId());
        double reqXp = plugin.getArtillerySkillManager().getRequiredXPForLevel(artLevel < 10 ? artLevel + 1 : 10);

        // 3. Осадная артиллерия
        inv.setItem(14, createItem(Material.DISPENSER,
                ChatColor.DARK_AQUA + "" + ChatColor.BOLD + "3. Осадные Мортиры (Siege Mortars)",
                Arrays.asList(
                        ChatColor.GRAY + "Дальнобойные настраиваемые осадные орудия.",
                        "",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Установка: " + ChatColor.WHITE + "ПКМ блоком мортиры на землю",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Прицеливание: " + ChatColor.WHITE + "ПКМ по мортире (вид от орудия)",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Выстрел: " + ChatColor.WHITE + "ЛКМ с инструментом наведения",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Перезарядка: " + ChatColor.GOLD + String.format(Locale.US, "%.1f", currentCd) + " сек. " + ChatColor.GRAY + "(10.0с ➔ 5.0с)",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Смена боеприпаса: " + ChatColor.WHITE + "клавиша [F] или /siege switch",
                        ChatColor.WHITE + " • " + ChatColor.GRAY + "Мортира наносит огромный урон стенам",
                        ChatColor.GRAY + "   и укреплениям во время активного штурма!",
                        "",
                        ChatColor.YELLOW + "» Нажмите, чтобы открыть крафт Мортиры!"
                )));

        // 4. Боеприпасы мортиры
        inv.setItem(16, createItem(Material.FIRE_CHARGE,
                ChatColor.YELLOW + "" + ChatColor.BOLD + "4. Боеприпасы (Фугасы и Бронебойные)",
                Arrays.asList(
                        ChatColor.GRAY + "Два типа ядер для разных тактических целей:",
                        "",
                        ChatColor.WHITE + "1. " + ChatColor.GOLD + "Фугасное Чугунное Ядро:",
                        ChatColor.GRAY + "   Мощная взрывная волна (радиус 4.5), сносит",
                        ChatColor.GRAY + "   камень, кирпичи, дерево и живую силу врага.",
                        ChatColor.WHITE + "2. " + ChatColor.DARK_PURPLE + "Бронебойное Ядро (Незерит):",
                        ChatColor.GRAY + "   Пробивает ОБСИДИАН, коробки, бункеры,",
                        ChatColor.GRAY + "   плачущий обсидиан и укрепленные стены!",
                        "",
                        ChatColor.YELLOW + "» Нажмите, чтобы открыть крафты снарядов!"
                )));

        // Row 2: Deep Mechanics (Skill, Wars, Captured Buildings)
        // 5. Навык «Артиллерист»
        inv.setItem(20, createItem(Material.TARGET,
                ChatColor.DARK_GREEN + "" + ChatColor.BOLD + "5. Навык «Артиллерист»",
                Arrays.asList(
                        ChatColor.GRAY + "Прокачиваемая ветка воинского мастерства стрелка.",
                        "",
                        ChatColor.WHITE + " • " + ChatColor.GREEN + "Ваш уровень: " + ChatColor.GOLD + artLevel + " / 10 ур.",
                        ChatColor.WHITE + " • " + ChatColor.AQUA + "Скорость перезарядки: " + ChatColor.YELLOW + String.format(Locale.US, "%.1f", currentCd) + " сек. " + ChatColor.GRAY + "(10.0s ➔ 5.0s)",
                        ChatColor.WHITE + " • " + ChatColor.LIGHT_PURPLE + "Опыт (XP): " + ChatColor.WHITE + String.format(Locale.US, "%.0f", artXp) + 
                                (artLevel < 10 ? " / " + String.format(Locale.US, "%.0f", reqXp) + " XP" : " XP (МАКС)"),
                        "",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Прокачка: " + ChatColor.GRAY + "+15 XP за каждый залп из мортиры,",
                        ChatColor.GRAY + "   а также урон игрокам и разрушение блоков.",
                        ChatColor.GRAY + "   С каждым уровнем прокачка усложняется.",
                        "",
                        ChatColor.YELLOW + "✦ Команда: /siege skill [игрок] [уровень]"
                )));

        // 6. Войны Наций
        inv.setItem(22, createItem(Material.DIAMOND_SWORD,
                ChatColor.LIGHT_PURPLE + "" + ChatColor.BOLD + "6. Войны Наций (Nation Wars)",
                Arrays.asList(
                        ChatColor.GRAY + "Масштабный межгосударственный конфликт наций.",
                        "",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Объявление войны: " + ChatColor.WHITE + "/siege nationwar declare <Нация>",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Статус войн: " + ChatColor.WHITE + "/siege nationwar status",
                        ChatColor.WHITE + " • " + ChatColor.GRAY + "Связывает осадные лагеря всех союзных городов.",
                        ChatColor.WHITE + " • " + ChatColor.GRAY + "Запрещает выход городов из нации во время осады.",
                        ChatColor.WHITE + " • " + ChatColor.GOLD + "Полная победа: " + ChatColor.WHITE + "передача казны защитников,",
                        ChatColor.GRAY + "   захват земель и ликвидация павшего города!"
                )));

        // 7. Захваченные здания и Лимиты
        inv.setItem(24, createItem(Material.IRON_DOOR,
                ChatColor.BLUE + "" + ChatColor.BOLD + "7. Захваченные Здания и Лимиты",
                Arrays.asList(
                        ChatColor.GRAY + "Правила перехода архитектуры при штурмах:",
                        "",
                        ChatColor.WHITE + " • " + ChatColor.GREEN + "Полностью захваченные постройки: " + ChatColor.WHITE + "переходят",
                        ChatColor.GRAY + "   к городу-победителю и становятся активными.",
                        ChatColor.WHITE + " • " + ChatColor.YELLOW + "Лимит 1 уникального здания (Казармы и др.):",
                        ChatColor.GRAY + "   при дубликатах лишние постройки деактивируются.",
                        ChatColor.WHITE + " • " + ChatColor.RED + "Частично захваченные мультичанковые постройки:",
                        ChatColor.GRAY + "   деактивируются для честного баланса.",
                        ChatColor.WHITE + " • " + ChatColor.DARK_AQUA + "Ликвидация города: " + ChatColor.WHITE + "разрывает любые связи",
                        ChatColor.GRAY + "   с уничтоженным или новым городом с тем же именем."
                )));

        // Row 3: Interactive Crafting Buttons
        inv.setItem(28, createItem(Material.DISPENSER,
                ChatColor.GOLD + "" + ChatColor.BOLD + "🔨 КРАФТ: Осадная Мортира",
                Arrays.asList(
                        ChatColor.GRAY + "Нажмите, чтобы увидеть рецепт 3х3 в верстаке.",
                        "",
                        ChatColor.WHITE + "Компоненты: " + ChatColor.YELLOW + "Железные блоки, Раздатчик,",
                        ChatColor.YELLOW + "Камень, Котёл и Дубовые бревна.",
                        "",
                        ChatColor.GREEN + "» Кликните для открытия сетки верстака!"
                )));

        inv.setItem(30, createItem(Material.FIRE_CHARGE,
                ChatColor.GOLD + "" + ChatColor.BOLD + "🔨 КРАФТ: Фугасное Ядро",
                Arrays.asList(
                        ChatColor.GRAY + "Нажмите, чтобы увидеть рецепт 3х3 в верстаке.",
                        "",
                        ChatColor.WHITE + "Компоненты: " + ChatColor.YELLOW + "Железные слитки, Порох, Уголь.",
                        "",
                        ChatColor.GREEN + "» Кликните для открытия сетки верстака!"
                )));

        inv.setItem(32, createItem(Material.NETHERITE_SCRAP,
                ChatColor.GOLD + "" + ChatColor.BOLD + "🔨 КРАФТ: Бронебойное Ядро",
                Arrays.asList(
                        ChatColor.GRAY + "Нажмите, чтобы увидеть рецепт 3х3 в верстаке.",
                        "",
                        ChatColor.WHITE + "Компоненты: " + ChatColor.YELLOW + "Алмазы, Обсидиан, Порох,",
                        ChatColor.YELLOW + "Динамит и Незеритовый обломок.",
                        "",
                        ChatColor.GREEN + "» Кликните для открытия сетки верстака!"
                )));

        inv.setItem(34, createItem(Material.RED_BANNER,
                ChatColor.GOLD + "" + ChatColor.BOLD + "🔨 КРАФТ: Штурмовой Флаг",
                Arrays.asList(
                        ChatColor.GRAY + "Нажмите, чтобы увидеть рецепт 3х3 в верстаке.",
                        "",
                        ChatColor.WHITE + "Компоненты: " + ChatColor.YELLOW + "Золото, Динамит, Красный флаг,",
                        ChatColor.YELLOW + "Огненный стержень ифрита.",
                        "",
                        ChatColor.GREEN + "» Кликните для открытия сетки верстака!"
                )));

        // Row 5: Commands Reference & Controls
        inv.setItem(46, createItem(Material.BOOK,
                ChatColor.AQUA + "" + ChatColor.BOLD + "📜 Команды Игрока",
                Arrays.asList(
                        ChatColor.YELLOW + "/siege menu " + ChatColor.GRAY + "- Открыть это интерактивное меню",
                        ChatColor.YELLOW + "/siege switch " + ChatColor.GRAY + "- Сменить тип снаряда (или клавиша [F])",
                        ChatColor.YELLOW + "/siege nationwar status " + ChatColor.GRAY + "- Список активных войн наций",
                        ChatColor.YELLOW + "/disband " + ChatColor.GRAY + "- Расформировать осадный лагерь (Мэр)"
                )));

        inv.setItem(49, createItem(Material.BARRIER,
                ChatColor.RED + "" + ChatColor.BOLD + "✕ Закрыть меню",
                Collections.singletonList(ChatColor.GRAY + "Нажмите, чтобы вернуться в игру.")));

        inv.setItem(52, createItem(Material.COMMAND_BLOCK,
                ChatColor.GOLD + "" + ChatColor.BOLD + "⚙ Команды Мэра и Админа",
                Arrays.asList(
                        ChatColor.YELLOW + "/siege camp <Город> " + ChatColor.GRAY + "- Разбить осадный лагерь",
                        ChatColor.YELLOW + "/siege expand " + ChatColor.GRAY + "- Расширить лагерь на чанк",
                        ChatColor.YELLOW + "/siege unclaim " + ChatColor.GRAY + "- Освободить чанк лагеря",
                        ChatColor.YELLOW + "/siege nationwar declare <Нация> " + ChatColor.GRAY + "- Объявить войну",
                        ChatColor.RED + "/siege admin skip-prep " + ChatColor.GRAY + "- Пропустить подготовку к штурму",
                        ChatColor.RED + "/siege admin end <Город> " + ChatColor.GRAY + "- Завершить осаду",
                        ChatColor.RED + "/siege recalculate " + ChatColor.GRAY + "- Полный перерасчет мира"
                )));

        player.openInventory(inv);
        player.playSound(player.getLocation(), Sound.BLOCK_CHEST_OPEN, 0.7f, 1.2f);
    }

    public void openCraftingView(Player player, SiegeMenuHolder.Type craftType) {
        SiegeMenuHolder holder = new SiegeMenuHolder(craftType);
        String name = switch (craftType) {
            case CRAFT_MORTAR -> "Крафт: Осадная Мортира";
            case CRAFT_REGULAR_AMMO -> "Крафт: Фугасное Ядро";
            case CRAFT_AP_AMMO -> "Крафт: Бронебойное Ядро";
            case CRAFT_BANNER -> "Крафт: Штурмовой Флаг";
            default -> "Крафт верстака";
        };

        Inventory inv = Bukkit.createInventory(holder, 54, ChatColor.DARK_RED + "" + ChatColor.BOLD + name);
        holder.setInventory(inv);

        ItemStack border = createGlassPane(Material.GRAY_STAINED_GLASS_PANE, " ");
        ItemStack gridBorder = createGlassPane(Material.BLACK_STAINED_GLASS_PANE, " ");
        for (int i = 0; i < 54; i++) {
            inv.setItem(i, border);
        }

        // Fill crafting 3x3 slots:
        // Slot rows: [10, 11, 12], [19, 20, 21], [28, 29, 30]
        int[] craftSlots = {10, 11, 12, 19, 20, 21, 28, 29, 30};
        for (int s : craftSlots) {
            inv.setItem(s, null); // clear for recipe ingredients
        }

        ItemStack arrow = createItem(Material.ARROW,
                ChatColor.YELLOW + "" + ChatColor.BOLD + "➔ Создание в Верстаке 3х3",
                Arrays.asList(
                        ChatColor.GRAY + "Расположите указанные предметы в обычном",
                        ChatColor.GRAY + "верстаке в точно таком же порядке."
                ));
        inv.setItem(23, arrow);

        ItemStack resultItem;
        ItemStack infoCard;

        switch (craftType) {
            case CRAFT_MORTAR -> {
                // Shape: "IDI", "SCS", "LLL"
                inv.setItem(10, new ItemStack(Material.IRON_BLOCK));
                inv.setItem(11, new ItemStack(Material.DISPENSER));
                inv.setItem(12, new ItemStack(Material.IRON_BLOCK));

                inv.setItem(19, new ItemStack(Material.STONE));
                inv.setItem(20, new ItemStack(Material.CAULDRON));
                inv.setItem(21, new ItemStack(Material.STONE));

                inv.setItem(28, new ItemStack(Material.OAK_LOG));
                inv.setItem(29, new ItemStack(Material.OAK_LOG));
                inv.setItem(30, new ItemStack(Material.OAK_LOG));

                resultItem = plugin.getCannonManager().getCannonItem();
                infoCard = createItem(Material.BOOK, ChatColor.GOLD + "Осадная Мортира",
                        Arrays.asList(
                                ChatColor.WHITE + "Рецепт Верстака (3х3):",
                                ChatColor.GRAY + " • 2 Железных блока",
                                ChatColor.GRAY + " • 1 Раздатчик",
                                ChatColor.GRAY + " • 2 Камня",
                                ChatColor.GRAY + " • 1 Котёл",
                                ChatColor.GRAY + " • 3 Дубовых бревна",
                                "",
                                ChatColor.YELLOW + "Перезарядка: 10 сек.",
                                ChatColor.YELLOW + "Снаряды: Фугасные и Бронебойные"
                        ));
            }
            case CRAFT_REGULAR_AMMO -> {
                // Shape: "III", "IGI", "CGC"
                inv.setItem(10, new ItemStack(Material.IRON_INGOT));
                inv.setItem(11, new ItemStack(Material.IRON_INGOT));
                inv.setItem(12, new ItemStack(Material.IRON_INGOT));

                inv.setItem(19, new ItemStack(Material.IRON_INGOT));
                inv.setItem(20, new ItemStack(Material.GUNPOWDER));
                inv.setItem(21, new ItemStack(Material.IRON_INGOT));

                inv.setItem(28, new ItemStack(Material.COAL));
                inv.setItem(29, new ItemStack(Material.GUNPOWDER));
                inv.setItem(30, new ItemStack(Material.COAL));

                resultItem = plugin.getCannonManager().getRegularAmmoItem();
                infoCard = createItem(Material.BOOK, ChatColor.GOLD + "Фугасное Чугунное Ядро",
                        Arrays.asList(
                                ChatColor.WHITE + "Рецепт Верстака (3х3):",
                                ChatColor.GRAY + " • 5 Железных слитков",
                                ChatColor.GRAY + " • 2 Пороха",
                                ChatColor.GRAY + " • 2 Угля",
                                "",
                                ChatColor.YELLOW + "Радиус взрыва: 4.5 блока",
                                ChatColor.YELLOW + "Эффект: Мощная взрывная волна"
                        ));
            }
            case CRAFT_AP_AMMO -> {
                // Shape: "DOD", "NTO", "DGD"
                inv.setItem(10, new ItemStack(Material.DIAMOND));
                inv.setItem(11, new ItemStack(Material.OBSIDIAN));
                inv.setItem(12, new ItemStack(Material.DIAMOND));

                inv.setItem(19, new ItemStack(Material.NETHERITE_SCRAP));
                inv.setItem(20, new ItemStack(Material.TNT));
                inv.setItem(21, new ItemStack(Material.OBSIDIAN));

                inv.setItem(28, new ItemStack(Material.DIAMOND));
                inv.setItem(29, new ItemStack(Material.GUNPOWDER));
                inv.setItem(30, new ItemStack(Material.DIAMOND));

                resultItem = plugin.getCannonManager().getArmorPiercingAmmoItem();
                infoCard = createItem(Material.BOOK, ChatColor.GOLD + "Бронебойное Ядро (Незерит)",
                        Arrays.asList(
                                ChatColor.WHITE + "Рецепт Верстака (3х3):",
                                ChatColor.GRAY + " • 4 Алмаза",
                                ChatColor.GRAY + " • 2 Обсидиана",
                                ChatColor.GRAY + " • 1 Незеритовый обломок",
                                ChatColor.GRAY + " • 1 Динамит (TNT)",
                                ChatColor.GRAY + " • 1 Порох",
                                "",
                                ChatColor.DARK_PURPLE + "Специальное свойство:",
                                ChatColor.RED + "ПРОБИВАЕТ ОБСИДИАНОВЫЕ БУНКЕРЫ!"
                        ));
            }
            case CRAFT_BANNER -> {
                // Shape: "GTG", "GBG", " R "
                inv.setItem(10, new ItemStack(Material.GOLD_INGOT));
                inv.setItem(11, new ItemStack(Material.TNT));
                inv.setItem(12, new ItemStack(Material.GOLD_INGOT));

                inv.setItem(19, new ItemStack(Material.GOLD_INGOT));
                inv.setItem(20, new ItemStack(Material.RED_BANNER));
                inv.setItem(21, new ItemStack(Material.GOLD_INGOT));

                inv.setItem(28, null);
                inv.setItem(29, new ItemStack(Material.BLAZE_ROD));
                inv.setItem(30, null);

                resultItem = plugin.getCaptureManager().getAssaultBannerItem();
                infoCard = createItem(Material.BOOK, ChatColor.GOLD + "Штурмовой Флаг Осады",
                        Arrays.asList(
                                ChatColor.WHITE + "Рецепт Верстака (3х3):",
                                ChatColor.GRAY + " • 4 Золотых слитка",
                                ChatColor.GRAY + " • 1 Динамит (TNT)",
                                ChatColor.GRAY + " • 1 Красный флаг",
                                ChatColor.GRAY + " • 1 Огненный стержень ифрита",
                                "",
                                ChatColor.YELLOW + "Создает луч маяка и BossBar захвата чанка."
                        ));
            }
            default -> {
                resultItem = new ItemStack(Material.BARRIER);
                infoCard = new ItemStack(Material.PAPER);
            }
        }

        inv.setItem(24, resultItem);
        inv.setItem(25, infoCard);

        // Back button
        inv.setItem(49, createItem(Material.SPECTRAL_ARROW,
                ChatColor.YELLOW + "" + ChatColor.BOLD + "« Назад в главное меню",
                Collections.singletonList(ChatColor.GRAY + "Вернуться к списку систем и крафтов.")));

        player.openInventory(inv);
        player.playSound(player.getLocation(), Sound.BLOCK_SMITHING_TABLE_USE, 0.8f, 1.2f);
    }

    @EventHandler
    public void onInventoryClick(InventoryClickEvent event) {
        if (!(event.getInventory().getHolder() instanceof SiegeMenuHolder holder)) {
            return;
        }

        event.setCancelled(true);
        if (!(event.getWhoClicked() instanceof Player player)) {
            return;
        }

        int slot = event.getRawSlot();
        if (slot < 0 || slot >= event.getInventory().getSize()) {
            return;
        }

        if (holder.getType() == SiegeMenuHolder.Type.MAIN) {
            switch (slot) {
                case 14, 28 -> openCraftingView(player, SiegeMenuHolder.Type.CRAFT_MORTAR);
                case 16, 30 -> openCraftingView(player, SiegeMenuHolder.Type.CRAFT_REGULAR_AMMO);
                case 32 -> openCraftingView(player, SiegeMenuHolder.Type.CRAFT_AP_AMMO);
                case 12, 34 -> openCraftingView(player, SiegeMenuHolder.Type.CRAFT_BANNER);
                case 49 -> {
                    player.closeInventory();
                    player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.6f, 1.0f);
                }
                default -> player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.4f, 1.2f);
            }
        } else {
            // Inside a crafting view
            if (slot == 49) {
                openMainMenu(player);
            }
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

    private ItemStack createItem(Material mat, String name, List<String> lore) {
        ItemStack item = new ItemStack(mat);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(name);
            meta.setLore(lore);
            meta.addItemFlags(ItemFlag.HIDE_ATTRIBUTES, ItemFlag.HIDE_ENCHANTS);
            item.setItemMeta(meta);
        }
        return item;
    }
}
