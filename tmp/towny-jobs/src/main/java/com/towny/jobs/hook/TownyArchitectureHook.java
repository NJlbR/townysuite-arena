package com.towny.jobs.hook;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.plugin.Plugin;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Collection;

/** Optional reflective integration so TownyJobs never links into or changes TownyArchitecture. */
public final class TownyArchitectureHook {
    private final Plugin owner;

    public TownyArchitectureHook(Plugin owner) {
        this.owner = owner;
    }

    public boolean isAvailable() {
        Plugin plugin = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
        return plugin != null && plugin.isEnabled() && getBuildingManager(plugin) != null;
    }

    public boolean hasActiveConstruction(String townName) {
        Plugin architecture = getArchitecturePlugin();
        Object manager = architecture == null ? null : getBuildingManager(architecture);
        if (manager == null || townName == null) return false;
        try {
            Object raw = invoke(manager, "getActiveBuildings");
            if (!(raw instanceof Collection<?>)) return false;
            for (Object building : (Collection<?>) raw) {
                if ("CONSTRUCTING".equalsIgnoreCase(String.valueOf(invoke(building, "getStatus")))
                        && townName.equalsIgnoreCase(String.valueOf(invoke(building, "getTownName")))) {
                    return true;
                }
            }
        } catch (Throwable error) {
            owner.getLogger().fine("TownyArchitecture construction lookup failed: " + error.getMessage());
        }
        return false;
    }

    /** Called at MONITOR after TownyArchitecture has accepted and recorded the block. */
    public boolean isCorrectCompletedBlueprintBlock(Player player, BlockPlaceEvent event, String townName) {
        if (player == null || event == null || townName == null || !isAvailable()) return false;
        Plugin architecture = getArchitecturePlugin();
        Object manager = architecture == null ? null : getBuildingManager(architecture);
        if (manager == null) return false;
        Location location = event.getBlockPlaced().getLocation();
        try {
            Object building = invoke(manager, "getBuildingAt", location);
            if (building == null) building = invoke(manager, "getBuildingTouching", location);
            if (building == null || !townName.equalsIgnoreCase(String.valueOf(invoke(building, "getTownName")))) return false;
            String status = String.valueOf(invoke(building, "getStatus"));
            if (!status.equalsIgnoreCase("CONSTRUCTING") && !status.equalsIgnoreCase("ACTIVE")) return false;

            int originX = number(invoke(building, "getOriginX"));
            int originY = number(invoke(building, "getOriginY"));
            int originZ = number(invoke(building, "getOriginZ"));
            int rotation = number(invoke(building, "getRotationDeg"));
            int dx = location.getBlockX() - originX;
            int dy = location.getBlockY() - originY;
            int dz = location.getBlockZ() - originZ;

            Object schematicManager = invoke(architecture, "getSchematicManager");
            Object schematic = invoke(schematicManager, "getSchematic", invoke(building, "getBlueprintId"));
            if (schematic == null) return false;
            int width = number(invoke(schematic, "getWidthX"));
            int length = number(invoke(schematic, "getLengthZ"));
            Class<?> buildingManagerClass = Class.forName(
                    "com.towny.architecture.manager.BuildingManager", false, architecture.getClass().getClassLoader());
            Object rotated = invokeStatic(buildingManagerClass, "unrotateRelativeCoords",
                    dx, dz, rotation, width, length);
            if (!(rotated instanceof int[]) || ((int[]) rotated).length < 2) return false;
            int[] local = (int[]) rotated;
            Object schematicBlock = invoke(schematic, "getBlock", local[0], dy, local[1]);
            if (schematicBlock == null) return false;
            Object required = invoke(schematicBlock, "getMaterial");
            if (!(required instanceof Material)) return false;
            Block placed = event.getBlockPlaced();
            if (!placed.getType().equals(required)) {
                Object matches = invokeStatic(buildingManagerClass, "isMaterialMatch", placed.getType(), required);
                if (!Boolean.TRUE.equals(matches)) return false;
            }
            return Boolean.TRUE.equals(invoke(building, "isBlockCompleted", local[0], dy, local[1]));
        } catch (Throwable error) {
            owner.getLogger().fine("Couldn't validate a blueprint placement for the builder quota: " + error.getMessage());
            return false;
        }
    }

    private Plugin getArchitecturePlugin() {
        Plugin plugin = Bukkit.getPluginManager().getPlugin("TownyArchitecture");
        return plugin != null && plugin.isEnabled() ? plugin : null;
    }

    private Object getBuildingManager(Plugin plugin) {
        try {
            return invoke(plugin, "getBuildingManager");
        } catch (Throwable ignored) {
            return null;
        }
    }

    private static int number(Object value) {
        if (value instanceof Number) return ((Number) value).intValue();
        throw new IllegalStateException("Expected numeric architecture data");
    }

    private static Object invoke(Object target, String name, Object... arguments) throws Exception {
        if (target == null) throw new IllegalStateException("Missing target for " + name);
        return invokeMethod(target.getClass(), target, name, false, arguments);
    }

    private static Object invokeStatic(Class<?> type, String name, Object... arguments) throws Exception {
        return invokeMethod(type, null, name, true, arguments);
    }

    private static Object invokeMethod(Class<?> type, Object target, String name, boolean requireStatic,
                                       Object... arguments) throws Exception {
        for (Method method : type.getMethods()) {
            if (!method.getName().equals(name) || method.getParameterCount() != arguments.length) continue;
            if (requireStatic != Modifier.isStatic(method.getModifiers())) continue;
            Class<?>[] parameters = method.getParameterTypes();
            boolean matches = true;
            for (int i = 0; i < parameters.length; i++) {
                if (!compatible(parameters[i], arguments[i])) {
                    matches = false;
                    break;
                }
            }
            if (!matches) continue;
            try {
                return method.invoke(target, arguments);
            } catch (java.lang.reflect.InvocationTargetException error) {
                Throwable cause = error.getCause();
                if (cause instanceof Exception) throw (Exception) cause;
                throw new RuntimeException(cause);
            }
        }
        throw new NoSuchMethodException(type.getName() + "." + name);
    }

    private static boolean compatible(Class<?> parameter, Object argument) {
        if (argument == null) return !parameter.isPrimitive();
        if (!parameter.isPrimitive()) return parameter.isAssignableFrom(argument.getClass());
        return (parameter == int.class && argument instanceof Integer)
                || (parameter == long.class && argument instanceof Long)
                || (parameter == boolean.class && argument instanceof Boolean)
                || (parameter == double.class && argument instanceof Double)
                || (parameter == float.class && argument instanceof Float)
                || (parameter == short.class && argument instanceof Short)
                || (parameter == byte.class && argument instanceof Byte)
                || (parameter == char.class && argument instanceof Character);
    }
}
