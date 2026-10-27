import struct
import unittest
import zlib
from rolo_extract import startup_integrity,indexed_pixels,png_indexed,font_evidence


class ExtractionTests(unittest.TestCase):
    def test_startup_checksum_skip_and_wrapping(self):
        data=bytearray(0x80000)
        struct.pack_into('>I',data,0,0xffffffff)
        struct.pack_into('>I',data,4,2)
        struct.pack_into('>I',data,0x18c,0x12345678)
        struct.pack_into('>I',data,0x7ffb0,0xabcdef01)
        self.assertEqual(startup_integrity(data)['computed'],1)

    def test_revision_rejected_before_extraction(self):
        with self.assertRaises(ValueError): font_evidence(bytes(0x80000))

    def test_indexed_tile_layout_and_empty_slots(self):
        width,height,pixels=indexed_pixels(bytes([0x1f])+bytes(31))
        self.assertEqual((width,height),(128,8))
        self.assertEqual(pixels[:2],bytes((1,15)))
        self.assertEqual(pixels[8:],bytes(len(pixels)-8))

    def test_png_crc_and_scanlines(self):
        png=png_indexed(2,1,bytes((1,15)),2)
        self.assertEqual(png[:8],b'\x89PNG\r\n\x1a\n')
        offset=8; idat=b''
        import binascii
        while offset < len(png):
            size=struct.unpack_from('>I',png,offset)[0]; kind=png[offset+4:offset+8]
            payload=png[offset+8:offset+8+size]
            self.assertEqual(struct.unpack_from('>I',png,offset+8+size)[0],binascii.crc32(kind+payload)&0xffffffff)
            if kind == b'IDAT': idat+=payload
            offset+=size+12
        self.assertEqual(zlib.decompress(idat),bytes((0,1,1,15,15))*2)

if __name__ == '__main__': unittest.main()
