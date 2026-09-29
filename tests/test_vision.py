import math
import random
import time
import unittest

from fogofwar.vision import behind_wall_count, sample_a, update, visible


def reference_visible(level, unit):
    """参考实现：逐格暴力扫描整张地图，每格采样连线（线段与墙列的交点）判定遮挡。"""
    ux = unit["x"]
    uy = unit["y"]
    radius = unit["radius"]
    wall_x = level["wall_x"]
    door_y = level["door_y"]
    cells = set()
    for y in range(level["height"]):
        for x in range(level["width"]):
            if max(abs(x - ux), abs(y - uy)) > radius:
                continue
            du = ux - wall_x
            dt = x - wall_x
            if du == 0 or dt == 0 or (du > 0) == (dt > 0):
                cells.add((x, y))
                continue
            t = (wall_x - ux) / (x - ux)
            y_cross = uy + t * (y - uy)
            if math.floor(y_cross + 0.5) == door_y:
                cells.add((x, y))
    return cells


class VisibleTest(unittest.TestCase):
    def test_radius_limits_cells(self):
        level = {"width": 3, "height": 3, "wall_x": 9, "door_y": 9}
        cells = visible(level, {"x": 1, "y": 1, "radius": 0})
        self.assertEqual(cells, [(1, 1)])

    def test_count_is_odd_for_odd_radius(self):
        level = sample_a()
        cells = visible(level, {"x": 4, "y": 4, "radius": 1})
        self.assertEqual(len(cells), 9)

    def test_behind_wall_helper_counts(self):
        level = sample_a()
        self.assertEqual(behind_wall_count(level, [(6, 0), (6, 4), (2, 2)]), 1)


class UpdateTest(unittest.TestCase):
    def test_first_update_equals_visible(self):
        level = sample_a()
        units = [{"x": 2, "y": 4, "radius": 2}]
        self.assertEqual(update(set(), level, units), set(visible(level, units[0])))

    def test_update_keeps_previous_cells(self):
        level = sample_a()
        previous = {(0, 0)}
        self.assertIn((0, 0), update(previous, level, []))


class WallOcclusionTest(unittest.TestCase):
    def test_cells_behind_wall_are_hidden(self):
        level = sample_a()
        cells = set(visible(level, level["units"][0]))
        self.assertNotIn((6, 0), cells)
        self.assertNotIn((6, 8), cells)
        self.assertEqual(behind_wall_count(level, cells), 0)

    def test_door_row_sees_through_wall(self):
        level = sample_a()
        cells = set(visible(level, level["units"][0]))
        self.assertIn((6, 4), cells)

    def test_wall_cells_themselves_are_visible(self):
        level = sample_a()
        cells = set(visible(level, level["units"][0]))
        self.assertIn((5, 0), cells)
        self.assertIn((5, 8), cells)


class IncrementalUpdateTest(unittest.TestCase):
    def test_moved_unit_leaves_no_stale_cells(self):
        level = sample_a()
        first = set(visible(level, level["units"][0]))
        moved = [{"x": 1, "y": 0, "radius": 2}]
        second = update(first, level, moved)
        fresh = set(visible(level, moved[0]))
        self.assertEqual(second - fresh, set())

    def test_removed_unit_cells_are_cleared(self):
        level = sample_a()
        units = [{"x": 2, "y": 4, "radius": 4}, {"x": 1, "y": 0, "radius": 2}]
        both = update(set(), level, units)
        remaining = update(both, level, units[1:])
        self.assertEqual(remaining, set(visible(level, units[1])))

    def test_update_matches_one_shot_when_units_unchanged(self):
        level = sample_a()
        units = [{"x": 2, "y": 4, "radius": 3}]
        once = update(set(), level, units)
        twice = update(once, level, units)
        self.assertEqual(twice, once)

    def test_update_only_keeps_in_map_cells(self):
        level = sample_a()
        self.assertEqual(update({(-1, 0), (0, 0)}, level, []), {(0, 0)})
        cells = update({(0, 0)}, level, level["units"])
        self.assertTrue(all(0 <= x < 9 and 0 <= y < 9 for x, y in cells))


class BruteForceConsistencyTest(unittest.TestCase):
    def test_random_maps_match_reference(self):
        rng = random.Random(20260930)
        for _ in range(200):
            width = rng.randint(3, 15)
            height = rng.randint(3, 15)
            level = {
                "width": width,
                "height": height,
                "wall_x": rng.randrange(width),
                "door_y": rng.randrange(height),
            }
            units = [
                {
                    "x": rng.randrange(width),
                    "y": rng.randrange(height),
                    "radius": rng.randint(0, 6),
                }
                for _ in range(rng.randint(1, 4))
            ]
            for unit in units:
                self.assertEqual(
                    set(visible(level, unit)), reference_visible(level, unit)
                )

    def test_repeated_computation_is_deterministic(self):
        level = sample_a()
        unit = level["units"][0]
        self.assertEqual(visible(level, unit), visible(level, unit))


class PerformanceTest(unittest.TestCase):
    def test_frame_update_within_budget(self):
        rng = random.Random(7)
        level = {"width": 200, "height": 200, "wall_x": 100, "door_y": 50}
        units = [
            {"x": rng.randrange(200), "y": rng.randrange(200), "radius": 20}
            for _ in range(100)
        ]
        start = time.perf_counter()
        cells = update(set(), level, units)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5)
        self.assertTrue(all(0 <= x < 200 and 0 <= y < 200 for x, y in cells))
