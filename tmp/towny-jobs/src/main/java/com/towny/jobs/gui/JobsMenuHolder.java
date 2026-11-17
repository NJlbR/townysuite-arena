package com.towny.jobs.gui;

import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;

public final class JobsMenuHolder implements InventoryHolder {
    public enum Mode { MAIN, MEMBERS }

    public final Mode mode;
    public final String townId;
    public final String roleId;
    public final int page;
    private Inventory inventory;

    JobsMenuHolder(Mode mode, String townId, String roleId, int page) {
        this.mode = mode;
        this.townId = townId;
        this.roleId = roleId;
        this.page = page;
    }

    void setInventory(Inventory inventory) {
        this.inventory = inventory;
    }

    @Override
    public Inventory getInventory() {
        return inventory;
    }
}
