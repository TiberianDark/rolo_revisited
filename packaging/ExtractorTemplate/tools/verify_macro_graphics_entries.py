"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "macro_graphics_entries",\n  "title": "macro factory and graphics publication contracts",\n  "sources": [\n    "src/core/macro_graphics_entries.hpp",\n    "tests/macro_graphics_entries_verification_tests.cpp"\n  ],\n  "dependencies": [\n    "docs/stage9/display-port-publication-verification.json"\n  ],\n  "results": {\n    "passed": true,\n    "publication_cases": 564,\n    "factory_cases": 524288,\n    "branch_cases": 1048576\n  },\n  "cases": 1573428,\n  "specs": [\n    {\n      "address": 18060,\n      "ranges": [\n        [\n          18060,\n          18064\n        ],\n        [\n          18552,\n          18632\n        ]\n      ],\n      "contract": "Actual4878 body: override/visited/signed-exclusion gate; wrapped signedWORD parameter*8 record, dynamic native macro factory, negative failure return; success B80A callback/54/55/50 fields and RAM definition selector34."\n    },\n    {\n      "address": 18084,\n      "ranges": [\n        [\n          18084,\n          18088\n        ],\n        [\n          18698,\n          18760\n        ]\n      ],\n      "contract": "Actual490A body: lowBYTE*4 definition, wrapped X+8 and ((row+2)*8)+1 with zero fractions, full retained marker/resource request; hide linked actor through live returned A4 even on allocation failure."\n    },\n    {\n      "address": 18776,\n      "ranges": [\n        [\n          18776,\n          19016\n        ]\n      ],\n      "contract": "Dynamic definition free-stack zero/failure/success, selective retained bytes, original macro dimensions and signed lowWORD product/2; saved graphics index and table key, XTRN graphics flags; native4B2E publication on success, definition remains mutated on failure."\n    },\n    {\n      "address": 19246,\n      "ranges": [\n        [\n          19246,\n          19640\n        ]\n      ],\n      "contract": "Native two-row/odd-final-row destination packing, original512-quad and11-bit tile masks, four14BYTE transfer packets percell; signed budget<=0 flush/retry, preserved caller context, WORD destination wrap and empty height publication."\n    }\n  ],\n  "proof": "One focused native family:564 independent geometric packet/address/mask/flush-budget cases including255-cell edges,524288 dynamic free-stack/failure/state cases and1048576 branch/gate/index partitions. Actual original lookup bytes are read as data; invalid negative external record windows are explicitly rejected. No ROM execution.",\n  "scope": "Local typed graphics publication payloads, valid positive16px-multiple width/nonnegative height below32768, readable macro header/cells/quads and resolved definition/actor handles. Incoming breakable WORD admits only ROM-readable signed-offset record windows; actual producer domains remain open. ZeroLONG queue sentinel/cursor and260A/8F02 device publication are represented by typed flush/publication services, not hardware timing. Allocator may fail while retaining a live A4; source registers are request values. No SDL integration claim.",\n  "data_pins": [\n    [\n      18632,\n      "15ff0400000142ea53ff010000014a7c"\n    ],\n    [\n      18760,\n      "00013f7600013f1000013f5400013f32"\n    ]\n  ]\n}')
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
