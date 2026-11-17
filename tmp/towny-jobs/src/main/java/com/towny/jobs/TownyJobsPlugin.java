package com.towny.jobs;

import com.palmergames.bukkit.towny.TownyCommandAddonAPI;
import com.palmergames.bukkit.towny.TownyCommandAddonAPI.CommandType;
import com.towny.jobs.command.TownyJobsCommand;
import com.towny.jobs.gui.JobsMenu;
import com.towny.jobs.hook.TownyArchitectureHook;
import com.towny.jobs.listener.JobsListener;
import com.towny.jobs.manager.TownyJobsManager;
import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;

public final class TownyJobsPlugin extends JavaPlugin {
    private TownyJobsManager manager;
    private JobsMenu menu;
    private TownyArchitectureHook architectureHook;
    private boolean townSubcommandRegistered;

    @Override
    public void onEnable() {
        saveDefaultConfig();
        architectureHook = new TownyArchitectureHook(this);
        manager = new TownyJobsManager(this, architectureHook);
        manager.load();
        menu = new JobsMenu(this, manager);

        TownyJobsCommand command = new TownyJobsCommand(this);
        if (getCommand("townyjobs") != null) {
            getCommand("townyjobs").setExecutor(command);
            getCommand("townyjobs").setTabCompleter(command);
        }
        Bukkit.getPluginManager().registerEvents(new JobsListener(this, menu, manager), this);

        try {
            townSubcommandRegistered = TownyCommandAddonAPI.addSubCommand(
                    CommandType.TOWN, "jobs", command);
            if (!townSubcommandRegistered) {
                getLogger().warning("Towny did not register /t jobs; use /townyjobs instead.");
            }
        } catch (Throwable error) {
            getLogger().warning("Couldn't register /t jobs; use /townyjobs instead: " + error.getMessage());
        }

        manager.syncOnlinePlayers();
        // Economy, Towny data, and World access all run synchronously on the server thread.
        Bukkit.getScheduler().runTaskTimer(this, manager::tick, 20L, 1200L);
        Bukkit.getScheduler().runTaskTimer(this, manager::refreshActiveConstructionSnapshot, 20L, 6000L);
        getLogger().info("TownyJobs enabled. Towny rank and construction integration are active where supported.");
    }

    @Override
    public void onDisable() {
        if (manager != null) manager.shutdown();
        if (townSubcommandRegistered) {
            try {
                TownyCommandAddonAPI.removeSubCommand(CommandType.TOWN, "jobs");
            } catch (Throwable ignored) {
            }
        }
    }

    public TownyJobsManager getManager() {
        return manager;
    }

    public JobsMenu getMenu() {
        return menu;
    }

    public TownyArchitectureHook getArchitectureHook() {
        return architectureHook;
    }
}
