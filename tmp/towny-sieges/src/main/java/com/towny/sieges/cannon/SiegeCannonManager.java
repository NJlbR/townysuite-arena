package com.towny.sieges.cannon;

import com.towny.sieges.TownySiegesPlugin;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.entity.*;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.ShapedRecipe;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.metadata.FixedMetadataValue;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.util.Transformation;
import org.bukkit.util.Vector;
import org.joml.AxisAngle4f;
import org.joml.Vector3f;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SiegeCannonManager {

    public enum AmmoType {
        REGULAR("⚪ Обычное ядро", ChatColor.WHITE, 7003),
        ARMOR_PIERCING("🟣 Бронебойное [Обсидиан]", ChatColor.LIGHT_PURPLE, 7004);

        private final String displayName;
        private final ChatColor color;
        private final int modelData;

        AmmoType(String displayName, ChatColor color, int modelData) {
            this.displayName = displayName;
            this.color = color;
            this.modelData = modelData;
        }

        public String getDisplayName() {
            return displayName;
        }

        public ChatColor getColor() {
            return color;
        }

        public int getModelData() {
            return modelData;
        }
    }

    private final TownySiegesPlugin plugin;
    private final Map<UUID, Location> mountedGunners = new ConcurrentHashMap<>();
    private final Map<UUID, ArmorStand> gunnerSeats = new ConcurrentHashMap<>();
    private final Map<UUID, Long> lastShotTime = new ConcurrentHashMap<>();
    private final Map<UUID, Long> lastMountTime = new ConcurrentHashMap<>();
    private final Map<UUID, ItemStack> savedHandItems = new ConcurrentHashMap<>();
    private final Map<UUID, ItemStack> savedOffHandItems = new ConcurrentHashMap<>();
    private final Set<UUID> aimingGunners = ConcurrentHashMap.newKeySet();
    private final Map<UUID, AmmoType> gunnerAmmoSelection = new ConcurrentHashMap<>();
    private final Map<UUID, Long> lastDropTime = new ConcurrentHashMap<>();
    private final Map<Location, String> deployedCannons = new ConcurrentHashMap<>();
    private final Map<Location, Float> cannonInitialYaw = new ConcurrentHashMap<>();

    public static final long SHOT_COOLDOWN_MS = 10000L; // 10 seconds reload delay

    public SiegeCannonManager(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    public ItemStack getCannonItem() {
        ItemStack item = new ItemStack(Material.DISPENSER, 1);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.GOLD + "⚔ Осадная Мортира (Nexo/Oraxen Model)");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Тяжелое осадное орудие для пробития городских стен.");
            lore.add(ChatColor.DARK_GRAY + "Тип: Нестакаемый осадный механизм [1 шт / слот]");
            lore.add(ChatColor.YELLOW + "Установите на твердую поверхность для развертывания.");
            lore.add(ChatColor.YELLOW + "Ограничение поворота: ±45° | Дуговая баллистика");
            lore.add(ChatColor.YELLOW + "Перезарядка: 10 сек (с таймером в Action Bar)");
            lore.add(ChatColor.AQUA + "ПКМ по мортире: занять место наводчика сверху.");
            lore.add(ChatColor.AQUA + "ПКМ в седле: оптический прицел (зум x2.0).");
            lore.add(ChatColor.GREEN + "Вторая рука (Off-Hand): поместите ядро (⚪/🟣) для зарядки.");
            lore.add(ChatColor.GOLD + "ЛКМ в седле: произвести выстрел из орудия.");
            lore.add(ChatColor.RED + "Shift: слезть | Shift+ЛКМ/ПКМ: демонтировать.");
            meta.setLore(lore);
            meta.setCustomModelData(7001);
            meta.getPersistentDataContainer().set(
                new NamespacedKey(plugin, "cannon_uid"),
                PersistentDataType.STRING,
                UUID.randomUUID().toString()
            );
            item.setItemMeta(meta);
        }
        return item;
    }

    public ItemStack getRegularAmmoItem() {
        ItemStack item = new ItemStack(Material.FIREWORK_STAR, 1);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.WHITE + "⚪ Осадное Ядро (Обычное)");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Тяжелое чугунное ядро для осадной мортиры.");
            lore.add(ChatColor.DARK_GRAY + "Тип: Нестакаемый боеприпас [1 шт / слот]");
            lore.add(ChatColor.YELLOW + "Действие: Разрушает стандартные городские стены.");
            lore.add(ChatColor.RED + "Не пробивает обсидиановую броню и бастионы.");
            lore.add(ChatColor.AQUA + "Используется наводчиком из инвентаря при выстреле.");
            meta.setLore(lore);
            meta.setCustomModelData(7003);
            meta.getPersistentDataContainer().set(
                new NamespacedKey(plugin, "ammo_uid"),
                PersistentDataType.STRING,
                UUID.randomUUID().toString()
            );
            meta.getPersistentDataContainer().set(
                new NamespacedKey(plugin, "ammo_type"),
                PersistentDataType.STRING,
                "REGULAR"
            );
            item.setItemMeta(meta);
        }
        return item;
    }

    public ItemStack getArmorPiercingAmmoItem() {
        ItemStack item = new ItemStack(Material.NETHERITE_SCRAP, 1);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.LIGHT_PURPLE + "🟣 Бронебойное Ядро (Пробитие Обсидиана)");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.LIGHT_PURPLE + "Сверхтяжелое бронебойное ядро с алмазно-обсидиановым сердечником.");
            lore.add(ChatColor.DARK_GRAY + "Тип: Нестакаемый бронебойный боеприпас [1 шт / слот]");
            lore.add(ChatColor.GOLD + "✦ ПРОБИВАЕТ ОБСИДИАН в радиусе 3.2 блоков во время штурма!");
            lore.add(ChatColor.YELLOW + "Тяжелый крафт: Алмазы, Обсидиан, Незерит, ТНТ.");
            lore.add(ChatColor.AQUA + "Используется наводчиком из инвентаря при выстреле.");
            meta.setLore(lore);
            meta.setCustomModelData(7004);
            meta.getPersistentDataContainer().set(
                new NamespacedKey(plugin, "ammo_uid"),
                PersistentDataType.STRING,
                UUID.randomUUID().toString()
            );
            meta.getPersistentDataContainer().set(
                new NamespacedKey(plugin, "ammo_type"),
                PersistentDataType.STRING,
                "ARMOR_PIERCING"
            );
            item.setItemMeta(meta);
        }
        return item;
    }

    public ItemStack createAmmoItem(boolean isAp) {
        return isAp ? getArmorPiercingAmmoItem() : getRegularAmmoItem();
    }

    public ItemStack getAimingTool() {
        ItemStack item = new ItemStack(Material.WARPED_FUNGUS_ON_A_STICK, 1);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.GOLD + "⚔ Управление Мортирой");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.AQUA + "• ПКМ: Включить/выключить оптический прицел (зум x2.0)");
            lore.add(ChatColor.GOLD + "• ЛКМ: Произвести выстрел из мортиры");
            lore.add(ChatColor.YELLOW + "• Клавиша F (смена руки): Переключить тип боеприпаса (⚪ / 🟣)");
            lore.add(ChatColor.GRAY + "• Нажатие Q заблокировано (выстрел не происходит)");
            lore.add(ChatColor.RED + "• Shift: Покинуть место наводчика");
            meta.setLore(lore);
            meta.setCustomModelData(7002);
            meta.getPersistentDataContainer().set(
                new NamespacedKey(plugin, "aiming_tool"),
                PersistentDataType.STRING,
                "true"
            );
            item.setItemMeta(meta);
        }
        return item;
    }

    public boolean isAimingTool(ItemStack item) {
        if (item == null || !item.hasItemMeta()) return false;
        ItemMeta meta = item.getItemMeta();
        if (meta.getPersistentDataContainer().has(new NamespacedKey(plugin, "aiming_tool"), PersistentDataType.STRING)) {
            return true;
        }
        if (meta.hasDisplayName() && meta.getDisplayName().contains("Управление Мортирой")) {
            return true;
        }
        if (meta.hasCustomModelData() && meta.getCustomModelData() == 7002) {
            return true;
        }
        return false;
    }

    public boolean isCannonItem(ItemStack item) {
        if (item == null) return false;
        if (item.getType() != Material.DISPENSER) return false;
        if (!item.hasItemMeta()) return false;
        ItemMeta meta = item.getItemMeta();
        if (meta.getPersistentDataContainer().has(new NamespacedKey(plugin, "cannon_uid"), PersistentDataType.STRING)) {
            return true;
        }
        if (meta.hasDisplayName()) {
            String dn = ChatColor.stripColor(meta.getDisplayName());
            if (dn.contains("Осадная Пушка") || dn.contains("Осадная Мортира") || dn.contains("Siege Cannon")) {
                return true;
            }
        }
        if (meta.hasCustomModelData()) {
            int cmd = meta.getCustomModelData();
            return cmd == 7001 || cmd == 99201;
        }
        return false;
    }

    public boolean isRegularAmmo(ItemStack item) {
        if (item == null) return false;
        if (!item.hasItemMeta()) return false;
        ItemMeta meta = item.getItemMeta();
        if (meta.getPersistentDataContainer().has(new NamespacedKey(plugin, "ammo_type"), PersistentDataType.STRING)) {
            String type = meta.getPersistentDataContainer().get(new NamespacedKey(plugin, "ammo_type"), PersistentDataType.STRING);
            if ("REGULAR".equalsIgnoreCase(type)) return true;
        }
        if (meta.hasDisplayName()) {
            String dn = ChatColor.stripColor(meta.getDisplayName());
            if (dn.contains("Осадное Ядро (Обычное)") || dn.contains("Regular Cannonball")) return true;
        }
        if (meta.hasCustomModelData() && meta.getCustomModelData() == 7003) return true;
        return false;
    }

    public boolean isArmorPiercingAmmo(ItemStack item) {
        if (item == null) return false;
        if (!item.hasItemMeta()) return false;
        ItemMeta meta = item.getItemMeta();
        if (meta.getPersistentDataContainer().has(new NamespacedKey(plugin, "ammo_type"), PersistentDataType.STRING)) {
            String type = meta.getPersistentDataContainer().get(new NamespacedKey(plugin, "ammo_type"), PersistentDataType.STRING);
            if ("ARMOR_PIERCING".equalsIgnoreCase(type)) return true;
        }
        if (meta.hasDisplayName()) {
            String dn = ChatColor.stripColor(meta.getDisplayName());
            if (dn.contains("Бронебойное Ядро") || dn.contains("Armor-Piercing")) return true;
        }
        if (meta.hasCustomModelData() && meta.getCustomModelData() == 7004) return true;
        return false;
    }

    public boolean isAnySiegeAmmoOrCannon(ItemStack item) {
        return isCannonItem(item) || isRegularAmmo(item) || isArmorPiercingAmmo(item);
    }

    public int countRegularAmmo(Player player) {
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
    }

    public boolean consumeRegularAmmo(Player player) {
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
    }

    public AmmoType getSelectedAmmo(Player player) {
        if (player == null) return AmmoType.REGULAR;
        return gunnerAmmoSelection.getOrDefault(player.getUniqueId(), AmmoType.REGULAR);
    }

    public void setSelectedAmmo(Player player, AmmoType ammoType) {
        if (player == null) return;
        gunnerAmmoSelection.put(player.getUniqueId(), ammoType);
    }



    public void recordDropPress(Player player) {
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

    public void registerRecipes() {
        // 1. Mortar Crafting Recipe
        try {
            NamespacedKey mortarKey = new NamespacedKey(plugin, "siege_mortar");
            try { Bukkit.removeRecipe(mortarKey); } catch (Throwable ignored) {}
            ShapedRecipe mortarRecipe = new ShapedRecipe(mortarKey, getCannonItem());
            mortarRecipe.setGroup("townysieges");
            mortarRecipe.shape("IDI", "SCS", "LLL");
            mortarRecipe.setIngredient('I', Material.IRON_BLOCK);
            mortarRecipe.setIngredient('D', Material.DISPENSER);
            mortarRecipe.setIngredient('S', Material.STONE);
            mortarRecipe.setIngredient('C', Material.CAULDRON);
            mortarRecipe.setIngredient('L', Material.OAK_LOG);
            Bukkit.addRecipe(mortarRecipe);
        } catch (Throwable ignored) {
        }

        // 2. Regular Cannonball Recipe
        try {
            NamespacedKey regKey = new NamespacedKey(plugin, "siege_cannonball_regular");
            try { Bukkit.removeRecipe(regKey); } catch (Throwable ignored) {}
            ShapedRecipe regRecipe = new ShapedRecipe(regKey, getRegularAmmoItem());
            regRecipe.setGroup("townysieges");
            regRecipe.shape("III", "IGI", "CGC");
            regRecipe.setIngredient('I', Material.IRON_INGOT);
            regRecipe.setIngredient('G', Material.GUNPOWDER);
            regRecipe.setIngredient('C', Material.COAL);
            Bukkit.addRecipe(regRecipe);
        } catch (Throwable ignored) {
        }

        // 3. Armor-Piercing Cannonball Recipe (Penetrates Obsidian)
        try {
            NamespacedKey apKey = new NamespacedKey(plugin, "siege_cannonball_ap");
            try { Bukkit.removeRecipe(apKey); } catch (Throwable ignored) {}
            ShapedRecipe apRecipe = new ShapedRecipe(apKey, getArmorPiercingAmmoItem());
            apRecipe.setGroup("townysieges");
            apRecipe.shape("DOD", "NTO", "DGD");
            apRecipe.setIngredient('D', Material.DIAMOND);
            apRecipe.setIngredient('O', Material.OBSIDIAN);
            apRecipe.setIngredient('N', Material.NETHERITE_SCRAP);
            apRecipe.setIngredient('T', Material.TNT);
            apRecipe.setIngredient('G', Material.GUNPOWDER);
            Bukkit.addRecipe(apRecipe);
        } catch (Throwable ignored) {
        }
    }

    public boolean deployCannon(Player player, Location loc) {
        if (player == null || loc == null) return false;

        String town = plugin.getTownyHook().getPlayerTownName(player);
        if (town == null && !player.hasPermission("townysieges.admin")) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Вы должны состоять в городе для установки осадной пушки!");
            return false;
        }

        com.towny.sieges.model.ChunkCoord coord = com.towny.sieges.model.ChunkCoord.fromLocation(loc);
        com.towny.sieges.model.SiegeCamp camp = null;
        if (town != null) {
            camp = plugin.getSiegeManager().getActiveSiegeForTown(town);
        }

        if (camp == null && !player.hasPermission("townysieges.admin")) {
            player.sendMessage(ChatColor.RED + "[TownySieges] У вашего города нет активного осадного лагеря!");
            return false;
        }

        if (camp != null && !player.hasPermission("townysieges.admin")) {
            boolean isValidChunk = camp.getInitialCampChunk().equals(coord) || camp.containsChunk(coord);
            if (!isValidChunk) {
                player.sendMessage(ChatColor.RED + "[TownySieges] ❌ Мортиры можно устанавливать ТОЛЬКО в чанках осадного лагеря, главном форпосте или присоединенных захваченных чанках!");
                return false;
            }
        }

        Location blockLoc = loc.getBlock().getLocation();
        if (deployedCannons.containsKey(blockLoc)) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Здесь уже установлена осадная пушка!");
            return false;
        }

        Block b = blockLoc.getBlock();
        b.setType(Material.BARRIER);
        b.setMetadata("siege_cannon", new FixedMetadataValue(plugin, town != null ? town : "Admin"));
        deployedCannons.put(blockLoc, town != null ? town : "Admin");

        float initialYaw = player.getLocation().getYaw();
        cannonInitialYaw.put(blockLoc, initialYaw);

        spawnCannonVisuals(blockLoc, initialYaw);

        Location holoLoc = blockLoc.clone().add(0.5, 1.85, 0.5);
        loc.getWorld().spawn(holoLoc, ArmorStand.class, (as) -> {
            as.setVisible(false);
            as.setMarker(true);
            as.setGravity(false);
            as.setCustomName(ChatColor.GOLD + "⚔ Осадная Мортира [" + (town != null ? town : "Армия") + "]");
            as.setCustomNameVisible(true);
            as.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
        });

        player.sendMessage(ChatColor.GREEN + "[TownySieges] ✔ Осадная мортира развернута! ПКМ по орудию, чтобы сесть наводчиком сверху.");
        loc.getWorld().playSound(loc, Sound.BLOCK_ANVIL_PLACE, 1.2f, 0.7f);
        return true;
    }

    private void spawnCannonVisuals(Location blockLoc, float yaw) {
        World world = blockLoc.getWorld();
        if (world == null) return;

        Location center = blockLoc.clone().add(0.5, 0.0, 0.5);
        center.setYaw(yaw);
        center.setPitch(0f);

        try {
            // Carriage Frame (Dark Oak)
            world.spawn(center, BlockDisplay.class, bd -> {
                bd.setBlock(Bukkit.createBlockData(Material.DARK_OAK_PLANKS));
                bd.setTransformation(new Transformation(
                    new Vector3f(-0.35f, 0.05f, -0.45f),
                    new AxisAngle4f(0, 0, 1, 0),
                    new Vector3f(0.7f, 0.3f, 0.9f),
                    new AxisAngle4f(0, 0, 1, 0)
                ));
                bd.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
            });

            // Left Wheel (Grindstone)
            world.spawn(center, BlockDisplay.class, bd -> {
                bd.setBlock(Bukkit.createBlockData(Material.GRINDSTONE));
                bd.setTransformation(new Transformation(
                    new Vector3f(-0.48f, 0.02f, -0.25f),
                    new AxisAngle4f(0, 0, 1, 0),
                    new Vector3f(0.18f, 0.48f, 0.5f),
                    new AxisAngle4f(0, 0, 1, 0)
                ));
                bd.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
            });

            // Right Wheel (Grindstone)
            world.spawn(center, BlockDisplay.class, bd -> {
                bd.setBlock(Bukkit.createBlockData(Material.GRINDSTONE));
                bd.setTransformation(new Transformation(
                    new Vector3f(0.30f, 0.02f, -0.25f),
                    new AxisAngle4f(0, 0, 1, 0),
                    new Vector3f(0.18f, 0.48f, 0.5f),
                    new AxisAngle4f(0, 0, 1, 0)
                ));
                bd.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
            });

            // Heavy Gun Barrel / Cannon Tube (Polished Basalt) - tilted up 12°
            world.spawn(center, BlockDisplay.class, bd -> {
                bd.setBlock(Bukkit.createBlockData(Material.POLISHED_BASALT));
                bd.setTransformation(new Transformation(
                    new Vector3f(-0.2f, 0.22f, -0.55f),
                    new AxisAngle4f((float) Math.toRadians(-12), 1, 0, 0),
                    new Vector3f(0.4f, 0.4f, 1.15f),
                    new AxisAngle4f(0, 0, 1, 0)
                ));
                bd.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
            });

            // Cannon Muzzle Rim (Anvil)
            world.spawn(center, BlockDisplay.class, bd -> {
                bd.setBlock(Bukkit.createBlockData(Material.ANVIL));
                bd.setTransformation(new Transformation(
                    new Vector3f(-0.18f, 0.32f, 0.45f),
                    new AxisAngle4f((float) Math.toRadians(-12), 1, 0, 0),
                    new Vector3f(0.36f, 0.36f, 0.25f),
                    new AxisAngle4f(0, 0, 1, 0)
                ));
                bd.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
            });
        } catch (Throwable ignored) {
        }

        try {
            world.spawn(blockLoc.clone().add(0.5, 0.0, 0.5), Interaction.class, it -> {
                it.setInteractionWidth(1.2f);
                it.setInteractionHeight(1.2f);
                it.setResponsive(true);
                it.setMetadata("siege_cannon_interaction", new FixedMetadataValue(plugin, blockLoc));
                it.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
            });
        } catch (Throwable t) {
            Location standLoc = blockLoc.clone().add(0.5, 0.0, 0.5);
            standLoc.setYaw(yaw);
            world.spawn(standLoc, ArmorStand.class, as -> {
                as.setVisible(false);
                as.setGravity(false);
                as.setSmall(true);
                as.setBasePlate(false);
                as.setMetadata("siege_cannon_interaction", new FixedMetadataValue(plugin, blockLoc));
                as.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
            });
        }
    }

    public boolean isCannonAt(Location loc) {
        if (loc == null) return false;
        return deployedCannons.containsKey(loc.getBlock().getLocation());
    }

    public Location getNearbyCannon(Location loc) {
        if (loc == null) return null;
        Location bLoc = loc.getBlock().getLocation();
        if (deployedCannons.containsKey(bLoc)) return bLoc;
        Location above = bLoc.clone().add(0, 1, 0);
        if (deployedCannons.containsKey(above)) return above;
        Location below = bLoc.clone().add(0, -1, 0);
        if (deployedCannons.containsKey(below)) return below;
        return null;
    }

    public void mountGunner(Player player, Location cannonLoc) {
        if (player == null || cannonLoc == null) return;
        Location blockLoc = cannonLoc.getBlock().getLocation();

        if (blockLoc.equals(mountedGunners.get(player.getUniqueId()))) {
            return;
        }

        for (Map.Entry<UUID, Location> entry : mountedGunners.entrySet()) {
            if (blockLoc.equals(entry.getValue()) && !entry.getKey().equals(player.getUniqueId())) {
                Player other = Bukkit.getPlayer(entry.getKey());
                if (other != null && other.isOnline()) {
                    player.sendMessage(ChatColor.RED + "[TownySieges] Это орудие уже занято другим наводчиком (" + other.getName() + ")!");
                    return;
                }
            }
        }

        unmountGunner(player);

        Float initYawObj = cannonInitialYaw.get(blockLoc);
        float initYaw = initYawObj != null ? initYawObj : player.getLocation().getYaw();
        double rad = Math.toRadians(initYaw);

        // SEAT POSITIONED PRECISELY ON THE CANNON CARRIAGE (Y + 0.62)
        double seatX = blockLoc.getX() + 0.5 + 0.12 * Math.sin(rad);
        double seatZ = blockLoc.getZ() + 0.5 - 0.12 * Math.cos(rad);
        Location seatLoc = new Location(blockLoc.getWorld(), seatX, blockLoc.getY() + 0.62, seatZ, initYaw, 0f);

        ArmorStand seat = blockLoc.getWorld().spawn(seatLoc, ArmorStand.class, as -> {
            as.setVisible(false);
            as.setMarker(true);
            as.setGravity(false);
            as.setBasePlate(false);
            as.setArms(false);
            as.setMetadata("cannon_seat", new FixedMetadataValue(plugin, blockLoc));
            as.setMetadata("siege_cannon_entity", new FixedMetadataValue(plugin, blockLoc));
        });

        seat.addPassenger(player);
        gunnerSeats.put(player.getUniqueId(), seat);
        mountedGunners.put(player.getUniqueId(), blockLoc);
        lastMountTime.put(player.getUniqueId(), System.currentTimeMillis());
        aimingGunners.remove(player.getUniqueId());
        player.removePotionEffect(PotionEffectType.SLOW);

        // Save original main hand item only
        ItemStack currentHand = player.getInventory().getItemInMainHand();
        savedHandItems.put(player.getUniqueId(), currentHand != null ? currentHand.clone() : new ItemStack(Material.AIR));

        // Provide Aiming Tool for main hand (leave off-hand unrestricted)
        player.getInventory().setItemInMainHand(getAimingTool());
        player.updateInventory();

        setSelectedAmmo(player, AmmoType.REGULAR);
        int regCount = countRegularAmmo(player);
        int apCount = countArmorPiercingAmmo(player);
        String regStr = ChatColor.WHITE + "⚪ " + regCount + " шт.";
        String apStr = ChatColor.LIGHT_PURPLE + "🟣 " + apCount + " шт.";

        player.sendMessage(ChatColor.GOLD + "══════════ Место Наводчика Мортиры ══════════");
        player.sendMessage(ChatColor.YELLOW + "• Вы зафиксированы на орудии! Вражеские лучники могут вести огонь по наводчику.");
        player.sendMessage(ChatColor.AQUA + "• Прицеливание: ПКМ (приближение оптического зума x2.0).");
        player.sendMessage(ChatColor.YELLOW + "• Смена боеприпаса: клавиша F (смена руки) — выбор ⚪ Обычное / 🟣 Бронебойное.");
        player.sendMessage(ChatColor.WHITE + "• Боекомплект стрелка: " + regStr + ChatColor.GRAY + " | " + apStr);
        double cdSec = plugin.getArtillerySkillManager() != null ?
                plugin.getArtillerySkillManager().getReloadCooldownSeconds(player.getUniqueId()) : 10.0;
        player.sendMessage(ChatColor.GOLD + "• Выстрел: ЛКМ (сектор огня ±45°, перезарядка " + String.format(Locale.US, "%.1f", cdSec) + " сек).");
        player.sendMessage(ChatColor.GRAY + "• Выстрел на Q заблокирован (защита от случайных залпов).");
        player.sendMessage(ChatColor.RED + "• Покинуть орудие: нажмите Shift (приседание).");
        player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");
        player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_IRON, 1.0f, 0.7f);

        try {
            player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                new TextComponent(ChatColor.GOLD + "Мортира: " + ChatColor.WHITE + "⚪ Обычное ядро" +
                    ChatColor.YELLOW + " | F: Смена снаряда | ПКМ: Прицел | ЛКМ: Залп"));
        } catch (Exception ignored) {}
    }

    public void toggleAiming(Player player) {
        if (player == null || !isMounted(player)) return;
        UUID uuid = player.getUniqueId();
        Long mountTime = lastMountTime.get(uuid);
        if (mountTime != null && System.currentTimeMillis() - mountTime < 500L) {
            return;
        }

        AmmoType curType = getSelectedAmmo(player);
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
        }
    }

    public boolean isAiming(Player player) {
        return player != null && aimingGunners.contains(player.getUniqueId());
    }

    public Long getLastMountTime(UUID uuid) {
        return lastMountTime.get(uuid);
    }

    public void unmountGunner(Player player) {
        if (player == null) return;
        UUID uuid = player.getUniqueId();
        aimingGunners.remove(uuid);
        lastMountTime.remove(uuid);
        player.removePotionEffect(PotionEffectType.SLOW);

        // Restore original main hand item cleanly
        ItemStack savedHand = savedHandItems.remove(uuid);
        if (savedHand != null) {
            player.getInventory().setItemInMainHand(savedHand);
        }
        savedOffHandItems.remove(uuid);
        player.updateInventory();

        ArmorStand seat = gunnerSeats.remove(uuid);
        if (seat != null && !seat.isDead()) {
            seat.removePassenger(player);
            seat.remove();
        }
        Location cannonLoc = mountedGunners.remove(uuid);
        if (cannonLoc != null) {
            Float initYawObj = cannonInitialYaw.get(cannonLoc.getBlock().getLocation());
            float initYaw = initYawObj != null ? initYawObj : player.getLocation().getYaw();
            double rad = Math.toRadians(initYaw);
            Location exitLoc = cannonLoc.getBlock().getLocation().clone().add(0.5 + 0.8 * Math.sin(rad), 0.1, 0.5 - 0.8 * Math.cos(rad));
            exitLoc.setYaw(player.getLocation().getYaw());
            exitLoc.setPitch(player.getLocation().getPitch());
            player.teleport(exitLoc);
            player.sendMessage(ChatColor.GRAY + "[TownySieges] Вы покинули место наводчика осадной мортиры.");
        }
    }

    public boolean isMounted(Player player) {
        return player != null && mountedGunners.containsKey(player.getUniqueId());
    }

    public Location getMountedCannon(Player player) {
        return player != null ? mountedGunners.get(player.getUniqueId()) : null;
    }

    public boolean fireCannon(Player player) {
        if (player == null) return false;
        if (!isMounted(player) || player.getVehicle() == null) {
            player.sendMessage(ChatColor.RED + "[TownySieges] Вы должны занять место наводчика на мортире (ПКМ), чтобы стрелять!");
            return false;
        }

        long now = System.currentTimeMillis();
        Long mountTime = lastMountTime.get(player.getUniqueId());
        if (mountTime != null && now - mountTime < 750L) {
            return false;
        }

        Location cannonLoc = getMountedCannon(player);
        if (cannonLoc == null) return false;

        // Dynamic reload cooldown according to Artillery skill (10.0s -> 5.0s)
        final long shotCooldownMs = plugin.getArtillerySkillManager() != null ?
                plugin.getArtillerySkillManager().getReloadCooldownMs(player.getUniqueId()) : 10000L;

        // 1. Check reload cooldown
        Long last = lastShotTime.get(player.getUniqueId());
        if (last != null && now - last < 250L) {
            return false; // Debounce simultaneous click/animation packets silently
        }
        if (last != null && now - last < shotCooldownMs) {
            double remaining = (shotCooldownMs - (now - last)) / 1000.0;
            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                    new TextComponent(ChatColor.RED + "⌛ Перезарядка орудия... " + String.format(Locale.US, "%.1f", remaining) + " сек."));
            } catch (Exception e) {
                player.sendMessage(ChatColor.RED + "⌛ Перезарядка орудия... " + String.format(Locale.US, "%.1f", remaining) + " сек.");
            }
            player.playSound(player.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 0.8f, 1.4f);
            return false;
        }

        // 2. Check ammunition according to gunner's selected ammo (cycled via F key)
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
        }

        // 5. Mark cooldown & award Artillery XP
        lastShotTime.put(player.getUniqueId(), now);
        if (plugin.getArtillerySkillManager() != null) {
            plugin.getArtillerySkillManager().addXP(player, 15.0);
        }

        // 6. Ballistics along player aim direction
        Location eye = player.getEyeLocation();
        Vector dir = eye.getDirection().normalize();
        double power = 1.35; // Authentic heavy siege ballistics speed
        Vector velocity = dir.multiply(power);
        velocity.setY(velocity.getY() + 0.26); // Graceful ballistic siege arc

        Location muzzle = cannonLoc.clone().add(0.5, 0.65, 0.5).add(dir.clone().multiply(0.85));

        World world = cannonLoc.getWorld();
        if (world != null) {
            world.spawnParticle(Particle.EXPLOSION_LARGE, muzzle, 2, 0.1, 0.1, 0.1, 0.05);
            world.spawnParticle(Particle.FLAME, muzzle, 25, 0.2, 0.2, 0.2, 0.08);
            world.spawnParticle(Particle.CAMPFIRE_COSY_SMOKE, muzzle, 30, 0.2, 0.3, 0.2, 0.05);
            world.playSound(cannonLoc, Sound.ENTITY_GENERIC_EXPLODE, 2.0f, 0.6f);
            world.playSound(cannonLoc, Sound.ENTITY_FIREWORK_ROCKET_BLAST, 1.5f, 0.5f);

            final AmmoType shotType = ammoToUse;
            TNTPrimed shell = world.spawn(muzzle, TNTPrimed.class, (tnt) -> {
                tnt.setFuseTicks(65);
                tnt.setIsIncendiary(true);
                tnt.setVelocity(velocity);
                tnt.setMetadata("siege_cannon_shell", new FixedMetadataValue(plugin, true));
                tnt.setMetadata("siege_cannon_shooter", new FixedMetadataValue(plugin, player.getUniqueId().toString()));
                if (shotType == AmmoType.ARMOR_PIERCING) {
                    tnt.setMetadata("siege_armor_piercing", new FixedMetadataValue(plugin, true));
                    tnt.setCustomName(ChatColor.LIGHT_PURPLE + "🟣 Бронебойный Осадный Снаряд");
                } else {
                    tnt.setCustomName(ChatColor.WHITE + "⚪ Осадный Снаряд");
                }
                tnt.setCustomNameVisible(true);
            });

            // Particles while projectile is flying
            if (shotType == AmmoType.ARMOR_PIERCING) {
                new BukkitRunnable() {
                    int ticks = 0;
                    @Override
                    public void run() {
                        if (shell.isDead() || !shell.isValid() || ticks > 70) {
                            cancel();
                            return;
                        }
                        shell.getWorld().spawnParticle(Particle.DRAGON_BREATH, shell.getLocation(), 4, 0.05, 0.05, 0.05, 0.02);
                        shell.getWorld().spawnParticle(Particle.CRIT_MAGIC, shell.getLocation(), 3, 0.05, 0.05, 0.05, 0.05);
                        ticks++;
                    }
                }.runTaskTimer(plugin, 1L, 1L);
            }
        }

        player.sendMessage(ChatColor.RED + "🔥 ЗАЛП МОРТИРЫ! Снаряд: " + ammoToUse.getColor() + ammoToUse.getDisplayName());

        // 7. Dynamic Action Bar reload countdown using player's Artillery reload speed
        final long shotTimestamp = now;
        final AmmoType lockedShotType = ammoToUse;
        new BukkitRunnable() {
            int step = 0;
            @Override
            public void run() {
                if (!isMounted(player)) {
                    cancel();
                    return;
                }
                long elapsed = System.currentTimeMillis() - shotTimestamp;
                double remaining = Math.max(0.0, (shotCooldownMs - elapsed) / 1000.0);

                AmmoType curSelected = getSelectedAmmo(player);
                int count = (curSelected == AmmoType.REGULAR) ? countRegularAmmo(player) : countArmorPiercingAmmo(player);
                boolean hasNextShell = count > 0 || player.getGameMode() == GameMode.CREATIVE;

                if (elapsed >= shotCooldownMs) {
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
                }

                if (step == 10) {
                    player.playSound(player.getLocation(), Sound.BLOCK_IRON_TRAPDOOR_CLOSE, 0.6f, 1.2f);
                }

                int filled = (int) Math.min(10, (elapsed * 10) / shotCooldownMs);
                StringBuilder bar = new StringBuilder();
                for (int i = 0; i < 10; i++) {
                    if (i < filled) bar.append("█");
                    else bar.append("░");
                }

                try {
                    String aimPrefix = isAiming(player) ? ChatColor.AQUA + "🎯 " : "";
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR,
                        new TextComponent(aimPrefix + ChatColor.GOLD + "🔥 Перезарядка " + lockedShotType.getColor() + lockedShotType.getDisplayName() +
                            ChatColor.YELLOW + " ⌛ " + String.format(Locale.US, "%.1f", remaining) + "с " +
                            ChatColor.DARK_GRAY + "[" + ChatColor.GREEN + bar + ChatColor.DARK_GRAY + "]"));
                } catch (Exception ignored) {}

                step++;
            }
        }.runTaskTimer(plugin, 1L, 4L);

        return true;
    }

    public void breakCannon(Player player, Location cannonLoc) {
        if (cannonLoc == null) return;
        Location blockLoc = cannonLoc.getBlock().getLocation();

        for (Map.Entry<UUID, Location> entry : mountedGunners.entrySet()) {
            if (entry.getValue().getBlock().getLocation().equals(blockLoc)) {
                Player p = Bukkit.getPlayer(entry.getKey());
                if (p != null) unmountGunner(p);
            }
        }

        blockLoc.getBlock().setType(Material.AIR);
        blockLoc.getBlock().removeMetadata("siege_cannon", plugin);
        deployedCannons.remove(blockLoc);
        cannonInitialYaw.remove(blockLoc);

        World world = blockLoc.getWorld();
        if (world != null) {
            for (Entity entity : world.getNearbyEntities(blockLoc.clone().add(0.5, 0.5, 0.5), 2.5, 2.5, 2.5)) {
                if (entity.hasMetadata("siege_cannon_entity") ||
                    entity.hasMetadata("siege_cannon_interaction") ||
                    entity.hasMetadata("cannon_seat")) {
                    entity.remove();
                }
            }
            world.dropItemNaturally(blockLoc.clone().add(0.5, 0.5, 0.5), getCannonItem());
        }

        if (player != null) {
            player.sendMessage(ChatColor.YELLOW + "[TownySieges] Осадная мортира демонтирована и возвращена в инвентарь.");
            player.playSound(blockLoc, Sound.BLOCK_ANVIL_BREAK, 1.0f, 1.0f);
        }
    }

    public void clearAll() {
        for (UUID uuid : new ArrayList<>(mountedGunners.keySet())) {
            Player p = Bukkit.getPlayer(uuid);
            if (p != null) unmountGunner(p);
        }
        for (ArmorStand seat : gunnerSeats.values()) {
            if (seat != null && !seat.isDead()) seat.remove();
        }
        gunnerSeats.clear();
        mountedGunners.clear();
        lastShotTime.clear();
        lastMountTime.clear();
        aimingGunners.clear();
        savedHandItems.clear();
        savedOffHandItems.clear();
        gunnerAmmoSelection.clear();
    }
}
