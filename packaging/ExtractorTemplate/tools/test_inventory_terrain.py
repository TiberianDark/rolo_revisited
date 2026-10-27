import unittest
from inventory_terrain import collision_record

class TerrainRecordTests(unittest.TestCase):
    def test_unsigned_offsets_and_shape_flags(self):
        rows=collision_record(bytes([255,0xc3,1,2,3,4,5,6]))
        self.assertEqual(rows[0]['offset_byte'],255)
        self.assertEqual(rows[0]['shape_index'],3)
        self.assertTrue(rows[0]['mirror_bit']);self.assertTrue(rows[0]['bit7'])
        self.assertEqual([row['direction'] for row in rows],['floor','ceiling','right','left'])
    def test_truncated_records_rejected(self):
        with self.assertRaises(ValueError):collision_record(bytes(7))

if __name__=='__main__':unittest.main()
