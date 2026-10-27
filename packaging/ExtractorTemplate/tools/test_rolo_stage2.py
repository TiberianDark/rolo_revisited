import struct
import unittest
from rolo_stage2 import map_pixels,bmp_rgb,png_palette


class Stage2Tests(unittest.TestCase):
    def test_loader_discards_source_attributes(self):
        vram=bytearray(0x10000); vram[32]=0x1f
        width,height,pixels,mask=map_pixels(vram,struct.pack('>H',0xf801),1,1,0x4000)
        self.assertEqual((width,height),(8,8))
        self.assertEqual(pixels[:2],bytes((33,47)))
        self.assertEqual(mask[:3],bytes((1,1,0)))

    def test_render_flip_from_resulting_attribute_word(self):
        vram=bytearray(0x10000); vram[32]=0x1f
        _,_,pixels,_=map_pixels(vram,struct.pack('>H',1),1,1,0x800)
        self.assertEqual(pixels[6:8],bytes((15,1)))

    def test_bmp_bgr_bottom_up_padding(self):
        image=bmp_rgb(1,2,bytes((0,1)),[(255,0,0),(0,0,255)])
        self.assertEqual(image[:2],b'BM')
        self.assertEqual(image[54:],bytes((255,0,0,0,0,0,255,0)))

    def test_invalid_image_inputs(self):
        with self.assertRaises(ValueError): map_pixels(bytes(0x10000),b'',1,1,0)
        with self.assertRaises(ValueError): png_palette(1,1,b'\x10',[(0,0,0)])
        with self.assertRaises(ValueError): bmp_rgb(2,1,b'\0',[(0,0,0)])

if __name__ == '__main__': unittest.main()
