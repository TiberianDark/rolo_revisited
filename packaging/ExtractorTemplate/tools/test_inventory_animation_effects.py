import unittest
from inventory_animation_effects import effects

class AnimationEffectsTests(unittest.TestCase):
    def control(self,command,parameter,extra=b''):
        control=dict(address=0,command=command,parameter=parameter)
        rom=((-command<<16)+parameter).to_bytes(4,'big',signed=True)+extra
        return effects(control,rom)

    def test_generic_write_preserves_high_offset_and_byte(self):
        row=self.control(56,0xff80)
        self.assertEqual(row['field_writes'],[dict(offset=255,width=1,value=128)])

    def test_conditional_read_sign_extends_word_index(self):
        self.assertEqual(self.control(16,0xffff)['field_reads'][0]['offset'],-1)

    def test_spawn_payload_and_sound_are_separate(self):
        self.assertEqual(self.control(100,16,bytes.fromhex('00013eaa'))['spawn_definition'],0x13eaa)
        self.assertEqual(self.control(116,75)['sound_request'],75)
        with self.assertRaisesRegex(ValueError,'truncated'):self.control(92,0)

    def test_control_operand_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'bytes differ'):
            effects(dict(address=0,command=56,parameter=0),bytes.fromhex('ffc80001'))

if __name__=='__main__':unittest.main()
