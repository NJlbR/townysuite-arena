package com.towny.respawn.gui;

import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;

public class RespawnMenuHolder implements InventoryHolder {

    public enum Mode {
        RESPAWN_SELECTION,
        DEATH_RESPAWN
    }

    private final Mode mode;
    private final Player player;
    private Inventory inventory;

    public RespawnMenuHolder(Mode mode, Player player) {
        this.mode = mode;
        this.player = player;
    }

    public Mode getMode() {
        return mode;
    }

    public Player getPlayer() {
        return player;
    }

    @Override
    public Inventory getInventory() {
        return inventory;
    }

    public void setInventory(Inventory inventory) {
        this.inventory = inventory;
    }
}
