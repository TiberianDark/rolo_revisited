import unittest
from inventory_dispatch_domains import local_domain

class SelectorDomainTests(unittest.TestCase):
    def test_masked_terrain_domain_includes_all_eight_slots(self):
        self.assertEqual(local_domain('terrain_mask'),list(range(0,32,4)))

    def test_flag_bits_select_exactly_four_offsets(self):
        self.assertEqual(local_domain('actor_flag_mask'),[0,4,8,12])

    def test_unknown_proof_cannot_fabricate_a_domain(self):
        with self.assertRaises(ValueError):local_domain('unproved_field')

if __name__=='__main__':unittest.main()
