import unittest
from inventory_ram_aliases import hints

class AliasHintTests(unittest.TestCase):
    def i(self,site,mnemonic,operands,flow='next',target=None):
        return dict(address=site,size=2,mnemonic=mnemonic,operands=operands,flow=flow,target=target)

    def test_mapping_field_writes_with_producer_evidence(self):
        rows=hints([self.i(0x200,'LEA','($FFFFC43C).L,A0'),self.i(0x202,'MOVE.B','#$07,(+7,A0)')])
        self.assertEqual(len(rows),1)
        self.assertEqual((rows[0]['address'],rows[0]['access'],rows[0]['producer_chain']),(0xffc443,'write',[0x200]))

    def test_calls_and_known_entries_end_hints(self):
        instructions=[self.i(0x200,'LEA','($FFFFC43C).L,A0'),self.i(0x202,'JSR','($00001000).L','call',0x1000),self.i(0x204,'CLR.B','(+0,A0)')]
        self.assertEqual(hints(instructions),[])
        self.assertEqual(hints([instructions[0],self.i(0x202,'CLR.B','(+0,A0)')],[0x202]),[])

    def test_memory_pointer_load_and_postincrement_invalidate_base(self):
        prefix=self.i(0x200,'LEA','($FFFFC43C).L,A0')
        self.assertEqual(len(hints([prefix,self.i(0x202,'MOVEA.L','(+0,A0),A0'),self.i(0x204,'CLR.B','(+0,A0)')])),1)
        self.assertEqual(hints([prefix,self.i(0x202,'MOVE.B','(A0)+,D0'),self.i(0x204,'CLR.B','(+0,A0)')]),[])

    def test_compare_preserves_but_derived_lea_has_a_chain(self):
        rows=hints([self.i(0x200,'LEA','($FFFFC43C).L,A0'),self.i(0x202,'CMPA.L','A1,A0'),self.i(0x204,'LEA','(+4,A0),A1'),self.i(0x206,'CLR.B','(+1,A1)')])
        self.assertEqual(rows[-1]['address'],0xffc441)
        self.assertEqual(rows[-1]['producer_chain'],[0x200,0x204])

if __name__=='__main__':unittest.main()
