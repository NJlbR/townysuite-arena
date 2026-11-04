package com.towny.architecture.util;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.block.BlockFace;
import org.bukkit.block.data.BlockData;
import org.bukkit.block.data.Directional;
import org.bukkit.util.BoundingBox;
import org.bukkit.util.VoxelShape;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Geometry helpers that describe the volume a block actually renders.
 *
 * <p>Construction highlights must follow the real Minecraft model: a flower, a stair,
 * a slab or a sign only occupies a part of its 1x1x1 cell, so outlining the whole cell
 * produces the "floating cube" artifact. Every method here works in block-local
 * coordinates (0..1), so callers can place glow points exactly on the model geometry.</p>
 */
public final class ModelShapeUtil {

    /** Tolerance used when comparing shape boxes with the block cell. */
    private static final double EPSILON = 1.0e-4;

    /** A single box must cover at least this much of the cell to keep the cube wireframe. */
    private static final double SOLID_AXIS_THRESHOLD = 0.85;
    private static final double SOLID_VOLUME_THRESHOLD = 0.80;

    /** Block data strings map to location-independent model boxes, so they are cached. */
    private static final Map<String, List<BoundingBox>> BOX_CACHE = new ConcurrentHashMap<>();
    private static final int BOX_CACHE_LIMIT = 1024;

    private ModelShapeUtil() {
    }

    /**
     * Returns the rendered volume of the given block data in block-local coordinates.
     *
     * <p>The server only exposes collision shapes, which already describe stairs, slabs,
     * fences, walls, doors, trapdoors and most machinery very well. Models that are not
     * collidable (flowers, grass, signs, banners, rails, torches, buttons...) fall back to
     * a conservative approximation of their visible geometry instead of the full cube.</p>
     */
    public static List<BoundingBox> modelBoxes(BlockData data, Location location) {
        if (data == null) return Collections.emptyList();

        String cacheKey = null;
        try {
            cacheKey = data.getAsString();
        } catch (Throwable ignored) {
            // Some custom block data implementations do not support string serialization.
        }
        if (cacheKey != null) {
            List<BoundingBox> cached = BOX_CACHE.get(cacheKey);
            if (cached != null) return new ArrayList<>(cached);
        }

        List<BoundingBox> boxes = new ArrayList<>(4);
        boolean cacheable = cacheKey != null;
        try {
            VoxelShape shape = data.getCollisionShape(location);
            if (shape != null) {
                for (BoundingBox raw : shape.getBoundingBoxes()) {
                    if (isWorldRelative(raw)) cacheable = false;
                    BoundingBox box = normalize(raw, location);
                    if (box != null) boxes.add(box);
                }
            }
        } catch (Throwable ignored) {
            // Shape lookup unavailable for this block/API combination: fall back below.
        }

        if (boxes.isEmpty()) {
            boxes.addAll(fallbackBoxes(data));
            cacheable = cacheKey != null;
        }

        if (cacheable) {
            if (BOX_CACHE.size() > BOX_CACHE_LIMIT) BOX_CACHE.clear();
            BOX_CACHE.put(cacheKey, Collections.unmodifiableList(new ArrayList<>(boxes)));
        }
        return boxes;
    }

    /**
     * True when the model can be treated as a normal solid block, i.e. the classic cube
     * wireframe is still the best highlight. Nearly-full blocks (farmland, dirt path...)
     * count as solid, while stairs, slabs, signs, flowers and every other partial model
     * must be highlighted along their own shape.
     */
    public static boolean isSolidBlock(Collection<BoundingBox> boxes) {
        if (boxes == null || boxes.size() != 1) return false;
        BoundingBox box = boxes.iterator().next();
        double axisX = box.getMaxX() - box.getMinX();
        double axisY = box.getMaxY() - box.getMinY();
        double axisZ = box.getMaxZ() - box.getMinZ();
        if (axisX < SOLID_AXIS_THRESHOLD || axisY < SOLID_AXIS_THRESHOLD || axisZ < SOLID_AXIS_THRESHOLD) {
            return false;
        }
        return axisX * axisY * axisZ >= SOLID_VOLUME_THRESHOLD;
    }

    /** True when the shape is exactly one box that fills the whole block cell. */
    public static boolean isFullCube(Collection<BoundingBox> boxes) {
        if (boxes == null || boxes.size() != 1) return false;
        BoundingBox box = boxes.iterator().next();
        return box.getMinX() <= EPSILON && box.getMinY() <= EPSILON && box.getMinZ() <= EPSILON
                && box.getMaxX() >= 1.0 - EPSILON
                && box.getMaxY() >= 1.0 - EPSILON
                && box.getMaxZ() >= 1.0 - EPSILON;
    }

    /**
     * True for models built from two crossed vertical planes (flowers, grass, ferns,
     * saplings, mushrooms, crops...). Their geometry cannot be derived from collision data
     * (they have none), so the highlight follows the crossed planes explicitly.
     */
    public static boolean isCrossModel(Material material) {
        if (material == null) return false;
        String name = material.name();
        if (name.equals("FLOWER_POT") || name.equals("POTTED_FLOWER")
                || name.equals("CHORUS_FLOWER") || name.startsWith("FLOWERING_")) {
            return false;
        }
        if (name.contains("FLOWER")) return true;
        if (name.endsWith("_TULIP") || name.endsWith("_ORCHID") || name.endsWith("_SAPLING")
                || name.endsWith("_MUSHROOM") || name.endsWith("_FUNGUS")) {
            return true;
        }
        switch (name) {
            case "DANDELION":
            case "POPPY":
            case "BLUE_ORCHID":
            case "ALLIUM":
            case "AZURE_BLUET":
            case "OXEYE_DAISY":
            case "CORNFLOWER":
            case "LILY_OF_THE_VALLEY":
            case "WITHER_ROSE":
            case "TORCHFLOWER":
            case "PITCHER_PLANT":
            case "SHORT_GRASS":
            case "GRASS":
            case "TALL_GRASS":
            case "FERN":
            case "LARGE_FERN":
            case "DEAD_BUSH":
            case "BROWN_MUSHROOM":
            case "RED_MUSHROOM":
            case "CRIMSON_FUNGUS":
            case "WARPED_FUNGUS":
            case "CRIMSON_ROOTS":
            case "WARPED_ROOTS":
            case "NETHER_SPROUTS":
            case "SWEET_BERRY_BUSH":
            case "SEAGRASS":
            case "TALL_SEAGRASS":
            case "KELP":
            case "KELP_PLANT":
            case "SUGAR_CANE":
            case "WHEAT":
            case "CARROTS":
            case "POTATOES":
            case "BEETROOTS":
            case "NETHER_WART":
                return true;
            default:
                return false;
        }
    }

    /**
     * Approximation of the visible model for blocks that have no collision shape.
     * Everything stays inside the block cell and is deliberately smaller than a cube,
     * so a highlight can never suggest a solid block that is not there.
     */
    private static List<BoundingBox> fallbackBoxes(BlockData data) {
        Material material = data.getMaterial();
        String name = material.name();
        List<BoundingBox> boxes = new ArrayList<>(2);

        // Crossed-plane plants are rendered by their own dedicated glow.
        if (isCrossModel(material)) return boxes;

        // Wall/standing signs and banners: thin panel plus its post.
        if (name.endsWith("_SIGN") || name.endsWith("_BANNER")) {
            return panelBoxes(data);
        }

        // Flat models: rails, plates, wires, carpets, lily pads, snow layers, hanging plants.
        if (name.endsWith("_RAIL") || name.endsWith("_PRESSURE_PLATE")
                || name.endsWith("_CARPET") || name.equals("REDSTONE_WIRE")
                || name.equals("TRIPWIRE") || name.equals("LILY_PAD") || name.equals("SNOW")
                || name.equals("GLOW_LICHEN") || name.equals("VINE") || name.equals("HANGING_ROOTS")
                || name.equals("PINK_PETALS") || name.equals("SCULK_VEIN")) {
            boxes.add(new BoundingBox(0.03, 0.0, 0.03, 0.97, 0.08, 0.97));
            return boxes;
        }

        // Small upright models: torches, lanterns, candles, chains, levers, buttons, pots.
        if (name.contains("TORCH") || name.contains("LANTERN") || name.contains("CANDLE")
                || name.equals("END_ROD") || name.equals("CHAIN") || name.equals("LEVER")
                || name.contains("BUTTON") || name.contains("FLOWER_POT")
                || name.equals("LADDER") || name.equals("TRIPWIRE_HOOK")
                || name.equals("LIGHTNING_ROD") || name.equals("BELL")) {
            boxes.add(new BoundingBox(0.34, 0.0, 0.34, 0.66, 0.62, 0.66));
            return boxes;
        }

        // Unknown non-cubic model: inset volume, never a full cube.
        boxes.add(new BoundingBox(0.10, 0.04, 0.10, 0.90, 0.92, 0.90));
        return boxes;
    }

    /** Thin panel for signs and banners, oriented by the block's own facing. */
    private static List<BoundingBox> panelBoxes(BlockData data) {
        List<BoundingBox> boxes = new ArrayList<>(2);
        boolean thinAlongZ = true;
        if (data instanceof Directional) {
            BlockFace facing = ((Directional) data).getFacing();
            thinAlongZ = facing == BlockFace.NORTH || facing == BlockFace.SOUTH
                    || facing == BlockFace.UP || facing == BlockFace.DOWN;
        }
        if (thinAlongZ) {
            boxes.add(new BoundingBox(0.07, 0.32, 0.44, 0.93, 1.00, 0.56));
        } else {
            boxes.add(new BoundingBox(0.44, 0.32, 0.07, 0.56, 1.00, 0.93));
        }
        boxes.add(new BoundingBox(0.44, 0.00, 0.44, 0.56, 0.32, 0.56));
        return boxes;
    }

    private static boolean isWorldRelative(BoundingBox box) {
        if (box == null) return false;
        return box.getMaxX() > 1.5 || box.getMaxY() > 1.5 || box.getMaxZ() > 1.5
                || box.getMinX() < -0.5 || box.getMinY() < -0.5 || box.getMinZ() < -0.5;
    }

    /**
     * Re-bases a shape box into block-local coordinates and rejects degenerate boxes.
     * Paper returns block-local shapes, but other/older implementations may return
     * world-relative ones - both are handled here.
     */
    private static BoundingBox normalize(BoundingBox raw, Location location) {
        if (raw == null) return null;

        double minX = raw.getMinX();
        double minY = raw.getMinY();
        double minZ = raw.getMinZ();
        double maxX = raw.getMaxX();
        double maxY = raw.getMaxY();
        double maxZ = raw.getMaxZ();

        if (isWorldRelative(raw) && location != null) {
            minX -= location.getBlockX();
            maxX -= location.getBlockX();
            minY -= location.getBlockY();
            maxY -= location.getBlockY();
            minZ -= location.getBlockZ();
            maxZ -= location.getBlockZ();
        }

        minX = clamp01(minX);
        minY = clamp01(minY);
        minZ = clamp01(minZ);
        maxX = clamp01(maxX);
        maxY = clamp01(maxY);
        maxZ = clamp01(maxZ);

        if (maxX - minX <= EPSILON || maxY - minY <= EPSILON || maxZ - minZ <= EPSILON) {
            return null;
        }
        return new BoundingBox(minX, minY, minZ, maxX, maxY, maxZ);
    }

    private static double clamp01(double value) {
        if (value < 0.0) return 0.0;
        if (value > 1.0) return 1.0;
        return value;
    }
}
