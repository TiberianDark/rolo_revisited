"""Reproduce next level asset export and full marker-definition dependency batch."""
import hashlib,json,re
from pathlib import Path
from collections import Counter
from export_level1_terrain import generate
from inventory_rom import ROM_HASH
from rolo_maps import parse_map,long
from rolo_codec import decode_backward_lz
p=Path(__file__).resolve().parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
header,assets=generate(p,3);assets['scope']=assets['scope'].replace('level1','level3')
(p/'src/core/level3_terrain_data.hpp').write_text(header,encoding='utf-8');(p/'docs/stage9/level3-terrain-assets.json').write_text(json.dumps(assets,indent=2)+'\n')
source=long(rom,0x4ab1a+24)&0xffffff;data=decode_backward_lz(rom,source)[0];layout=parse_map(data)
known=set()
for file in (p/'src/core').glob('*data.hpp'):
 if file.name not in ['level1_object_data.hpp','level1_world_data.hpp','level1_hud_data.hpp']:continue
 known.update(int(v,0) for v in re.findall(r'ActorDefinition\{(0x[a-f0-9]+|[0-9]+)',file.read_text()))
world=(p/'src/core/level1_enemy_slice.hpp').read_text();bound={int(v,16) for v in re.findall(r'callback==0x([a-f0-9]+)',world)}
rows=[];definitions={}
for record in layout['records']:
 if record['visual']:continue
 kind,parameter=record['type']>>8,record['type']&255;table={4:0x46c6,5:0x4762,6:0x47ba,0x12:0x4948}.get(kind)
 key=long(rom,table+(parameter if kind in (6,0x12) else parameter//2)*4) if table else 0x14482 if kind==0xb else None
 rows.append(dict(marker=f'{record["type"]:04X}',record=record,definition=None if key is None else f'{key:06X}'))
 seen=set()
 while key and key not in seen:
  seen.add(key);callback=long(rom,key+12);linked=long(rom,key)
  definitions[key]=dict(key=f'{key:06X}',original_bytes=rom[key:key+34].hex(),callback=f'{callback:06X}',linked=f'{linked:06X}',definition_exported=key in known,callback_bound=callback in bound,response=f'{long(rom,key+22):06X}')
  key=linked
report=dict(rom_sha256=ROM_HASH,selector=3,width=layout['width'],height=layout['height'],terrain_shared_with_first_two=True,markers=rows,definitions=list(definitions.values()),marker_counts=dict(Counter(r['marker'] for r in rows)),remaining=['Export missing definition chains, selected animations and graphics.','Translate unbound original callbacks and any new companion controls.','Review pickup response handlers, trigger/camera mode and completion selector.','Enable overworld admission only once the original objects can initialize/update without unsupported paths.'],status='Terrain data connected; full gameplay admission pending original actor dependencies')
(p/'docs/stage9/level3-marker-dependencies.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(dimensions=[layout['width'],layout['height']],markers=len(rows),definitions=len(definitions),missing=[v for v in definitions.values() if not v['definition_exported'] or not v['callback_bound']]),indent=1))


