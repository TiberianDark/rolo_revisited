"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "linked_actor_families",\n  "title": "linked actor coordinator contracts",\n  "sources": [\n    "src/core/linked_actor_families.hpp",\n    "tests/linked_actor_families_verification_tests.cpp",\n    "tests/remaining_actor_reference.hpp"\n  ],\n  "dependencies": [\n    "docs/stage9/actor-corner-motion-verification.json",\n    "docs/stage9/anchor-step-verification.json",\n    "docs/stage9/actor-remaining-motion-verification.json"\n  ],\n  "results": {\n    "passed": true,\n    "chain_cases": 327680,\n    "pursuit_cases": 1048576,\n    "ride_cases": 1048576\n  },\n  "cases": 2424832,\n  "specs": [\n    {\n      "address": 56820,\n      "ranges": [\n        [\n          56820,\n          57318\n        ]\n      ],\n      "contract": "Ride mount/unmount and ordered input/probe services; shared native gravity, integration, signed supports and four linked children; raw overlapping C502/C506 writes retained, captured controlled actor survives chain-flag service."\n    },\n    {\n      "address": 63018,\n      "ranges": [\n        [\n          63018,\n          63156\n        ]\n      ],\n      "contract": "Finite acyclic chain initialization/visual propagation, full contact-byte reduction, head preservation across hurt, four-way corner service and signed head retirement."\n    },\n    {\n      "address": 63658,\n      "ranges": [\n        [\n          63658,\n          63982\n        ]\n      ],\n      "contract": "Native random initialization and signed-axis pursuit, original wobble bytes, signed live-count/timer guards and allocation requests preserving live A5 changes and FFFF fractions."\n    }\n  ],\n  "proof": "Assertions-enabled native tests cover all WORD seeds across chain lengths and 16 service partitions; independent arithmetic oracle for pursuit/physics, explicit request and identity assertions. Original reviewed instructions statically decoded; no ROM execution.",\n  "scope": "Local caller/state contract within valid finite linked actors and typed mount/input/probe/corner/contact/allocation services. Service implementations, actual caller reachability and shared RAM alias binding remain separate; not whole-level fidelity.",\n  "data_pins": [\n    [\n      58472,\n      "00000100010100010000ff00ffff00ff"\n    ],\n    [\n      63156,\n      "6000000e6000007c6000002c6000004e"\n    ]\n  ],\n  "boundary_extensions": [\n    [\n      56912,\n      56922\n    ]\n  ],\n  "boundary_producers": [\n    [\n      56902,\n      "23fc00008078ffffc502"\n    ]\n  ],\n  "boundary_basis": "Direct sequential fallthrough: reviewed ten-byte MOVE.L at DE46 ends at DE50; reviewed ten-byte MOVE.L at DE50 ends at existing DE5A boundary. Local evidence only."\n}')
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
