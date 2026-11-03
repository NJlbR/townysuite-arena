package com.towny.architecture;

import com.towny.architecture.command.BuildCommand;
import com.towny.architecture.gui.BuildsMenuGui;
import com.towny.architecture.hook.TownyHook;
import com.towny.architecture.listener.TownyPlotEventListener;
import com.towny.architecture.manager.*;
import com.towny.architecture.model.*;
import com.towny.architecture.model.ChunkCoord;
import org.bukkit.Bukkit;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockBurnEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.player.PlayerCommandPreprocessEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

import java.io.File;

public class TownyArchitecturePlugin extends JavaPlugin implements Listener {

    private static TownyArchitecturePlugin instance;

    private TownyHook townyHook;

    private BuildingManager buildingManager;
    private BuffManager buffManager;
    private SiegeDamageManager siegeDamageManager;
    private BuildingHudManager buildingHudManager;
    private ArchitectManager architectManager;

    private BuildsMenuGui buildsMenuGui;
    private BuildCommand buildCommand;

    private File buildingsFile;
    private FileConfiguration buildingsConfig;

    private BukkitTask buffTask;
    private BukkitTask hudTask;
    private BukkitTask integrityTask;
    private BukkitTask particleTask;

    @Override
    public void onEnable() {
        instance = this;
        saveDefaultConfig();
        saveResourceIfNotExists("buildings.yml");

        townyHook = new TownyHook();

        architectManager = new ArchitectManager(this);
        buildingManager = new BuildingManager(this);
        buffManager = new BuffManager(this);
        siegeDamageManager = new SiegeDamageManager(this);
        buildingHudManager = new BuildingHudManager(this);
        buildsMenuGui = new BuildsMenuGui(this);

        loadBuildingsConfig();
        buildingManager.loadBlueprints(buildingsConfig);
        buildingManager.loadData();

        buildCommand = new BuildCommand(this);
        if (getCommand("builds") != null) {
            getCommand("builds").setExecutor(buildCommand);
            getCommand("builds").setTabCompleter(buildCommand);
        }

        getServer().getPluginManager().registerEvents(this, this);
        getServer().getPluginManager().registerEvents(buildsMenuGui, this);
        getServer().getPluginManager().registerEvents(siegeDamageManager, this);
        if (townyHook.isTownyEnabled()) {
            getServer().getPluginManager().registerEvents(new TownyPlotEventListener(this), this);
            buildingManager.syncAllPlotTags();
        }

        int intervalSeconds = getConfig().getInt("settings.buff-check-interval-seconds", 5);
        buffTask = Bukkit.getScheduler().runTaskTimer(this, () -> {
            buffManager.applyBuffs();
        }, 40L, intervalSeconds * 20L);

        hudTask = Bukkit.getScheduler().runTaskTimer(this, () -> {
            buildingHudManager.updateHud();
        }, 20L, 20L);

        particleTask = Bukkit.getScheduler().runTaskTimer(this, () -> {
            buildingHudManager.renderParticles();
        }, 20L, 10L);

        integrityTask = Bukkit.getScheduler().runTaskTimer(this, () -> {
            buildingManager.performPeriodicIntegrityCheck();
        }, 600L, 1200L);

        getLogger().info("=================================================");
        getLogger().info(" TownyArchitecture v" + getDescription().getVersion() + " успешно активирован!");
        getLogger().info(" Towny Hook: " + (townyHook.isTownyEnabled() ? "Подключен" : "Отсутствует (Автономия)"));
        getLogger().info(" Встроенная система прокачки Архитектора: АКТИВНА");
        getLogger().info(" Чанковая система построек: АКТИВНА (/plot set build)");
        getLogger().info(" Подсветка зон действия (1х1): АКТИВНА (/build меню)");
        getLogger().info(" Загружено чертежей зданий: " + buildingManager.getBlueprints().size());
        getLogger().info(" Периодический аудит блоков: АКТИВЕН (каждые 60 сек)");
        getLogger().info("=================================================");
    }

    @Override
    public void onDisable() {
        if (buffTask != null) buffTask.cancel();
        if (hudTask != null) hudTask.cancel();
        if (integrityTask != null) integrityTask.cancel();
        if (particleTask != null) particleTask.cancel();
        
        if (buildingHudManager != null) buildingHudManager.clearAll();
        if (buildingManager != null) buildingManager.saveData();
        if (architectManager != null) architectManager.save();
        
        getLogger().info("TownyArchitecture выключен. Данные сохранены.");
    }

    private void saveResourceIfNotExists(String resourcePath) {
        File file = new File(getDataFolder(), resourcePath);
        if (!file.exists()) {
            saveResource(resourcePath, false);
        }
    }

    public void loadBuildingsConfig() {
        buildingsFile = new File(getDataFolder(), "buildings.yml");
        if (!buildingsFile.exists()) {
            saveResource("buildings.yml", false);
        }
        buildingsConfig = YamlConfiguration.loadConfiguration(buildingsFile);
    }

    public void reloadPluginConfig() {
        reloadConfig();
        loadBuildingsConfig();
        buildingManager.loadBlueprints(buildingsConfig);
        buildingManager.loadData();
    }

    public String getMsg(String path) {
        return getConfig().getString("messages." + path, "");
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void onBlockPlace(BlockPlaceEvent event) {
        boolean allow = buildingManager.handleBlockPlaced(
                event.getPlayer(), 
                event.getBlock().getLocation(), 
                event.getBlock().getType()
        );
        if (!allow) {
            event.setCancelled(true);
            return;
        }
        
        // Prevent XP exploit: if this block is inside an active building plot and is a building material,
        // it was already handled by buildingManager (with strict isNewMax check). Do not give generic town XP!
        ActiveBuilding bld = buildingManager.getBuildingAt(event.getBlock().getLocation());
        if (bld != null) {
            BuildingBlueprint bp = buildingManager.getBlueprint(bld.getBlueprintId());
            if (bp != null && bp.getResources().containsKey(event.getBlock().getType())) {
                return;
            }
        }

        if (townyHook.isResidentOfTownAt(event.getPlayer(), event.getBlock().getLocation())) {
            architectManager.handleTownBlockPlace(event.getPlayer(), event.getBlock().getType());
        }
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        boolean allow = buildingManager.handleBlockBroken(
                event.getPlayer(),
                event.getBlock().getLocation(),
                event.getBlock().getType()
        );
        if (!allow) {
            event.setCancelled(true);
            return;
        }

        // Prevent XP exploit: if inside an active building plot and is a building material
        ActiveBuilding bld = buildingManager.getBuildingAt(event.getBlock().getLocation());
        if (bld != null) {
            BuildingBlueprint bp = buildingManager.getBlueprint(bld.getBlueprintId());
            if (bp != null && bp.getResources().containsKey(event.getBlock().getType())) {
                return;
            }
        }

        if (townyHook.isResidentOfTownAt(event.getPlayer(), event.getBlock().getLocation())) {
            architectManager.handleTownBlockBreak(event.getPlayer(), event.getBlock().getType());
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockBurn(BlockBurnEvent event) {
        buildingManager.handleBlockBroken(
                null,
                event.getBlock().getLocation(),
                event.getBlock().getType()
        );
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerCommandPreprocess(PlayerCommandPreprocessEvent event) {
        String msg = event.getMessage().trim().toLowerCase();
        org.bukkit.entity.Player player = event.getPlayer();
        if (msg.startsWith("/plot set bank")) {
            event.setCancelled(true);
            player.sendMessage(org.bukkit.ChatColor.RED + "[!] Ванильные банки Towny отключены. Вместо этого постройте здание Банка через /builds!");
            return;
        }

        if (msg.startsWith("/t deposit") || msg.startsWith("/town deposit") || 
            msg.startsWith("/t withdraw") || msg.startsWith("/town withdraw")) {
            
            String townName = townyHook.getPlayerTownName(player);
            if (townName != null) {
                org.bukkit.Location loc = player.getLocation();
                if (townyHook.isLocationInPlayerTown(loc, player)) {
                    boolean isHomeBlock = townyHook.isLocationTownHomeBlock(loc);
                    if (!isHomeBlock) {
                        boolean nearBank = false;
                        com.towny.architecture.model.ChunkCoord pCoord = com.towny.architecture.model.ChunkCoord.fromLocation(loc);
                        
                        for (com.towny.architecture.model.ActiveBuilding bld : buildingManager.getActiveBuildings()) {
                            if (bld.getTownName().equalsIgnoreCase(townName) && 
                                bld.getBlueprintId().equalsIgnoreCase("bank") && 
                                bld.getStatus() == com.towny.architecture.model.ActiveBuilding.Status.ACTIVE) {
                                
                                for (com.towny.architecture.model.ChunkCoord c : bld.getAssignedChunks()) {
                                    if (Math.abs(c.getX() - pCoord.getX()) <= 5 && Math.abs(c.getZ() - pCoord.getZ()) <= 5) {
                                        nearBank = true;
                                        break;
                                    }
                                }
                            }
                            if (nearBank) break;
                        }

                        if (!nearBank) {
                            event.setCancelled(true);
                            player.sendMessage(org.bukkit.ChatColor.RED + "Финансовые операции доступны только в здании Банка (радиус 5 чанков) или на Home-чанке города!");
                            return;
                        }
                    }
                } else {
                    event.setCancelled(true);
                    player.sendMessage(org.bukkit.ChatColor.RED + "Вы можете использовать банк только на территории своего города!");
                    return;
                }
            }
        }
        
        if (msg.equals("/plot set build") || msg.equals("/plot set building") || 
            msg.equals("/plot set стройка") || msg.startsWith("/plot set build ")) {
            event.setCancelled(true);
            buildCommand.processPlotSetBuild(event.getPlayer());
        } else if (msg.startsWith("/plot set ")) {
            String town = townyHook.getPlayerTown(player);
            if (town != null && townyHook.hasBuildRights(player, player.getLocation())) {
                ChunkCoord cc = ChunkCoord.fromLocation(player.getLocation());
                if (buildingManager.getTownBuildPlots(town).contains(cc)) {
                    buildingManager.removeTownBuildPlot(town, cc);
                    player.sendMessage(org.bukkit.ChatColor.YELLOW + "[TownyArchitecture] Статус участка «Стройка» снят с этого чанка, так как вы изменили его тип.");
                }
            }
        }
    }

    @EventHandler(priority = EventPriority.NORMAL)
    public void onTabComplete(org.bukkit.event.server.TabCompleteEvent event) {
        String buffer = event.getBuffer();
        String[] args = buffer.split(" ", -1);
        if (args.length == 3 && args[0].equalsIgnoreCase("/plot") && args[1].equalsIgnoreCase("set")) {
            if ("build".startsWith(args[2].toLowerCase())) {
                java.util.List<String> completions = new java.util.ArrayList<>(event.getCompletions());
                if (!completions.contains("build")) {
                    completions.add("build");
                    event.setCompletions(completions);
                }
            }
        }
    }



    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        if (buildingHudManager != null) {
            buildingHudManager.removePlayer(event.getPlayer());
        }
        if (architectManager != null) {
            architectManager.removeBossBar(event.getPlayer());
        }
    }

    public static TownyArchitecturePlugin getInstance() { return instance; }
    public TownyHook getTownyHook() { return townyHook; }
    public ArchitectManager getArchitectManager() { return architectManager; }
    public BuildingManager getBuildingManager() { return buildingManager; }
    public BuffManager getBuffManager() { return buffManager; }
    public SiegeDamageManager getSiegeDamageManager() { return siegeDamageManager; }
    public BuildingHudManager getBuildingHudManager() { return buildingHudManager; }
    public BuildsMenuGui getBuildsMenuGui() { return buildsMenuGui; }
    public BuildCommand getBuildCommand() { return buildCommand; }
    public FileConfiguration getBuildingsConfig() { return buildingsConfig; }
}
