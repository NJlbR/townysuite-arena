package com.towny.architecture.model;

import org.bukkit.Material;
import java.util.Collections;
import java.util.Map;

public class BuildingBlueprint {
    private final String id;
    private final String name;
    private final String nameRu;
    private final String description;
    private final Material icon;
    private final int requiredSkillLevel;
    private final boolean isWorldWonder;
    private final int chunkWidth;   // Width in chunks (1 or 2)
    private final int chunkLength;  // Length in chunks (1 or 2)
    private final int heightY;      // Nominal structure height
    private final Map<Material, Integer> resources;
    private final Map<String, Object> buffs;
    private final String particleColorHex;
    private String wonderCompletedByTown;

    public BuildingBlueprint(
            String id,
            String name,
            String nameRu,
            String description,
            Material icon,
            int requiredSkillLevel,
            boolean isWorldWonder,
            int chunkWidth,
            int chunkLength,
            int heightY,
            Map<Material, Integer> resources,
            Map<String, Object> buffs,
            String particleColorHex) {
        this.id = id;
        this.name = name;
        this.nameRu = nameRu;
        this.description = description;
        this.icon = icon;
        this.requiredSkillLevel = requiredSkillLevel;
        this.isWorldWonder = isWorldWonder;
        this.chunkWidth = Math.max(1, chunkWidth);
        this.chunkLength = Math.max(1, chunkLength);
        this.heightY = heightY;
        this.resources = resources != null ? resources : Collections.emptyMap();
        this.buffs = buffs != null ? buffs : Collections.emptyMap();
        this.particleColorHex = particleColorHex;
        this.wonderCompletedByTown = null;
    }
    
    public String getParticleColorHex() { return particleColorHex; }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getNameRu() { return nameRu; }
    public String getDescription() { return description; }
    public Material getIcon() { return icon; }
    public int getRequiredSkillLevel() { return requiredSkillLevel; }
    public boolean isWorldWonder() { return isWorldWonder; }
    public int getChunkWidth() { return chunkWidth; }
    public int getChunkLength() { return chunkLength; }
    public int getHeightY() { return heightY; }
    public Map<Material, Integer> getResources() { return resources; }
    public Map<String, Object> getBuffs() { return buffs; }
    public String getWonderCompletedByTown() { return wonderCompletedByTown; }
    public void setWonderCompletedByTown(String town) { this.wonderCompletedByTown = town; }

    public int getTotalRequiredBlocks() {
        int total = 0;
        for (int count : resources.values()) {
            total += count;
        }
        return total > 0 ? total : (chunkWidth * chunkLength * 16 * 16);
    }

    public String getFootprintDisplay() {
        if (chunkWidth == 1 && chunkLength == 1) {
            return "1x1 чанк (16x16 блоков)";
        } else if (chunkWidth == 1 && chunkLength == 2) {
            return "1x2 чанка (16x32 блоков)";
        } else if (chunkWidth == 2 && chunkLength == 1) {
            return "2x1 чанка (32x16 блоков)";
        } else if (chunkWidth == 2 && chunkLength == 2) {
            return isWorldWonder ? "2x2 чанка (32x32 блока) - ЧУДО СВЕТА" : "2x2 чанка (32x32 блока)";
        }
        return chunkWidth + "x" + chunkLength + " чанков";
    }
}
