package com.towny.respawn.manager;

import com.towny.respawn.TownyRespawnPlugin;
import com.towny.respawn.gui.RespawnMenuHolder;
import com.towny.respawn.model.PlayerBed;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.OfflinePlayer;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.BlockFace;
import org.bukkit.block.data.type.Bed;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.permissions.PermissionAttachmentInfo;

import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Manages player bed respawn points with:
 * 1. Automatic removal of destroyed beds from the menu and database.
 * 2. Strict limit: exactly 1 player can claim a bed.
 * 3. Two-block bed normalization: HEAD and FOOT are treated as the same canonical bed.
 */
public class BedManager {

    private final TownyRespawnPlugin plugin;
    private final File dataFile;
    private final Map<UUID, List<PlayerBed>> playerBeds = new ConcurrentHashMap<>();
    private final Map<UUID, UUID> pendingRenames = new ConcurrentHashMap<>();

    private static final BlockFace[] HORIZONTAL_FACES = {
            BlockFace.NORTH, BlockFace.SOUTH, BlockFace.EAST, BlockFace.WEST
    };

    public BedManager(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
        this.dataFile = new File(plugin.getDataFolder(), "player_beds.yml");
    }

    public void load() {
        playerBeds.clear();
        if (!dataFile.exists()) return;

        FileConfiguration config = YamlConfiguration.loadConfiguration(dataFile);
        ConfigurationSection root = config.getConfigurationSection("players");
        if (root == null) return;

        for (String uuidStr : root.getKeys(false)) {
            try {
                UUID uuid = UUID.fromString(uuidStr);
                List<?> rawList = root.getList(uuidStr);
                if (rawList != null) {
                    List<PlayerBed> beds = new ArrayList<>();
                    for (Object obj : rawList) {
                        if (obj instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> map = (Map<String, Object>) obj;
                            beds.add(PlayerBed.deserialize(map));
                        } else if (obj instanceof PlayerBed) {
                            beds.add((PlayerBed) obj);
                        }
                    }
                    playerBeds.put(uuid, beds);
                }
            } catch (Exception e) {
                plugin.getLogger().warning("Could not load beds for UUID " + uuidStr + ": " + e.getMessage());
            }
        }
    }

    public void save() {
        FileConfiguration config = new YamlConfiguration();
        for (Map.Entry<UUID, List<PlayerBed>> entry : playerBeds.entrySet()) {
            List<Map<String, Object>> serialized = new ArrayList<>();
            for (PlayerBed bed : entry.getValue()) {
                serialized.add(bed.serialize());
            }
            config.set("players." + entry.getKey().toString(), serialized);
        }

        try {
            config.save(dataFile);
        } catch (IOException e) {
            plugin.getLogger().severe("Failed to save player_beds.yml: " + e.getMessage());
        }
    }

    /**
     * Resolves the canonical HEAD block of a 2-block bed.
     * In Minecraft, clicking either the HEAD or FOOT will always resolve to the canonical HEAD.
     */
    public static Block getCanonicalBedHead(Block block) {
        if (block == null) return null;
        if (!(block.getBlockData() instanceof Bed)) {
            return block;
        }

        Bed bedData = (Bed) block.getBlockData();
        if (bedData.getPart() == Bed.Part.HEAD) {
            return block;
        }

        // FOOT block: find the head block
        // 1. Try direction of facing
        Block target = block.getRelative(bedData.getFacing());
        if (target.getBlockData() instanceof Bed && ((Bed) target.getBlockData()).getPart() == Bed.Part.HEAD) {
            return target;
        }

        // 2. Try opposite direction of facing
        Block oppTarget = block.getRelative(bedData.getFacing().getOppositeFace());
        if (oppTarget.getBlockData() instanceof Bed && ((Bed) oppTarget.getBlockData()).getPart() == Bed.Part.HEAD) {
            return oppTarget;
        }

        // 3. Fallback: check all horizontal neighbors
        for (BlockFace face : HORIZONTAL_FACES) {
            Block neighbor = block.getRelative(face);
            if (neighbor.getBlockData() instanceof Bed && ((Bed) neighbor.getBlockData()).getPart() == Bed.Part.HEAD) {
                return neighbor;
            }
        }

        return block;
    }

    /**
     * Finds the connected FOOT block for a given canonical HEAD block.
     */
    public static Block getConnectedBedFoot(Block headBlock) {
        if (headBlock == null) return null;
        if (!(headBlock.getBlockData() instanceof Bed)) {
            return null;
        }

        Bed headData = (Bed) headBlock.getBlockData();
        if (headData.getPart() == Bed.Part.FOOT) {
            return headBlock;
        }

        // 1. Try opposite direction of facing
        Block foot = headBlock.getRelative(headData.getFacing().getOppositeFace());
        if (foot.getBlockData() instanceof Bed && ((Bed) foot.getBlockData()).getPart() == Bed.Part.FOOT) {
            return foot;
        }

        // 2. Try direction of facing
        Block fFacing = headBlock.getRelative(headData.getFacing());
        if (fFacing.getBlockData() instanceof Bed && ((Bed) fFacing.getBlockData()).getPart() == Bed.Part.FOOT) {
            return fFacing;
        }

        // 3. Check all horizontal neighbors
        for (BlockFace face : HORIZONTAL_FACES) {
            Block neighbor = headBlock.getRelative(face);
            if (neighbor.getBlockData() instanceof Bed && ((Bed) neighbor.getBlockData()).getPart() == Bed.Part.FOOT) {
                return neighbor;
            }
        }

        return null;
    }

    public List<PlayerBed> getBeds(Player player) {
        if (player == null) return Collections.emptyList();
        cleanupDestroyedBeds(player);
        return getBeds(player.getUniqueId());
    }

    public List<PlayerBed> getBeds(UUID uuid) {
        return playerBeds.computeIfAbsent(uuid, k -> new ArrayList<>());
    }

    public int getMaxBeds(Player player) {
        if (player == null) return plugin.getConfig().getInt("beds.max-beds-default", 3);
        if (player.hasPermission("townyrespawn.beds.unlimited") || player.isOp()) {
            return 20;
        }

        int max = plugin.getConfig().getInt("beds.max-beds-default", 3);
        if (!plugin.getConfig().getBoolean("beds.use-permission-limits", true)) {
            return max;
        }

        for (PermissionAttachmentInfo pai : player.getEffectivePermissions()) {
            String perm = pai.getPermission().toLowerCase();
            if (perm.startsWith("townyrespawn.beds.") && pai.getValue()) {
                String suffix = perm.substring("townyrespawn.beds.".length());
                try {
                    int val = Integer.parseInt(suffix);
                    if (val > max) {
                        max = val;
                    }
                } catch (NumberFormatException ignored) {}
            }
        }
        return max;
    }

    /**
     * Checks if a bed (either head or foot block) is already claimed by any player.
     * Automatically purges destroyed beds so players can claim freshly placed beds.
     * Returns the UUID of the owner, or null if unclaimed.
     */
    public UUID getBedOwner(Block block) {
        if (block == null) return null;

        for (Map.Entry<UUID, List<PlayerBed>> entry : playerBeds.entrySet()) {
            UUID ownerUuid = entry.getKey();
            Iterator<PlayerBed> it = entry.getValue().iterator();
            while (it.hasNext()) {
                PlayerBed bed = it.next();
                if (bed.matchesBlock(block)) {
                    if (!isBedPhysicallyValid(bed)) {
                        // Destroyed bed cleanup on the fly
                        it.remove();
                        save();
                        continue;
                    }
                    return ownerUuid;
                }
            }
        }
        return null;
    }

    /**
     * Registers a bed for a player with:
     * 1. 2-block bed normalization (both head and foot resolve to the same canonical bed).
     * 2. Exclusive ownership: only 1 player can claim a bed.
     * 3. Max beds per player limit.
     */
    public boolean registerBed(Player player, Block clickedBlock) {
        if (player == null || clickedBlock == null) return false;

        // Clean up any previously destroyed beds for this player first
        cleanupDestroyedBeds(player);

        Block headBlock = getCanonicalBedHead(clickedBlock);
        if (headBlock == null) return false;
        Block footBlock = getConnectedBedFoot(headBlock);

        // 1. Check if the player already registered this exact bed (either head or foot)
        List<PlayerBed> beds = getBeds(player.getUniqueId());
        for (PlayerBed existing : beds) {
            if (existing.matchesBlock(headBlock) || existing.matchesBlock(clickedBlock)) {
                String prefix = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.prefix", "&b&l[TownyRespawn]&r "));
                player.sendMessage(prefix + ChatColor.YELLOW + "Эта кровать уже привязана к вам («" + existing.getName() + "»)! Повторная привязка не требуется.");
                return false;
            }
        }

        // 2. Check if ANOTHER player has already claimed this bed
        boolean exclusive = plugin.getConfig().getBoolean("beds.exclusive-one-player-per-bed", true);
        if (exclusive) {
            UUID existingOwner = getBedOwner(headBlock);
            if (existingOwner == null && footBlock != null) {
                existingOwner = getBedOwner(footBlock);
            }

            if (existingOwner != null && !existingOwner.equals(player.getUniqueId())) {
                OfflinePlayer op = Bukkit.getOfflinePlayer(existingOwner);
                String ownerName = (op.getName() != null) ? op.getName() : "другим игроком";
                String prefix = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.prefix", "&b&l[TownyRespawn]&r "));
                player.sendMessage(prefix + ChatColor.RED + "Эта кровать уже занята игроком " + ChatColor.YELLOW + ownerName + ChatColor.RED + "! На одной кровати может поставить спавн только один игрок.");
                return false;
            }
        }

        // 3. Check player's max bed limit
        int maxAllowed = getMaxBeds(player);
        if (beds.size() >= maxAllowed) {
            String prefix = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.prefix", "&b&l[TownyRespawn]&r "));
            String msg = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.bed-limit-reached", "&cУ вас достигнут лимит кроватей ({max})!"))
                    .replace("{max}", String.valueOf(maxAllowed));
            player.sendMessage(prefix + msg);
            return false;
        }

        int nextIndex = beds.size() + 1;
        String format = plugin.getConfig().getString("beds.default-bed-name-format", "Кровать #{number}");
        String name = format.replace("{number}", String.valueOf(nextIndex));

        PlayerBed newBed = new PlayerBed(player.getUniqueId(), name, headBlock, footBlock, player.getLocation().getYaw(), 0.0f);
        beds.add(newBed);
        save();
        return true;
    }

    public boolean removeBed(Player player, PlayerBed bed) {
        if (player == null || bed == null) return false;
        List<PlayerBed> beds = getBeds(player.getUniqueId());
        boolean removed = beds.removeIf(b -> b.getId().equals(bed.getId()));
        if (removed) {
            save();
        }
        return removed;
    }

    public boolean removeBedByIndex(Player player, int index) {
        List<PlayerBed> beds = getBeds(player.getUniqueId());
        if (index < 0 || index >= beds.size()) return false;
        beds.remove(index);
        save();
        return true;
    }

    public boolean renameBed(Player player, UUID bedId, String newName) {
        if (player == null || bedId == null || newName == null) return false;
        String trimmed = newName.trim();
        if (trimmed.isEmpty()) return false;
        if (trimmed.length() > 32) trimmed = trimmed.substring(0, 32);

        List<PlayerBed> beds = getBeds(player.getUniqueId());
        for (PlayerBed bed : beds) {
            if (bed.getId().equals(bedId)) {
                bed.setName(trimmed);
                save();
                return true;
            }
        }
        return false;
    }

    public boolean renameBedByIndex(Player player, int index, String newName) {
        List<PlayerBed> beds = getBeds(player.getUniqueId());
        if (index < 0 || index >= beds.size()) return false;
        String trimmed = newName.trim();
        if (trimmed.isEmpty()) return false;
        if (trimmed.length() > 32) trimmed = trimmed.substring(0, 32);

        beds.get(index).setName(trimmed);
        save();
        return true;
    }

    public PlayerBed getBedById(Player player, UUID bedId) {
        List<PlayerBed> beds = getBeds(player.getUniqueId());
        for (PlayerBed bed : beds) {
            if (bed.getId().equals(bedId)) return bed;
        }
        return null;
    }

    public void setPendingRename(UUID playerUuid, UUID bedId) {
        pendingRenames.put(playerUuid, bedId);
    }

    public UUID getPendingRenameBedId(UUID playerUuid) {
        return pendingRenames.get(playerUuid);
    }

    public void clearPendingRename(UUID playerUuid) {
        pendingRenames.remove(playerUuid);
    }

    public boolean isAwaitingRename(UUID playerUuid) {
        return pendingRenames.containsKey(playerUuid);
    }

    /**
     * Checks if a bed is still physically present in the Minecraft world.
     * Verifies both the head and foot coordinates.
     */
    public boolean isBedPhysicallyValid(PlayerBed bed) {
        if (bed == null) return false;
        if (!plugin.getConfig().getBoolean("beds.verify-bed-block-exists", true)) {
            return true;
        }

        World world = Bukkit.getWorld(bed.getWorldName());
        if (world == null) return false;

        int cx = bed.getHeadX() >> 4;
        int cz = bed.getHeadZ() >> 4;

        if (!world.isChunkLoaded(cx, cz)) {
            boolean loaded = world.loadChunk(cx, cz, false);
            if (!loaded) {
                // If chunk doesn't exist, invalid
                return false;
            }
        }

        Block headBlock = world.getBlockAt(bed.getHeadX(), bed.getHeadY(), bed.getHeadZ());
        if (headBlock.getType().name().endsWith("_BED")) {
            return true;
        }

        // Also check foot block in case head was broken or offset
        Block footBlock = world.getBlockAt(bed.getFootX(), bed.getFootY(), bed.getFootZ());
        return footBlock.getType().name().endsWith("_BED");
    }

    /**
     * Automatically cleans up destroyed beds for a specific player and saves data.
     * Returns true if any destroyed bed was removed.
     */
    public boolean cleanupDestroyedBeds(Player player) {
        if (player == null) return false;
        List<PlayerBed> beds = playerBeds.computeIfAbsent(player.getUniqueId(), k -> new ArrayList<>());
        boolean changed = false;
        Iterator<PlayerBed> it = beds.iterator();
        while (it.hasNext()) {
            PlayerBed bed = it.next();
            if (!isBedPhysicallyValid(bed)) {
                it.remove();
                changed = true;
            }
        }
        if (changed) {
            save();
        }
        return changed;
    }

    /**
     * Cleans up any bed matching a broken block across ALL players in the database.
     * Called when a block is broken, exploded, burned, or moved.
     * Automatically refreshes any currently open /respawn GUI in real-time!
     */
    public void cleanupDestroyedBedsAt(Block block) {
        if (block == null) return;
        boolean changed = false;

        for (Map.Entry<UUID, List<PlayerBed>> entry : playerBeds.entrySet()) {
            UUID ownerUuid = entry.getKey();
            List<PlayerBed> beds = entry.getValue();
            Iterator<PlayerBed> it = beds.iterator();

            while (it.hasNext()) {
                PlayerBed bed = it.next();
                if (bed.matchesBlock(block)) {
                    it.remove();
                    changed = true;

                    // Notify online owner that their bed was destroyed and automatically removed
                    Player owner = Bukkit.getPlayer(ownerUuid);
                    if (owner != null && owner.isOnline()) {
                        String prefix = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.prefix", "&b&l[TownyRespawn]&r "));
                        owner.sendMessage(prefix + ChatColor.RED + "Ваша кровать «" + ChatColor.WHITE + bed.getName() + ChatColor.RED + "» была разрушена и автоматически удалена из меню /respawn.");

                        // If the owner has the /respawn menu open, refresh it instantly!
                        if (owner.getOpenInventory().getTopInventory().getHolder() instanceof RespawnMenuHolder) {
                            RespawnMenuHolder holder = (RespawnMenuHolder) owner.getOpenInventory().getTopInventory().getHolder();
                            plugin.getGuiManager().renderGui(holder);
                        }
                    }
                }
            }
        }

        if (changed) {
            save();
        }
    }
}
