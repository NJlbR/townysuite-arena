package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.BuildingSchematic;
import com.towny.architecture.model.SchematicBlock;
import com.towny.architecture.util.RussianTranslator;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.entity.TNTPrimed;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.EntitySpawnEvent;
import org.bukkit.inventory.ItemFlag;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.ShapedRecipe;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.metadata.FixedMetadataValue;
import org.bukkit.persistence.PersistentDataType;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SiegeDamageManager implements Listener {
    private final TownyArchitecturePlugin plugin;
    private final NamespacedKey siegeTntItemKey;
    private final Set<Location> primedSiegeBlocks = Collections.synchronizedSet(new HashSet<>());

    // Damage tracking for City Wall blocks with 2x Blast Resistance
    private final Map<Location, Integer> cityWallDamageHits = new ConcurrentHashMap<>();
    private final Map<Location, Long> cityWallLastHitTime = new ConcurrentHashMap<>();

    public SiegeDamageManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
        this.siegeTntItemKey = new NamespacedKey(plugin, "siege_tnt");
        registerSiegeTntRecipe();
    }

    public ItemStack createSiegeTnt(int amount) {
        ItemStack item = new ItemStack(Material.TNT, amount);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(ChatColor.DARK_RED + "" + ChatColor.BOLD + "Осадный Динамит (Siege TNT)");
            List<String> lore = new ArrayList<>();
            lore.add(ChatColor.GRAY + "Тяжелый фортификационный фугас.");
            lore.add(ChatColor.GOLD + "⚡ Пробивает обсидиановые коробки и стены бункеров!");
            lore.add(ChatColor.YELLOW + "Радиус разрушения обсидиана: 3 блока.");
            lore.add(ChatColor.DARK_GRAY + "[Используется при затяжных осадах]");
            meta.setLore(lore);
            meta.getPersistentDataContainer().set(siegeTntItemKey, PersistentDataType.BYTE, (byte) 1);
            meta.addItemFlags(ItemFlag.HIDE_ENCHANTS);
            item.setItemMeta(meta);
        }
        return item;
    }

    private void registerSiegeTntRecipe() {
        NamespacedKey recipeKey = new NamespacedKey(plugin, "siege_tnt_recipe");
        if (Bukkit.getRecipe(recipeKey) != null) {
            Bukkit.removeRecipe(recipeKey);
        }
        ShapedRecipe recipe = new ShapedRecipe(recipeKey, createSiegeTnt(1));
        recipe.shape("IGI", "GTG", "IGI");
        recipe.setIngredient('T', Material.TNT);
        recipe.setIngredient('I', Material.IRON_INGOT);
        recipe.setIngredient('G', Material.GUNPOWDER);
        try {
            Bukkit.addRecipe(recipe);
        } catch (Exception e) {
            plugin.getLogger().warning("Не удалось зарегистрировать рецепт Осадного Динамита: " + e.getMessage());
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockPlace(BlockPlaceEvent event) {
        ItemStack item = event.getItemInHand();
        if (item.getType() == Material.TNT && item.hasItemMeta()) {
            if (item.getItemMeta().getPersistentDataContainer().has(siegeTntItemKey, PersistentDataType.BYTE)) {
                primedSiegeBlocks.add(event.getBlockPlaced().getLocation());
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        Location loc = event.getBlock().getLocation();
        primedSiegeBlocks.remove(loc);
        cityWallDamageHits.remove(loc);
        cityWallLastHitTime.remove(loc);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onTntSpawn(EntitySpawnEvent event) {
        if (event.getEntity() instanceof TNTPrimed) {
            TNTPrimed tnt = (TNTPrimed) event.getEntity();
            Location loc = tnt.getLocation().getBlock().getLocation();
            if (primedSiegeBlocks.remove(loc)) {
                tnt.setMetadata("is_siege_tnt", new FixedMetadataValue(plugin, true));
                tnt.setCustomName(ChatColor.RED + "⚡ Осадный TNT");
                tnt.setCustomNameVisible(true);
            }
        }
    }

    /**
     * Helper to get standard vanilla blast resistance for a block material.
     */
    public static float getBaseBlastResistance(Material mat) {
        if (mat == null) return 0f;
        String name = mat.name();
        if (name.contains("OBSIDIAN") || name.contains("ANVIL") || name.contains("RESPAWN_ANCHOR") || name.contains("NETHERITE_BLOCK") || name.contains("REINFORCED_DEEPSLATE")) {
            return 1200.0f;
        }
        if (name.contains("STONE") || name.contains("BRICK") || name.contains("COBBLE") || name.contains("PRISMARINE") || name.contains("IRON_BLOCK") || name.contains("DEEPSLATE")) {
            return 6.0f;
        }
        if (name.contains("IRON_BARS") || name.contains("CHAIN")) {
            return 6.0f;
        }
        if (name.contains("LANTERN")) {
            return 3.5f;
        }
        if (name.contains("WOOD") || name.contains("LOG") || name.contains("PLANK") || name.contains("FENCE") || name.contains("SLAB") || name.contains("STAIRS")) {
            return 3.0f;
        }
        if (name.contains("DIRT") || name.contains("SAND") || name.contains("GRAVEL") || name.contains("GRASS")) {
            return 0.5f;
        }
        if (name.contains("GLASS") || name.contains("LEAVES") || name.contains("WOOL") || name.contains("CARPET")) {
            return 0.2f;
        }
        return 2.0f;
    }

    /**
     * Evaluates 2x Blast Resistance for blocks belonging to "Городская Стена" (City Wall).
     * 
     * Requirement: Only blocks that are placed in their exact blueprint positions
     * receive double explosion resistance (2x blast resistance).
     * Random blocks or blocks not matching the blueprint have standard 1x resistance.
     * 
     * @return true if the block survives the explosion and should be removed from blockList(), false if destroyed.
     */
    public boolean processCityWallExplosionResistance(Block block, Location explosionCenter, float explosionPower, boolean isSiege) {
        if (block == null) return false;
        Location loc = block.getLocation();

        // 1. Strict Blueprint Verification:
        // Must belong to an active "city_wall" and match the exact schematic coordinate & material.
        if (!plugin.getBuildingManager().isProperCityWallBlock(loc)) {
            return false; // Not a verified blueprint block -> normal vanilla explosion physics
        }

        Material mat = block.getType();
        float baseResistance = getBaseBlastResistance(mat);
        float doubleResistance = baseResistance * 2.0f; // 2x Blast Resistance!

        double distance = (explosionCenter != null && explosionCenter.getWorld() == loc.getWorld())
                ? explosionCenter.distance(loc)
                : 1.0;

        // In Minecraft physics, blast power attenuates with distance and material resistance.
        // Effective blast force at distance d:
        float blastEnergyAtDistance = explosionPower / (float) Math.max(0.6, distance * 0.85);

        // Required threshold to destroy a 2x-reinforced block in a single blast:
        float singleHitThreshold = (doubleResistance / 5.0f + 0.3f) * 2.2f;

        long now = System.currentTimeMillis();
        Long lastHit = cityWallLastHitTime.get(loc);
        int hits = (lastHit != null && (now - lastHit) < 60000) ? cityWallDamageHits.getOrDefault(loc, 0) : 0;

        // If the blast energy does not exceed the 2x single-hit threshold, or if it's the 1st hit absorbed:
        if (blastEnergyAtDistance < singleHitThreshold || hits < 1) {
            // Block withstands the explosion thanks to double explosion resistance!
            cityWallDamageHits.put(loc, hits + 1);
            cityWallLastHitTime.put(loc, now);

            // Defensive fortification audio/visual impact feedback
            World world = loc.getWorld();
            if (world != null) {
                world.spawnParticle(Particle.BLOCK_CRACK, loc.clone().add(0.5, 0.5, 0.5), 14, 0.25, 0.25, 0.25, block.getBlockData());
                world.playSound(loc, Sound.BLOCK_ANVIL_LAND, 0.6f, 1.7f);
            }
            return true; // Survived! Block is protected from this explosion
        }

        // 2nd blast hit within 60s or massive direct point-blank siege blast: block breaks!
        cityWallDamageHits.remove(loc);
        cityWallLastHitTime.remove(loc);
        return false; // Broken
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onExplosion(EntityExplodeEvent event) {
        Entity entity = event.getEntity();
        boolean isSiege = entity != null && entity.hasMetadata("is_siege_tnt");
        Location center = event.getLocation();
        World world = center.getWorld();

        // 1. If it's a Siege TNT, breach obsidian and bunkers
        if (isSiege && world != null) {
            world.spawnParticle(Particle.EXPLOSION_HUGE, center, 3, 0.5, 0.5, 0.5, 0);
            world.playSound(center, Sound.ENTITY_GENERIC_EXPLODE, 2.0f, 0.5f);

            int r = 3;
            for (int x = -r; x <= r; x++) {
                for (int y = -r; y <= r; y++) {
                    for (int z = -r; z <= r; z++) {
                        if (x * x + y * y + z * z <= r * r + 1) {
                            Block b = world.getBlockAt(center.getBlockX() + x, center.getBlockY() + y, center.getBlockZ() + z);
                            Material type = b.getType();
                            if (type == Material.OBSIDIAN || type == Material.CRYING_OBSIDIAN || type == Material.REINFORCED_DEEPSLATE) {
                                if (isBlockInTownOutsideSiege(b.getLocation())) {
                                    continue;
                                }
                                if (!event.blockList().contains(b)) {
                                    event.blockList().add(b);
                                }
                                b.breakNaturally();
                            }
                        }
                    }
                }
            }
        }

        float power = isSiege ? 7.0f : 4.0f;

        // 2. Apply Double Blast Resistance to blueprint City Wall blocks
        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (processCityWallExplosionResistance(b, center, power, isSiege)) {
                it.remove(); // Protected and saved by 2x blast resistance!
            }
        }

        // 3. Process remaining broken blocks for active buildings health tracking
        List<Location> brokenLocs = new ArrayList<>();
        List<Material> brokenMats = new ArrayList<>();
        for (Block b : event.blockList()) {
            brokenLocs.add(b.getLocation().clone());
            brokenMats.add(b.getType());
            cityWallDamageHits.remove(b.getLocation());
            cityWallLastHitTime.remove(b.getLocation());
        }

        // Post-explosion verification on next tick (after the server turns broken blocks to AIR)
        Bukkit.getScheduler().runTask(plugin, () -> {
            for (int i = 0; i < brokenLocs.size(); i++) {
                Location bLoc = brokenLocs.get(i);
                plugin.getBuildingManager().handleBlockBroken(null, bLoc, brokenMats.get(i));
            }
        });
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onBlockExplosion(BlockExplodeEvent event) {
        Location center = event.getBlock().getLocation();
        float power = 4.0f;

        // 1. Apply Double Blast Resistance to blueprint City Wall blocks
        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (processCityWallExplosionResistance(b, center, power, false)) {
                it.remove(); // Protected and saved by 2x blast resistance!
            }
        }

        // 2. Process remaining broken blocks
        List<Location> brokenLocs = new ArrayList<>();
        List<Material> brokenMats = new ArrayList<>();
        for (Block b : event.blockList()) {
            brokenLocs.add(b.getLocation().clone());
            brokenMats.add(b.getType());
            cityWallDamageHits.remove(b.getLocation());
            cityWallLastHitTime.remove(b.getLocation());
        }

        // Post-explosion verification on next tick
        Bukkit.getScheduler().runTask(plugin, () -> {
            for (int i = 0; i < brokenLocs.size(); i++) {
                Location bLoc = brokenLocs.get(i);
                plugin.getBuildingManager().handleBlockBroken(null, bLoc, brokenMats.get(i));
            }
        });
    }

    /**
     * Informs players that repairs can ONLY be performed by physically placing missing blocks!
     */
    public void showRepairInstructions(Player player, ActiveBuilding building) {
        BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(building.getBlueprintId());
        String bpName = bp != null ? bp.getNameRu() : building.getBlueprintId();
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(building.getBlueprintId());

        if (building.getHealthPercent() >= 100.0 && building.isFullyBuilt()) {
            player.sendMessage(ChatColor.GREEN + "[TownyArchitecture v2] Здание «" + bpName + "» в идеальном состоянии (Прочность: 100%).");
            return;
        }

        player.sendMessage(ChatColor.GOLD + "══════ Ремонт чертежа «" + bpName + "» ══════");
        player.sendMessage(ChatColor.RED + "✖ Мгновенный ремонт командами отключен!");
        player.sendMessage(ChatColor.YELLOW + "Для восстановления найдите голограммы недостающих блоков и установите их:");

        if (schem != null) {
            World world = Bukkit.getWorld(building.getWorldName());
            int missingCount = 0;
            Map<Material, Integer> missingMats = new HashMap<>();
            if (world != null) {
                for (SchematicBlock sb : schem.getBlocks()) {
                    int wx = building.getOriginX() + sb.getDx();
                    int wy = building.getOriginY() + sb.getDy();
                    int wz = building.getOriginZ() + sb.getDz();
                    if (world.getBlockAt(wx, wy, wz).getType() != sb.getMaterial()) {
                        missingCount++;
                        missingMats.put(sb.getMaterial(), missingMats.getOrDefault(sb.getMaterial(), 0) + 1);
                        plugin.getHologramDisplayManager().respawnHologramForMissingBlock(building, sb.getDx(), sb.getDy(), sb.getDz(), sb.getMaterial());
                    }
                }
            }

            for (Map.Entry<Material, Integer> entry : missingMats.entrySet()) {
                player.sendMessage(ChatColor.GRAY + " - " + ChatColor.WHITE + RussianTranslator.getMaterialRu(entry.getKey()) + ": " +
                        ChatColor.RED + "требуется восстановить " + entry.getValue() + " шт.");
            }

            if (missingCount == 0) {
                player.sendMessage(ChatColor.GREEN + "✔ Все блоки чертежа целы!");
            }
        }

        player.sendMessage(ChatColor.GOLD + "Текущая прочность: " + 
                (building.getHealthPercent() >= 70.0 ? ChatColor.GREEN : ChatColor.RED) + 
                String.format("%.1f", building.getHealthPercent()) + "% " +
                ChatColor.GRAY + "(баффы активны только при прочности >= 70%)");
        player.sendMessage(ChatColor.DARK_GRAY + "💡 Подсказка: Крафтите Осадный TNT (I G I / G T G / I G I) для штурма обсидиановых укреплений!");
        player.sendMessage(ChatColor.GOLD + "════════════════════════════════════════════════");
    }

    private boolean isBlockInTownOutsideSiege(Location loc) {
        if (loc == null) return false;
        String town = plugin.getTownyHook().getTownName(loc);
        if (town == null) return false;
        try {
            org.bukkit.plugin.Plugin ts = Bukkit.getPluginManager().getPlugin("TownySieges");
            if (ts != null && ts.isEnabled()) {
                Object sm = ts.getClass().getMethod("getSiegeManager").invoke(ts);
                if (sm != null) {
                    Object res = sm.getClass().getMethod("isTownUnderActiveSiege", String.class).invoke(sm, town);
                    if (res instanceof Boolean && (Boolean) res) {
                        return false;
                    }
                }
                return true;
            }
        } catch (Throwable ignored) {}
        return true;
    }
}
