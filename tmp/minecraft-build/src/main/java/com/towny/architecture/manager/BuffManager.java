package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.model.ChunkCoord;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;

import java.util.Map;

public class BuffManager {
    private final TownyArchitecturePlugin plugin;

    public BuffManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
    }

    public void applyBuffs() {
        double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);

        for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
            // Only active buildings with health >= threshold grant buffs!
            if (bld.getStatus() != ActiveBuilding.Status.ACTIVE) continue;
            if (bld.getHealthPercent() < threshold) continue;

            BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
            if (bp == null) continue;

            Map<String, Object> buffs = bp.getBuffs();
            if (buffs.isEmpty()) continue;

            int chunkWidth = bp.getChunkWidth();
            int chunkLength = bp.getChunkLength();

            for (Player player : Bukkit.getOnlinePlayers()) {
                // RULE 1: STRICT CITIZENSHIP CHECK — ALL BUFFS ARE ONLY FOR CITIZENS OF THIS TOWN!
                String pTown = plugin.getTownyHook().getPlayerTownName(player);
                if (pTown == null || !pTown.equalsIgnoreCase(bld.getTownName())) {
                    continue; // Foreign players or wilderness wanderers NEVER receive buffs
                }

                // RULE 2: DISTANCE / TERRITORY BASED ON CHUNK FOOTPRINT
                // - 1x1: active only within 5 chunks of the building (citizens of this town only)
                // - 2x1 / 1x2: active across the entire town territory (citizens of this town only)
                // - 2x2 (World Wonders): active everywhere on the entire map (citizens of this town only)
                boolean eligible = false;
                Location pLoc = player.getLocation();

                if (chunkWidth == 1 && chunkLength == 1) {
                    // 1x1 chunk: buffs spread ONLY within a 2-chunk radius (5x5 area) around the building!
                    int radiusChunks = plugin.getConfig().getInt("settings.buff-1x1-chunk-radius", 2);
                    if (pLoc.getWorld() != null && pLoc.getWorld().getName().equals(bld.getWorldName())) {
                        int pChunkX = pLoc.getBlockX() >> 4;
                        int pChunkZ = pLoc.getBlockZ() >> 4;
                        for (ChunkCoord bChunk : bld.getAssignedChunks()) {
                            if (Math.abs(pChunkX - bChunk.getX()) <= radiusChunks && Math.abs(pChunkZ - bChunk.getZ()) <= radiusChunks) {
                                eligible = true;
                                break;
                            }
                        }
                    }
                } else if ((chunkWidth == 1 && chunkLength == 2) || (chunkWidth == 2 && chunkLength == 1)) {
                    // 2x1 or 1x2 chunks: buffs apply anywhere on the entire territory of the town!
                    eligible = plugin.getTownyHook().isLocationInTown(pLoc, bld.getTownName());
                } else if ((chunkWidth >= 2 && chunkLength >= 2) || bp.isWorldWonder()) {
                    // 2x2 chunks (World Wonders): buffs apply everywhere on the entire map / server, BUT STILL ONLY for citizens of this town!
                    eligible = true;
                } else {
                    // Fallback: entire town territory
                    eligible = plugin.getTownyHook().isLocationInTown(pLoc, bld.getTownName());
                }

                if (eligible) {
                    applyEffectsToPlayer(player, buffs);
                }
            }
        }
    }

    private void applyEffectsToPlayer(Player player, Map<String, Object> buffs) {
        // Duration in ticks (140 ticks = 7 seconds, refreshed every 5 seconds)
        int durationTicks = 140;

        if (buffs.containsKey("health-boost-hearts")) {
            int hearts = (int) buffs.get("health-boost-hearts");
            int amplifier = Math.max(0, hearts - 1);
            player.addPotionEffect(new PotionEffect(PotionEffectType.HEALTH_BOOST, durationTicks, amplifier, false, false, true));
        }

        if (buffs.containsKey("regeneration-level")) {
            int lvl = (int) buffs.get("regeneration-level");
            player.addPotionEffect(new PotionEffect(PotionEffectType.REGENERATION, durationTicks, Math.max(0, lvl - 1), false, false, true));
        }

        if (buffs.containsKey("strength-level")) {
            int lvl = (int) buffs.get("strength-level");
            player.addPotionEffect(new PotionEffect(PotionEffectType.INCREASE_DAMAGE, durationTicks, Math.max(0, lvl - 1), false, false, true));
        }

        if (buffs.containsKey("speed-level")) {
            int lvl = (int) buffs.get("speed-level");
            player.addPotionEffect(new PotionEffect(PotionEffectType.SPEED, durationTicks, Math.max(0, lvl - 1), false, false, true));
        }

        if (buffs.containsKey("haste-level")) {
            int lvl = (int) buffs.get("haste-level");
            player.addPotionEffect(new PotionEffect(PotionEffectType.FAST_DIGGING, durationTicks, Math.max(0, lvl - 1), false, false, true));
        }

        if (buffs.containsKey("resistance-level")) {
            int lvl = (int) buffs.get("resistance-level");
            player.addPotionEffect(new PotionEffect(PotionEffectType.DAMAGE_RESISTANCE, durationTicks, Math.max(0, lvl - 1), false, false, true));
        }

        if (buffs.containsKey("night-vision") && Boolean.TRUE.equals(buffs.get("night-vision"))) {
            player.addPotionEffect(new PotionEffect(PotionEffectType.NIGHT_VISION, 260, 0, false, false, true));
        }
    }
}

