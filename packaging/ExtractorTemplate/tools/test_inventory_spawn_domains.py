import unittest
from inventory_spawn_domains import selector, definition_index, terrain_selector


class SpawnDomainTests(unittest.TestCase):
    def test_visual_threshold(self):
        self.assertEqual(selector(0x3ff)['path'], 'visual descriptor')
        self.assertEqual(selector(0x400)['branch_offset'], 0)

    def test_signed_high_byte_gate(self):
        self.assertEqual(selector(0x2000)['initial_mode_offset'], 0)
        self.assertEqual(selector(0x7fff)['initial_mode_offset'], 380)
        self.assertEqual(selector(0x8000)['path'], 'spawn branch')
        self.assertEqual(selector(0x8000)['branch_offset'], 496)
        self.assertEqual(selector(0xffff)['branch_offset'], 1004)

    def test_slot_boundary_without_invented_clamp(self):
        self.assertTrue(selector(0x17ff)['within_catalogued_slots'])
        self.assertFalse(selector(0x1800)['within_catalogued_slots'])
        self.assertFalse(selector(0x1fff)['within_catalogued_slots'])

    def test_direct_and_paired_tables_differ(self):
        self.assertEqual(definition_index(4, 73)['index'], 36)
        self.assertTrue(definition_index(4, 73)['within_table'])
        self.assertFalse(definition_index(4, 74)['within_table'])
        self.assertEqual(definition_index(6, 23)['index'], 23)
        self.assertTrue(definition_index(6, 23)['within_table'])
        self.assertFalse(definition_index(6, 24)['within_table'])

    def test_progress_gate_ignores_parameter_for_table(self):
        self.assertEqual(definition_index(11, 255)['index'], 0)
        self.assertTrue(definition_index(11, 255)['within_table'])

    def test_trigger_selector_extent(self):
        self.assertEqual(terrain_selector(7, 255)['offset'], 64)
        self.assertEqual(terrain_selector(9, 255)['offset'], 68)
        self.assertTrue(terrain_selector(10, 17)['within_catalogued_slots'])
        self.assertFalse(terrain_selector(10, 18)['within_catalogued_slots'])
        self.assertEqual(terrain_selector(10, 255)['offset'], 1020)


if __name__ == '__main__':
    unittest.main()
