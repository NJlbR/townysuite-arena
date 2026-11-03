package com.towny.sieges.bossbar;

import com.towny.sieges.TownySiegesPlugin;
import com.towny.sieges.model.NationWar;
import com.towny.sieges.model.SiegeCamp;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.entity.Player;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SiegeBossBarManager {

    private final TownySiegesPlugin plugin;
    private final Map<UUID, BossBar> playerBossBars = new ConcurrentHashMap<>();

    public SiegeBossBarManager(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    public void updateAllBossBars() {
        if (!plugin.getConfig().getBoolean("bossbar.enabled", true)) {
            clearAll();
            return;
        }

        for (Player player : Bukkit.getOnlinePlayers()) {
            updatePlayerBossBar(player);
        }
    }

    public void updatePlayerBossBar(Player player) {
        if (player == null || !player.isOnline()) return;

        if (!plugin.getConfig().getBoolean("bossbar.enabled", true)) {
            removePlayerBossBar(player);
            return;
        }

        String townName = plugin.getTownyHook().getPlayerTownName(player);
        if (townName == null) {
            removePlayerBossBar(player);
            return;
        }

        // 1. Check Nation Wars First (Unified Global BossBar)
        NationWar war = plugin.getSiegeManager().getActiveNationWarForTown(townName);
        if (war != null && war.getStatus() != NationWar.Status.COMPLETED) {
            displayNationWarBossBar(player, war);
            return;
        }

        // 2. Check Individual Local Town Siege
        SiegeCamp camp = plugin.getSiegeManager().getActiveSiegeForTown(townName);
        if (camp == null || camp.getStatus() == SiegeCamp.Status.COMPLETED || camp.getStatus() == SiegeCamp.Status.CANCELLED) {
            removePlayerBossBar(player);
            return;
        }

        displayLocalSiegeBossBar(player, townName, camp);
    }

    private void displayNationWarBossBar(Player player, NationWar war) {
        BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), k -> {
            BossBar b = Bukkit.createBossBar(
                    "Война Наций",
                    BarColor.YELLOW,
                    BarStyle.SEGMENTED_10
            );
            b.addPlayer(player);
            b.setVisible(true);
            return b;
        });

        if (bar == null) return;
        if (!bar.getPlayers().contains(player)) {
            bar.addPlayer(player);
        }

        String timeStr = war.getFormattedRemainingTime();
        if (war.isPreparation()) {
            bar.setColor(BarColor.YELLOW);
            bar.setStyle(BarStyle.SEGMENTED_10);
            long totalPrep = plugin.getConfig().getLong("nationwar.preparation-duration-seconds", 86400L);
            long rem = war.getRemainingSeconds();
            double progress = Math.max(0.0, Math.min(1.0, (double) rem / (double) totalPrep));
            bar.setProgress(progress);

            String title = ChatColor.translateAlternateColorCodes('&',
                    "&6&l⚔ ВОЙНА НАЦИЙ: &e" + war.getAttackerNation() + " &7vs &c" + war.getDefenderNation() +
                    " &7| &eШтурм через: &b" + timeStr + " &7(Единый таймер)");
            bar.setTitle(title);
        } else if (war.isActiveAssault()) {
            bar.setColor(BarColor.RED);
            bar.setStyle(BarStyle.SOLID);
            long totalAssault = plugin.getConfig().getLong("nationwar.assault-duration-seconds", 7200L);
            long rem = war.getRemainingSeconds();
            double progress = Math.max(0.0, Math.min(1.0, (double) rem / (double) totalAssault));
            bar.setProgress(progress);

            String title = ChatColor.translateAlternateColorCodes('&',
                    "&4&l⚡ ШТУРМ НАЦИЙ! &e" + war.getAttackerNation() + " &4⚔ &c" + war.getDefenderNation() +
                    " &7| &cВЗРЫВЫ ВО ВСЕХ ГОРОДАХ! &7| &e" + timeStr + " &4⚡");
            bar.setTitle(title);
        }
    }

    private void displayLocalSiegeBossBar(Player player, String townName, SiegeCamp camp) {
        boolean isDefender = townName.equalsIgnoreCase(camp.getDefendingTown());
        boolean isAttacker = townName.equalsIgnoreCase(camp.getAttackingTown());

        if (!isDefender && !isAttacker) {
            removePlayerBossBar(player);
            return;
        }

        BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), k -> {
            BossBar b = Bukkit.createBossBar(
                    "Осада",
                    BarColor.YELLOW,
                    BarStyle.SEGMENTED_10
            );
            b.addPlayer(player);
            b.setVisible(true);
            return b;
        });

        if (bar == null) return;
        if (!bar.getPlayers().contains(player)) {
            bar.addPlayer(player);
        }

        String timeStr = camp.getFormattedRemainingTime();
        int chunkCount = camp.getClaimedChunks().size();

        if (camp.isPreparationPhase()) {
            long totalPrep = plugin.getConfig().getLong("siege.preparation-duration-seconds", 86400L);
            long rem = camp.getRemainingPreparationSeconds();
            double progress = Math.max(0.0, Math.min(1.0, (double) rem / (double) totalPrep));

            bar.setColor(BarColor.YELLOW);
            bar.setStyle(BarStyle.SEGMENTED_10);
            bar.setProgress(progress);

            String title = isDefender ?
                    "&c&l⚔ ВАШ ГОРОД ОСАЖДЁН! &eВраг: &6" + camp.getAttackingTown() + " &7| &eШтурм через: &b" + timeStr :
                    "&6&l⚔ ОСАДА ГОРОДА &c" + camp.getDefendingTown() + "&r &7| &eШтурм через: &b" + timeStr;
            bar.setTitle(ChatColor.translateAlternateColorCodes('&', title));
        } else if (camp.isActiveSiege()) {
            long totalActive = plugin.getConfig().getLong("siege.active-duration-seconds", 7200L);
            long rem = camp.getRemainingActiveSeconds();
            double progress = Math.max(0.0, Math.min(1.0, (double) rem / (double) totalActive));

            bar.setColor(BarColor.RED);
            bar.setStyle(BarStyle.SOLID);
            bar.setProgress(progress);

            String title = isDefender ?
                    "&4&l⚡ ИДЁТ ШТУРМ ВАШЕГО ГОРОДА! &cВзрывы активны! &7| &fОсталось: &e" + timeStr :
                    "&4&l⚡ ШТУРМ ГОРОДА &6" + camp.getDefendingTown() + "&4! &cОрудия активны! &7| &fОсталось: &e" + timeStr;
            bar.setTitle(ChatColor.translateAlternateColorCodes('&', title));
        }
    }

    public void removePlayerBossBar(Player player) {
        if (player == null) return;
        BossBar bar = playerBossBars.remove(player.getUniqueId());
        if (bar != null) {
            bar.removePlayer(player);
            bar.setVisible(false);
        }
    }

    public void clearAll() {
        for (BossBar bar : playerBossBars.values()) {
            bar.removeAll();
            bar.setVisible(false);
        }
        playerBossBars.clear();
    }
}
