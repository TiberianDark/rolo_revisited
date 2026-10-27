import unittest
from romtool import analyze, extract, read_rom, tiles_ppm
from pathlib import Path
from unittest.mock import patch

class RomTests(unittest.TestCase):
    def test_checksum_big_endian_and_header_exclusion(self):
        data = bytearray(516); data[0x100:0x104] = b'SEGA'
        data[512:] = bytes.fromhex('1234abcd'); data[0x18e:0x190] = bytes.fromhex('be01')
        self.assertTrue(analyze(bytes(data))['checksum']['matches'])

    def test_reject_truncated_and_non_raw(self):
        for blob in (b'SEGA', bytes(512), bytes(513)):
            with patch.object(Path, 'read_bytes', return_value=blob):
                with self.assertRaises(ValueError): read_rom('unused')

    def test_extract_bounds(self):
        self.assertEqual(extract(b'abcd', 1, 2), b'bc')
        for start, size in ((-1, 2), (0, 0), (3, 2)):
            with self.assertRaises(ValueError): extract(b'abcd', start, size)

    def test_tile_nibble_order(self):
        ppm = tiles_ppm(bytes([0x1f])+bytes(31))
        pixels = ppm.split(b'\n', 3)[3]
        self.assertEqual(pixels[:6], bytes([17]*3+[255]*3))
        with self.assertRaises(ValueError): tiles_ppm(b'x')

if __name__ == '__main__': unittest.main()
