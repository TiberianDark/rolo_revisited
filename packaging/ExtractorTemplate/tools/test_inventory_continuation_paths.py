import unittest
from inventory_continuation_paths import split_operands, provenance, prove


def instruction(address, mnemonic, operands='', flow='next', target=None, references=()):
    return dict(address=address,size=2,mnemonic=mnemonic,operands=operands,flow=flow,target=target,references=list(references))


class ContinuationProofTests(unittest.TestCase):
    def test_index_commas_do_not_split_operands(self):
        self.assertEqual(split_operands('(+0,A4,D0.W),D1'), ['(+0,A4,D0.W)', 'D1'])

    def test_memory_write_preserves_base_but_postincrement_does_not(self):
        self.assertEqual(provenance(instruction(0,'MOVE.W','D0,(+8,A4)'), 'A4', 100), (100,None))
        self.assertIsNone(provenance(instruction(0,'MOVE.W','D0,(A4)+'), 'A4',100)[0])

    def test_movem_save_and_restore_are_distinct(self):
        self.assertEqual(provenance(instruction(0,'MOVEM.L','A4/D0,-(A7)'), 'A4',100), (100,None))
        self.assertIsNone(provenance(instruction(0,'MOVEM.L','(A7)+,D0/A4'), 'A4',100)[0])

    def test_calls_and_exchanges_discard_provenance(self):
        for item in (instruction(0,'BSR','$100',flow='call',target=100), instruction(0,'EXG','A4,A0')):
            self.assertIsNone(provenance(item,'A4',100)[0])

    def test_both_conditional_paths_must_preserve_pointer(self):
        rows=[instruction(0,'LEA','($100,PC),A4',references=[100]),
              instruction(2,'BNE','$6',flow='branch',target=6),
              instruction(4,'MOVEA.L','D0,A4'),instruction(6,'JMP','(A4)',flow='jump')]
        result=prove(rows,[0],6,'A4')
        self.assertEqual(result['targets'],[100])
        self.assertTrue(result['unknown_reaches_site'])

    def test_explicit_alternate_path_is_reported(self):
        rows=[instruction(0,'LEA','($100,PC),A4',references=[100]),
              instruction(2,'BNE','$8',flow='branch',target=8),
              instruction(4,'JMP','(A4)',flow='jump')]
        result=prove(rows,[0],4,'A4',excluded_paths=(8,))
        self.assertEqual(result['targets'],[100]);self.assertFalse(result['unknown_reaches_site'])
        self.assertIn(dict(site=8,reason='explicitly excluded alternate path'),result['other_exits'])


if __name__=='__main__':unittest.main()
