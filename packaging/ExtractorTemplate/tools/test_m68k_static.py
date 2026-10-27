import unittest
from m68k_static import Decoder, Unsupported, walk


class DecoderTests(unittest.TestCase):
    def decode(self,hexbytes,start=0x200):
        data = bytes(start)+bytes.fromhex(hexbytes)
        return Decoder(data,start).decode()

    def test_pc_branch_base_and_word_extension(self):
        self.assertEqual(self.decode('610005c0')['target'],0x7c2)
        self.assertEqual(self.decode('66fe')['target'],0x200)
        self.assertEqual(self.decode('51c9fffc')['target'],0x1fe)

    def test_pc_lea_and_signed_absolute_short(self):
        self.assertEqual(self.decode('4bfa007c')['references'],[0x27e])
        self.assertEqual(self.decode('4ff8ffde')['references'],[0xffffde])

    def test_instruction_sizes_and_masks(self):
        self.assertEqual(self.decode('203c00027040')['size'],6)
        self.assertEqual(self.decode('23fc6000000000c00004')['size'],10)
        self.assertEqual(self.decode('91c8')['mnemonic'],'SUBA.L')
        self.assertEqual(self.decode('b1c8')['mnemonic'],'CMPA.L')
        self.assertEqual(self.decode('e284')['operands'],'#1,D4')

    def test_movem_predecrement_register_mask(self):
        self.assertEqual(self.decode('48e7fffe')['operands'],
                         'A6/A5/A4/A3/A2/A1/A0/D7/D6/D5/D4/D3/D2/D1/D0,-(A7)')

    def test_unknown_and_truncated_stop(self):
        for value in ('a000','203c0002','9100'):
            with self.assertRaises(Unsupported): self.decode(value)

    def test_unconditional_branch_skips_data(self):
        data=bytes(0x200)+bytes.fromhex('6004414243444e75')
        result=walk(data,[0x200])
        self.assertEqual([i['address'] for i in result['instructions']],[0x200,0x206])

    def test_indirect_jump_is_reported(self):
        result=walk(bytes(0x200)+bytes.fromhex('4ed0'),[0x200])
        self.assertEqual(result['stops'][0]['reason'],'Unresolved indirect jump')

if __name__ == '__main__': unittest.main()
