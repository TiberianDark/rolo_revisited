import struct, unittest
from rolo_sprites import sprite_pixels,sequence_frames,frame_record

class SpriteTests(unittest.TestCase):
    def test_column_tiles_and_chunk_order(self):
        raw=b''.join(bytes([i*17])*32 for i in range(1,11))
        pixels=sprite_pixels(raw,40,16)
        self.assertEqual([pixels[x] for x in (0,8,16,24,32)],[1,3,5,7,9])
        self.assertEqual([pixels[8*40+x] for x in (0,8,16,24,32)],[2,4,6,8,10])
    def test_invalid_size(self):
        with self.assertRaises(ValueError):sprite_pixels(bytes(32),16,8)
    def test_loop_deduplicates(self):
        data=struct.pack('>IIII',12,0,0,0)
        self.assertEqual(sequence_frames(data,0)[0],[12])
    def test_random_jump_is_not_frame(self):
        data=struct.pack('>IIIIIII',0xffd40002,20,24,0xfffc0000,0,24,0xfffc0000)
        self.assertEqual(sequence_frames(data,0)[0],[24])
    def test_frame_signed_offsets(self):
        data=struct.pack('>IIhhHHH',64,0,-12,-100,16,16,128)
        self.assertEqual(frame_record(data,0)['offset_y'],-100)
    def test_condition_repeats_previous_word_or_advances_one_word(self):
        # Jump operand at +12 must never be treated as a standalone instruction.
        data=struct.pack('>IIIIIII',24,0xffe4007a,0,20,0x12345678,24,0xfffc0000)
        self.assertEqual(sequence_frames(data,0)[0],[24])
    def test_spawn_definition_is_not_a_frame(self):
        data=struct.pack('>IIII',0xffa40000,0x13eaa,32,0xfffc0000)
        self.assertEqual(sequence_frames(data,0)[0],[32])
    def test_invalid_frame_geometry(self):
        with self.assertRaises(ValueError):frame_record(bytes(18),0)

if __name__=='__main__':unittest.main()
