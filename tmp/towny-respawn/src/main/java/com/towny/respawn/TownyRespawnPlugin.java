package com.towny.respawn;

import com.towny.respawn.command.RespawnCommand;
import com.towny.respawn.hook.TownyHook;
import com.towny.respawn.hook.TownySiegesHook;
import com.towny.respawn.listener.BedInteractListener;
import com.towny.respawn.listener.ChatRenameListener;
import com.towny.respawn.listener.DeathRespawnListener;
import com.towny.respawn.listener.GuiListener;
import com.towny.respawn.manager.BedManager;
import com.towny.respawn.manager.GuiManager;
import com.towny.respawn.manager.RespawnManager;
import org.bukkit.plugin.java.JavaPlugin;

public class TownyRespawnPlugin extends JavaPlugin {

    private static TownyRespawnPlugin instance;

    private TownyHook townyHook;
    private TownySiegesHook townySiegesHook;
    private BedManager bedManager;
    private RespawnManager respawnManager;
    private GuiManager guiManager;

    @Override
    public void onEnable() {
        instance = this;
        saveDefaultConfig();

        townyHook = new TownyHook();
        townySiegesHook = new TownySiegesHook();

        bedManager = new BedManager(this);
        respawnManager = new RespawnManager(this);
        guiManager = new GuiManager(this);

        bedManager.load();

        RespawnCommand cmd = new RespawnCommand(this);
        if (getCommand("respawn") != null) {
            getCommand("respawn").setExecutor(cmd);
            getCommand("respawn").setTabCompleter(cmd);
        }
        if (getCommand("townyrespawn") != null) {
            getCommand("townyrespawn").setExecutor(cmd);
            getCommand("townyrespawn").setTabCompleter(cmd);
        }

        getServer().getPluginManager().registerEvents(new DeathRespawnListener(this), this);
        getServer().getPluginManager().registerEvents(new BedInteractListener(this), this);
        getServer().getPluginManager().registerEvents(new GuiListener(this), this);
        getServer().getPluginManager().registerEvents(new ChatRenameListener(this), this);

        getLogger().info("[TownyRespawn] v1.1.0 успешно запущен: мульти-кровати, меню выбора респавна и переименование кроватей активны!");
    }

    @Override
    public void onDisable() {
        if (bedManager != null) {
            bedManager.save();
        }
        getLogger().info("[TownyRespawn] Плагин выключен. База кроватей сохранена.");
    }

    public static TownyRespawnPlugin getInstance() {
        return instance;
    }

    public TownyHook getTownyHook() {
        return townyHook;
    }

    public TownySiegesHook getTownySiegesHook() {
        return townySiegesHook;
    }

    public BedManager getBedManager() {
        return bedManager;
    }

    public RespawnManager getRespawnManager() {
        return respawnManager;
    }

    public GuiManager getGuiManager() {
        return guiManager;
    }
}
