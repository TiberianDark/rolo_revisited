"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "player_side_entries",\n  "title": "local direct side collision entries",\n  "sources": [\n    "src/core/player_side_entries.hpp",\n    "tests/player_side_entries_verification_tests.cpp",\n    "tests/wall_terrain_fixture.hpp"\n  ],\n  "dependencies": [\n    "docs/stage9/wall-probe-verification.json"\n  ],\n  "results": {\n    "passed": true,\n    "state_cases": 4194304\n  },\n  "cases": 2097152,\n  "specs": [\n    {\n      "address": 33446,\n      "ranges": [\n        [\n          33446,\n          33550\n        ]\n      ],\n      "contract": "Direct left entry, arbitrary caller D6 WORD reach; signed first distance and unsigned fallback, retains prior side bits and all unrelated fields; hit clears X fraction,121 and58LONG, sets124bit1."\n    },\n    {\n      "address": 33550,\n      "ranges": [\n        [\n          33550,\n          33654\n        ]\n      ],\n      "contract": "Direct right entry, arbitrary caller D6 WORD reach; signed first distance and unsigned fallback, retains prior side bits; hit clears X fraction,121 and58LONG,sets124bit2."\n    }\n  ],\n  "proof": "One focused direct-entry batch over all65536callerreachWORDs,eightstatepartitions,two directions,fourheterogeneousstableterrain/shift/mirror/profilefixtures. IndependentrawMapprobe and signed/unsigned branch oracle comparesall130actorbytes. Parent827Aproof unchanged; unlikeparentderivedreach, directD6domainindependentofactorspeeds.",\n  "scope": "Local stable actor and immutable populated terrain. Existing player_wall_probe implementation within its reviewed domain; actual caller D6 provenance and live streaming/collision ownership remain external."\n}')
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
slug=CONFIG['name'].replace('_','-');result=root/('work/'+slug+'-results.json');r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==CONFIG['results']
sources=list(CONFIG['sources']);pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
exe=root/('work/'+CONFIG['name']+'_verification_tests.exe');assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
sources+=CONFIG.get('dependencies',[])
for at,expected in CONFIG.get('data_pins',[]):assert rom[at:at+len(bytes.fromhex(expected))].hex()==expected
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
for spec in CONFIG['specs']:
 start=spec['address'];ranges=spec['ranges'];items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 end=max(b for a,b in ranges)
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: '+CONFIG['title'],native_sources=[CONFIG['sources'][0]],checked_cases=spec.get('cases',CONFIG['cases']),contract=spec['contract'],proof=CONFIG['proof'],scope=spec.get('scope',CONFIG['scope'])))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/('docs/stage9/'+slug+'-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(str(len(records))+' local contracts registered: '+slug)
