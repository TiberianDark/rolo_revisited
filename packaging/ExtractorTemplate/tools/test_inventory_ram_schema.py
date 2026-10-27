import unittest
from inventory_ram_schema import accesses,operands

class RamSchemaTests(unittest.TestCase):
    def instruction(self,mnemonic,text):
        return dict(address=0x200,mnemonic=mnemonic,operands=text)

    def test_memory_to_memory_and_short_sign_extension(self):
        rows=accesses(self.instruction('MOVE.W','($C444).W,($FFFFC448).L'))
        self.assertEqual([(r['address'],r['access'],r['width']) for r in rows],[(0xffc444,'read',2),(0xffc448,'write',2)])

    def test_operand_split_keeps_index_commas(self):
        self.assertEqual(operands('(+0,A0,D1.W),($FFFFC444).L'),['(+0,A0,D1.W)','($FFFFC444).L'])

    def test_compare_does_not_write_and_add_reads_or_mutates(self):
        self.assertEqual(accesses(self.instruction('CMP.W','D0,($FFFFC444).L'))[0]['access'],'read')
        self.assertEqual(accesses(self.instruction('ADD.W','($FFFFC444).L,D0'))[0]['access'],'read')
        self.assertEqual(accesses(self.instruction('ADD.W','D0,($FFFFC444).L'))[0]['access'],'read_modify_write')

    def test_bit_memory_width_and_pointer_are_distinct(self):
        row=accesses(self.instruction('BCLR','#7,($FFFFC444).L'))[0]
        self.assertEqual((row['access'],row['width']),('read_modify_write',1))
        row=accesses(self.instruction('LEA','($FFFFC444).L,A0'))[0]
        self.assertEqual((row['access'],row['width']),('address',None))
        self.assertEqual(accesses(self.instruction('MOVE.L','($00C00004).L,D0')),[])

if __name__=='__main__':unittest.main()
