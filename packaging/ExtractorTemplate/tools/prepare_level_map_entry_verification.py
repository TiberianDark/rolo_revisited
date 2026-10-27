"""Reproduce data-only MAP test fixture from pinned extraction manifests."""
from pathlib import Path
import json,struct,hashlib
from inventory_rom import ROM_HASH
p=Path(__file__).resolve().parents[1];root=p.parents[1];assert hashlib.sha256((p/'local/rolo.md').read_bytes()).hexdigest()==ROM_HASH
records=[];blob=bytearray()
for selector in range(80):
 m=json.loads((p/f'assets/extracted/all-levels/selector-{selector:02d}/manifest.json').read_text(encoding='utf-8'));assert m['rom_sha256']==ROM_HASH
 for layer in ['foreground','background']:
  binary=m['layers'][layer]['binary'];raw=(p/binary['path']).read_bytes();digest=hashlib.sha256(raw).hexdigest();assert len(raw)==binary['size'] and digest==binary['sha256'];records.append(dict(selector=selector,layer=layer,size=len(raw),sha256=digest));blob+=struct.pack('>I',len(raw))+raw
(root/'work/level-map-entry-fixtures.bin').write_bytes(blob)
(p/'docs/stage9/level-map-entry-fixtures-reference.json').write_text(json.dumps(dict(rom_sha256=ROM_HASH,fixture_sha256=hashlib.sha256(blob).hexdigest(),records=records),indent=2)+'\n',encoding='utf-8');print('Prepared160pinnedMAPdatareferences.')
