package com.towny.architecture.model;

import org.bukkit.Material;

import java.util.*;

public class BuildingSchematic {
    public static class ExteriorFace {
        private final int dx, dy, dz;
        private final int ox, oy, oz;

        public ExteriorFace(int dx, int dy, int dz, int ox, int oy, int oz) {
            this.dx = dx;
            this.dy = dy;
            this.dz = dz;
            this.ox = ox;
            this.oy = oy;
            this.oz = oz;
        }

        public int getDx() { return dx; }
        public int getDy() { return dy; }
        public int getDz() { return dz; }
        public int getOx() { return ox; }
        public int getOy() { return oy; }
        public int getOz() { return oz; }

        public boolean isRoof() { return oy > 0; }
        public boolean isWall() { return oy == 0; }

        public String getFaceNeighborKey() {
            return (dx + ox) + "," + (dy + oy) + "," + (dz + oz);
        }
    }

    private final String blueprintId;
    private final int widthX;
    private final int heightY;
    private final int lengthZ;
    private final List<SchematicBlock> blocks;
    private final Map<String, SchematicBlock> blockMap;
    private final Map<Integer, List<SchematicBlock>> blocksByLayer;
    private final Map<Material, Integer> totalMaterials;
    private final List<ExteriorFace> exteriorFaces;

    public BuildingSchematic(String blueprintId, int widthX, int heightY, int lengthZ, List<SchematicBlock> inputBlocks) {
        this.blueprintId = blueprintId;
        this.widthX = widthX;
        this.heightY = heightY;
        this.lengthZ = lengthZ;

        // Guaranteed deduplication by coordinate key
        this.blockMap = new LinkedHashMap<>();
        if (inputBlocks != null) {
            for (SchematicBlock sb : inputBlocks) {
                if (sb != null) {
                    this.blockMap.put(sb.getKey(), sb);
                }
            }
        }
        this.blocks = new ArrayList<>(this.blockMap.values());
        this.blocksByLayer = new TreeMap<>();
        this.totalMaterials = new LinkedHashMap<>();
        this.exteriorFaces = new ArrayList<>();

        for (SchematicBlock sb : this.blocks) {
            this.blocksByLayer.computeIfAbsent(sb.getDy(), k -> new ArrayList<>()).add(sb);
            this.totalMaterials.put(sb.getMaterial(), this.totalMaterials.getOrDefault(sb.getMaterial(), 0) + 1);
        }

        // Calculate exterior facade faces: outer wall sides AND outer roof tops
        int[][] horizontalDirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        for (SchematicBlock sb : this.blocks) {
            // 1. Exterior walls (horizontal contact)
            for (int[] dir : horizontalDirs) {
                int nx = sb.getDx() + dir[0];
                int ny = sb.getDy();
                int nz = sb.getDz() + dir[1];
                if (!blockMap.containsKey(nx + "," + ny + "," + nz)) {
                    exteriorFaces.add(new ExteriorFace(sb.getDx(), sb.getDy(), sb.getDz(), dir[0], 0, dir[1]));
                }
            }
            // 2. Exterior roof (vertical upward contact with open air)
            int topY = sb.getDy() + 1;
            if (!blockMap.containsKey(sb.getDx() + "," + topY + "," + sb.getDz())) {
                exteriorFaces.add(new ExteriorFace(sb.getDx(), sb.getDy(), sb.getDz(), 0, 1, 0));
            }
        }
    }

    public String getBlueprintId() { return blueprintId; }
    public int getWidthX() { return widthX; }
    public int getHeightY() { return heightY; }
    public int getLengthZ() { return lengthZ; }
    public List<SchematicBlock> getBlocks() { return Collections.unmodifiableList(blocks); }
    public int getTotalBlockCount() { return blocks.size(); }
    public Map<Material, Integer> getTotalMaterials() { return Collections.unmodifiableMap(totalMaterials); }
    public List<ExteriorFace> getExteriorFaces() { return Collections.unmodifiableList(exteriorFaces); }
    public int getExteriorFaceCount() { return exteriorFaces.size(); }

    public SchematicBlock getBlock(int dx, int dy, int dz) {
        return blockMap.get(dx + "," + dy + "," + dz);
    }

    public boolean hasBlockAt(int dx, int dy, int dz) {
        return blockMap.containsKey(dx + "," + dy + "," + dz);
    }

    public List<SchematicBlock> getBlocksAtLayer(int layerY) {
        return blocksByLayer.getOrDefault(layerY, Collections.emptyList());
    }

    public int getMaxLayer() {
        return blocksByLayer.isEmpty() ? 0 : ((TreeMap<Integer, List<SchematicBlock>>) blocksByLayer).lastKey();
    }

    public Set<Integer> getLayers() {
        return blocksByLayer.keySet();
    }
}
