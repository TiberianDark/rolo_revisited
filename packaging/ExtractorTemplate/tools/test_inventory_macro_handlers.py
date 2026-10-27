import unittest
from inventory_macro_handlers import actor_accesses

class ActorAccessTests(unittest.TestCase):
    def i(self,name,ops):return dict(address=0x200,mnemonic=name,operands=ops)

    def test_memory_copy_has_separate_widths_and_directions(self):
        rows=actor_accesses(self.i('MOVE.W','(+12,A5),(+94,A5)'))
        self.assertEqual([(r['offset'],r['access'],r['width']) for r in rows],[(12,'read',2),(94,'write',2)])

    def test_plain_indirect_is_offset_zero_without_auto_increment(self):
        from inventory_rom import object_fields
        instruction=self.i('TST.W','(A5)')
        self.assertEqual(object_fields([instruction])[0]['offset'],0)
        self.assertEqual([(r['offset'],r['access'],r['width']) for r in actor_accesses(instruction)],[(0,'read',2)])
        self.assertEqual(actor_accesses(self.i('MOVE.W','(A5)+,D0')),[])
    def test_bit_change_is_one_byte_rmw(self):
        self.assertEqual([(r['access'],r['width']) for r in actor_accesses(self.i('BSET','#3,(+126,A5)'))],[('read_modify_write',1)])

    def test_other_registers_and_dynamic_index_not_guessed(self):
        self.assertEqual(actor_accesses(self.i('MOVE.L','(+42,A4),A0')),[])
        self.assertEqual(actor_accesses(self.i('MOVE.B','D1,(+0,A5,D0.W)')),[])

if __name__=='__main__':unittest.main()
