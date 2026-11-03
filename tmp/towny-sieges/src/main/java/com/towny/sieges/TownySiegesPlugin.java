package com.towny.sieges;

import com.towny.sieges.bossbar.SiegeBossBarManager;
import com.towny.sieges.cannon.SiegeCannonManager;
import com.towny.sieges.command.SiegeCommand;
import com.towny.sieges.hook.TownyHook;
import com.towny.sieges.listener.SiegeProtectionListener;
import com.towny.sieges.manager.SiegeManager;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

public class TownySiegesPlugin extends JavaPlugin {

    private static TownySiegesPlugin instance;
    private TownyHook townyHook;
    private SiegeManager siegeManager;
    private SiegeBossBarManager bossBarManager;
    private SiegeCannonManager cannonManager;
    private com.towny.sieges.manager.SiegeCaptureManager captureManager;
    private com.towny.sieges.manager.ArtillerySkillManager artillerySkillManager;
    private com.towny.sieges.gui.SiegeMenuGui siegeMenuGui;
    private BukkitTask tickerTask;

    @Override
    public void onEnable() {
        instance = this;
        saveDefaultConfig();

        townyHook = new TownyHook();
        siegeManager = new SiegeManager(this);
        bossBarManager = new SiegeBossBarManager(this);
        cannonManager = new SiegeCannonManager(this);
        captureManager = new com.towny.sieges.manager.SiegeCaptureManager(this);
        artillerySkillManager = new com.towny.sieges.manager.ArtillerySkillManager(this);
        siegeMenuGui = new com.towny.sieges.gui.SiegeMenuGui(this);

        siegeManager.loadData();

        SiegeCommand cmd = new SiegeCommand(this);
        
        // Register ALL commands defined in plugin.yml
        String[] commands = {"siege", "disband", "cancel", "skip-prep", "skip", "assault"};
        for (String cmdName : commands) {
            org.bukkit.command.PluginCommand pluginCmd = getCommand(cmdName);
            if (pluginCmd != null) {
                pluginCmd.setExecutor(cmd);
                pluginCmd.setTabCompleter(cmd);
            }
        }

        cannonManager.registerRecipes();
        captureManager.registerRecipes();

        // Unlock all recipes for online players so they appear in recipe book search
        for (org.bukkit.entity.Player onlinePlayer : Bukkit.getOnlinePlayers()) {
            try {
                onlinePlayer.discoverRecipe(new org.bukkit.NamespacedKey(this, "siege_mortar"));
                onlinePlayer.discoverRecipe(new org.bukkit.NamespacedKey(this, "siege_cannonball_regular"));
                onlinePlayer.discoverRecipe(new org.bukkit.NamespacedKey(this, "siege_cannonball_ap"));
                onlinePlayer.discoverRecipe(new org.bukkit.NamespacedKey(this, "siege_assault_banner_recipe"));
            } catch (Throwable ignored) {
            }
        }

        getServer().getPluginManager().registerEvents(new SiegeProtectionListener(this), this);
        getServer().getPluginManager().registerEvents(siegeMenuGui, this);

        // Register Towny notification interceptor
        if (townyHook != null && townyHook.isTownyEnabled()) {
            try {
                Class.forName("com.palmergames.bukkit.towny.event.ChunkNotificationEvent");
                getServer().getPluginManager().registerEvents(new com.towny.sieges.listener.TownyNotificationListener(this), this);
            } catch (Throwable ignored) {
            }
        }

        tickerTask = Bukkit.getScheduler().runTaskTimer(this, () -> {
            siegeManager.tick();
            if (captureManager != null) {
                captureManager.tick();
            }
        }, 20L, 20L);

        getLogger().info("TownySieges v" + getDescription().getVersion() + " успешно активирован!");
    }

    @Override
    public void onDisable() {
        if (tickerTask != null) tickerTask.cancel();
        if (siegeManager != null) siegeManager.saveData();
        if (artillerySkillManager != null) artillerySkillManager.saveData();
        if (bossBarManager != null) bossBarManager.clearAll();
        if (cannonManager != null) cannonManager.clearAll();
        if (captureManager != null) captureManager.clearAll();
        getLogger().info("[TownySieges] Плагин выключен. Данные сохранены.");
    }

    public static TownySiegesPlugin getInstance() { return instance; }
    public TownyHook getTownyHook() { return townyHook; }
    public SiegeManager getSiegeManager() { return siegeManager; }
    public SiegeBossBarManager getBossBarManager() { return bossBarManager; }
    public SiegeCannonManager getCannonManager() { return cannonManager; }
    public com.towny.sieges.manager.SiegeCaptureManager getCaptureManager() { return captureManager; }
    public com.towny.sieges.manager.ArtillerySkillManager getArtillerySkillManager() { return artillerySkillManager; }
    public com.towny.sieges.gui.SiegeMenuGui getSiegeMenuGui() { return siegeMenuGui; }

    public static boolean isTownUnderActiveSiege(String townName) {
        if (instance == null || instance.getSiegeManager() == null) return false;
        return instance.getSiegeManager().isTownUnderActiveSiege(townName);
    }

    public static boolean isLocationUnderActiveSiege(Location loc) {
        if (instance == null || instance.getSiegeManager() == null) return false;
        return instance.getSiegeManager().isLocationUnderActiveSiege(loc);
    }
}
