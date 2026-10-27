import unittest
from inventory_world_routes import route_pairs


class WorldRouteDataTests(unittest.TestCase):
    def test_odd_start_retains_pair_alignment(self):
        result = route_pairs(bytes([99, 1, 0, 0, 2, 128]), 1, 6)
        self.assertEqual(result['pairs'], [[1, 0], [0, 2]])
        self.assertEqual(result['end_exclusive'], 6)

    def test_negative_second_byte_is_magnitude_not_terminator(self):
        result = route_pairs(bytes([1, 255, 129]), 0, 3)
        self.assertEqual(result['unsigned_totals'], [1, 255])
        self.assertEqual(result['terminator'], 129)

    def test_missing_terminator_or_partial_pair_rejected(self):
        for data in (bytes([1]), bytes([1, 0])):
            with self.assertRaises(ValueError):
                route_pairs(data, 0, len(data))
