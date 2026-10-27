import unittest
from inventory_dynamic_macros import geometry

class MacroGeometryTests(unittest.TestCase):
    def test_anchor_is_center_x_and_bottom_y(self):
        row=geometry(dict(x=100,y=200),2,3)
        self.assertEqual((row['canonical_x_word'],row['canonical_y_word'],row['definition_size_word']),(116,248,768))

    def test_coordinates_and_size_keep_word_arithmetic(self):
        row=geometry(dict(x=65530,y=65530),16,16)
        self.assertEqual((row['canonical_x_word'],row['canonical_y_word']),(122,250))
        self.assertEqual(row['definition_size_word'],0)
        self.assertEqual(geometry(dict(x=0,y=0),16,8)['definition_size_word'],0xc000)

if __name__=='__main__':unittest.main()
