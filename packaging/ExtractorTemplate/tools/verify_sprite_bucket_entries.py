"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "sprite_bucket_entries",\n  "title": "word bucket sprite assembly contract",\n  "sources": [\n    "src/core/sprite_bucket_entries.hpp",\n    "tests/sprite_bucket_entries_verification_tests.cpp"\n  ],\n  "dependencies": [\n    "docs/stage9/macro-graphics-entries-verification.json"\n  ],\n  "results": {\n    "passed": true,\n    "sprite_cases": 1048640,\n    "capacity_cases": 4\n  },\n  "cases": 1048644,\n  "specs": [\n    {\n      "address": 13376,\n      "ranges": [\n        [\n          12878,\n          13392\n        ],\n        [\n          13424,\n          13432\n        ]\n      ],\n      "contract": "Consume sign-extendedFFFF WORD keys untilzero, hidden/nullgraphics gates, graphics-cache mutation and14BYTE upload packets, actual32px SAT subdivision/partial8px chunks and flips, inclusive signed clipping, original tile stride table, count81 global escape and prior SAT link termination; normal bucket clears pending count only."\n    }\n  ],\n  "proof": "One focused native family over65536 coordinate/tile/state patterns and16 flip/cache/camera partitions; independent geometric chunk oracle and packet decoding;64 explicit clipping boundaries; capacity77..80 escape fixtures verify80 published records, prior tail link, preserved pending count and no next actor read. Original instructions reviewed and table3450 pinned; no ROM execution.",\n  "scope": "Local finite zero-terminated buckets with resolved actor/definition handles, positive8px-multiple dimensions below32768, valid initial SAT tail/count<=80 and sufficient native queue storage. Typed vectors contain published packets/SAT records, excluding zeroLONG queue sentinel and discarded three-byte unpublished overflow scratch. Outer31DC preparation, device transfer timing and SDL renderer adoption remain separate. Native actor_sprite_view reused for origin; independent test computes origin and chunk coordinates.",\n  "data_pins": [\n    [\n      13392,\n      "00010002000300040002000400060008000300060009000c00040008000c0010"\n    ]\n  ]\n}')
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
for lo,hi in CONFIG.get('boundary_extensions',[]):
 assert CONFIG.get('boundary_basis') and CONFIG.get('boundary_producers')
 for source,encoded in CONFIG['boundary_producers']:assert rom[source:source+len(bytes.fromhex(encoded))].hex()==encoded
 cursor=lo
 while cursor<hi:
  accepted.add(cursor);cursor+=Decoder(rom,cursor).decode()['size']
 assert cursor==hi
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
