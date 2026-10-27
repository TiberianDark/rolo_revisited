import struct
import unittest
from rolo_codec import DecodeError,decode_backward_lz


def bits(value,width): return [(value>>shift)&1 for shift in range(width-1,-1,-1)]


def block(stream,output_size):
    # Synthetic format fixtures built independently of the decoder's sentinel state.
    padding=(-len(stream))%32
    stream=stream+[0]*padding
    words=[sum(bit<<i for i,bit in enumerate(stream[start:start+32])) for start in range(0,len(stream),32)]
    payload=b''.join(struct.pack('>I',word) for word in reversed(words))
    return struct.pack('>I',12+len(payload))+bytes((3,4,5,6))+payload+struct.pack('>I',output_size<<8)


class CodecTests(unittest.TestCase):
    def literal_a(self): return [0]+bits(0,2)+bits(ord('A'),8)

    def test_one_literal(self):
        value=block(self.literal_a(),1)
        self.assertEqual(decode_backward_lz(value,0)[0],b'A')

    def test_literal_run_across_word_boundary(self):
        stream=[0]+bits(3,2)+bits(0,2) # 4-byte run.
        for value in b'DCBA': stream+=bits(value,8)
        self.assertEqual(decode_backward_lz(block(stream,4),0)[0],b'ABCD')

    def test_overlapping_matches_all_small_selectors(self):
        for selector,width,count in ((0,3,2),(1,4,3),(2,5,4)):
            stream=self.literal_a()+bits(selector,2)+bits(0,width)
            self.assertEqual(decode_backward_lz(block(stream,count+1),0)[0],b'A'*(count+1))

    def test_extended_match_short_and_long_distance(self):
        for flag,width in ((0,7),(1,6)):
            stream=self.literal_a()+bits(3,2)+[flag]+bits(0,width)+bits(7,3)+bits(0,3)
            self.assertEqual(decode_backward_lz(block(stream,13),0)[0],b'A'*13)

    def test_padding_bits(self):
        stream=[1]*5+self.literal_a()
        value=bytearray(block(stream,1)); value[-1]=5
        self.assertEqual(decode_backward_lz(value,0)[0],b'A')

    def test_reject_uninitialized_reference_and_overrun(self):
        values=[block([1]+bits(0,2)+bits(0,3),2),
                block(self.literal_a()+bits(2,2)+bits(0,5),2)]
        for value in values:
            with self.assertRaises(DecodeError): decode_backward_lz(value,0)

    def test_invalid_headers_and_exhaustion(self):
        for value in (b'',bytes(16),block([0]*32,100)):
            with self.assertRaises(DecodeError): decode_backward_lz(value,0)
        value=block(self.literal_a(),1)
        with self.assertRaises(DecodeError): decode_backward_lz(value,0,max_output=0)

if __name__ == '__main__': unittest.main()
