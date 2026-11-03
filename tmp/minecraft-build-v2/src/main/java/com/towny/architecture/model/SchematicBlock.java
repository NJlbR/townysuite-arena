package com.towny.architecture.model;

import org.bukkit.Material;

public class SchematicBlock {
    private final int dx;
    private final int dy;
    private final int dz;
    private final Material material;

    public SchematicBlock(int dx, int dy, int dz, Material material) {
        this.dx = dx;
        this.dy = dy;
        this.dz = dz;
        this.material = material;
    }

    public int getDx() { return dx; }
    public int getDy() { return dy; }
    public int getDz() { return dz; }
    public Material getMaterial() { return material; }

    public String getKey() {
        return dx + "," + dy + "," + dz;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SchematicBlock that = (SchematicBlock) o;
        return dx == that.dx && dy == that.dy && dz == that.dz && material == that.material;
    }

    @Override
    public int hashCode() {
        int result = dx;
        result = 31 * result + dy;
        result = 31 * result + dz;
        result = 31 * result + (material != null ? material.hashCode() : 0);
        return result;
    }
}
