import re

# 1. Update SiegeCannonManager.java
with open('tmp/towny-sieges/src/main/java/com/towny/sieges/cannon/SiegeCannonManager.java', 'r', encoding='utf-8') as f:
    cm_content = f.read()

# Add lastDropTime field if not present
if 'private final Map<UUID, Long> lastDropTime' not in cm_content:
    cm_content = cm_content.replace(
        'private final Map<UUID, AmmoType> gunnerAmmoSelection = new ConcurrentHashMap<>();',
        'private final Map<UUID, AmmoType> gunnerAmmoSelection = new ConcurrentHashMap<>();\n    private final Map<UUID, Long> lastDropTime = new ConcurrentHashMap<>();'
    )

# Add recordDropPress & isDropDebounced & cycleAmmo
methods_to_add = """    public void recordDropPress(Player player) {
        if (player == null) return;
        lastDropTime.put(player.getUniqueId(), System.currentTimeMillis());
    }

    public boolean isDropDebounced(Player player) {
        if (player == null) return false;
        Long t = lastDropTime.get(player.getUniqueId());
        return t != null && (System.currentTimeMillis() - t < 500L);
    }

    public void cycleAmmo(Player player) {
        if (player == null || !isMounted(player)) return;
        UUID uuid = player.getUniqueId();
        AmmoType current = getSelectedAmmo(player);
        AmmoType next = (current == AmmoType.REGULAR) ? AmmoType.ARMOR_PIERCING : AmmoType.REGULAR;
        setSelectedAmmo(player, next);

        // Mechanical reload sound effects
        player.playSound(player.getLocation(), Sound.BLOCK_IRON_TRAPDOOR_OPEN, 1.0f, 1.4f);
        player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_SNARE, 1.0f, 1.8f);

        int regCount = countRegularAmmo(player);
        int apCount = countArmorPiercingAmmo(player);

        String regStr = ChatColor.WHITE + "⚪ " + regCount + " шт.";
        String apStr = ChatColor.LIGHT_PURPLE + "🟣 " + apCount + " шт.";

        String aimPrefix = isAiming(player) ? ChatColor.AQUA + "🎯 [ПРИЦЕЛ] " : "";
        String activeTitle = (next == AmmoType.REGULAR) ?
            ChatColor.WHITE + "⚪ Обычное ядро (ОФ)" :
            ChatColor.LIGHT_PURPLE + "🟣 Бронебойное ядро (Обсидиан)";

        try {
            player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                new TextComponent(aimPrefix + ChatColor.GOLD + "Боеприпас: " + activeTitle +
                    ChatColor.YELLOW + " | Запас: [" + regStr + ChatColor.DARK_GRAY + " / " + apStr + ChatColor.YELLOW + "] | F: Смена | ЛКМ: Залп"));
        } catch (Exception ignored) {}

        player.sendMessage(ChatColor.GOLD + "[TownySieges] Переключен боеприпас: " + activeTitle +
            ChatColor.GRAY + " (В наличии: " + regCount + " обычных, " + apCount + " бронебойных). Нажмите F для смены.");
    }
"""

if 'public void cycleAmmo(' not in cm_content:
    # insert before registerRecipes
    cm_content = cm_content.replace('    public void registerRecipes() {', methods_to_add + '\n    public void registerRecipes() {')

# Update countRegularAmmo and countArmorPiercingAmmo to count both main inventory and off-hand
old_counts = """    public int countRegularAmmo(Player player) {
        if (player == null) return 0;
        int count = 0;
        for (ItemStack item : player.getInventory().getContents()) {
            if (isRegularAmmo(item)) {
                count += item.getAmount();
            }
        }
        return count;
    }

    public int countArmorPiercingAmmo(Player player) {
        if (player == null) return 0;
        int count = 0;
        for (ItemStack item : player.getInventory().getContents()) {
            if (isArmorPiercingAmmo(item)) {
                count += item.getAmount();
            }
        }
        return count;
    }"""

new_counts = """    public int countRegularAmmo(Player player) {
        if (player == null) return 0;
        int count = 0;
        for (ItemStack item : player.getInventory().getContents()) {
            if (isRegularAmmo(item)) {
                count += item.getAmount();
            }
        }
        ItemStack off = player.getInventory().getItemInOffHand();
        if (isRegularAmmo(off)) {
            count += off.getAmount();
        }
        return count;
    }

    public int countArmorPiercingAmmo(Player player) {
        if (player == null) return 0;
        int count = 0;
        for (ItemStack item : player.getInventory().getContents()) {
            if (isArmorPiercingAmmo(item)) {
                count += item.getAmount();
            }
        }
        ItemStack off = player.getInventory().getItemInOffHand();
        if (isArmorPiercingAmmo(off)) {
            count += off.getAmount();
        }
        return count;
    }"""

if old_counts in cm_content:
    cm_content = cm_content.replace(old_counts, new_counts)

# Update consumeRegularAmmo & consumeArmorPiercingAmmo to check offhand first, then inventory
old_consumes = """    public boolean consumeRegularAmmo(Player player) {
        if (player == null) return false;
        if (player.getGameMode() == GameMode.CREATIVE) return true;
        ItemStack[] contents = player.getInventory().getContents();
        for (int i = 0; i < contents.length; i++) {
            ItemStack item = contents[i];
            if (isRegularAmmo(item)) {
                if (item.getAmount() > 1) {
                    item.setAmount(item.getAmount() - 1);
                } else {
                    player.getInventory().setItem(i, null);
                }
                player.updateInventory();
                return true;
            }
        }
        return false;
    }

    public boolean consumeArmorPiercingAmmo(Player player) {
        if (player == null) return false;
        if (player.getGameMode() == GameMode.CREATIVE) return true;
        ItemStack[] contents = player.getInventory().getContents();
        for (int i = 0; i < contents.length; i++) {
            ItemStack item = contents[i];
            if (isArmorPiercingAmmo(item)) {
                if (item.getAmount() > 1) {
                    item.setAmount(item.getAmount() - 1);
                } else {
                    player.getInventory().setItem(i, null);
                }
                player.updateInventory();
                return true;
            }
        }
        return false;
    }"""

new_consumes = """    public boolean consumeRegularAmmo(Player player) {
        if (player == null) return false;
        if (player.getGameMode() == GameMode.CREATIVE) return true;
        ItemStack off = player.getInventory().getItemInOffHand();
        if (isRegularAmmo(off)) {
            if (off.getAmount() > 1) {
                off.setAmount(off.getAmount() - 1);
            } else {
                player.getInventory().setItemInOffHand(null);
            }
            player.updateInventory();
            return true;
        }
        ItemStack[] contents = player.getInventory().getContents();
        for (int i = 0; i < contents.length; i++) {
            ItemStack item = contents[i];
            if (isRegularAmmo(item)) {
                if (item.getAmount() > 1) {
                    item.setAmount(item.getAmount() - 1);
                } else {
                    player.getInventory().setItem(i, null);
                }
                player.updateInventory();
                return true;
            }
        }
        return false;
    }

    public boolean consumeArmorPiercingAmmo(Player player) {
        if (player == null) return false;
        if (player.getGameMode() == GameMode.CREATIVE) return true;
        ItemStack off = player.getInventory().getItemInOffHand();
        if (isArmorPiercingAmmo(off)) {
            if (off.getAmount() > 1) {
                off.setAmount(off.getAmount() - 1);
            } else {
                player.getInventory().setItemInOffHand(null);
            }
            player.updateInventory();
            return true;
        }
        ItemStack[] contents = player.getInventory().getContents();
        for (int i = 0; i < contents.length; i++) {
            ItemStack item = contents[i];
            if (isArmorPiercingAmmo(item)) {
                if (item.getAmount() > 1) {
                    item.setAmount(item.getAmount() - 1);
                } else {
                    player.getInventory().setItem(i, null);
                }
                player.updateInventory();
                return true;
            }
        }
        return false;
    }"""

if old_consumes in cm_content:
    cm_content = cm_content.replace(old_consumes, new_consumes)

# Update getAimingTool lore
old_aim_lore = """            meta.setDisplayName(ChatColor.GOLD + "⚔ Управление Мортирой");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.AQUA + "• ПКМ: Включить/выключить прицел (зум x2.0)");
            lore.add(ChatColor.GOLD + "• ЛКМ: Произвести выстрел из мортиры");
            lore.add(ChatColor.YELLOW + "• Вторая рука (Off-Hand): Заряжаемое ядро (⚪ / 🟣)");
            lore.add(ChatColor.RED + "• Shift: Покинуть место наводчика");
            meta.setLore(lore);"""

new_aim_lore = """            meta.setDisplayName(ChatColor.GOLD + "⚔ Управление Мортирой");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.AQUA + "• ПКМ: Включить/выключить оптический прицел (зум x2.0)");
            lore.add(ChatColor.GOLD + "• ЛКМ: Произвести выстрел из мортиры");
            lore.add(ChatColor.YELLOW + "• Клавиша F (смена руки): Переключить тип боеприпаса (⚪ / 🟣)");
            lore.add(ChatColor.GRAY + "• Нажатие Q заблокировано (выстрел не происходит)");
            lore.add(ChatColor.RED + "• Shift: Покинуть место наводчика");
            meta.setLore(lore);"""

if old_aim_lore in cm_content:
    cm_content = cm_content.replace(old_aim_lore, new_aim_lore)

# Update mount messages in mountGunner
old_mount_msg = """        ItemStack offHand = player.getInventory().getItemInOffHand();
        String ammoStatus;
        if (isRegularAmmo(offHand)) {
            ammoStatus = ChatColor.WHITE + "⚪ Обычное Ядро (Заряжено)";
        } else if (isArmorPiercingAmmo(offHand)) {
            ammoStatus = ChatColor.LIGHT_PURPLE + "🟣 Бронебойное Ядро (Заряжено)";
        } else {
            ammoStatus = ChatColor.RED + "❌ Не заряжена (положите ядро во 2-ю руку)";
        }

        player.sendMessage(ChatColor.GOLD + "══════════ Место Наводчика Мортиры ══════════");
        player.sendMessage(ChatColor.YELLOW + "• Вы зафиксированы на орудии! Вражеские лучники могут вести огонь по наводчику.");
        player.sendMessage(ChatColor.AQUA + "• Прицеливание: ПКМ (приближение зума x2.0).");
        player.sendMessage(ChatColor.GOLD + "• Зарядка: Поместите ядро (⚪ / 🟣) во ВТОРУЮ РУКУ (Off-Hand).");
        player.sendMessage(ChatColor.WHITE + "• Состояние: " + ammoStatus);
        player.sendMessage(ChatColor.GOLD + "• Выстрел: ЛКМ (сектор огня ±45°, перезарядка 4 сек).");
        player.sendMessage(ChatColor.RED + "• Покинуть орудие: нажмите Shift (приседание).");
        player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");
        player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_IRON, 1.0f, 0.7f);

        try {
            player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                new TextComponent(ChatColor.GOLD + "Мортира: " + ammoStatus + ChatColor.YELLOW + " | ПКМ: Прицел | ЛКМ: Залп"));
        } catch (Exception ignored) {}"""

new_mount_msg = """        setSelectedAmmo(player, AmmoType.REGULAR);
        int regCount = countRegularAmmo(player);
        int apCount = countArmorPiercingAmmo(player);
        String regStr = ChatColor.WHITE + "⚪ " + regCount + " шт.";
        String apStr = ChatColor.LIGHT_PURPLE + "🟣 " + apCount + " шт.";

        player.sendMessage(ChatColor.GOLD + "══════════ Место Наводчика Мортиры ══════════");
        player.sendMessage(ChatColor.YELLOW + "• Вы зафиксированы на орудии! Вражеские лучники могут вести огонь по наводчику.");
        player.sendMessage(ChatColor.AQUA + "• Прицеливание: ПКМ (приближение оптического зума x2.0).");
        player.sendMessage(ChatColor.YELLOW + "• Смена боеприпаса: клавиша F (смена руки) — выбор ⚪ Обычное / 🟣 Бронебойное.");
        player.sendMessage(ChatColor.WHITE + "• Боекомплект стрелка: " + regStr + ChatColor.GRAY + " | " + apStr);
        player.sendMessage(ChatColor.GOLD + "• Выстрел: ЛКМ (сектор огня ±45°, перезарядка 4 сек).");
        player.sendMessage(ChatColor.GRAY + "• Выстрел на Q заблокирован (защита от случайных залпов).");
        player.sendMessage(ChatColor.RED + "• Покинуть орудие: нажмите Shift (приседание).");
        player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");
        player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_IRON, 1.0f, 0.7f);

        try {
            player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                new TextComponent(ChatColor.GOLD + "Мортира: " + ChatColor.WHITE + "⚪ Обычное ядро" +
                    ChatColor.YELLOW + " | F: Смена снаряда | ПКМ: Прицел | ЛКМ: Залп"));
        } catch (Exception ignored) {}"""

if old_mount_msg in cm_content:
    cm_content = cm_content.replace(old_mount_msg, new_mount_msg)

# Update toggleAiming
old_toggle_aim = """        ItemStack offHand = player.getInventory().getItemInOffHand();
        String status = isRegularAmmo(offHand) ? ChatColor.WHITE + "⚪ Заряжено" :
                       (isArmorPiercingAmmo(offHand) ? ChatColor.LIGHT_PURPLE + "🟣 Бронебойное" : ChatColor.RED + "❌ Не заряжено");

        if (aimingGunners.contains(uuid)) {
            aimingGunners.remove(uuid);
            player.removePotionEffect(PotionEffectType.SLOW);
            player.playSound(player.getLocation(), Sound.ITEM_SPYGLASS_STOP_USING, 1.0f, 1.1f);
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                    new TextComponent(ChatColor.GRAY + "🎯 Прицел выключен | " + status + " | ЛКМ: Выстрел"));
            } catch (Exception ignored) {}
        } else {
            aimingGunners.add(uuid);
            player.addPotionEffect(new PotionEffect(PotionEffectType.SLOW, 72000, 3, false, false, false));
            player.playSound(player.getLocation(), Sound.ITEM_SPYGLASS_USE, 1.2f, 1.0f);
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                    new TextComponent(ChatColor.AQUA + "🎯 [ПРИЦЕЛ ВКЛ x2.0] | " + status + " | ЛКМ: Выстрел"));
            } catch (Exception ignored) {}
        }"""

new_toggle_aim = """        AmmoType curType = getSelectedAmmo(player);
        String ammoName = curType == AmmoType.REGULAR ? ChatColor.WHITE + "⚪ Обычное" : ChatColor.LIGHT_PURPLE + "🟣 Бронебойное";

        if (aimingGunners.contains(uuid)) {
            aimingGunners.remove(uuid);
            player.removePotionEffect(PotionEffectType.SLOW);
            player.playSound(player.getLocation(), Sound.ITEM_SPYGLASS_STOP_USING, 1.0f, 1.1f);
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                    new TextComponent(ChatColor.GRAY + "Прицел выкл | " + ammoName + ChatColor.YELLOW + " | F: Смена типа | ЛКМ: Выстрел"));
            } catch (Exception ignored) {}
        } else {
            aimingGunners.add(uuid);
            player.addPotionEffect(new PotionEffect(PotionEffectType.SLOW, 72000, 3, false, false, false));
            player.playSound(player.getLocation(), Sound.ITEM_SPYGLASS_USE, 1.2f, 1.0f);
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                    new TextComponent(ChatColor.AQUA + "🎯 [ПРИЦЕЛ ВКЛ x2.0] | " + ammoName + ChatColor.YELLOW + " | F: Смена типа | ЛКМ: Выстрел"));
            } catch (Exception ignored) {}
        }"""

if old_toggle_aim in cm_content:
    cm_content = cm_content.replace(old_toggle_aim, new_toggle_aim)

# Update fireCannon ammo check and consumption
# Look for: // 2. Check ammunition in player's OFF-HAND ... up to // 4. Consume ammunition directly from off-hand!
old_fire_ammo_chunk = """        // 2. Check ammunition in player's OFF-HAND
        ItemStack offHand = player.getInventory().getItemInOffHand();
        AmmoType ammoToUse = null;
        if (isRegularAmmo(offHand)) {
            ammoToUse = AmmoType.REGULAR;
        } else if (isArmorPiercingAmmo(offHand)) {
            ammoToUse = AmmoType.ARMOR_PIERCING;
        } else if (player.getGameMode() == GameMode.CREATIVE) {
            ammoToUse = AmmoType.REGULAR;
        }

        if (ammoToUse == null) {
            player.playSound(player.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 1.0f, 1.6f);
            player.playSound(player.getLocation(), Sound.ITEM_CROSSBOW_SHOOT, 0.8f, 0.6f);

            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                    new TextComponent(ChatColor.RED + "❌ Орудие не заряжено! Поместите ядро во 2-ю руку."));
            } catch (Exception ignored) {}

            player.sendMessage(ChatColor.RED + "[TownySieges] ❌ Орудие не заряжено! Для стрельбы поместите осадное ядро во 2-ю руку (Off-Hand).");
            return false;
        }

        // 3. Check horizontal ±45 degree sector constraint
        Float initYawObj = cannonInitialYaw.get(cannonLoc.getBlock().getLocation());
        float initYaw = initYawObj != null ? initYawObj : 0f;
        float playerYaw = player.getLocation().getYaw();
        float diffYaw = playerYaw - initYaw;
        while (diffYaw < -180f) diffYaw += 360f;
        while (diffYaw > 180f) diffYaw -= 360f;

        if (Math.abs(diffYaw) > 45.0f) {
            player.sendMessage(ChatColor.RED + "[TownySieges] ❌ Превышен угол поворота мортиры! Максимальный сектор обстрела: ±45°.");
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                    new TextComponent(ChatColor.RED + "❌ Вне сектора обстрела (±45°)! Поверните орудие к цели."));
            } catch (Exception ignored) {}
            player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASS, 1.0f, 0.5f);
            return false;
        }

        // 4. Consume ammunition directly from off-hand!
        if (player.getGameMode() != GameMode.CREATIVE) {
            if (offHand.getAmount() > 1) {
                offHand.setAmount(offHand.getAmount() - 1);
            } else {
                offHand = new ItemStack(Material.AIR);
            }
            player.getInventory().setItemInOffHand(offHand);
            player.updateInventory();
        }"""

new_fire_ammo_chunk = """        // 2. Check ammunition according to gunner's selected ammo (cycled via F key)
        AmmoType ammoToUse = getSelectedAmmo(player);
        boolean isCreative = player.getGameMode() == GameMode.CREATIVE;
        int currentCount = (ammoToUse == AmmoType.REGULAR) ? countRegularAmmo(player) : countArmorPiercingAmmo(player);

        if (!isCreative && currentCount <= 0) {
            // Check if player has the alternative type
            AmmoType alternative = (ammoToUse == AmmoType.REGULAR) ? AmmoType.ARMOR_PIERCING : AmmoType.REGULAR;
            int altCount = (alternative == AmmoType.REGULAR) ? countRegularAmmo(player) : countArmorPiercingAmmo(player);

            player.playSound(player.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 1.0f, 1.6f);
            player.playSound(player.getLocation(), Sound.ITEM_CROSSBOW_SHOOT, 0.8f, 0.6f);

            if (altCount > 0) {
                String altName = alternative == AmmoType.REGULAR ? "⚪ Обычные ядра" : "🟣 Бронебойные ядра";
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                        new TextComponent(ChatColor.RED + "❌ Нет выбранных ядер! Нажмите [F] для выбора: " + altName + " (" + altCount + " шт.)"));
                } catch (Exception ignored) {}
                player.sendMessage(ChatColor.RED + "[TownySieges] ❌ Закончились " + ammoToUse.getDisplayName() + "! Нажмите клавишу смены руки [F], чтобы переключить на " + altName + " (" + altCount + " шт. в инвентаре).");
            } else {
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                        new TextComponent(ChatColor.RED + "❌ Боекомплект пуст! Вам нужны осадные ядра для стрельбы."));
                } catch (Exception ignored) {}
                player.sendMessage(ChatColor.RED + "[TownySieges] ❌ Боекомплект пуст! Для стрельбы требуются ядра в инвентаре (⚪ Обычные или 🟣 Бронебойные).");
            }
            return false;
        }

        // 3. Check horizontal ±45 degree sector constraint
        Float initYawObj = cannonInitialYaw.get(cannonLoc.getBlock().getLocation());
        float initYaw = initYawObj != null ? initYawObj : 0f;
        float playerYaw = player.getLocation().getYaw();
        float diffYaw = playerYaw - initYaw;
        while (diffYaw < -180f) diffYaw += 360f;
        while (diffYaw > 180f) diffYaw -= 360f;

        if (Math.abs(diffYaw) > 45.0f) {
            player.sendMessage(ChatColor.RED + "[TownySieges] ❌ Превышен угол поворота мортиры! Максимальный сектор обстрела: ±45°.");
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                    new TextComponent(ChatColor.RED + "❌ Вне сектора обстрела (±45°)! Поверните орудие к цели."));
            } catch (Exception ignored) {}
            player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASS, 1.0f, 0.5f);
            return false;
        }

        // 4. Consume ammunition (from offhand or main inventory)
        if (!isCreative) {
            boolean consumed = (ammoToUse == AmmoType.REGULAR) ? consumeRegularAmmo(player) : consumeArmorPiercingAmmo(player);
            if (!consumed) {
                return false;
            }
        }"""

if old_fire_ammo_chunk in cm_content:
    cm_content = cm_content.replace(old_fire_ammo_chunk, new_fire_ammo_chunk)
    print("Replaced fire ammo chunk in SiegeCannonManager")
else:
    print("Could not find old_fire_ammo_chunk directly, trying regex")

# Update reload runnable in fireCannon to reference F key
old_runnable_chunk = """                ItemStack currentOffHand = player.getInventory().getItemInOffHand();
                boolean hasNextShell = isRegularAmmo(currentOffHand) || isArmorPiercingAmmo(currentOffHand) || player.getGameMode() == GameMode.CREATIVE;

                if (elapsed >= SHOT_COOLDOWN_MS) {
                    try {
                        String aimPrefix = isAiming(player) ? ChatColor.AQUA + "🎯 [ПРИЦЕЛ] " : "";
                        if (hasNextShell) {
                            String shellName = isRegularAmmo(currentOffHand) ? ChatColor.WHITE + "⚪ Обычное" : ChatColor.LIGHT_PURPLE + "🟣 Бронебойное";
                            if (player.getGameMode() == GameMode.CREATIVE && !hasNextShell) shellName = ChatColor.WHITE + "⚪ Обычное (Креатив)";
                            player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                                new TextComponent(aimPrefix + ChatColor.GREEN + "✔ Мортира заряжена! [" + shellName + "]" + ChatColor.YELLOW + " | ЛКМ: Выстрел"));
                            player.playSound(player.getLocation(), Sound.BLOCK_IRON_DOOR_OPEN, 0.8f, 1.4f);
                            player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_PLING, 1.0f, 1.5f);
                        } else {
                            player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                                new TextComponent(aimPrefix + ChatColor.RED + "❌ Орудие не заряжено! Поместите новое ядро во 2-ю руку."));
                            player.playSound(player.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 0.8f, 1.2f);
                        }
                    } catch (Exception ignored) {}
                    cancel();
                    return;
                }"""

new_runnable_chunk = """                AmmoType curSelected = getSelectedAmmo(player);
                int count = (curSelected == AmmoType.REGULAR) ? countRegularAmmo(player) : countArmorPiercingAmmo(player);
                boolean hasNextShell = count > 0 || player.getGameMode() == GameMode.CREATIVE;

                if (elapsed >= SHOT_COOLDOWN_MS) {
                    try {
                        String aimPrefix = isAiming(player) ? ChatColor.AQUA + "🎯 [ПРИЦЕЛ] " : "";
                        String shellName = curSelected == AmmoType.REGULAR ? ChatColor.WHITE + "⚪ Обычное" : ChatColor.LIGHT_PURPLE + "🟣 Бронебойное";
                        if (hasNextShell) {
                            player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                                new TextComponent(aimPrefix + ChatColor.GREEN + "✔ Мортира заряжена! [" + shellName + " (" + count + " шт.)]" +
                                    ChatColor.YELLOW + " | F: Смена типа | ЛКМ: Залп"));
                            player.playSound(player.getLocation(), Sound.BLOCK_IRON_DOOR_OPEN, 0.8f, 1.4f);
                            player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_PLING, 1.0f, 1.5f);
                        } else {
                            player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                                new TextComponent(aimPrefix + ChatColor.RED + "❌ Орудие не заряжено! Закончились ядра выбранного типа. Нажмите F для смены."));
                            player.playSound(player.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 0.8f, 1.2f);
                        }
                    } catch (Exception ignored) {}
                    cancel();
                    return;
                }"""

if old_runnable_chunk in cm_content:
    cm_content = cm_content.replace(old_runnable_chunk, new_runnable_chunk)
    print("Replaced reload runnable in SiegeCannonManager")

with open('tmp/towny-sieges/src/main/java/com/towny/sieges/cannon/SiegeCannonManager.java', 'w', encoding='utf-8') as f:
    f.write(cm_content)

print("SiegeCannonManager updated successfully!")

# 2. Update SiegeProtectionListener.java
with open('tmp/towny-sieges/src/main/java/com/towny/sieges/listener/SiegeProtectionListener.java', 'r', encoding='utf-8') as f:
    spl_content = f.read()

# Make sure onPlayerInteract checks isDropDebounced
old_interact_start = """        // 1. If player is seated on a cannon:
        if (cannonManager.isMounted(player)) {
            event.setCancelled(true);
            Long mountTime = cannonManager.getLastMountTime(player.getUniqueId());
            if (mountTime != null && System.currentTimeMillis() - mountTime < 600L) {
                return; // Lockout during mount transition
            }"""

new_interact_start = """        // 1. If player is seated on a cannon:
        if (cannonManager.isMounted(player)) {
            event.setCancelled(true);
            Long mountTime = cannonManager.getLastMountTime(player.getUniqueId());
            if (mountTime != null && System.currentTimeMillis() - mountTime < 600L) {
                return; // Lockout during mount transition
            }

            // Strictly ignore ghost click packets fired right after pressing Q (Drop key)
            if (cannonManager.isDropDebounced(player)) {
                return;
            }"""

if old_interact_start in spl_content:
    spl_content = spl_content.replace(old_interact_start, new_interact_start)
    print("Added isDropDebounced check to onPlayerInteract")

# Update onPlayerDropItem to recordDropPress and ensure NO shooting
old_drop = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerDropItem(PlayerDropItemEvent event) {
        if (cannonManager.isMounted(event.getPlayer())) {
            event.setCancelled(true);
        }
    }"""

new_drop = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerDropItem(PlayerDropItemEvent event) {
        Player player = event.getPlayer();
        if (cannonManager.isMounted(player)) {
            event.setCancelled(true);
            // Record drop key press so any following ghost click is strictly suppressed
            cannonManager.recordDropPress(player);
            // NO fireCannon() here under any circumstances!
        }
    }"""

if old_drop in spl_content:
    spl_content = spl_content.replace(old_drop, new_drop)
    print("Updated onPlayerDropItem to debounce drop and never fire")

# Update onPlayerSwapHandItems to cycleAmmo
old_swap = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerSwapHandItems(PlayerSwapHandItemsEvent event) {
        Player player = event.getPlayer();
        if (cannonManager.isMounted(player)) {
            // Prevent swapping out the main hand control tool with F key while mounted
            event.setCancelled(true);
        }
    }"""

new_swap = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerSwapHandItems(PlayerSwapHandItemsEvent event) {
        Player player = event.getPlayer();
        if (cannonManager.isMounted(player)) {
            event.setCancelled(true);
            // Cycle ammunition between Regular and Armor-Piercing on Hand Swap (F key)
            cannonManager.cycleAmmo(player);
        }
    }"""

if old_swap in spl_content:
    spl_content = spl_content.replace(old_swap, new_swap)
    print("Updated onPlayerSwapHandItems to call cycleAmmo!")

with open('tmp/towny-sieges/src/main/java/com/towny/sieges/listener/SiegeProtectionListener.java', 'w', encoding='utf-8') as f:
    f.write(spl_content)

print("SiegeProtectionListener updated successfully!")

# 3. Update SiegeCommand.java for /siege switch or /siege ammo switch
with open('tmp/towny-sieges/src/main/java/com/towny/sieges/command/SiegeCommand.java', 'r', encoding='utf-8') as f:
    cmd_content = f.read()

old_switch1 = """            if (args.length >= 2 && (args[1].equalsIgnoreCase("switch") || args[1].equalsIgnoreCase("toggle"))) {
                sender.sendMessage(ChatColor.GOLD + "[TownySieges] Зарядка происходит автоматически из 2-й руки (Off-Hand)!");
                sender.sendMessage(ChatColor.YELLOW + "Поместите осадное ядро (⚪ / 🟣) во 2-ю руку через инвентарь (клавиша E).");
                return true;
            }"""

new_switch1 = """            if (args.length >= 2 && (args[1].equalsIgnoreCase("switch") || args[1].equalsIgnoreCase("toggle"))) {
                if (sender instanceof Player) {
                    Player p = (Player) sender;
                    if (plugin.getCannonManager().isMounted(p)) {
                        plugin.getCannonManager().cycleAmmo(p);
                        return true;
                    }
                }
                sender.sendMessage(ChatColor.GOLD + "[TownySieges] Смена боеприпасов: нажмите клавишу смены руки [F] сидя за орудием!");
                return true;
            }"""

old_switch2 = """        if (args[0].equalsIgnoreCase("switch") || args[0].equalsIgnoreCase("toggle")) {
            sender.sendMessage(ChatColor.GOLD + "[TownySieges] Зарядка происходит автоматически из 2-й руки (Off-Hand)!");
            sender.sendMessage(ChatColor.YELLOW + "Поместите осадное ядро (⚪ / 🟣) во 2-ю руку через инвентарь (клавиша E).");
            return true;
        }"""

new_switch2 = """        if (args[0].equalsIgnoreCase("switch") || args[0].equalsIgnoreCase("toggle")) {
            if (sender instanceof Player) {
                Player p = (Player) sender;
                if (plugin.getCannonManager().isMounted(p)) {
                    plugin.getCannonManager().cycleAmmo(p);
                    return true;
                }
            }
            sender.sendMessage(ChatColor.GOLD + "[TownySieges] Смена боеприпасов: нажмите клавишу смены руки [F] сидя за орудием!");
            return true;
        }"""

if old_switch1 in cmd_content:
    cmd_content = cmd_content.replace(old_switch1, new_switch1)
    print("Updated /siege ammo switch in SiegeCommand")
if old_switch2 in cmd_content:
    cmd_content = cmd_content.replace(old_switch2, new_switch2)
    print("Updated /siege switch in SiegeCommand")

with open('tmp/towny-sieges/src/main/java/com/towny/sieges/command/SiegeCommand.java', 'w', encoding='utf-8') as f:
    f.write(cmd_content)

print("SiegeCommand updated successfully!")
