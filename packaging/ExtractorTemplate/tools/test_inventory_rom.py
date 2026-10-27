import unittest
from pathlib import Path
from inventory_rom import definitions, inventory, continuation_candidates, indexed_inline_candidates, stack_continuation_candidates
from m68k_static import Decoder

class InventoryTests(unittest.TestCase):
    def test_explicit_pushed_continuation_target_is_seeded(self):
        data=bytes(0x200)+bytes.fromhex('48790000020c')+bytes(6)+bytes.fromhex('4e75')
        context=dict(producer='200',target='20C',target_instruction=['RTS',''])
        self.assertEqual(stack_continuation_candidates(data,[context]),{0x20c})

    def test_data_pointer_or_unmatched_continuation_not_accepted(self):
        data=bytes(0x200)+bytes.fromhex('48790000020c')+bytes(6)+bytes.fromhex('4e75')
        with self.assertRaisesRegex(ValueError,'instruction differs'):
            stack_continuation_candidates(data,[dict(producer='200',target='20C',target_instruction=['MOVEQ','#0,D0'])])
        with self.assertRaisesRegex(ValueError,'producer differs'):
            stack_continuation_candidates(data,[dict(producer='200',target='20E',target_instruction=['RTS',''])])

    def inline_fixture(self):
        data=bytearray(0x300)
        data[0x200:0x204]=bytes.fromhex('4efb4002')
        data[0x20a:0x20e]=bytes.fromhex('0c450003')
        data[0x220:0x226]=bytes.fromhex('3f006100ffdc')
        data[0x240:0x246]=bytes.fromhex('78066100ffdc')
        context=dict(dispatch='200',register='D4',base='204',forwarding_entry='220',forwarding_call='222',
            producer_contexts=[dict(producer='240',call='242',value=6)],inline_targets=[dict(offset=6,address='20A')])
        return data,context

    def test_non_branch_inline_target_uses_actual_immediate_context(self):
        data,context=self.inline_fixture()
        self.assertEqual(indexed_inline_candidates(data,[context]),{0x20a})
        self.assertEqual(Decoder(data,0x20a).decode()['mnemonic'],'CMPI.W')

    def test_inline_target_without_observed_selector_rejected(self):
        data,context=self.inline_fixture();context['inline_targets'][0]=dict(offset=8,address='20C')
        with self.assertRaisesRegex(ValueError,'not justified'):
            indexed_inline_candidates(data,[context])

    def test_inline_forwarder_must_preserve_selector_prefix(self):
        data,context=self.inline_fixture();data[0x220:0x222]=bytes.fromhex('7800')
        with self.assertRaisesRegex(ValueError,'forwarding prefix'):
            indexed_inline_candidates(data,[context])

    def test_inline_producer_must_be_adjacent_to_forwarding_call(self):
        data,context=self.inline_fixture();context['producer_contexts'][0]['call']='222'
        with self.assertRaisesRegex(ValueError,'producer call'):
            indexed_inline_candidates(data,[context])

    def test_continuation_producer_roots_include_code_target(self):
        data=bytes(0x200)+bytes.fromhex('49fa000a')+bytes(32)
        context={'producer':'200','register':'A4','targets':['20C']}
        self.assertEqual(continuation_candidates(data,[context]),{0x20c})
        context['targets']=['20E']
        with self.assertRaisesRegex(ValueError,'targets differ'):
            continuation_candidates(data,[context])

    def test_continuation_wrong_register_rejected(self):
        data=bytes(0x200)+bytes.fromhex('49fa000a')+bytes(32)
        with self.assertRaisesRegex(ValueError,'producer'):
            continuation_candidates(data,[{'producer':'200','register':'A2','targets':['20C']}])

    def test_definition_stride_and_fields(self):
        data=bytearray(0x1582a)
        data[0x13eaa+12:0x13eaa+16]=(0xa84c).to_bytes(4,'big')
        records=definitions(data)
        self.assertEqual(len(records),192)
        self.assertEqual(records[0]['handler'],0xa84c)
        self.assertEqual(records[-1]['address']+34,0x1582a)

    def test_wrong_rom_rejected_before_analysis(self):
        with self.assertRaisesRegex(ValueError,'revision'):
            inventory(bytes(0x80000),Path('.'))

    def test_cmpm_postincrement_registers_and_sizes(self):
        for opcode,suffix in [('b308','B'),('b348','W'),('b388','L')]:
            i=Decoder(bytes(0x200)+bytes.fromhex(opcode),0x200).decode()
            self.assertEqual(i['mnemonic'],'CMPM.'+suffix)
            self.assertEqual(i['operands'],'(A0)+,(A1)+')
            self.assertEqual(i['size'],2)

if __name__=='__main__': unittest.main()
