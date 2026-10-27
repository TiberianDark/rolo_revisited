"""Reproducible pinned-ROM asset batch for the connected forest levels."""
import hashlib,json,runpy
from pathlib import Path
from inventory_rom import ROM_HASH
from export_level1_terrain import generate
from export_level1_objects import export as objects
from export_actor_patterns import export as patterns
from export_dynamic_platforms import export as platforms
p=Path(__file__).resolve().parents[1]
assert hashlib.sha256((p/'local/rolo.md').read_bytes()).hexdigest()==ROM_HASH,'Wrong ROM revision'
outputs=[]
for selector in (1,2,3,4,8):
 header,report=generate(p,selector);report['scope']=report['scope'].replace('level1',f'level{selector}')
 target=p/f'src/core/level{selector}_terrain_data.hpp';target.write_text(header,encoding='utf-8');outputs.append(target)
 (p/f'docs/stage9/level{selector}-terrain-assets.json').write_text(json.dumps(report,indent=2)+'\n')
runpy.run_path(str(p/'tools/export_level1_world.py'),run_name='__main__')
runpy.run_path(str(p/'tools/export_native_all_levels.py'),run_name='__main__')
objects(p);patterns(p);platforms(p)
outputs.extend(p/f for f in ['src/core/all_native_level_data.hpp','src/core/level1_world_data.hpp','src/core/level1_player_animation_data.hpp','bin/level1-player-assets.rla','src/core/dynamic_platform_data.hpp','src/core/level1_object_data.hpp','src/core/level1_object_animation_data.hpp','src/core/actor_pattern_data.hpp','bin/level1-object-assets.rla'])
manifest=dict(rom_sha256=ROM_HASH,selectors=[1,2,3,4,8],files={str(f.relative_to(p)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in outputs},scope='Deterministic data extraction only. Native compilation and gameplay fidelity are separate steps; no ROM instructions executed.')
(p/'docs/stage9/connected-level-asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Pinned ROM validated; five terrain selectors, original actor animations and indexed graphics extracted.')
