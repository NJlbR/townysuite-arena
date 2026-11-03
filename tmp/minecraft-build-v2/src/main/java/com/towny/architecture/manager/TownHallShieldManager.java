package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import org.bukkit.ChatColor;
import org.bukkit.entity.Player;

import java.util.HashMap;
import java.util.Map;

public class TownHallShieldManager {

    private final TownyArchitecturePlugin plugin;
    private boolean globalWarActive = false;
    private final Map<String, Boolean> townWarStates = new HashMap<>();
    private final Map<String, Double> townShieldHp = new HashMap<>();

    public static class DamageResult {
        public final boolean shieldDamaged;
        public final double damageDealt;
        public final double remainingShield;
        public final String message;

        public DamageResult(boolean shieldDamaged, double damageDealt, double remainingShield, String message) {
            this.shieldDamaged = shieldDamaged;
            this.damageDealt = damageDealt;
            this.remainingShield = remainingShield;
            this.message = message;
        }
    }

    public static enum DamageStatus {
        PEACE,
        SHIELD_ABSORBED,
        TOWNHALL_DAMAGED
    }

    public TownHallShieldManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
    }

    public boolean isGlobalWarActive() {
        return globalWarActive;
    }

    public void setGlobalWarActive(boolean active) {
        this.globalWarActive = active;
    }

    public boolean isWarActive(String townName) {
        if (globalWarActive) return true;
        if (townName == null) return false;
        return townWarStates.getOrDefault(townName.toLowerCase(), false);
    }

    public void setTownWarActive(String townName, boolean active) {
        if (townName != null) {
            townWarStates.put(townName.toLowerCase(), active);
        }
    }

    public ActiveBuilding getTownHall(String townName) {
        if (townName == null) return null;
        for (ActiveBuilding b : plugin.getBuildingManager().getActiveBuildings()) {
            if ("town_hall".equalsIgnoreCase(b.getBlueprintId()) && townName.equalsIgnoreCase(b.getTownName())) {
                return b;
            }
        }
        return null;
    }

    public int getWallCount(String townName) {
        if (townName == null) return 0;
        int count = 0;
        for (ActiveBuilding b : plugin.getBuildingManager().getActiveBuildings()) {
            if ("city_wall".equalsIgnoreCase(b.getBlueprintId()) && townName.equalsIgnoreCase(b.getTownName())) {
                count++;
            }
        }
        return count;
    }

    public double getMaxShieldHp(String townName) {
        int walls = getWallCount(townName);
        return walls * 100.0;
    }

    public double getShieldHp(String townName) {
        if (townName == null) return 0.0;
        double max = getMaxShieldHp(townName);
        return townShieldHp.getOrDefault(townName.toLowerCase(), max);
    }

    public double getTownHallIntegrityPercent(String townName) {
        ActiveBuilding th = getTownHall(townName);
        if (th == null) return 100.0;
        int total = th.getTotalRequiredBlocks();
        if (total <= 0) return 100.0;
        int placed = th.getTotalPlacedBlocks();
        return Math.min(100.0, Math.max(0.0, (placed * 100.0) / total));
    }

    public DamageResult simulateDamage(String townName, double amount, Player attacker) {
        if (townName == null) {
            return new DamageResult(false, 0, 0, ChatColor.RED + "Город не найден!");
        }

        if (!isWarActive(townName)) {
            return new DamageResult(false, 0, getShieldHp(townName), ChatColor.YELLOW + "В мирное время щит Мэрии не принимает урон. Включите режим войны (/build war on).");
        }

        double currentShield = getShieldHp(townName);
        if (currentShield > 0) {
            double newShield = Math.max(0.0, currentShield - amount);
            townShieldHp.put(townName.toLowerCase(), newShield);
            return new DamageResult(true, amount, newShield,
                    ChatColor.GOLD + "[Осада] Щит Мэрии города " + townName + " принял " + amount + " урона! Остаток щита: " + String.format("%.1f", newShield) + " HP.");
        } else {
            ActiveBuilding th = getTownHall(townName);
            if (th == null) {
                return new DamageResult(false, amount, 0, ChatColor.RED + "У города " + townName + " нет постройки Мэрия!");
            }
            return new DamageResult(false, amount, 0,
                    ChatColor.DARK_RED + "[Осада] Щит уничтожен! Урон " + amount + " напрямую нанесён конструкции Мэрии города " + townName + "!");
        }
    }
}
