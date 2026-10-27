import struct
import unittest
from rolo_maps import parse_map, initial_selection, render_foreground,bmp_alpha

class MapTests(unittest.TestCase):
    def test_common_upload_clear_preserves_other_patterns_and_bank_tiles(self):
        rom=bytearray(0x6b452+28*8);macro=0x100;quad=0x200
        struct.pack_into('>H',rom,macro+6,8);rom[macro+8:macro+10]=bytes((1,1))
        struct.pack_into('>H',rom,macro+10,1)
        for i,pattern in enumerate((1,2,3,4)):
            struct.pack_into('>H',rom,0x6b452+8+i*2,pattern)
            rom[0x53dc2+pattern*32:0x53dc2+(pattern+1)*32]=bytes((0x55,))*32
        layout={'width':16,'height':16,'records':[{'type':0,'x':0,'y':0,'visual':True}]}
        self.assertEqual(render_foreground(rom,layout,b'',quad,macro),bytes(256))
        struct.pack_into('>H',rom,0x6b452+8,5)
        rom[0x53dc2+5*32:0x53dc2+6*32]=bytes((0x66,))*32
        self.assertEqual(render_foreground(rom,layout,b'',quad,macro)[0],6)
        struct.pack_into('>H',rom,macro+10,28)
        for i in range(4): struct.pack_into('>H',rom,quad+i*2,i+1)
        self.assertEqual(render_foreground(rom,layout,bytes((0x55,))*160,quad,macro),bytes((5,))*256)

    def test_large_sparse_map_without_image_allocation(self):
        data=b'MAP\x06'+struct.pack('>HHHH',12016,16,12,12)
        result=parse_map(data)
        self.assertEqual(result['width'],12016)
        self.assertEqual(result['records'],[])

    def test_alpha_keeps_opaque_black_and_transparent_index_zero_distinct(self):
        image=bmp_alpha(2,1,bytes((0,1)),[(0,0,0),(0,0,0)])
        self.assertEqual(struct.unpack_from('<I',image,10)[0],122)
        self.assertEqual(image[122:],bytes((0,0,0,0,0,0,0,255)))

    def test_sparse_rows_and_markers(self):
        data=b'MAP\x01'+struct.pack('>HHHHHHHH',32,32,14,18,22,3,16,0x1100)+struct.pack('>H',8)
        result=parse_map(data)
        self.assertEqual([(r['type'],r['x'],r['y'],r['visual']) for r in result['records']],
                         [(3,16,0,True),(0x1100,8,16,False)])

    def test_reject_bad_offsets_and_partial_records(self):
        for offsets in ((8,14),(12,17),(20,12),(12,100)):
            data=b'MAP\0'+struct.pack('>HHHH',32,16,*offsets)+bytes(8)
            with self.assertRaises(ValueError): parse_map(data)

    def test_selection_uses_stride(self):
        rom=bytearray(0x4bac6+32)
        struct.pack_into('>IHH',rom,0x4baaa,0x4bac6,8,4)
        rom[0x4bac6+3]=29;rom[0x4bac6+24]=1
        self.assertEqual(initial_selection(rom),1)

    def test_quad_vdp_row_order_and_vertical_macro_flip(self):
        rom=bytearray(0x6b452+28*8);macro=0x100;quad=0x200
        struct.pack_into('>H',rom,macro+6,8);rom[macro+8:macro+10]=bytes((1,1))
        struct.pack_into('>H',rom,macro+10,28)
        for i in range(4): struct.pack_into('>H',rom,quad+i*2,i)
        tiles=b''.join(bytes((v*17,))*32 for v in (1,2,3,4))
        layout={'width':16,'height':16,'records':[{'type':0,'x':0,'y':0,'visual':True}]}
        image=render_foreground(rom,layout,tiles,quad,macro)
        self.assertEqual((image[0],image[8],image[128],image[136]),(1,2,3,4))
        layout['records'][0]['type']=0x200
        flipped=render_foreground(rom,layout,tiles,quad,macro)
        self.assertEqual((flipped[0],flipped[8],flipped[128],flipped[136]),(3,4,1,2))
        # Unaligned section boundaries must preserve flipped pixels exactly.
        section=render_foreground(rom,layout,tiles,quad,macro,(5,3,9,11))
        expected=b''.join(flipped[y*16+5:y*16+14] for y in range(3,14))
        self.assertEqual(section,expected)
        with self.assertRaises(ValueError):
            render_foreground(rom,layout,tiles,quad,macro,(15,0,2,1))

if __name__=='__main__': unittest.main()
