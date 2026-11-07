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
    # Partial collision shapes do not hide a whole face; only a full voxel does.
    return neighbor in {"air", "partial"}


def ray_hits_aabb(start, end, box_min, box_max):
    direction = [end[i] - start[i] for i in range(3)]
    enter, leave = 0.0, 1.0
    epsilon = 1e-9
    for axis in range(3):
        if abs(direction[axis]) < epsilon:
            if start[axis] <= box_min[axis] + epsilon or start[axis] >= box_max[axis] - epsilon:
                return False
            continue
        first = (box_min[axis] - start[axis]) / direction[axis]
        last = (box_max[axis] - start[axis]) / direction[axis]
        if first > last:
            first, last = last, first
        enter, leave = max(enter, first), min(leave, last)
        if leave - enter <= epsilon:
            return False
    return leave - enter > epsilon


def model_visible_to_any_sample(eye, samples, occluders):
    return any(
        not any(ray_hits_aabb(eye, sample, box_min, box_max) for box_min, box_max in occluders)
        for sample in samples
    )


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


def rotate_horizontal_direction(x, z, rotation):
    if rotation == 90:
        return z, -x
    if rotation == 180:
        return -x, -z
    if rotation == 270:
        return -z, x
    return x, z


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
        self.assertTrue(face_is_exposed("partial"))
        self.assertFalse(face_is_exposed("hologram"))
        self.assertFalse(face_is_exposed("full glass"))
        self.assertFalse(face_is_exposed("obstacle"))

    def test_corner_crossings_do_not_false_occlude_side_voxels(self):
        # The ray passes exactly through grid corners. Side voxels are touched
        # only at their corners and must not make an otherwise visible edge vanish.
        visited = trace_voxels((0.5, 0.5, 0.5), (2.5, 2.5, 0.5))
        self.assertEqual(visited, [(1, 1, 0), (2, 2, 0)])
        self.assertTrue(ray_is_unoccluded((0.5, 0.5, 0.5), (2.5, 2.5, 0.5), {(1, 0, 0)}))

    def test_collision_shape_visibility_does_not_treat_partial_blocks_as_full_cubes(self):
        # A stair/slab-like shape fills only the lower half of its voxel.
        lower_half = ((1.0, 0.0, 0.0), (2.0, 0.5, 1.0))
        self.assertTrue(ray_hits_aabb((0.25, 0.25, 0.5), (2.75, 0.25, 0.5), *lower_half))
        self.assertFalse(ray_hits_aabb((0.25, 0.75, 0.5), (2.75, 0.75, 0.5), *lower_half))
        # Merely touching the shape boundary is not a positive-volume occlusion.
        self.assertFalse(ray_hits_aabb((0.25, 0.5, 0.5), (2.75, 0.5, 0.5), *lower_half))

    def test_non_cubic_model_glow_is_suppressed_when_all_model_samples_are_occluded(self):
        eye = (0.5, 1.0, 0.5)
        samples = [(4.5, 1.2, 0.5), (4.5, 1.5, 0.5), (4.5, 1.8, 0.5)]
        full_wall = [((2.0, 0.0, 0.0), (3.0, 3.0, 1.0))]
        self.assertFalse(model_visible_to_any_sample(eye, samples, full_wall))
        # If a real opening exposes any part of the model, the model can glow.
        partial_wall = [((2.0, 0.0, 0.0), (3.0, 1.3, 1.0))]
        self.assertTrue(model_visible_to_any_sample(eye, samples, partial_wall))

    def test_non_cubic_model_visibility_has_no_short_distance_cutoff(self):
        hud = HUD_SOURCE.read_text()
        visibility = hud[hud.index("private boolean hasWireframeLineOfSight"):hud.index("private String particlePointKey")]
        self.assertNotIn("distance > 64.0", visibility)
        self.assertIn("hasWireframeLineOfSight(player, world", hud)
        self.assertIn("if (distance < 0.001) return true", visibility)
        model_display = hud[hud.index("private void showBlockModelGlow"):hud.index("private void renderLayerWireframes")]
        self.assertIn("entity.setViewRange(2.0f)", model_display)

    def test_matching_uncompleted_blocks_keep_their_current_layer_wireframe(self):
        hud = HUD_SOURCE.read_text()
        cell_type = hud[hud.index("private byte getCellType"):hud.index("private BlockData getRotatedSchematicBlockData")]
        self.assertIn("if (bld.isBlockCompleted(dx, dy, dz)) return TYPE_OTHER_LAYER", cell_type)
        self.assertIn("if (BuildingManager.isMaterialMatch(mat, sb.getMaterial())) return TYPE_HOLOGRAM", cell_type)
        self.assertIn("return TYPE_OBSTACLE", cell_type)

    def test_partial_block_preview_uses_building_rotation(self):
        hud = HUD_SOURCE.read_text()
        rotation = hud[hud.index("private BlockData getRotatedSchematicBlockData"):hud.index("private BlockData getBlockDataAtCell")]
        lookup = hud[hud.index("private BlockData getBlockDataAtCell"):hud.index("private Collection<BoundingBox> getCellCollisionBoxes")]
        self.assertIn("StructureRotation.COUNTERCLOCKWISE_90", rotation)
        self.assertIn("StructureRotation.CLOCKWISE_180", rotation)
        self.assertIn("StructureRotation.CLOCKWISE_90", rotation)
        self.assertIn("getRotatedSchematicBlockData(target, bld.getRotationDeg())", lookup)
        self.assertEqual(rotate_horizontal_direction(0, -1, 90), (-1, 0))
        self.assertEqual(rotate_horizontal_direction(0, -1, 180), (0, 1))
        self.assertEqual(rotate_horizontal_direction(0, -1, 270), (1, 0))

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
        line_renderer = hud[hud.index("private void showWireframeSegment"):hud.index("private void syncWireframeDisplays")]
        full_cube_renderer = hud[hud.index("private void renderLayerWireframes"):hud.index("public void updateHud")]
        config = (ROOT / "tmp/minecraft-build-v2/src/main/resources/config.yml").read_text()
        self.assertIn("world.spawn(spawnLocation, BlockDisplay.class", hud)
        self.assertIn("entity.setGlowing(false)", line_renderer)
        self.assertIn("Material.RED_CONCRETE", line_renderer)
        self.assertIn("Material.LIGHT_BLUE_CONCRETE", line_renderer)
        self.assertIn("entity.setViewRange(2.0f)", line_renderer)
        self.assertIn("double surfaceOffset = thickness / 2.0 + 0.002", line_renderer)
        self.assertIn("vertices[edge], vertices[(edge + 1) % 4], color, desiredSegments", full_cube_renderer)
        self.assertIn("|view:\" + normalX", line_renderer)
        self.assertIn("entity.setVisibleByDefault(false)", line_renderer)
        self.assertIn("player.showEntity(plugin, display)", line_renderer)
        self.assertNotIn("spawnParticle", line_renderer)
        self.assertIn("showWireframeSegment(player, world, bld.getInstanceId()", full_cube_renderer)
        self.assertNotIn("drawVisibleEdge", full_cube_renderer)
        self.assertNotIn("hasWireframeLineOfSight", line_renderer)
        self.assertIn("line-thickness: 0.035", config)

    def test_diagonal_wireframe_displays_rotate_a_solid_rod_instead_of_stretching_texture(self):
        hud = HUD_SOURCE.read_text()
        self.assertIn("rotationTo(new Vector3f(1.0f, 0.0f, 0.0f), direction)", hud)
        self.assertIn("rotation.transform(new Vector3f(", hud)
        line_renderer = hud[hud.index("private void showWireframeSegment"):hud.index("private void syncWireframeDisplays")]
        model_glow = hud[hud.index("private void showBlockModelGlow"):hud.index("private void renderLayerWireframes")]
        self.assertIn("entity.setBlock(lineMaterial.createBlockData())", line_renderer)
        self.assertIn("entity.setGlowing(false)", line_renderer)
        self.assertIn("entity.setBlock(blockData)", model_glow)
        self.assertIn("entity.setGlowing(true)", model_glow)
        self.assertNotIn("entity.setBlock(Material.SEA_LANTERN.createBlockData())", hud)

    def test_non_cubic_models_glow_in_their_shape_without_a_cube_outline(self):
        hud = HUD_SOURCE.read_text()
        renderer = hud[hud.index("private void renderLayerWireframes"):hud.index("public void updateHud")]
        self.assertIn("getCollisionShape(", renderer)
        self.assertIn("showBlockModelGlow", renderer)
        self.assertIn("isBlockModelVisible(player, world, x, layerY, z, shape", renderer)
        self.assertIn("entity.setBlock(blockData)", hud)
        visibility = hud[hud.index("private boolean isBlockModelVisible"):hud.index("private void showBlockModelGlow")]
        self.assertIn("hasWireframeLineOfSight", visibility)
        self.assertIn("for (int ix = 0; ix < 3; ix++)", visibility)
        self.assertIn("for (int iy = 0; iy < 3; iy++)", visibility)
        self.assertIn("for (int iz = 0; iz < 3; iz++)", visibility)
        self.assertIn("if (isBlockModelVisible", renderer)
        self.assertIn("entity.setGlowing(true)", hud)
        self.assertIn("if (shape.isEmpty() || !isFullCubeShape(shape))", renderer)
        self.assertNotIn("drawCollisionVolumeGlow", hud)
        self.assertNotIn("drawCrossModelPlantGlow", hud)
        self.assertNotIn("spawnParticle(dustParticle", renderer)
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
        self.assertIn("Amanatides-Woo cell traversal", hud)
        self.assertIn("tieEpsilon", hud)
        self.assertNotIn("isWireframePointVisible", hud)
        line_renderer = hud[hud.index("private void showWireframeSegment"):hud.index("private void syncWireframeDisplays")]
        self.assertIn("entity.setGlowing(false)", line_renderer)
        self.assertIn("if (facing <= 0.0001) continue", hud)
        self.assertIn("isFullCubeCell(world, bld, schem", hud)
        neighbor_culling = hud[hud.index("private boolean isFullCubeCell"):hud.index("private boolean rayIntersectsBox")]
        self.assertIn("if (!world.isChunkLoaded(x >> 4, z >> 4)) return false", neighbor_culling)
        collision_boxes = hud[hud.index("private Collection<BoundingBox> getCellCollisionBoxes"):hud.index("private boolean isFullCubeShape")]
        self.assertIn("if (!physicalOccupancy && !displayOccupancy)", collision_boxes)
        self.assertIn("x + nx, layerY + ny, z + nz", hud)
        self.assertIn("rayIntersectsBox(ox, oy, oz", hud)
        self.assertIn("getCollisionShape(", hud)
        self.assertNotIn("if (!isAirCell(neighborType)) continue", hud)
        self.assertNotIn("double yTop = Y + 1.015", hud)
        self.assertNotIn("yPillarStart", hud)


if __name__ == "__main__":
    unittest.main()
