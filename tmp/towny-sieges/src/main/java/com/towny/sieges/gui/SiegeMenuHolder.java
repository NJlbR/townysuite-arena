package com.towny.sieges.gui;

import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;

public class SiegeMenuHolder implements InventoryHolder {

    public enum Type {
        MAIN,
        CRAFT_MORTAR,
        CRAFT_REGULAR_AMMO,
        CRAFT_AP_AMMO,
        CRAFT_BANNER
    }

    private final Type type;
    private Inventory inventory;

    public SiegeMenuHolder(Type type) {
        this.type = type;
    }

    public Type getType() {
        return type;
    }

    public void setInventory(Inventory inventory) {
        this.inventory = inventory;
    }

    @Override
    public Inventory getInventory() {
        return inventory;
    }
}
