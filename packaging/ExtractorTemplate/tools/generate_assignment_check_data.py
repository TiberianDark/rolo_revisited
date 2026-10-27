"""Generate expected placement/definition chains and current build pins for the local compiled checker."""
import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
selectors=[n for n in range(1,80) if n not in (46,74,75,76,79)]
rows=[]
for n in selectors:
 d=json.loads((p/f'assets/extracted/all-levels/selector-{n:02}/coverage.json').read_text(encoding='utf-8-sig'))
 for r in d['marker_links']:
  chain=[int(x,16) for x in r.get('definition_chain',[])]
  if len(chain)>16:raise ValueError('Chain extent')
  rows.append('{'+','.join(map(str,[n,r['record_offset'],r['type'],r['x'],r['y'],r.get('definition',0),len(chain)]))+',{{'+','.join(map(str,chain))+'}}},')
files=sorted(list((p/'src').rglob('*.hpp'))+list((p/'src').glob('*.cpp'))+[p/'bin/Rolo.exe']+list((p/'bin').glob('*.rla'))+[p/'assets/extracted/all-levels/manifest.json'])
lines=['#pragma once','#include <array>','namespace assignment_data {','struct Case{unsigned level,offset,type,x,y,root,count;std::array<unsigned,16> chain;};',f'inline constexpr std::array<Case,{len(rows)}> cases{{{{',*rows,'}};','struct Pin{const char*path;const char*sha;};',f'inline constexpr std::array<Pin,{len(files)}> pins{{{{']
for f in files:lines.append('{'+json.dumps(f.relative_to(p).as_posix())+','+json.dumps(hashlib.sha256(f.read_bytes()).hexdigest())+'},')
lines+=['}};','}']
(p/'tests/assignment_check_data.hpp').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'{len(selectors)} connected selectors, {len(rows)} original marker records, {len(files)} build pins')

