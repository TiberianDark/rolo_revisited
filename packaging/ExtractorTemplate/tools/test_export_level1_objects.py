"""Check factory-domain boundaries and immutable ROM-to-native asset exports."""
import hashlib,json,re,struct,tempfile,unittest
from pathlib import Path
from export_level1_objects import export
from inventory_rom import ROM_HASH

PROJECT=Path(__file__).resolve().parents[1]

class ExportTests(unittest.TestCase):
    def test_roster_definitions_and_factory_tables(self):
        rom=(PROJECT/'local/rolo.md').read_bytes()
        self.assertEqual(hashlib.sha256(rom).hexdigest(),ROM_HASH)
        # The cross-level variant starts in the active key-enemy callback.
        # Every other definition byte and all four reached selectors match.
        baseline=rom[0x144a4:0x144a4+34]
        active=rom[0x144c6:0x144c6+34]
        self.assertEqual(active[:12]+active[16:],baseline[:12]+baseline[16:])
        self.assertEqual(int.from_bytes(active[12:16],'big'),0xb314)
        generated=(PROJECT/'src/core/level1_object_animation_data.hpp').read_text()
        for selector in (0,4,48,52):
            self.assertIn(f'AnimationProgram{{0x144c6,{selector},',generated)
        report=json.loads((PROJECT/'docs/stage9/first-level-roster.json').read_text())
        for marker in report['markers']:
            if not marker.get('definition'):continue
            category=marker['category'];parameter=marker['parameter']
            if category==4:address=0x46c6+(parameter//2)*4
            elif category==5:address=0x4762+(parameter//2)*4;self.assertLess(address,0x4796)
            elif category==6:address=0x47ba+parameter*4
            elif category==18:address=0x4948+parameter*4
            else:continue
            self.assertEqual(struct.unpack_from('>I',rom,address)[0],marker['definition'])
        self.assertEqual(rom[0x4796:0x4798],bytes.fromhex('4a39')) # Exact instruction, not a definition pointer.

    def test_exported_animation_spawn_definitions_are_bound(self):
        headers=[PROJECT/'src/core'/name for name in ('level1_object_data.hpp','level1_world_data.hpp')]
        definitions=set()
        for header in headers:
            definitions.update(int(v,0) for v in re.findall(r'ActorDefinition\{(0x[0-9a-f]+|[0-9]+),',header.read_text()))
        nodes=(PROJECT/'src/core/level1_object_animation_data.hpp').read_text()
        for value in re.findall(r'AnimationNode\{AnimationOp::Spawn(?:Inherited|Random),[0-9]+,([0-9]+),',nodes):
            self.assertIn(int(value),definitions,f'Unbound animation child {int(value):06X}')

    def test_reproducible_objects_and_all_roster_assets(self):
        scratch=(PROJECT/'build-core').resolve();scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='rolo-object-export-',dir=scratch) as directory:
            temp=Path(directory).resolve()
            self.assertTrue(temp.is_relative_to(scratch))
            for relative in ['local','src/core','docs/stage9','bin']:(temp/relative).mkdir(parents=True,exist_ok=True)
            for relative in ['local/rolo.md','docs/stage9/first-level-roster.json']:(temp/relative).write_bytes((PROJECT/relative).read_bytes())
            report=export(temp)
            required={marker['definition'] for marker in json.loads((temp/'docs/stage9/first-level-roster.json').read_text())['markers'] if marker.get('definition') and marker['definition'] not in (0x13f98,)}
            self.assertTrue(required.issubset({int(key,16) for key in report['definitions']}))
            for relative in ['src/core/level1_object_data.hpp','src/core/level1_object_animation_data.hpp','bin/level1-object-assets.rla','docs/stage9/level1-object-export.json']:
                self.assertEqual((temp/relative).read_bytes(),(PROJECT/relative).read_bytes(),relative)

if __name__=='__main__':unittest.main()
