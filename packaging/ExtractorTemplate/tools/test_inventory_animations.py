import unittest
from inventory_animations import table_candidates
from inventory_spawns import resolve_marker

class CatalogueTests(unittest.TestCase):
    def test_prefix_stops_before_first_sequence_data(self):
        rom=bytearray(0x14000);table=0x11000
        rom[table:table+8]=bytes.fromhex('0001100803011010')
        rows=table_candidates(rom,table,0x12000)
        self.assertEqual([r['selector'] for r in rows],[0,4])
        self.assertEqual(rows[1]['delay'],3)

    def test_invalid_sequence_pointer_is_not_followed(self):
        rom=bytearray(0x14000)
        self.assertEqual(table_candidates(rom,0x11000,0x12000),[])

    def test_paired_marker_keeps_lookup_and_direction_separate(self):
        rom=bytearray(0x15000);rom[0x4762:0x4766]=(0x14020).to_bytes(4,'big')
        rom[0x14020+12:0x14020+16]=(0xb702).to_bytes(4,'big')
        a,b=resolve_marker(rom,0x0500),resolve_marker(rom,0x0501)
        self.assertEqual(a['definition'],b['definition'])
        self.assertEqual(b['parameter'],1)

    def test_dynamic_macro_mode_uses_class_offset(self):
        record=resolve_marker(b'',0x351a)
        self.assertEqual((record['handler'],record['mode'],record['macro'],record['dispatch_offset']),(0xbe4e,21,26,84))

    def test_signed_macro_class_gate(self):
        self.assertNotIn('mode',resolve_marker(b'',0x8000))
        self.assertNotIn('mode',resolve_marker(b'',0xff1a))

    def test_companion_class_is_eighteen_not_twenty_three(self):
        rom=bytearray(0x15000);rom[0x4948:0x494c]=(0x14020).to_bytes(4,'big')
        rom[0x14020+12:0x14020+16]=(0xb702).to_bytes(4,'big')
        self.assertEqual(resolve_marker(rom,0x1200)['definition'],0x14020)
        self.assertNotIn('definition',resolve_marker(rom,0x1700))

    def test_terrain_list_parameter_fields(self):
        row=resolve_marker(b'',0x0907)
        self.assertEqual((row['field8'],row['field10'],row['field11']),(68,7,255))
        row=resolve_marker(b'',0x0a07)
        self.assertEqual((row['field8'],row['field10'],row['field11']),(28,0,0))

    def test_direct_return_marker_preserves_consumer_uncertainty(self):
        row=resolve_marker(b'',0x0e09)
        self.assertEqual(row['spawn_handler'],0x4904)
        self.assertIn('other marker consumers pending',row['status'])

if __name__=='__main__':unittest.main()
