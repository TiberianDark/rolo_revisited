import hashlib,struct,unittest
from pathlib import Path
from export_preview import rgba,build_pack

ROOT=Path(__file__).resolve().parents[1]
class PreviewFormatTests(unittest.TestCase):
    def test_transparent_indices_across_palette_banks(self):
        colors=[(i,i,i) for i in range(32)]
        self.assertEqual(rgba(bytes([0,16,17]),colors,True),bytes([0,0,0,0,16,16,16,0,17,17,17,255]))
    def test_background_zero_is_opaque(self):
        self.assertEqual(rgba(bytes([0]),[(10,20,30)],False),bytes([10,20,30,255]))
    @unittest.skipUnless((ROOT/'local/rolo.md').exists(),'Pinned local ROM needed')
    def test_pack_reproducible_and_complete(self):
        payload,manifest=build_pack((ROOT/'local/rolo.md').read_bytes(),(ROOT/'src/core/entrance_data.hpp').read_text())
        self.assertEqual(payload,(ROOT/'bin/entrance-assets.rla').read_bytes())
        self.assertEqual(payload[:8],b'RLOAS01\0')
        self.assertEqual(struct.unpack_from('<I',payload,8)[0],37)
        self.assertEqual(len([r for r in manifest['records'] if r['kind']==3]),34)
        self.assertEqual(hashlib.sha256(payload).hexdigest(),manifest['pack_sha256'])
    @unittest.skipUnless((ROOT/'local/rolo.md').exists(),'Pinned local ROM needed')
    def test_uninspected_rom_rejected(self):
        data=bytearray((ROOT/'local/rolo.md').read_bytes());data[0]^=1
        with self.assertRaises(ValueError):build_pack(data,(ROOT/'src/core/entrance_data.hpp').read_text())
if __name__=='__main__':unittest.main()
