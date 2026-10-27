import unittest
from inventory_states import immediate_state_write

class StateWriteTests(unittest.TestCase):
    def instruction(self,mnemonic,operands):return dict(address=0x1388,mnemonic=mnemonic,operands=operands)
    def test_immediate_dispatch_destination(self):
        result=immediate_state_write(self.instruction('MOVE.L','#$0000165E,($FFFFC444).L'))
        self.assertEqual((result['role'],result['target']),('main_dispatch',0x165e))
    def test_compare_and_pointer_read_are_not_transitions(self):
        self.assertIsNone(immediate_state_write(self.instruction('CMPI.L','#$0000165E,($FFFFC466).L')))
        self.assertIsNone(immediate_state_write(self.instruction('MOVEA.L','($FFFFC444).L,A0')))
    def test_marker_distinct_from_dispatch(self):
        result=immediate_state_write(self.instruction('MOVE.L','#$00001C6C,($FFFFC466).L'))
        self.assertEqual(result['role'],'initialization_marker')
        self.assertIsNone(immediate_state_write(self.instruction('MOVE.L','#$00001C6C,($FFFFC448).L')))

if __name__=='__main__':unittest.main()
