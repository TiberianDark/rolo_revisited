import unittest
from pathlib import Path
from verify_entrance import reference
from export_entrance import export
from unittest.mock import patch

ROM=Path(__file__).resolve().parents[1]/'local/rolo.md'

@unittest.skipUnless(ROM.exists(),'Pinned local ROM needed for entrance reference tests')
class EntranceReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rom=ROM.read_bytes();cls.rows=reference(cls.rom)
    def row(self,tick,index):return self.rows[(tick-1)*6+index]
    def test_delayed_walk(self):
        self.assertEqual(self.row(200,3)[2],528<<16)
        self.assertEqual(self.row(201,3)[2],527<<16)
        self.assertEqual(self.row(408,3)[2:5],[320<<16,239<<16,0])
    def test_elephant_clamp_and_head(self):
        for t in (1,199,200,850):self.assertEqual(self.row(t,0)[2:5],self.row(t,1)[2:5])
        self.assertEqual(self.row(199,0)[2],279<<16)
        self.assertEqual(self.row(200,0)[4],60)
    def test_gravity_start(self):
        self.assertEqual(self.row(250,2)[3],162<<16)
        self.assertEqual(self.row(251,2)[3],(162<<16)+0x6000)
        self.assertEqual(self.row(272,2)[3]>>16,241)
        self.assertEqual(self.row(272,2)[4],0)
    def test_fractional_motion(self):
        self.assertEqual(self.row(1,5)[2],78<<16)
        self.assertEqual(self.row(2,5)[2],(78<<16)+0x2000)
        self.assertEqual(self.row(769,5)[2:4],[174<<16,237<<16])
    def test_delay_override_frame_period(self):
        self.assertEqual(self.row(1,5)[5:7],[0x10994,9])
        self.assertEqual(self.row(10,5)[5],0x10994)
        self.assertEqual(self.row(11,5)[5:7],[0x109a6,6])
    def test_normal_period(self):
        self.assertEqual(self.row(1,0)[5],self.row(4,0)[5])
        self.assertNotEqual(self.row(4,0)[5],self.row(5,0)[5])
    def test_export_reproducible(self):
        with patch('pathlib.Path.write_text') as write:
            result=export(self.rom,Path('generated.hpp'))
            self.assertEqual((result['programs'],result['nodes'],result['frames']),(12,91,59))
            self.assertEqual(write.call_args.args[0],(ROM.parents[1]/'src/core/entrance_data.hpp').read_text())

if __name__=='__main__':unittest.main()

