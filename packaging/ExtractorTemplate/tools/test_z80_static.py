import unittest
from z80_static import decode,walk,Unsupported

class Z80StaticTests(unittest.TestCase):
    def test_little_endian_jump_and_relative_signed_wrap(self):
        self.assertEqual(decode(bytes.fromhex('c38d01'),0)['target'],0x18d)
        self.assertEqual(decode(bytes.fromhex('18fc'),0)['target'],0xfffe)

    def test_conditional_return_keeps_fallthrough(self):
        r=walk(bytes.fromhex('c0c9'),[0])
        self.assertEqual([i['address'] for i in r['instructions']],[0,1])

    def test_call_and_return_boundaries(self):
        r=walk(bytes.fromhex('cd0400c9c9'),[0])
        self.assertEqual([i['address'] for i in r['instructions']],[0,3,4])
        self.assertEqual(r['stops'],[])

    def test_index_memory_displacement_before_immediate(self):
        i=decode(bytes.fromhex('dd36fe7a'),0)
        self.assertEqual(i['text'],'LD (IX-2),$7A')
        self.assertEqual(i['size'],4)
        self.assertEqual(decode(bytes.fromhex('fd66ff'),0)['text'],'LD H,(IY-1)')

    def test_cb_and_ed_instruction_sizes(self):
        self.assertEqual(decode(bytes.fromhex('ddcbfe46'),0)['text'],'BIT 0,(IX-2)')
        self.assertEqual(decode(bytes.fromhex('ed4b3412'),0)['text'],'LD BC,($1234)')
        self.assertEqual(decode(bytes.fromhex('ed4d'),0)['flow'],'return')

    def test_absolute_memory_references(self):
        self.assertEqual(decode(bytes.fromhex('320040'),0)['references'],[0x4000])

    def test_truncated_undocumented_and_indirect_paths_stay_explicit(self):
        for code in ['cd01','ddcb0040','dd24','ed00']:
            with self.assertRaises(Unsupported): decode(bytes.fromhex(code),0)
        self.assertEqual(walk(bytes.fromhex('e9'),[0])['stops'][0]['reason'],'Indirect jump')

if __name__=='__main__':unittest.main()
