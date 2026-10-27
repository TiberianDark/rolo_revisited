import unittest
from inventory_object_schema import allocator_write

class AllocatorWriteTests(unittest.TestCase):
    def instruction(self,mnemonic,operands):return dict(address=0x28fe,mnemonic=mnemonic,operands=operands)
    def test_position_longword(self):
        row=allocator_write(self.instruction('MOVE.L','D2,(+12,A3)'))
        self.assertEqual((row['offset'],row['size'],row['source']),(12,4,'D2'))
    def test_memory_source_comma_kept(self):
        row=allocator_write(self.instruction('MOVE.W','(+12,A3),(+94,A3)'))
        self.assertEqual(row['source'],'(+12,A3)');self.assertEqual(row['offset'],94)
    def test_reads_and_other_aliases_not_marked_allocator_writes(self):
        self.assertIsNone(allocator_write(self.instruction('MOVE.L','(+12,A3),D2')))
        self.assertIsNone(allocator_write(self.instruction('MOVE.L','D2,(+12,A5)')))
        self.assertIsNone(allocator_write(self.instruction('CMPI.W','#$0000,(+12,A3)')))

if __name__=='__main__':unittest.main()
