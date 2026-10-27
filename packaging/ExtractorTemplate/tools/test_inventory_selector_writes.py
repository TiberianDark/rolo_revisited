import unittest
from inventory_selector_writes import selector_accesses
class SelectorTests(unittest.TestCase):
    def test_long_overlap_preserves_register_and_operand(self):
        rows=selector_accesses(dict(address=1,mnemonic='MOVE.L',operands='(+52,A4),(+54,A5)'))
        self.assertEqual([(r['offset'],r['width'],r['register'],r['access']) for r in rows],[(52,4,'A4','read'),(54,4,'A5','write')])
    def test_word_before_selector_does_not_overlap(self):
        self.assertEqual(selector_accesses(dict(address=1,mnemonic='CLR.W',operands='(+52,A5)')),[])
    def test_byte_low_half_detected(self):
        row=selector_accesses(dict(address=1,mnemonic='ADDQ.B',operands='#1,(+55,A2)'))[0]
        self.assertEqual((row['offset'],row['width'],row['access']),(55,1,'read_modify_write'))
if __name__=='__main__':unittest.main()
