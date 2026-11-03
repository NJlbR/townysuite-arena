package com.towny.architecture.gui;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.manager.ArchitectManager;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.ChunkCoord;
import com.towny.architecture.util.RussianTranslator;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Material;
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

public class BuildsMenuGui implements Listener {
    private final TownyArchitecturePlugin plugin;
    private String title;
    private final Map<Integer, String> slotBlueprintMap = new HashMap<>();

    public BuildsMenuGui(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
        
    }

    public void open(Player player) {
        this.title = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("gui.title", "&f\uE000\uE001\uE002&fЧертежи и постройки"));
        Inventory inv = Bukkit.createInventory(null, plugin.getConfig().getInt("gui.size", 54), title);
        slotBlueprintMap.clear();

        String townName = plugin.getTownyHook().getPlayerTownName(player);
        boolean isMayorOrAssistant = plugin.getTownyHook().isPlayerMayorOrAssistant(player);

        int currentSkillLevel = plugin.getArchitectManager().getLevel(player);
        ArchitectManager.ArchitectStats stats = plugin.getArchitectManager().getStats(player);
        int nextLevelXp = ArchitectManager.getXpForLevel(currentSkillLevel + 1);
        int currentLevelBaseXp = ArchitectManager.getXpForLevel(currentSkillLevel);
        int xpProgress = stats.xp - currentLevelBaseXp;
        int xpNeeded = nextLevelXp - currentLevelBaseXp;
        if (xpNeeded <= 0) xpNeeded = 100;

        // 1. Fill borders and frame for a polished RPG aesthetic
        ItemStack borderPane = createGlassPane(Material.GRAY_STAINED_GLASS_PANE, " ");
        ItemStack cornerPane = createGlassPane(Material.CYAN_STAINED_GLASS_PANE, " ");
        ItemStack goldDivider = createGlassPane(Material.ORANGE_STAINED_GLASS_PANE, " ");

        if (plugin.getConfig().getBoolean("gui.fill-empty-slots", false)) {
            int size = plugin.getConfig().getInt("gui.size", 54);
            for (int i = 0; i < size; i++) {
                if (i < 9 || i >= size - 9 || i % 9 == 0 || i % 9 == 8) {
                    inv.setItem(i, borderPane);
                }
            }
            inv.setItem(0, cornerPane);
            inv.setItem(8, cornerPane);
            inv.setItem(size - 9, cornerPane);
            inv.setItem(size - 1, cornerPane);
        }

        // 2. Header Indicators
        // Slot 2: Town Info
        Material townIndicatorMat = Material.matchMaterial(plugin.getConfig().getString("gui.items.town-info.material", "BEACON"));
        if (townIndicatorMat == null || townIndicatorMat == Material.PAPER) townIndicatorMat = Material.BEACON;
        ItemStack townIndicator = new ItemStack(townIndicatorMat);
        ItemMeta townMeta = townIndicator.getItemMeta();
        if (townMeta != null) {
            townMeta.setDisplayName(ChatColor.GOLD + "" + ChatColor.BOLD + "🏛 Ваш Город: " + 
                    (townName != null ? ChatColor.YELLOW + townName : ChatColor.RED + "Нет города"));
            List<String> lore = new ArrayList<>();
            if (townName != null) {
                lore.add(ChatColor.GRAY + "Статус роли: " + 
                        (isMayorOrAssistant ? ChatColor.GREEN + "Мэр / Помощник (Право выбора)" : ChatColor.YELLOW + "Житель / Строитель"));
                
                int activeCount = 0;
                for (ActiveBuilding b : plugin.getBuildingManager().getActiveBuildings()) {
                    if (b.getTownName().equalsIgnoreCase(townName)) {
                        activeCount++;
                    }
                }
                lore.add(ChatColor.GRAY + "Действующих построек: " + ChatColor.WHITE + activeCount);
                
                // Show prepared plots count
                Set<ChunkCoord> plots = plugin.getBuildingManager().getTownBuildPlots(townName);
                lore.add(ChatColor.GRAY + "Выделено строй-чанков: " + ChatColor.AQUA + plots.size() + " шт. (/plot set build)");
            } else {
                lore.add(ChatColor.RED + "Вы не состоите в городе!");
                lore.add(ChatColor.DARK_GRAY + "Вступите в город, чтобы открывать проекты.");
            }
            townMeta.setLore(lore);
            townMeta.addItemFlags(ItemFlag.HIDE_ENCHANTS);
            if(plugin.getConfig().getInt("gui.items.town-info.custom-model-data", 0) > 0) townMeta.setCustomModelData(plugin.getConfig().getInt("gui.items.town-info.custom-model-data"));
            townIndicator.setItemMeta(townMeta);
        }
        inv.setItem(plugin.getConfig().getInt("gui.items.town-info.slot", 2), townIndicator);

        // Slot 4: Main Title Book
        Material catalogHeaderMat = Material.matchMaterial(plugin.getConfig().getString("gui.items.catalog-header.material", "KNOWLEDGE_BOOK"));
        if (catalogHeaderMat == null || catalogHeaderMat == Material.PAPER) catalogHeaderMat = Material.KNOWLEDGE_BOOK;
        ItemStack catalogHeader = new ItemStack(catalogHeaderMat);
        ItemMeta catalogMeta = catalogHeader.getItemMeta();
        if (catalogMeta != null) {
            catalogMeta.setDisplayName(ChatColor.AQUA + "" + ChatColor.BOLD + "📖 Каталог Архитектурных Чертежей");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Выберите проект для начала строительства.");
            lore.add(ChatColor.GRAY + "Постройки дают постоянные баффы жителям");
            lore.add(ChatColor.GRAY + "в пределах чанков, города или всего мира!");
            lore.add("");
            lore.add(ChatColor.YELLOW + "Для начала постройки:");
            lore.add(ChatColor.WHITE + "1. Выделите чанки: " + ChatColor.AQUA + "/plot set build");
            lore.add(ChatColor.WHITE + "2. Нажмите ЛКМ по чертежу в этом меню");
            lore.add(ChatColor.WHITE + "3. Ставьте стройматериалы в границах участка");
            catalogMeta.setLore(lore);
            catalogMeta.addItemFlags(ItemFlag.HIDE_ENCHANTS);
            if(plugin.getConfig().getInt("gui.items.catalog-header.custom-model-data", 0) > 0) catalogMeta.setCustomModelData(plugin.getConfig().getInt("gui.items.catalog-header.custom-model-data"));
            catalogHeader.setItemMeta(catalogMeta);
        }
        inv.setItem(plugin.getConfig().getInt("gui.items.catalog-header.slot", 4), catalogHeader);

        // Slot 6: Built-in Architect Skill Badge
        Material skillBadgeMat = Material.matchMaterial(plugin.getConfig().getString("gui.items.skill-badge.material", "GOLDEN_PICKAXE"));
        if (skillBadgeMat == null || skillBadgeMat == Material.PAPER) skillBadgeMat = Material.GOLDEN_PICKAXE;
        ItemStack skillBadge = new ItemStack(skillBadgeMat);
        ItemMeta skillMeta = skillBadge.getItemMeta();
        if (skillMeta != null) {
            skillMeta.setDisplayName(ChatColor.YELLOW + "" + ChatColor.BOLD + "⛏ Навык «Архитектор»");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Текущий уровень: " + ChatColor.GREEN + "" + currentSkillLevel + " ур.");
            lore.add(ChatColor.GRAY + "Общий опыт (XP): " + ChatColor.AQUA + stats.xp + " XP");
            lore.add(ChatColor.GRAY + "Прогресс до след. ур: " + ChatColor.WHITE + Math.max(0, xpProgress) + "/" + xpNeeded + " XP");
            lore.add(ChatColor.GRAY + "Поставлено стройматериалов: " + ChatColor.WHITE + stats.placed + " шт.");
            lore.add("");
            lore.add(ChatColor.YELLOW + "Как прокачивать:");
            lore.add(ChatColor.GRAY + "• Строительство зданий: " + ChatColor.AQUA + "+15 XP" + ChatColor.GRAY + " за блок");
            lore.add(ChatColor.GRAY + "• Установка блоков в городе: " + ChatColor.AQUA + "+1 XP" + ChatColor.GRAY + " за блок");
            lore.add(ChatColor.DARK_GRAY + "(С защитой от накрутки High-Water Mark)");
            skillMeta.setLore(lore);
            skillMeta.addItemFlags(ItemFlag.HIDE_ATTRIBUTES);
            if(plugin.getConfig().getInt("gui.items.skill-badge.custom-model-data", 0) > 0) skillMeta.setCustomModelData(plugin.getConfig().getInt("gui.items.skill-badge.custom-model-data"));
            skillBadge.setItemMeta(skillMeta);
        }
        inv.setItem(plugin.getConfig().getInt("gui.items.skill-badge.slot", 6), skillBadge);

        // 3. Central Grid Blueprint Showcase (Slots 10..16, 19..25, 28..34)
        java.util.List<Integer> contentSlotsList = plugin.getConfig().getIntegerList("gui.blueprint-slots");
        if (contentSlotsList == null || contentSlotsList.isEmpty() || contentSlotsList.size() < 16) {
            contentSlotsList = java.util.Arrays.asList(
                10, 11, 12, 13, 14, 15, 16,
                19, 20, 21, 22, 23, 24, 25,
                28, 29, 30, 31, 32, 33, 34
            );
        }
        int[] contentSlots = contentSlotsList.stream().mapToInt(i -> i).toArray();
        int blueprintIndex = 0;

        Collection<BuildingBlueprint> blueprints = plugin.getBuildingManager().getBlueprints();
        for (BuildingBlueprint bp : blueprints) {
            if (blueprintIndex >= contentSlots.length) break;
            int targetSlot = contentSlots[blueprintIndex++];

            ItemStack item = new ItemStack(bp.getIcon());
            ItemMeta meta = item.getItemMeta();
            if (meta != null) {
                String wonderTag = bp.isWorldWonder() ? ChatColor.GOLD + "★ [ЧУДО СВЕТА] " : ChatColor.YELLOW + "» ";
                meta.setDisplayName(wonderTag + ChatColor.WHITE + "" + ChatColor.BOLD + bp.getNameRu());

                List<String> lore = new ArrayList<>();
                lore.add(ChatColor.GRAY + bp.getDescription());
                lore.add(ChatColor.DARK_GRAY + "───────────────────────────────────");

                // Dimensions & Area
                String areaType;
                if (bp.getChunkWidth() == 1 && bp.getChunkLength() == 1) {
                    areaType = ChatColor.AQUA + "Радиус 5 чанков вокруг здания";
                } else if (bp.isWorldWonder() || (bp.getChunkWidth() >= 2 && bp.getChunkLength() >= 2)) {
                    areaType = ChatColor.GOLD + "" + ChatColor.BOLD + "ВЕСЬ МИР (Вся карта сервера!)";
                } else {
                    areaType = ChatColor.YELLOW + "Вся территория города";
                }

                lore.add(ChatColor.WHITE + "Размер участка: " + ChatColor.YELLOW + bp.getFootprintDisplay() + 
                         ChatColor.DARK_GRAY + " (" + bp.getChunkWidth() + "x" + bp.getChunkLength() + " чанков)");
                lore.add(ChatColor.WHITE + "Зона действия баффа: " + areaType);

                // Architect Requirement
                boolean levelOk = currentSkillLevel >= bp.getRequiredSkillLevel();
                String levelStr = levelOk 
                        ? ChatColor.GREEN + "✔ Доступно (Ваш: " + currentSkillLevel + ")" 
                        : ChatColor.RED + "✖ Требуется " + bp.getRequiredSkillLevel() + " ур. (Ваш: " + currentSkillLevel + ")";
                lore.add(ChatColor.WHITE + "Требование Архитектора: " + levelStr);

                // Town Free Plot Check
                boolean hasPlot = false;
                if (townName != null) {
                    ChunkCoord pChunk = ChunkCoord.fromLocation(player.getLocation());
                    Set<ChunkCoord> freeArea = plugin.getBuildingManager().findFreePlotArea(
                            townName, player.getWorld().getName(), bp.getChunkWidth(), bp.getChunkLength(), pChunk, player.getLocation().getYaw()
                    );
                    hasPlot = freeArea != null;
                    if (hasPlot) {
                        lore.add(ChatColor.GREEN + "✔ Участок в городе подготовлен (/plot set build)");
                    } else {
                        lore.add(ChatColor.RED + "✖ Нет свободного участка " + bp.getFootprintDisplay());
                    }
                }

                // Multiplicity / Wonder Status
                int areaChunks = bp.getChunkWidth() * bp.getChunkLength();
                boolean townAlreadyHasLarge = false;
                if (townName != null) {
                    for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                        if (bld.getTownName().equalsIgnoreCase(townName) && bld.getBlueprintId().equalsIgnoreCase(bp.getId())) {
                            if (areaChunks > 1) {
                                townAlreadyHasLarge = true;
                            }
                        }
                    }
                }

                if (bp.isWorldWonder()) {
                    if (bp.getWonderCompletedByTown() != null) {
                        lore.add(ChatColor.DARK_RED + "" + ChatColor.BOLD + "✖ Построено городом «" + bp.getWonderCompletedByTown() + "» (Заблокировано)");
                    } else {
                        lore.add(ChatColor.GOLD + "✦ Свободно для постройки первым городом мира!");
                    }
                } else if (areaChunks > 1) {
                    if (townAlreadyHasLarge) {
                        lore.add(ChatColor.DARK_RED + "✖ Уже есть в городе (лимит: 1)");
                    } else {
                        lore.add(ChatColor.YELLOW + "✦ Лимит: 1 постройка на город");
                    }
                } else {
                    lore.add(ChatColor.GREEN + "✦ Без ограничений на количество в городе");
                }

                // Passive Buffs list in Russian
                lore.add(ChatColor.DARK_GRAY + "───────────────────────────────────");
                lore.add(ChatColor.GOLD + "Пассивные эффекты для жителей:");
                if (!bp.getBuffs().isEmpty()) {
                    for (Map.Entry<String, Object> bEntry : bp.getBuffs().entrySet()) {
                        String buffText = RussianTranslator.formatBuffRu(bEntry.getKey(), bEntry.getValue());
                        if (!buffText.isEmpty()) {
                            lore.add(ChatColor.GREEN + " • " + ChatColor.WHITE + buffText);
                        }
                    }
                } else {
                    lore.add(ChatColor.GRAY + " • Особые городские привилегии");
                }

                // Required Materials in Russian
                lore.add(ChatColor.DARK_GRAY + "───────────────────────────────────");
                lore.add(ChatColor.YELLOW + "Необходимые материалы:");
                for (Map.Entry<Material, Integer> res : bp.getResources().entrySet()) {
                    lore.add(ChatColor.GRAY + " • " + ChatColor.WHITE + RussianTranslator.getMaterialRu(res.getKey()) + 
                             ": " + ChatColor.YELLOW + res.getValue() + " шт.");
                }

                // Particle zone color info for 1x1 buildings
                if (bp.getChunkWidth() == 1 && bp.getChunkLength() == 1 && bp.getParticleColorHex() != null) {
                    lore.add(ChatColor.DARK_GRAY + "───────────────────────────────────");
                    lore.add(ChatColor.AQUA + "✨ Цвет подсветки зоны (1х1): " + ChatColor.WHITE + bp.getParticleColorHex() + " " + ChatColor.GRAY + "(радиус 5 чанков)");
                }

                // Action Callout
                lore.add(ChatColor.DARK_GRAY + "───────────────────────────────────");
                if (townName == null) {
                    lore.add(ChatColor.DARK_RED + "✖ Вы не состоите в городе");
                } else if (!isMayorOrAssistant) {
                    lore.add(ChatColor.DARK_RED + "✖ Только мэр или помощник могут начать проект");
                } else if (bp.isWorldWonder() && bp.getWonderCompletedByTown() != null) {
                    lore.add(ChatColor.DARK_RED + "✖ Недоступно: Чудо Света уже возведено");
                } else if (townAlreadyHasLarge) {
                    lore.add(ChatColor.DARK_RED + "✖ Недоступно: Превышен лимит (1) для города");
                } else if (!levelOk) {
                    lore.add(ChatColor.RED + "✖ Недостаточный уровень Архитектора");
                } else if (!hasPlot) {
                    lore.add(ChatColor.GOLD + "▶ Сначала выделите чанк: /plot set build");
                } else {
                    lore.add(ChatColor.GREEN + "" + ChatColor.BOLD + "▶ Нажмите ЛКМ для утверждения проекта!");
                }

                meta.setLore(lore);
                meta.addItemFlags(ItemFlag.HIDE_ATTRIBUTES);
                item.setItemMeta(meta);
            }

            inv.setItem(targetSlot, item);
            slotBlueprintMap.put(targetSlot, bp.getId());
        }

        // 4. Bottom Controls
        // Active Buildings summary item
        Material activeMat = Material.matchMaterial(plugin.getConfig().getString("gui.items.active-buildings.material", "COMPASS"));
        if (activeMat == null || activeMat == Material.PAPER) activeMat = Material.COMPASS;
        ItemStack activeStatus = new ItemStack(activeMat);
        ItemMeta activeMeta = activeStatus.getItemMeta();
        if (activeMeta != null) {
            activeMeta.setDisplayName(ChatColor.GOLD + "" + ChatColor.BOLD + "🧭 Текущие проекты города");
            List<String> lore = new ArrayList<>();
            if (townName != null) {
                boolean found = false;
                for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                    if (bld.getTownName().equalsIgnoreCase(townName)) {
                        BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                        String name = bp != null ? bp.getNameRu() : bld.getBlueprintId();
                        lore.add(ChatColor.YELLOW + "• " + name + " " + ChatColor.DARK_GRAY + "[" + 
                                 RussianTranslator.getStatusRu(bld.getStatus()) + ChatColor.DARK_GRAY + "] " +
                                 ChatColor.GREEN + bld.getProgressPercent() + "%");
                        found = true;
                    }
                }
                if (!found) {
                    lore.add(ChatColor.GRAY + "Нет активных строек. Выберите чертеж выше!");
                }
            } else {
                lore.add(ChatColor.RED + "Город не определен.");
            }
            lore.add("");
            lore.add(ChatColor.DARK_AQUA + "Используйте " + ChatColor.AQUA + "/build info" + ChatColor.DARK_AQUA + " для подробного списка блоков.");
            activeMeta.setLore(lore);
            if(plugin.getConfig().getInt("gui.items.active-buildings.custom-model-data", 0) > 0) activeMeta.setCustomModelData(plugin.getConfig().getInt("gui.items.active-buildings.custom-model-data"));
            activeStatus.setItemMeta(activeMeta);
        }
        inv.setItem(plugin.getConfig().getInt("gui.items.active-buildings.slot", 49), activeStatus);

        // Close button
        Material closeBtnMat = Material.matchMaterial(plugin.getConfig().getString("gui.items.close-button.material", "BARRIER"));
        if (closeBtnMat == null || closeBtnMat == Material.PAPER) closeBtnMat = Material.BARRIER;
        ItemStack closeBtn = new ItemStack(closeBtnMat);
        ItemMeta closeMeta = closeBtn.getItemMeta();
        if (closeMeta != null) {
            closeMeta.setDisplayName(ChatColor.RED + "" + ChatColor.BOLD + "❌ Закрыть меню");
            if(plugin.getConfig().getInt("gui.items.close-button.custom-model-data", 0) > 0) closeMeta.setCustomModelData(plugin.getConfig().getInt("gui.items.close-button.custom-model-data"));
            closeBtn.setItemMeta(closeMeta);
        }
        inv.setItem(plugin.getConfig().getInt("gui.items.close-button.slot", 48), closeBtn);

        // Stats command info
        Material statsBtnMat = Material.matchMaterial(plugin.getConfig().getString("gui.items.stats-button.material", "EXPERIENCE_BOTTLE"));
        if (statsBtnMat == null || statsBtnMat == Material.PAPER) statsBtnMat = Material.EXPERIENCE_BOTTLE;
        ItemStack statsBtn = new ItemStack(statsBtnMat);
        ItemMeta statsMeta = statsBtn.getItemMeta();
        if (statsMeta != null) {
            statsMeta.setDisplayName(ChatColor.GREEN + "" + ChatColor.BOLD + "📊 Личная статистика: /build stats");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Просматривайте в чате свой прогресс");
            lore.add(ChatColor.GRAY + "и количество установленных стройматериалов.");
            statsMeta.setLore(lore);
            if(plugin.getConfig().getInt("gui.items.stats-button.custom-model-data", 0) > 0) statsMeta.setCustomModelData(plugin.getConfig().getInt("gui.items.stats-button.custom-model-data"));
            statsBtn.setItemMeta(statsMeta);
        }
        inv.setItem(plugin.getConfig().getInt("gui.items.stats-button.slot", 50), statsBtn);

        // Particle toggle button
        boolean particlesEnabled = plugin.getBuildingHudManager().hasParticlesEnabled(player);
        Material particleBtnMat = Material.matchMaterial(plugin.getConfig().getString("gui.items.border-particles.material", "GLOWSTONE_DUST"));
        if (particleBtnMat == null || particleBtnMat == Material.PAPER) particleBtnMat = Material.GLOWSTONE_DUST;
        ItemStack particleBtn = new ItemStack(particleBtnMat);
        ItemMeta pMeta = particleBtn.getItemMeta();
        if (pMeta != null) {
            pMeta.setDisplayName(ChatColor.AQUA + "" + ChatColor.BOLD + "✨ Подсветка границ участков");
            List<String> pLore = new ArrayList<>();
            pLore.add(ChatColor.GRAY + "Отображает границы назначенных");
            pLore.add(ChatColor.GRAY + "строительных чанков.");
            pLore.add("");
            pLore.add(ChatColor.WHITE + "Состояние: " + (particlesEnabled ? ChatColor.GREEN + "ВКЛЮЧЕНО" : ChatColor.RED + "ВЫКЛЮЧЕНО"));
            pLore.add(ChatColor.DARK_GRAY + "Команда: /build borders");
            pLore.add("");
            pLore.add(ChatColor.YELLOW + "Нажмите, чтобы переключить.");
            pMeta.setLore(pLore);
            if(plugin.getConfig().getInt("gui.items.border-particles.custom-model-data", 0) > 0) pMeta.setCustomModelData(plugin.getConfig().getInt("gui.items.border-particles.custom-model-data"));
            particleBtn.setItemMeta(pMeta);
        }
        inv.setItem(plugin.getConfig().getInt("gui.items.border-particles.slot", 51), particleBtn);

        // Effects toggle button
        boolean effectParticlesEnabled = plugin.getBuildingHudManager().hasEffectParticlesEnabled(player);
        Material effectParticleBtnMat = Material.matchMaterial(plugin.getConfig().getString("gui.items.effect-particles.material", "REDSTONE_TORCH"));
        if (effectParticleBtnMat == null || effectParticleBtnMat == Material.PAPER) effectParticleBtnMat = Material.REDSTONE_TORCH;
        ItemStack effectParticleBtn = new ItemStack(effectParticleBtnMat);
        ItemMeta epMeta = effectParticleBtn.getItemMeta();
        if (epMeta != null) {
            epMeta.setDisplayName(ChatColor.AQUA + "" + ChatColor.BOLD + "✨ Подсветка зон эффектов");
            List<String> pLore = new ArrayList<>();
            pLore.add(ChatColor.GRAY + "Отображает границы действия эффектов");
            pLore.add(ChatColor.GRAY + "от построенных зданий.");
            pLore.add("");
            pLore.add(ChatColor.WHITE + "Состояние: " + (effectParticlesEnabled ? ChatColor.GREEN + "ВКЛЮЧЕНО" : ChatColor.RED + "ВЫКЛЮЧЕНО"));
            pLore.add(ChatColor.DARK_GRAY + "Команда: /build effects");
            pLore.add("");
            pLore.add(ChatColor.YELLOW + "Нажмите, чтобы переключить.");
            epMeta.setLore(pLore);
            if(plugin.getConfig().getInt("gui.items.effect-particles.custom-model-data", 0) > 0) epMeta.setCustomModelData(plugin.getConfig().getInt("gui.items.effect-particles.custom-model-data"));
            effectParticleBtn.setItemMeta(epMeta);
        }
        inv.setItem(plugin.getConfig().getInt("gui.items.effect-particles.slot", 52), effectParticleBtn);

        player.openInventory(inv);
        player.playSound(player.getLocation(), Sound.BLOCK_CHEST_OPEN, 0.7f, 1.2f);
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

    @EventHandler
    public void onInventoryClick(InventoryClickEvent event) {
        if (!event.getView().getTitle().equals(title)) return;
        event.setCancelled(true);

        if (!(event.getWhoClicked() instanceof Player)) return;
        Player player = (Player) event.getWhoClicked();

        int slot = event.getRawSlot();
        if (slot < 0 || slot >= plugin.getConfig().getInt("gui.size", 54)) return;

        // Close button
        if (slot == plugin.getConfig().getInt("gui.items.close-button.slot", 48)) {
            player.closeInventory();
            player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.0f);
            return;
        }

        if (slot == plugin.getConfig().getInt("gui.items.stats-button.slot", 50)) {
            player.closeInventory();
            player.performCommand("build stats");
            return;
        }

        // Particle toggle button
        if (slot == plugin.getConfig().getInt("gui.items.border-particles.slot", 51)) {
            boolean newState = plugin.getBuildingHudManager().toggleParticles(player);
            player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.2f);
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + (newState ? "&aПодсветка границ построек &2ВКЛЮЧЕНА&a (видна только вам)!" : "&cПодсветка границ построек &4ВЫКЛЮЧЕНА&c.")));
            open(player);
            return;
        }

        // Effect particle toggle button
        if (slot == plugin.getConfig().getInt("gui.items.effect-particles.slot", 52)) {
            boolean newState = plugin.getBuildingHudManager().toggleEffectParticles(player);
            player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.2f);
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + (newState ? "&aПодсветка зон эффектов &2ВКЛЮЧЕНА&a (видна только вам)!" : "&cПодсветка зон эффектов &4ВЫКЛЮЧЕНА&c.")));
            open(player);
            return;
        }

        if (!slotBlueprintMap.containsKey(slot)) return;

        String bpId = slotBlueprintMap.get(slot);
        BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bpId);
        if (bp == null) return;

        // Security Check 1: Town membership
        String townName = plugin.getTownyHook().getPlayerTownName(player);
        if (townName == null) {
            player.sendMessage(ChatColor.RED + "Вы должны состоять в городе!");
            player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
            return;
        }

        // Security Check 2: Mayor or Assistant rank
        if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player)) {
            player.sendMessage(ChatColor.RED + "Только мэр или помощник города могут утверждать строительные проекты!");
            player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
            return;
        }

        // Security Check 3: Architect level check
        if (plugin.getConfig().getBoolean("settings.enforce-skill-level", true)) {
            int level = plugin.getArchitectManager().getLevel(player);
            if (level < bp.getRequiredSkillLevel()) {
                player.sendMessage(ChatColor.RED + "Ваш уровень Архитектора (" + level + 
                        ") ниже требуемого (" + bp.getRequiredSkillLevel() + ") для чертежа «" + bp.getNameRu() + "»!");
                player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
                return;
            }
        }

        // Security Check 4: Wonder uniqueness
        if (bp.isWorldWonder() && bp.getWonderCompletedByTown() != null) {
            player.sendMessage(ChatColor.RED + "Это Чудо Света уже воздвигнуто городом «" + bp.getWonderCompletedByTown() + "»!");
            player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
            return;
        }

        player.closeInventory();
        ActiveBuilding started = plugin.getBuildingManager().startBuilding(player, bp);
        if (started != null) {
            player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1.1f);
        } else {
            player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 1.0f, 1.0f);
        }
    }
}
