package com.towny.explosion;

import com.towny.explosion.command.ExplosionUnblockerCommand;
import com.towny.explosion.listener.CannonExplosionListener;
import com.towny.explosion.util.CannonDetector;
import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;

public class TownyExplosionUnblockerPlugin extends JavaPlugin {

    private static TownyExplosionUnblockerPlugin instance;
    private CannonDetector cannonDetector;

    @Override
    public void onEnable() {
        instance = this;
        saveDefaultConfig();

        cannonDetector = new CannonDetector(this);

        // Register explosion listener
        getServer().getPluginManager().registerEvents(new CannonExplosionListener(this), this);

        // Register admin command
        ExplosionUnblockerCommand cmd = new ExplosionUnblockerCommand(this);
        if (getCommand("explosionunblocker") != null) {
            getCommand("explosionunblocker").setExecutor(cmd);
            getCommand("explosionunblocker").setTabCompleter(cmd);
        }

        getLogger().info("TownyExplosionUnblocker v" + getDescription().getVersion() + " успешно активирован!");
    }

    @Override
    public void onDisable() {
        getLogger().info("[TownyExplosionUnblocker] Плагин отключен.");
    }

    public void reloadPluginConfig() {
        reloadConfig();
    }

    public boolean isUnblockerEnabled() {
        return getConfig().getBoolean("enabled", true);
    }

    public boolean isDebugEnabled() {
        return getConfig().getBoolean("debug-logging", false);
    }

    public CannonDetector getCannonDetector() {
        return cannonDetector;
    }

    public static TownyExplosionUnblockerPlugin getInstance() {
        return instance;
    }
}
