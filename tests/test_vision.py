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
