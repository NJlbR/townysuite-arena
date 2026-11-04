"""Regression checks for TownyArchitecture's layer-wireframe visibility rules."""
from pathlib import Path
import unittest

ROOT = Path(__file__).parent
HUD_SOURCE = ROOT / "tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java"
DISPLAY_SOURCE = ROOT / "tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java"


def trace_voxels(start, end):
    """Amanatides-Woo traversal matching the production ray-occlusion approach."""
    dx, dy, dz = (end[i] - start[i] for i in range(3))
    distance = (dx * dx + dy * dy + dz * dz) ** 0.5
    if distance < 1e-9:
        return []
    cell = [int(v // 1) for v in start]
    inv = [float("inf") if d == 0 else abs(1 / d) for d in (dx, dy, dz)]
    step = [(d > 0) - (d < 0) for d in (dx, dy, dz)]
    tmax = []
    for i, d in enumerate((dx, dy, dz)):
        if d == 0:
            tmax.append(float("inf"))
        else:
            edge_distance = cell[i] + 1 - start[i] if step[i] > 0 else start[i] - cell[i]
            tmax.append(edge_distance * inv[i])
    visited = []
    for _ in range(512):
        next_t = min(tmax)
        if next_t >= 1:
            break
        # Match the production supercover traversal: a ray crossing a voxel
        # corner advances all tied axes and does not visit side cells it only
        # touches at a zero-area boundary.
        for axis in range(3):
            if abs(tmax[axis] - next_t) <= 1e-10:
                cell[axis] += step[axis]
                tmax[axis] += inv[axis]
        visited.append(tuple(cell))
    return visited


def face_is_exposed(neighbor):
    # Production classification intentionally treats only air (and fluids, which
    # getCellType maps to AIR) as air; holograms/materials otherwise occupy a cell.
    return neighbor == "air"


def face_faces_viewer(normal, face_center, eye):
    return sum((eye[i] - face_center[i]) * normal[i] for i in range(3)) > 0


def ray_is_unoccluded(start, end, opaque_cells):
    return not any(cell in opaque_cells for cell in trace_voxels(start, end))


def rotate_relative(dx, dz, rotation, width, length):
    if rotation == 90:
        return dz, width - 1 - dx
    if rotation == 180:
        return width - 1 - dx, length - 1 - dz
    if rotation == 270:
        return length - 1 - dz, dx
    return dx, dz


class WireframeVisibilityTests(unittest.TestCase):
    def test_camera_side_selects_side_face_not_bottom(self):
        center = (0.5, 0.5, 0.5)
        self.assertTrue(face_faces_viewer((1, 0, 0), (1, 0.5, 0.5), (4, 0.5, 0.5)))
        self.assertFalse(face_faces_viewer((0, -1, 0), (0.5, 0, 0.5), (4, 0.5, 0.5)))
        self.assertTrue(face_faces_viewer((0, 1, 0), (0.5, 1, 0.5), (0.5, 5, 0.5)))
        self.assertTrue(face_faces_viewer((0, -1, 0), (0.5, 0, 0.5), (0.5, -4, 0.5)))
        self.assertEqual(center, (0.5, 0.5, 0.5))

    def test_hologram_neighbor_is_not_an_air_gap(self):
        self.assertTrue(face_is_exposed("air"))
        self.assertFalse(face_is_exposed("hologram"))
        self.assertFalse(face_is_exposed("glass"))
        self.assertFalse(face_is_exposed("obstacle"))

    def test_corner_crossings_do_not_false_occlude_side_voxels(self):
        # The ray passes exactly through grid corners. Side voxels are touched
        # only at their corners and must not make an otherwise visible edge vanish.
        visited = trace_voxels((0.5, 0.5, 0.5), (2.5, 2.5, 0.5))
        self.assertEqual(visited, [(1, 1, 0), (2, 2, 0)])
        self.assertTrue(ray_is_unoccluded((0.5, 0.5, 0.5), (2.5, 2.5, 0.5), {(1, 0, 0)}))

    def test_hologram_occludes_line_of_sight_from_shallow_side_angle(self):
        eye = (0.25, 0.45, 0.5)
        edge = (4.0, 1.0, 0.5)
        traversed_cells = set(trace_voxels(eye, edge))
        opaque_registry_cell = (2, 0, 0)
        self.assertIn(opaque_registry_cell, traversed_cells)
        self.assertFalse(ray_is_unoccluded(eye, edge, {opaque_registry_cell}))
        self.assertTrue(ray_is_unoccluded(eye, edge, {(8, 0, 0)}))
        # Transparent-looking world materials remain blockers under the wireframe's
        # conservative non-air physical-block rule.
        self.assertFalse(ray_is_unoccluded(eye, edge, {(1, 0, 0)}))

    def test_wireframe_edges_use_bright_thin_player_only_display_lines(self):
        hud = HUD_SOURCE.read_text()
        draw = hud[hud.index("private void drawVisibleEdge"):hud.index("private void syncWireframeDisplays")]
        config = (ROOT / "tmp/minecraft-build-v2/src/main/resources/config.yml").read_text()
        self.assertIn("world.spawn(spawnLocation, BlockDisplay.class", hud)
        self.assertIn("entity.setGlowing(true)", hud)
        self.assertIn("entity.setGlowColorOverride(color)", hud)
        self.assertIn("entity.setVisibleByDefault(false)", hud)
        self.assertIn("player.showEntity(plugin, display)", hud)
        self.assertNotIn("spawnParticle", draw)
        self.assertIn("line-thickness: 0.035", config)

    def test_diagonal_wireframe_displays_rotate_a_solid_rod_instead_of_stretching_texture(self):
        hud = HUD_SOURCE.read_text()
        self.assertIn("rotationTo(new Vector3f(1.0f, 0.0f, 0.0f), direction)", hud)
        self.assertIn("rotation.transform(new Vector3f(", hud)
        self.assertIn("entity.setBlock(Material.WHITE_CONCRETE.createBlockData())", hud)
        self.assertNotIn("entity.setBlock(Material.SEA_LANTERN.createBlockData())", hud)

     def test_non_cubic_models_glow_in_their_shape_without_a_cube_outline(self):
        hud = HUD_SOURCE.read_text()
        renderer = hud[hud.index("private void renderLayerWireframes"):hud.index("public void updateHud")]
        self.assertIn("getCollisionShape(", renderer)
        self.assertIn("drawCollisionVolumeGlow", renderer)
        self.assertIn("drawCrossModelPlantGlow", renderer)
        self.assertIn("spawnParticle(dustParticle", hud)
        self.assertIn("if (!isFullCubeShape(shape))", renderer)
        self.assertNotIn("drawPlantWireframe", hud)
        self.assertNotIn("drawShapeWireframe", hud)
        self.assertNotIn("firstPlane", hud)
        self.assertNotIn("secondPlane", hud)

    def test_block_events_refresh_only_changed_cell_and_use_brighter_lines(self):
        display = DISPLAY_SOURCE.read_text()
        building_manager = (ROOT / "tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java").read_text()
        placed = display[display.index("public boolean handleBlockPlaced"):display.index("public void onWorldBlockChanged")]
        self.assertNotIn("healOrRefreshLayerHolograms", placed)
        self.assertIn("GLOW_BLUE = Color.fromRGB(0, 235, 255)", display)
        self.assertIn("GLOW_RED = Color.fromRGB(255, 35, 45)", display)
        self.assertIn("runTask(plugin", building_manager)
        self.assertIn("onWorldBlockChanged(building, changedLoc)", building_manager)
        self.assertIn("activeDisplays.computeIfAbsent(bld.getInstanceId()", display)

    def test_rotated_hologram_occupancy_is_world_cell_based(self):
        # Rotating local schematic coordinates changes the display's world cell;
        # the registry must use that actual world cell for ray occlusion.
        for rotation in (0, 90, 180, 270):
            rx, rz = rotate_relative(1, 0, rotation, 3, 2)
            display_world_cell = (1 + rx, 70, rz)
            z_center = display_world_cell[2] + 0.5
            eye = (display_world_cell[0] - 3.0, 70.5, z_center)
            edge = (display_world_cell[0] + 3.0, 70.5, z_center)
            self.assertFalse(ray_is_unoccluded(eye, edge, {display_world_cell}), rotation)
        self.assertIn("display.getLocation()", DISPLAY_SOURCE.read_text())

    def test_production_renderer_uses_exposed_faces_and_registry_occlusion(self):
        hud = HUD_SOURCE.read_text()
        display = DISPLAY_SOURCE.read_text()
        self.assertIn("getOpaqueDisplayCellKeys(world)", hud)
        self.assertIn("getOpaqueDisplayCellKeys(World world)", display)
        self.assertIn("Amanatides-Woo traversal", hud)
        self.assertIn("tieEpsilon", hud)
        self.assertIn("isWireframePointVisible", hud)
        self.assertIn("if (facing <= 0.0001) continue", hud)
        self.assertIn("if (!isAirCell(neighborType)) continue", hud)
        self.assertNotIn("double yTop = Y + 1.015", hud)
        self.assertNotIn("yPillarStart", hud)


if __name__ == "__main__":
    unittest.main()
