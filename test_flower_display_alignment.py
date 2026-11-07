"""Regression checks for vanilla coordinate-seeded flower offsets on BlockDisplays."""
from pathlib import Path
import unittest

ROOT = Path(__file__).parent
DISPLAY_SOURCE = ROOT / "tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java"
HUD_SOURCE = ROOT / "tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java"


def signed(value, bits):
    mask = (1 << bits) - 1
    value &= mask
    return value - (1 << bits) if value >= (1 << (bits - 1)) else value


def vanilla_flower_offset(x, z):
    """Reproduce Mth.getSeed(x, 0, z) and vanilla's flower XZ offset."""
    seed = signed(x * 3129871, 32) ^ signed(z * 116129781, 64)
    seed = signed(seed * seed * 42317861 + seed * 11, 64)
    x_fraction = ((seed >> 16) & 15) / 15.0
    z_fraction = ((seed >> 24) & 15) / 15.0
    return ((x_fraction - 0.5) * 0.5, (z_fraction - 0.5) * 0.5)


class FlowerDisplayAlignmentTests(unittest.TestCase):
    def test_vanilla_offsets_are_position_seeded_and_bounded(self):
        self.assertEqual(vanilla_flower_offset(0, 0), (-0.25, -0.25))
        self.assertAlmostEqual(vanilla_flower_offset(1, 0)[0], 0.11666666666666667)
        self.assertAlmostEqual(vanilla_flower_offset(0, 1)[1], 0.08333333333333333)
        self.assertNotEqual(vanilla_flower_offset(1234, -5678), vanilla_flower_offset(0, 0))
        for x in range(-24, 25):
            for z in range(-24, 25):
                dx, dz = vanilla_flower_offset(x, z)
                self.assertGreaterEqual(dx, -0.25)
                self.assertLessEqual(dx, 0.25)
                self.assertGreaterEqual(dz, -0.25)
                self.assertLessEqual(dz, 0.25)

    def test_hologram_transformation_uses_vanilla_flower_hash_and_tags(self):
        source = DISPLAY_SOURCE.read_text()
        method = source[source.index("public Transformation createBlockTransformation(BlockData data"):
                            source.index("public BlockData getRotatedSchematicBlockData")]
        self.assertIn("Tag.SMALL_FLOWERS.isTagged(data.getMaterial())", method)
        self.assertIn("Tag.TALL_FLOWERS.isTagged(data.getMaterial())", method)
        self.assertIn("blockX * 3129871", method)
        self.assertIn("blockZ * 116129781L", method)
        self.assertIn("seed * seed * 42317861L + seed * 11L", method)
        self.assertIn("seed >> 16 & 15L", method)
        self.assertIn("seed >> 24 & 15L", method)
        self.assertIn("flowerOffsetX", method)
        self.assertIn("flowerOffsetZ", method)

    def test_primary_and_glow_displays_use_the_same_world_cell_offset(self):
        display = DISPLAY_SOURCE.read_text()
        hud = HUD_SOURCE.read_text()
        self.assertIn("createBlockTransformation(\n                display.getBlock(), location.getBlockX(), location.getBlockZ())", display)
        self.assertGreaterEqual(display.count("applyBlockTransformation(entity);"), 3)
        self.assertIn("applyBlockTransformation(disp);", display)
        self.assertIn("applyBlockTransformation(existing);", display)
        self.assertIn("createBlockTransformation(entity.getBlock(), blockX, blockZ)", hud)

    def test_non_flower_transform_remains_zero_offset(self):
        source = DISPLAY_SOURCE.read_text()
        method = source[source.index("public Transformation createBlockTransformation(BlockData data"):
                            source.index("public BlockData getRotatedSchematicBlockData")]
        self.assertIn("double flowerOffsetX = 0.0", method)
        self.assertIn("double flowerOffsetZ = 0.0", method)
        self.assertEqual(vanilla_flower_offset(0, 0), (-0.25, -0.25))


if __name__ == "__main__":
    unittest.main()
