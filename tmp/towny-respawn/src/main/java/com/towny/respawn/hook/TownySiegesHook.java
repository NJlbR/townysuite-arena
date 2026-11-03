package com.towny.respawn.hook;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.plugin.Plugin;

import java.lang.reflect.Method;

public class TownySiegesHook {

    private boolean siegesPresent;
    private Method isTownUnderActiveSiegeMethod;
    private Method isLocationUnderActiveSiegeMethod;

    public TownySiegesHook() {
        init();
    }

    private void init() {
        Plugin plugin = Bukkit.getPluginManager().getPlugin("TownySieges");
        if (plugin != null && plugin.isEnabled()) {
            try {
                Class<?> clazz = Class.forName("com.towny.sieges.TownySiegesPlugin");
                isTownUnderActiveSiegeMethod = clazz.getMethod("isTownUnderActiveSiege", String.class);
                isLocationUnderActiveSiegeMethod = clazz.getMethod("isLocationUnderActiveSiege", Location.class);
                siegesPresent = true;
            } catch (Exception ignored) {
                siegesPresent = false;
            }
        } else {
            siegesPresent = false;
        }
    }

    public boolean isSiegesAvailable() {
        if (!siegesPresent) {
            init();
        }
        return siegesPresent;
    }

    public boolean isTownUnderActiveSiege(String townName) {
        if (!isSiegesAvailable() || townName == null || isTownUnderActiveSiegeMethod == null) return false;
        try {
            Object result = isTownUnderActiveSiegeMethod.invoke(null, townName);
            return result instanceof Boolean && (Boolean) result;
        } catch (Exception ignored) {
            return false;
        }
    }

    public boolean isLocationUnderActiveSiege(Location loc) {
        if (!isSiegesAvailable() || loc == null || isLocationUnderActiveSiegeMethod == null) return false;
        try {
            Object result = isLocationUnderActiveSiegeMethod.invoke(null, loc);
            return result instanceof Boolean && (Boolean) result;
        } catch (Exception ignored) {
            return false;
        }
    }
}
