package com.towny.sieges.manager;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.ChunkCoord;
import com.towny.sieges.model.NationWar;
import com.towny.sieges.model.SiegeBannerCapture;
import com.towny.sieges.model.SiegeCamp;
import org.bukkit.*;
import org.bukkit.block.Banner;
import org.bukkit.block.Block;
import org.bukkit.block.banner.Pattern;
import org.bukkit.block.banner.PatternType;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.ShapedRecipe;
import org.bukkit.inventory.meta.BannerMeta;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.metadata.FixedMetadataValue;
import org.bukkit.persistence.PersistentDataType;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Менеджер почанкового захвата территории во время активного штурма осады.
 * Поддерживает одновременный захват нескольких чанков, кастомный крафт штурмового флага,
 * луч маяка в небо, звуковые эффекты и динамический боссбар на чанке.
 */
public class SiegeCaptureManager {

    private final TownySiegesPlugin plugin;
    private final Map<ChunkCoord, SiegeBannerCapture> activeCaptures = new ConcurrentHashMap<>();
    private final Map<ChunkCoord, BossBar> captureBossBars = new ConcurrentHashMap<>();
    private final Map<ChunkCoord, Location> bannerBlockLocations = new ConcurrentHashMap<>();

    public SiegeCaptureManager(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    /**
     * Создание кастомного штурмового флага с уникальными метаданными и рецептом.
     */
    public ItemStack getAssaultBannerItem() {
        ItemStack item = new ItemStack(Material.RED_BANNER, 1);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.DARK_RED + "" + ChatColor.BOLD + "⚔ Штурмовой Флаг Осады (Siege Assault Banner)");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Тактический боевой стяг для почанкового захвата территории.");
            lore.add(ChatColor.DARK_GRAY + "Категория: Осадное снаряжение [1 шт / слот]");
            lore.add(ChatColor.YELLOW + "Установка: ПКМ на чанк диких земель или атакуемого города,");
            lore.add(ChatColor.YELLOW + "ОБЯЗАТЕЛЬНО граничащий с чанком осадного лагеря!");
            lore.add(ChatColor.AQUA + "✦ При установке: громкий боевой горн и луч маяка в небо.");
            lore.add(ChatColor.GOLD + "✦ Базовое время захвата: 5 минут (300 сек).");
            lore.add(ChatColor.GREEN + "✦ Скорость захвата зависит от перевеса атакующих бойцов!");
            lore.add(ChatColor.WHITE + "✦ BossBar отображает актуальное число атакующих и защитников.");
            lore.add(ChatColor.RED + "✦ Если защитников больше: прогресс откатывается назад.");
            lore.add(ChatColor.LIGHT_PURPLE + "✦ При уходе прогресса в минус: чанк переходит защитникам!");
            lore.add(ChatColor.LIGHT_PURPLE + "  (Если не граничит — становится официальным Аванпостом Towny).");
            lore.add(ChatColor.DARK_AQUA + "✦ Можно захватывать сразу несколько чанков одновременно!");
            meta.setLore(lore);
            meta.setCustomModelData(7005);
            meta.getPersistentDataContainer().set(
                    new NamespacedKey(plugin, "siege_assault_banner"),
                    PersistentDataType.STRING,
                    "true"
            );
            item.setItemMeta(meta);

            if (meta instanceof BannerMeta) {
                BannerMeta bm = (BannerMeta) meta;
                bm.addPattern(new Pattern(DyeColor.BLACK, PatternType.CROSS));
                bm.addPattern(new Pattern(DyeColor.YELLOW, PatternType.STRIPE_MIDDLE));
                bm.addPattern(new Pattern(DyeColor.BLACK, PatternType.BORDER));
                item.setItemMeta(bm);
            }
        }
        return item;
    }

    public boolean isAssaultBanner(ItemStack item) {
        if (item == null || !item.hasItemMeta()) return false;
        ItemMeta meta = item.getItemMeta();
        if (meta.getPersistentDataContainer().has(new NamespacedKey(plugin, "siege_assault_banner"), PersistentDataType.STRING)) {
            return true;
        }
        if (meta.hasCustomModelData() && meta.getCustomModelData() == 7005) {
            return true;
        }
        if (meta.hasDisplayName() && meta.getDisplayName().contains("Штурмовой Флаг")) {
            return true;
        }
        return false;
    }

    /**
     * Регистрация кастомного рецепта верстака 3x3 для штурмового флага.
     */
    public void registerRecipes() {
        try {
            NamespacedKey bannerKey = new NamespacedKey(plugin, "siege_assault_banner_recipe");
            try { Bukkit.removeRecipe(bannerKey); } catch (Throwable ignored) {}
            ShapedRecipe bannerRecipe = new ShapedRecipe(bannerKey, getAssaultBannerItem());
            bannerRecipe.setGroup("townysieges");
            bannerRecipe.shape("GTG", "GBG", " R ");
            bannerRecipe.setIngredient('G', Material.GOLD_INGOT);
            bannerRecipe.setIngredient('T', Material.TNT);
            bannerRecipe.setIngredient('B', Material.RED_BANNER);
            bannerRecipe.setIngredient('R', Material.BLAZE_ROD);
            Bukkit.addRecipe(bannerRecipe);
        } catch (Throwable ignored) {
        }
    }

    /**
     * Попытка установки штурмового флага игроком атакующей стороны.
     */
    public boolean placeAssaultBanner(Player player, Location loc) {
        if (player == null || loc == null) return false;

        String playerTown = plugin.getTownyHook().getPlayerTownName(player);
        if (playerTown == null) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Вы должны состоять в городе, чтобы ставить штурмовой флаг!");
            return false;
        }

        ChunkCoord coord = ChunkCoord.fromLocation(loc);
        if (coord == null) return false;

        // 1. Поиск активной осады или Войны Наций для атакующего
        SiegeCamp camp = null;
        NationWar war = plugin.getSiegeManager().getActiveNationWarForTown(playerTown);
        boolean isNationWar = false;

        if (war != null && war.isActiveAssault()) {
            isNationWar = true;
            // Ищем лагерь, привязанный к этой войне, либо лагерь города игрока
            for (String campId : war.getLinkedCampIds()) {
                SiegeCamp sc = plugin.getSiegeManager().getAllSieges().stream()
                        .filter(c -> c.getSiegeId().equalsIgnoreCase(campId))
                        .findFirst().orElse(null);
                if (sc != null && sc.isAdjacentToCamp(coord)) {
                    camp = sc;
                    break;
                }
            }
            if (camp == null) {
                // Берем любой активный осадный лагерь города игрока
                camp = plugin.getSiegeManager().getActiveSiegeForTown(playerTown);
            }
        } else {
            camp = plugin.getSiegeManager().getActiveSiegeForTown(playerTown);
        }

        if (camp == null) {
            player.sendMessage(ChatColor.RED + "[TownySieges] У вашей стороны нет активного осадного лагеря!");
            return false;
        }

        // Проверяем, что сейчас активна именно фаза ШТУРМА (2-часовая активная фаза с взрывами и пушками)
        boolean isAssaultPhase = camp.isActiveSiege() || (war != null && war.isActiveAssault());
        if (!isAssaultPhase) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Почанковый захват штурмовым флагом доступен ТОЛЬКО во время активного штурма (2ч фаза)!");
            player.sendMessage(ChatColor.YELLOW + "Текущая фаза: Подготовка. До штурма осталось: " + camp.getFormattedRemainingTime());
            return false;
        }

        // Проверяем, принадлежит ли игрок атакующей стороне
        boolean isAttacker = false;
        if (isNationWar && war != null) {
            isAttacker = war.isTownAttacker(playerTown);
        } else {
            isAttacker = playerTown.equalsIgnoreCase(camp.getAttackingTown());
        }

        if (!isAttacker && !player.hasPermission("townysieges.admin")) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Только игроки атакующей стороны могут ставить штурмовой флаг!");
            return false;
        }

        // 2. Проверка чанка:
        // Не должен быть уже захвачен лагерем
        if (camp.containsChunk(coord)) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Этот чанк уже входит в ваш осадный лагерь!");
            return false;
        }

        // На этом чанке не должно быть уже активного захвата
        if (activeCaptures.containsKey(coord)) {
            player.sendMessage(ChatColor.RED + "[TownySieges] На этом чанке уже идет активный штурмовой захват другим флагом!");
            return false;
        }

        // ГЛАВНОЕ ПРАВИЛО: ЧАНК ОБЯЗАН ГРАНИЧИТЬ С ЧАНКОМ ОСАДНОГО ЛАГЕРЯ!
        if (!camp.isAdjacentToCamp(coord)) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Нельзя поставить флаг! Чанк ОБЯЗАН непосредственно граничить с чанком вашего осадного лагеря.");
            player.sendMessage(ChatColor.GRAY + "Захватывайте территорию шаг за шагом (почанково), расширяя осадный плацдарм!");
            return false;
        }

        // Чанк может быть дикими землями (Wilderness) или территорией атакуемого города
        String townAtLoc = plugin.getTownyHook().getTownNameAt(loc);
        if (townAtLoc != null) {
            boolean isTargetTown = townAtLoc.equalsIgnoreCase(camp.getDefendingTown());
            if (isNationWar && war != null) {
                isTargetTown = war.isTownDefender(townAtLoc);
            }
            if (!isTargetTown) {
                player.sendMessage(ChatColor.RED + "[TownySieges] Нельзя ставить флаг на территории нейтрального города «" + townAtLoc + "»!");
                return false;
            }
        }

        // 3. Создание сессии захвата чанка
        long baseTimeSeconds = plugin.getConfig().getLong("capture.base-capture-duration-seconds", 300L); // 5 минут
        
        // Интеграция с Щитом TownyArchitecture для Homeblock
        boolean isHomeBlock = plugin.getTownyHook().isHomeBlock(coord, camp.getDefendingTown());
        long shieldBonus = 0;
        if (isHomeBlock) {
            shieldBonus = plugin.getTownyHook().getTownShieldBonusSeconds(camp.getDefendingTown());
            if (shieldBonus > 0) {
                player.sendMessage(ChatColor.GOLD + "[TownyArchitecture] 🛡 Обнаружен активный ЩИТ Мэрии! Время захвата увеличено на " + shieldBonus + " сек.");
            }
        }

        String captureId = "capture_" + coord.serialize() + "_" + System.currentTimeMillis();

        SiegeBannerCapture capture = new SiegeBannerCapture(
                captureId, coord, loc.clone(), camp.getSiegeId(),
                camp.getAttackingTown(), camp.getDefendingTown(),
                war != null ? war.getAttackerNation() : null,
                war != null ? war.getDefenderNation() : null,
                isNationWar, baseTimeSeconds, isHomeBlock, shieldBonus
        );

        activeCaptures.put(coord, capture);
        bannerBlockLocations.put(coord, loc.getBlock().getLocation());

        // Метаданные на блоке флага
        Block b = loc.getBlock();
        b.setMetadata("siege_banner_capture", new FixedMetadataValue(plugin, captureId));

        // ЗВУКОВЫЕ ЭФФЕКТЫ:
        // "при установке издает громкий звук"
        World world = loc.getWorld();
        if (world != null) {
            world.playSound(loc, Sound.ITEM_TOTEM_USE, 2.0f, 0.8f);
            world.playSound(loc, Sound.EVENT_RAID_HORN, 2.5f, 0.75f);
            world.playSound(loc, Sound.BLOCK_BEACON_ACTIVATE, 2.0f, 1.2f);
            world.playSound(loc, Sound.ENTITY_WITHER_SPAWN, 1.2f, 0.6f);
        }

        // ЛУЧ МАЯКА:
        // "и появляется идущий из него луч маяка"
        spawnBeaconEffect(loc);

        // Создание отдельного BossBar для этого чанка
        BossBar bar = Bukkit.createBossBar(
                ChatColor.RED + "⚔ Захват чанка: инициализация...",
                BarColor.RED,
                BarStyle.SOLID
        );
        bar.setProgress(0.0);
        bar.setVisible(true);
        captureBossBars.put(coord, bar);

        // Оповещения
        String broadcastMsg = ChatColor.translateAlternateColorCodes('&',
                "&4&l[ШТУРМОВОЙ ЗАХВАТ] &eИгрок &6" + player.getName() +
                " &eустановил &c&lШтурмовой Флаг &eна чанке &f[" + coord.getX() + ", " + coord.getZ() + "]&e! " +
                "Запущен почанковый захват осадным лагерем (&6" + camp.getAttackingTown() +
                " &e➔ &c" + camp.getDefendingTown() + "&e)! Базовое время: &f" + (baseTimeSeconds / 60) + " мин&e.");

        Bukkit.broadcastMessage(broadcastMsg);

        player.sendMessage(ChatColor.GREEN + "[TownySieges] ✔ Штурмовой флаг развернут! Удерживайте чанк: чем больше перевес атакующих над защитниками, тем быстрее падет чанк!");
        return true;
    }

    /**
     * Создание визуального луча маяка из точки флага до небес.
     */
    public void spawnBeaconEffect(Location loc) {
        World world = loc.getWorld();
        if (world == null) return;

        int startY = loc.getBlockY();
        int endY = Math.min(319, startY + 120);

        for (int y = startY; y <= endY; y += 2) {
            Location pLoc = new Location(world, loc.getBlockX() + 0.5, y, loc.getBlockZ() + 0.5);
            world.spawnParticle(Particle.END_ROD, pLoc, 2, 0.1, 0.5, 0.1, 0.02);
            world.spawnParticle(Particle.FLAME, pLoc, 1, 0.15, 0.3, 0.15, 0.01);
        }
    }

    /**
     * Ежесекундный тик системы почанкового захвата.
     */
    public void tick() {
        if (activeCaptures.isEmpty()) return;

        Iterator<Map.Entry<ChunkCoord, SiegeBannerCapture>> it = activeCaptures.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<ChunkCoord, SiegeBannerCapture> entry = it.next();
            ChunkCoord coord = entry.getKey();
            SiegeBannerCapture capture = entry.getValue();

            World world = Bukkit.getWorld(coord.getWorld());
            if (world == null) continue;

            // 1. Сканируем игроков на данном чанке
            int attackers = 0;
            int defenders = 0;
            List<Player> playersOnChunk = new ArrayList<>();

            for (Player p : world.getPlayers()) {
                if (!p.isOnline() || p.isDead() || p.getGameMode() == GameMode.SPECTATOR) continue;
                Location pLoc = p.getLocation();
                int pChunkX = pLoc.getBlockX() >> 4;
                int pChunkZ = pLoc.getBlockZ() >> 4;

                if (pChunkX == coord.getX() && pChunkZ == coord.getZ()) {
                    playersOnChunk.add(p);
                    String pTown = plugin.getTownyHook().getPlayerTownName(p);
                    if (pTown != null) {
                        if (capture.isNationWar()) {
                            NationWar war = plugin.getSiegeManager().getActiveNationWar(capture.getAttackerNation());
                            if (war != null) {
                                if (war.isTownAttacker(pTown)) attackers++;
                                else if (war.isTownDefender(pTown)) defenders++;
                            }
                        } else {
                            if (pTown.equalsIgnoreCase(capture.getAttackingTown())) attackers++;
                            else if (pTown.equalsIgnoreCase(capture.getDefendingTown())) defenders++;
                        }
                    }
                }
            }

            // 1.5 Интеграция с Щитом TownyArchitecture (динамическое обновление)
            if (capture.isHomeBlock()) {
                long standardBaseTime = plugin.getConfig().getLong("capture.base-capture-duration-seconds", 300L);
                long currentBonus = plugin.getTownyHook().getTownShieldBonusSeconds(capture.getDefendingTown());
                
                if (capture.getShieldBonusSeconds() > 0 && currentBonus == 0) {
                    // Щит упал!
                    Bukkit.broadcastMessage(ChatColor.translateAlternateColorCodes('&', 
                        "&4&l[ОСАДА] &cЩит Мэрии города &6" + capture.getDefendingTown() + " &cРУХНУЛ! Конструкция повреждена (>50%). Захват ускорен!"));
                }
                capture.updateShieldBonus(currentBonus, standardBaseTime);
            }

            // 2. Тикаем прогресс
            capture.tickSecond(attackers, defenders);

            // 3. Эффект луча маяка в небо
            Location bannerLoc = bannerBlockLocations.get(coord);
            if (bannerLoc != null && bannerLoc.getWorld() != null) {
                spawnBeaconEffect(bannerLoc);
            }

            // 4. Обновляем BossBar для игроков на чанке
            BossBar bar = captureBossBars.get(coord);
            if (bar != null) {
                // Синхронизируем зрителей боссбара: только игроки на чанке видят этот BossBar
                for (Player current : bar.getPlayers()) {
                    if (!playersOnChunk.contains(current)) {
                        bar.removePlayer(current);
                    }
                }
                for (Player p : playersOnChunk) {
                    if (!bar.getPlayers().contains(p)) {
                        bar.addPlayer(p);
                    }
                }

                double prog = Math.max(0.0, Math.min(1.0, capture.getProgress()));
                bar.setProgress(prog);

                int percent = (int) Math.round(capture.getProgress() * 100);
                long remSec = capture.getEstimatedRemainingSeconds();
                String remTimeStr = String.format("%02d:%02d", remSec / 60, remSec % 60);

                if (capture.getCurrentAttackers() >= capture.getCurrentDefenders()) {
                    bar.setColor(BarColor.RED);
                    bar.setStyle(BarStyle.SEGMENTED_10);
                    bar.setTitle(ChatColor.translateAlternateColorCodes('&',
                            "&4&l⚔ ШТУРМ ЧАНКА &7[" + coord.getX() + "," + coord.getZ() + "] " +
                            "&f| &c⚔ Атак.: &e" + attackers + " &7vs &9🛡 Защит.: &e" + defenders +
                            " &f| &cПрогресс: &e" + percent + "% &7(Осталось: &f" + remTimeStr + "&7)"));
                } else {
                    // Перевес защитников: откат назад!
                    bar.setColor(BarColor.BLUE);
                    bar.setStyle(BarStyle.SEGMENTED_10);
                    bar.setTitle(ChatColor.translateAlternateColorCodes('&',
                            "&9&l🛡 КОНТРАТАКА ЗАЩИТЫ! &7[" + coord.getX() + "," + coord.getZ() + "] " +
                            "&f| &9🛡 Защит.: &e" + defenders + " &7vs &c⚔ Атак.: &e" + attackers +
                            " &f| &eОткат назад: &b" + percent + "% &f(Контр-захват при <0%)"));
                }
            }

            // 5. Обработка успешного завершения захвата атакующими (100%)
            if (capture.isCompleted()) {
                handleCaptureSuccess(capture, coord);
                cleanupCapture(coord);
                it.remove();
                continue;
            }

            // 6. Обработка контр-захвата защитниками (прогресс стал отрицательным)
            if (capture.isRepelled()) {
                handleCaptureRepelled(capture, coord);
                cleanupCapture(coord);
                it.remove();
                continue;
            }
        }
    }

    /**
     * Успешный захват чанка атакующей стороной:
     * Чанк становится частью осадного лагеря, открывается возможность ставить флаги на соседние участки.
     */
    private void handleCaptureSuccess(SiegeBannerCapture capture, ChunkCoord coord) {
        SiegeCamp camp = plugin.getSiegeManager().getAllSieges().stream()
                .filter(c -> c.getSiegeId().equalsIgnoreCase(capture.getSiegeId()))
                .findFirst().orElse(null);

        World world = Bukkit.getWorld(coord.getWorld());
        Location center = new Location(world, (coord.getX() << 4) + 8, 80, (coord.getZ() << 4) + 8);

        String defendingTown = capture.getDefendingTown();
        String townAtCoord = plugin.getTownyHook().getTownNameAt(center);
        boolean isHomeBlock = capture.isHomeBlock() || plugin.getTownyHook().isHomeBlock(coord, defendingTown);
        boolean isDefendingTownBlock = isHomeBlock || (townAtCoord != null && townAtCoord.equalsIgnoreCase(defendingTown));

        if (camp != null) {
            plugin.getSiegeManager().addCapturedChunk(camp, coord);

            if (isDefendingTownBlock) {
                String attackingTown = capture.getAttackingTown();

                // 1. Annex all remaining chunks of defending town
                Set<ChunkCoord> defendingTownChunks = plugin.getTownyHook().getTownChunks(defendingTown);
                for (ChunkCoord tc : defendingTownChunks) {
                    if (!camp.containsChunk(tc)) {
                        plugin.getSiegeManager().addCapturedChunk(camp, tc);
                    }
                }
                plugin.getSiegeManager().saveData();

                // 2. Finalize victory: claim/outpost all chunks for attackingTown
                plugin.getSiegeManager().finalizeVictory(camp);
                plugin.getSiegeManager().unregisterSiege(camp);
                plugin.getCaptureManager().cancelCapturesForCamp(camp);

                // 3. TRANSFER TREASURY BANK BALANCE TO ATTACKING TOWN
                double transferredTreasury = plugin.getTownyHook().transferTownTreasury(defendingTown, attackingTown);

                // 4. TRANSFER BUILDINGS AND ENFORCE LIMITS IN TOWNYARCHITECTURE
                // We pass all chunks currently claimed by the camp (which now includes all of defending town's chunks)
                plugin.getTownyHook().transferCapturedBuildings(attackingTown, camp.getClaimedChunks());

                // 5. EVICT ALL RESIDENTS & COMPLETELY ERASE DEFENDING TOWN FROM TOWNY
                plugin.getTownyHook().destroyAndEraseTown(defendingTown);

                if (world != null) {
                    world.playSound(center, Sound.UI_TOAST_CHALLENGE_COMPLETE, 2.0f, 1.0f);
                    world.playSound(center, Sound.ENTITY_ENDER_DRAGON_GROWL, 1.5f, 0.8f);
                    world.spawnParticle(getParticleSafe("FIREWORK", "FIREWORKS_SPARK"), center, 100, 4.0, 4.0, 4.0, 0.2);
                }

                String totalMsg = ChatColor.translateAlternateColorCodes('&',
                        "&4&l[ПОЛНОЕ УНИЧТОЖЕНИЕ ГОРОДА!] &eОсадный лагерь города &6" + attackingTown +
                        " &eзахватил Домашний Чанк (Homeblock) города &c" + defendingTown +
                        "&e! Город «&c" + defendingTown + "&e» полностью УНИЧТОЖЕН и СТЕРТ из системы Towny!\n" +
                        "&a✔ Казна (&f" + String.format("%.0f", transferredTreasury) + " монет&a) переведена в банк города " + attackingTown + ".\n" +
                        "&a✔ Все жители города &c" + defendingTown + " &aизгнаны и стали кочевниками.\n" +
                        "&a✔ Все земли присоединены к победителям, а постройки приведены к лимитам (приоритет у победителей)!");

                Bukkit.broadcastMessage(totalMsg);
                return;
            }

            plugin.getSiegeManager().saveData();
        }

        if (world != null) {
            world.playSound(center, Sound.UI_TOAST_CHALLENGE_COMPLETE, 2.0f, 1.0f);
            world.playSound(center, Sound.ENTITY_ENDER_DRAGON_GROWL, 1.5f, 0.8f);
            world.spawnParticle(getParticleSafe("FIREWORK", "FIREWORKS_SPARK"), center, 80, 4.0, 4.0, 4.0, 0.2);
        }

        String successMsg = ChatColor.translateAlternateColorCodes('&',
                "&4&l[ЧАНК ЗАХВАЧЕН!] &eОсадный лагерь города &6" + capture.getAttackingTown() +
                " &eуспешно захватил чанк &f[" + coord.getX() + ", " + coord.getZ() + "]&e! " +
                "Чанк вошел в осадный лагерь. &aТеперь атакующие могут ставить Штурмовые Флаги на соседние с ним участки!");

        Bukkit.broadcastMessage(successMsg);
    }

    private Particle getParticleSafe(String primary, String fallback) {
        try {
            return Particle.valueOf(primary);
        } catch (Throwable ignored) {
            try {
                return Particle.valueOf(fallback);
            } catch (Throwable ignored2) {
                return Particle.FLAME;
            }
        }
    }

    /**
     * Контр-захват чанка защищающимся городом:
     * "когда становится отрицательным, чанк становится владением защищающегося города, неважно,
     * был ли он его чанком или был ничейным. если не граничит - становится аванпостом с официальным
     * статусом аванпоста в towny и всем вытекающим."
     */
    private void handleCaptureRepelled(SiegeBannerCapture capture, ChunkCoord coord) {
        String defendingTown = capture.getDefendingTown();
        World world = Bukkit.getWorld(coord.getWorld());
        Location center = new Location(world, (coord.getX() << 4) + 8, 80, (coord.getZ() << 4) + 8);

        // Проверяем, граничит ли чанк с основным городом защитников
        boolean isAdjacentToDefenderTown = plugin.getTownyHook().isChunkAdjacentToTown(coord, defendingTown);
        boolean becomesOutpost = !isAdjacentToDefenderTown;

        if (becomesOutpost) {
            // Становится официальным аванпостом (Outpost) в Towny!
            plugin.getTownyHook().createOutpostForTown(defendingTown, coord);
        } else {
            // Присоединяется как обычный чанк города
            plugin.getTownyHook().claimChunkForTown(defendingTown, coord);
        }

        if (world != null) {
            world.playSound(center, Sound.BLOCK_ANVIL_USE, 2.0f, 1.0f);
            world.playSound(center, Sound.EVENT_RAID_HORN, 2.5f, 1.2f);
            world.spawnParticle(getParticleSafe("HAPPY_VILLAGER", "VILLAGER_HAPPY"), center, 60, 3.0, 3.0, 3.0, 0.1);
        }

        String outpostNotice = becomesOutpost ?
                "&6&lЧанк объявлен официальным АВАНПОСТОМ (Outpost) города в Towny!" :
                "&aЧанк присоединен к территории города!";

        String repelledMsg = ChatColor.translateAlternateColorCodes('&',
                "&9&l[ТРИУМФ ОБОРОНЫ] &eЗащитники города &6" + defendingTown +
                " &eвыбили врага и контр-захватили чанк &f[" + coord.getX() + ", " + coord.getZ() + "]&e! " +
                "Прогресс штурма сведен в минус. Чанк перешел во владение обороняющегося города! " + outpostNotice);

        Bukkit.broadcastMessage(repelledMsg);
    }

    /**
     * Очистка BossBar и разрушение штурмового флага после окончания захвата.
     */
    private void cleanupCapture(ChunkCoord coord) {
        BossBar bar = captureBossBars.remove(coord);
        if (bar != null) {
            bar.removeAll();
            bar.setVisible(false);
        }

        Location loc = bannerBlockLocations.remove(coord);
        if (loc != null && loc.getBlock() != null) {
            Block b = loc.getBlock();
            if (b.getType() == Material.RED_BANNER || b.getType() == Material.RED_WALL_BANNER) {
                b.setType(Material.AIR);
            }
            b.removeMetadata("siege_banner_capture", plugin);
        }
    }

    public Collection<SiegeBannerCapture> getActiveCaptures() {
        return Collections.unmodifiableCollection(activeCaptures.values());
    }

    public SiegeBannerCapture getCaptureAt(ChunkCoord coord) {
        return activeCaptures.get(coord);
    }

    /**
     * Снятие всех активных штурмовых захватов и флагов для указанного лагеря
     * при расформировании лагеря мэром или принудительном завершении осады.
     */
    public void cancelCapturesForCamp(SiegeCamp camp) {
        if (camp == null) return;
        List<ChunkCoord> toCancel = new ArrayList<>();
        for (SiegeBannerCapture cap : activeCaptures.values()) {
            if (cap.getCampId().equalsIgnoreCase(camp.getSiegeId()) ||
                cap.getAttackingTown().equalsIgnoreCase(camp.getAttackingTown())) {
                toCancel.add(cap.getChunk());
            }
        }
        for (ChunkCoord cc : toCancel) {
            activeCaptures.remove(cc);
            cleanupCapture(cc);
        }
    }

    public void clearAll() {
        for (BossBar bar : captureBossBars.values()) {
            bar.removeAll();
            bar.setVisible(false);
        }
        captureBossBars.clear();
        activeCaptures.clear();
        bannerBlockLocations.clear();
    }
}
