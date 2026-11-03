package com.towny.sieges.manager;

import com.towny.sieges.TownySiegesPlugin;
import org.bukkit.ChatColor;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class ArtillerySkillManager {
    private final TownySiegesPlugin plugin;
    private final Map<UUID, Double> artilleryXP = new HashMap<>();
    private final File dataFile;

    public ArtillerySkillManager(TownySiegesPlugin plugin) {
        this.plugin = plugin;
        this.dataFile = new File(plugin.getDataFolder(), "artillery_skills.yml");
        loadData();
    }

    public static final int MAX_LEVEL = 10;

    public double getRequiredXPForLevel(int level) {
        if (level <= 1) return 0.0;
        if (level > MAX_LEVEL) level = MAX_LEVEL;
        return Math.floor(100.0 * Math.pow(level - 1, 2.15));
    }

    public int getLevelFromXP(double xp) {
        if (xp <= 0) return 1;
        for (int lvl = MAX_LEVEL; lvl >= 1; lvl--) {
            if (xp >= getRequiredXPForLevel(lvl)) {
                return lvl;
            }
        }
        return 1;
    }

    public void setLevel(UUID uuid, int level) {
        if (uuid == null) return;
        level = Math.max(1, Math.min(MAX_LEVEL, level));
        double reqXP = getRequiredXPForLevel(level);
        artilleryXP.put(uuid, reqXP);
        saveData();
    }

    public double getReloadCooldownSeconds(UUID uuid) {
        if (uuid == null) return 10.0;
        int level = getLevel(uuid);
        level = Math.max(1, Math.min(MAX_LEVEL, level));
        // Level 1 = 10.0s, Level 10 = 5.0s
        double cd = 10.0 - ((level - 1) * (5.0 / (MAX_LEVEL - 1)));
        return Math.max(5.0, Math.min(10.0, cd));
    }

    public long getReloadCooldownMs(UUID uuid) {
        return (long) (getReloadCooldownSeconds(uuid) * 1000.0);
    }

    public void addXP(Player player, double amount) {
        if (player == null || amount <= 0) return;
        UUID uuid = player.getUniqueId();
        double currentXP = artilleryXP.getOrDefault(uuid, 0.0);
        int oldLevel = getLevelFromXP(currentXP);
        double newXP = currentXP + amount;
        artilleryXP.put(uuid, newXP);
        int newLevel = getLevelFromXP(newXP);

        if (newLevel > oldLevel) {
            double newCooldown = getReloadCooldownSeconds(uuid);
            player.sendMessage(ChatColor.GOLD + "⚔ [Навык: Артиллерист] Уровень ПОВЫШЕН до " + newLevel + " ур.!");
            player.sendMessage(ChatColor.YELLOW + "⚡ Перезарядка вашей мортиры ускорена до " + 
                String.format(java.util.Locale.US, "%.1f", newCooldown) + " сек.!");
            try {
                player.playSound(player.getLocation(), org.bukkit.Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.0f, 1.2f);
            } catch (Throwable ignored) {}
        }
        saveData();
    }

    public int getLevel(UUID uuid) {
        if (uuid == null) return 1;
        return getLevelFromXP(artilleryXP.getOrDefault(uuid, 0.0));
    }

    public double getXP(UUID uuid) {
        if (uuid == null) return 0.0;
        return artilleryXP.getOrDefault(uuid, 0.0);
    }

    public void loadData() {
        if (!dataFile.exists()) return;
        FileConfiguration config = YamlConfiguration.loadConfiguration(dataFile);
        if (config.contains("artillery")) {
            for (String key : config.getConfigurationSection("artillery").getKeys(false)) {
                try {
                    artilleryXP.put(UUID.fromString(key), config.getDouble("artillery." + key));
                } catch (IllegalArgumentException ignored) {}
            }
        }
    }

    public void saveData() {
        FileConfiguration config = new YamlConfiguration();
        for (Map.Entry<UUID, Double> entry : artilleryXP.entrySet()) {
            config.set("artillery." + entry.getKey().toString(), entry.getValue());
        }
        try {
            config.save(dataFile);
        } catch (IOException e) {
            plugin.getLogger().severe("Could not save artillery_skills.yml: " + e.getMessage());
        }
    }
}
