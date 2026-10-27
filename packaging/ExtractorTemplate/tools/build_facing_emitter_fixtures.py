"""Reproduce original MAP fixtures for the shared facing/projectile enemy."""
import json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parents[1]
assert hashlib.sha256((p/'local/rolo.md').read_bytes()).hexdigest()=='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
manifest=json.loads((p/'assets/extracted/all-levels/manifest.json').read_text());rows=[]
for level in manifest['selectors']:
 if not level['world_referenced']:continue
 for record in level['markers']:
  if record.get('definition')==0x1498e:rows.append((level['selector'],record['record_offset'],record['type'],record['x'],record['y']))
assert len(rows)==17
(p/'docs/stage9/facing-emitter-fixtures.txt').write_text('\n'.join(' '.join(map(str,row))for row in rows)+'\n')
print('17 original facing enemy placements exported.')
