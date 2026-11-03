package com.towny.respawn.model;

import org.bukkit.Location;
import org.bukkit.Material;

import java.util.List;

public class RespawnPoint {

    public enum Type {
        BED,
        TOWN_SPAWN,
        NATION_SPAWN,
        VANILLA,
        VANILLA_RANDOM,
        SERVER_SPAWN
    }

    private final Type type;
    private final String id;
    private final String title;
    private final List<String> lore;
    private final Material icon;
    private final Location location;
    private final boolean available;
    private final String unavailableReason;

    public RespawnPoint(Type type, String id, String title, List<String> lore, Material icon, Location location, boolean available, String unavailableReason) {
        this.type = type;
        this.id = id;
        this.title = title;
        this.lore = lore;
        this.icon = icon;
        this.location = location;
        this.available = available;
        this.unavailableReason = unavailableReason;
    }

    public Type getType() {
        return type;
    }

    public String getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getDisplayName() {
        return title;
    }

    public List<String> getLore() {
        return lore;
    }

    public Material getIcon() {
        return icon;
    }

    public Location getLocation() {
        return location;
    }

    public Location getTargetLocation() {
        return location;
    }

    public boolean isAvailable() {
        return available;
    }

    public String getUnavailableReason() {
        return unavailableReason;
    }
}
