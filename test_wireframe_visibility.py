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
        axis = min(range(3), key=lambda i: tmax[i])
        next_t = tmax[axis]
        cell[axis] += step[axis]
        tmax[axis] += inv[axis]
        if next_t >= 1:
            break
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
        self.assertIn("Amanatides-Woo voxel traversal", hud)
        self.assertIn("if (facing <= 0.0001) continue", hud)
        self.assertIn("if (!isAirCell(neighborType)) continue", hud)
        self.assertNotIn("double yTop = Y + 1.015", hud)
        self.assertNotIn("yPillarStart", hud)


if __name__ == "__main__":
    unittest.main()
