import unittest
from inventory_world_progression import edge_glyph


class JigsawGlyphTests(unittest.TestCase):
    tables={0xa656:[2,2,1,1],0xa65e:[6,5,4,3],0xa666:[9,10,7,8]}

    def test_unfinished_cell_keeps_default_for_nonconnecting_codes(self):
        for code in (0,1,3):
            for neighbour in (False,True):
                self.assertEqual(edge_glyph(code,False,neighbour,6,self.tables),1)

    def test_incomplete_cell_adjacent_to_complete_uses_connection_table(self):
        self.assertEqual([edge_glyph(2,False,True,d,self.tables) for d in (0,2,4,6)],[6,5,4,3])

    def test_completed_cell_edge_exposed_to_incomplete_neighbour(self):
        self.assertEqual([edge_glyph(2,True,False,d,self.tables) for d in (0,2,4,6)],[9,10,7,8])
        self.assertEqual(edge_glyph(2,True,True,0,self.tables),0)

    def test_completed_cell_other_codes_leave_existing_graphics(self):
        for code in (0,1,3):
            for neighbour in (False,True):
                self.assertEqual(edge_glyph(code,True,neighbour,4,self.tables),0)

    def test_invalid_indices_are_not_silently_clamped(self):
        with self.assertRaises(ValueError):edge_glyph(4,False,False,0,self.tables)
        with self.assertRaises(ValueError):edge_glyph(2,False,True,8,self.tables)


if __name__=='__main__':unittest.main()
