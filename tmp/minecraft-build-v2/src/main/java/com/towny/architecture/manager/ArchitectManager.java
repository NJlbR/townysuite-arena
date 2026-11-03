package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.Sound;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;

import java.io.File;
import java.io.IOException;
import java.util.*;

/**
 * Полностью независимый менеджер профессии «Архитектор».
 * Не требует AuraSkills или mcMMO!
 * 
 * Включает:
 * 1. Начисление опыта за стройку в чертежах (+15 XP)
 * 2. Начисление опыта за размещение любых стройматериалов в черте города (+1 XP с защитой High-Water Mark)
 * 3. Таблицу уровней (1..100)
 * 4. Автоматическое сохранение в architects.yml
 * 5. Консольные и звуковые уведомления о повышении уровня
 */
public class ArchitectManager {
    private final TownyArchitecturePlugin plugin;
    private final File file;
    private FileConfiguration config;
    
    private final Map<UUID, ArchitectStats> statsMap = new HashMap<>();
    private final Set<Material> constructionMaterials = EnumSet.noneOf(Material.class);
    private final Map<UUID, org.bukkit.boss.BossBar> playerBossBars = new HashMap<>();
    private final Map<UUID, Integer> bossBarTasks = new HashMap<>();

    public ArchitectManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
        this.file = new File(plugin.getDataFolder(), "architects.yml");
        initMaterials();
        load();
    }
    
    private void initMaterials() {
        for (Material m : Material.values()) {
            if (!m.isBlock() || m.isAir()) continue;
            String name = m.name();
            
            // Исключаем системные и технические блоки
            if (name.contains("COMMAND") || name.contains("STRUCTURE") || name.contains("JIGSAW") || 
                name.contains("BARRIER") || name.contains("LIGHT_BLOCK") || name.contains("PORTAL")) continue;
            
            // Исключаем жидкости и эфемерные блоки
            if (name.contains("WATER") || name.contains("LAVA") || name.contains("FIRE") || 
                name.contains("FROSTED_ICE") || name.contains("BUBBLE_COLUMN")) continue;
            
            // Исключаем базовые природные блоки, которые слишком легко спамить (хотя HWM защищает)
            if (name.equals("DIRT") || name.equals("GRASS_BLOCK") || name.equals("NETHERRACK") || 
                name.equals("SAND") || name.equals("GRAVEL") || name.equals("TALL_GRASS") || 
                name.equals("GRASS") || name.equals("FERN") || name.endsWith("SAPLING")) continue;

            constructionMaterials.add(m);
        }
    }

    public void removeBossBar(Player player) {
        org.bukkit.boss.BossBar bar = playerBossBars.remove(player.getUniqueId());
        if (bar != null) {
            bar.removeAll();
        }
        Integer taskId = bossBarTasks.remove(player.getUniqueId());
        if (taskId != null) {
            org.bukkit.Bukkit.getScheduler().cancelTask(taskId);
        }
    }

    public void load() {
        statsMap.clear();
        if (!file.exists()) {
            try { 
                file.getParentFile().mkdirs();
                file.createNewFile(); 
            } catch (IOException e) {
                plugin.getLogger().warning("Не удалось создать architects.yml: " + e.getMessage());
            }
        }
        config = YamlConfiguration.loadConfiguration(file);
        if (config.contains("players")) {
            for (String key : config.getConfigurationSection("players").getKeys(false)) {
                try {
                    UUID uuid = UUID.fromString(key);
                    int xp = config.getInt("players." + key + ".xp", 0);
                    int placed = config.getInt("players." + key + ".placed", 0);
                    int broken = config.getInt("players." + key + ".broken", 0);
                    int maxNet = config.getInt("players." + key + ".maxNet", 0);
                    statsMap.put(uuid, new ArchitectStats(xp, placed, broken, maxNet));
                } catch (Exception ignored) {}
            }
        }
    }

    public void save() {
        if (config == null) config = new YamlConfiguration();
        for (Map.Entry<UUID, ArchitectStats> entry : statsMap.entrySet()) {
            String key = "players." + entry.getKey().toString();
            ArchitectStats st = entry.getValue();
            config.set(key + ".xp", st.xp);
            config.set(key + ".placed", st.placed);
            config.set(key + ".broken", st.broken);
            config.set(key + ".maxNet", st.maxNet);
            config.set(key + ".level", calculateLevel(st.xp));
        }
        try { 
            config.save(file); 
        } catch (IOException e) {
            plugin.getLogger().warning("Ошибка сохранения architects.yml: " + e.getMessage());
        }
    }
    
    public ArchitectStats getStats(UUID uuid) {
        return statsMap.computeIfAbsent(uuid, k -> new ArchitectStats(0, 0, 0, 0));
    }

    public ArchitectStats getStats(Player player) {
        return getStats(player.getUniqueId());
    }

    public int getLevel(UUID uuid) {
        ArchitectStats st = getStats(uuid);
        return calculateLevel(st.xp);
    }

    public int getLevel(Player player) {
        return getLevel(player.getUniqueId());
    }
    
    /**
     * Динамическая формула уровней (кубический корень):
     * Ранние уровни пролетают очень быстро, высокие требуют огромных вложений.
     */
    public static int calculateLevel(int xp) {
        if (xp <= 0) return 1;
        // Level = 1 + cbrt(xp / 5)
        int lvl = (int) Math.floor(Math.cbrt(xp / 5.0)) + 1;
        return Math.min(100, Math.max(1, lvl));
    }
    
    public static int getXpForLevel(int level) {
        if (level <= 1) return 0;
        return 5 * (int) Math.pow(level - 1, 3);
    }

    private void showProgressBossBar(Player player, int currentLevel, int currentXp, int addedXp) {
        org.bukkit.boss.BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), uuid -> {
            org.bukkit.boss.BossBar newBar = org.bukkit.Bukkit.createBossBar("", org.bukkit.boss.BarColor.YELLOW, org.bukkit.boss.BarStyle.SEGMENTED_10);
            newBar.addPlayer(player);
            return newBar;
        });

        int baseLevelXp = getXpForLevel(currentLevel);
        int nextLevelXp = getXpForLevel(currentLevel + 1);
        int progress = currentXp - baseLevelXp;
        int required = nextLevelXp - baseLevelXp;
        if (required <= 0) required = 1;
        
        double percentage = (double) progress / required;
        
        bar.setTitle(ChatColor.GOLD + "Архитектор " + currentLevel + " ур. " + 
                     ChatColor.YELLOW + "[+" + addedXp + " XP]");
        bar.setProgress(Math.min(1.0, Math.max(0.0, percentage)));
        bar.setVisible(true);

        Integer taskId = bossBarTasks.get(player.getUniqueId());
        if (taskId != null) {
            org.bukkit.Bukkit.getScheduler().cancelTask(taskId);
        }

        int newTaskId = org.bukkit.Bukkit.getScheduler().runTaskLater(plugin, () -> {
            bar.setVisible(false);
        }, 60L).getTaskId(); // 3 seconds

        bossBarTasks.put(player.getUniqueId(), newTaskId);
    }

    public void addXp(Player player, int amount) {
        if (amount <= 0) return;
        ArchitectStats st = getStats(player);
        int oldLevel = calculateLevel(st.xp);
        st.xp += amount;
        int newLevel = calculateLevel(st.xp);
        
        showProgressBossBar(player, newLevel > oldLevel ? newLevel : oldLevel, st.xp, amount);
        
        if (newLevel > oldLevel) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&', 
                    "&6✦ &e&lПОВЫШЕНИЕ НАВЫКА! &fВаш уровень Архитектора повышен: &e" + oldLevel + " &7➜ &a&l" + newLevel + " &6✦"));
            try {
                player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.9f, 1.2f);
            } catch (Exception ignored) {}
        }
    }

    public void resetStats(UUID uuid) {
        statsMap.remove(uuid);
        Player player = org.bukkit.Bukkit.getPlayer(uuid);
        if (player != null) {
            removeBossBar(player);
            player.sendMessage(ChatColor.GREEN + "Ваш опыт архитектора и лимит блоков успешно сброшены.");
        }
        save();
    }

    public void resetStats(Player player) {
        resetStats(player.getUniqueId());
    }

    public void setLevel(UUID uuid, int level) {
        ArchitectStats stats = getStats(uuid);
        stats.xp = getXpForLevel(level);
        save();
        Player player = org.bukkit.Bukkit.getPlayer(uuid);
        if (player != null) {
            showProgressBossBar(player, level, stats.xp, 0);
        }
    }

    public void setLevel(Player player, int level) {
        setLevel(player.getUniqueId(), level);
    }

    public void handleTownBlockPlace(Player player, Material mat) {
        if (!constructionMaterials.contains(mat)) return;
        ArchitectStats st = getStats(player);
        st.placed++;
        int net = st.placed - st.broken;
        
        // High-Water Mark: опыт дается только за превышение исторического максимума поставленных блоков
        if (net > st.maxNet) {
            st.maxNet = net;
            addXp(player, 1);
        }
    }

    public void handleTownBlockBreak(Player player, Material mat) {
        if (!constructionMaterials.contains(mat)) return;
        ArchitectStats st = getStats(player);
        st.broken++;
    }
    
    public static class ArchitectStats {
        public int xp;
        public int placed;
        public int broken;
        public int maxNet;
        public ArchitectStats(int xp, int placed, int broken, int maxNet) {
            this.xp = xp; this.placed = placed; this.broken = broken; this.maxNet = maxNet;
        }
    }
}
