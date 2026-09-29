import unittest

from fogofwar.vision import behind_wall_count, sample_a, update, visible


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


import random

from fogofwar.vision import reference_visible


class WallOcclusionTest(unittest.TestCase):
    def setUp(self):
        self.level = sample_a()
        self.cells = set(visible(self.level, self.level["units"][0]))

    def test_behind_wall_not_visible(self):
        for y in (0, 1, 2, 3, 5, 6, 7, 8):
            self.assertNotIn((6, y), self.cells)
        self.assertEqual(behind_wall_count(self.level, self.cells), 0)

    def test_wall_cell_itself_visible(self):
        for y in range(9):
            self.assertIn((5, y), self.cells)

    def test_door_row_see_through(self):
        self.assertIn((6, 4), self.cells)


class IncrementalCleanupTest(unittest.TestCase):
    def test_stale_cells_removed_after_move(self):
        level = sample_a()
        first = set(visible(level, level["units"][0]))
        moved = [{"x": 1, "y": 0, "radius": 2}]
        second = update(first, level, moved)
        fresh = set(visible(level, moved[0]))
        self.assertEqual(second, fresh)
        self.assertEqual(second - fresh, set())

    def test_update_equals_recompute_when_units_unchanged(self):
        level = sample_a()
        units = [{"x": 2, "y": 4, "radius": 4}]
        first = update(set(), level, units)
        self.assertEqual(update(first, level, units), first)

    def test_cells_stay_within_map(self):
        level = sample_a()
        cells = update(set(), level, [{"x": 0, "y": 0, "radius": 9}])
        for x, y in cells:
            self.assertTrue(0 <= x < level["width"])
            self.assertTrue(0 <= y < level["height"])


class ReferenceConsistencyTest(unittest.TestCase):
    def test_random_maps_match_reference(self):
        rng = random.Random(20260930)
        for _ in range(200):
            width = rng.randint(3, 12)
            height = rng.randint(3, 12)
            level = {
                "width": width,
                "height": height,
                "wall_x": rng.randint(0, width + 1),
                "door_y": rng.randint(0, height - 1),
            }
            for _ in range(rng.randint(1, 4)):
                unit = {
                    "x": rng.randint(0, width - 1),
                    "y": rng.randint(0, height - 1),
                    "radius": rng.randint(0, 6),
                }
                self.assertEqual(
                    set(visible(level, unit)), set(reference_visible(level, unit))
                )

    def test_repeated_computation_is_deterministic(self):
        level = sample_a()
        unit = level["units"][0]
        self.assertEqual(visible(level, unit), visible(level, unit))
