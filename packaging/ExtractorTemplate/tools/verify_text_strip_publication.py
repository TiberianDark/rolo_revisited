"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "text_strip_publication",\n  "title": "text strip state and publication",\n  "sources": [\n    "src/core/text_strip_publication.hpp",\n    "tests/text_strip_publication_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 131978\n  },\n  "cases": 131978,\n  "specs": [\n    {\n      "address": 24194,\n      "ranges": [\n        [\n          24194,\n          24240\n        ]\n      ],\n      "contract": "Gate low20cursor bits; clear20glyph cells only on boundary; negative source returns after clear; zero source skips write; scroll then publication otherwise."\n    },\n    {\n      "address": 24330,\n      "ranges": [\n        [\n          24330,\n          24376\n        ]\n      ],\n      "contract": "Scan for BYTE1 through at most65536DBEQ iterations; preserve LONG-negation and WORD signed centering including odd halfcell, exhausted loop wraps count to0."\n    },\n    {\n      "address": 24376,\n      "ranges": [\n        [\n          24376,\n          24406\n        ]\n      ],\n      "contract": "Twenty glyph0 service calls at live WORD offset0,4..76, saved loop index; finaloffset80."\n    },\n    {\n      "address": 24406,\n      "ranges": [\n        [\n          24406,\n          24466\n        ]\n      ],\n      "contract": "Unsigned byte subtract32 then N controls glyph continuation; codes32..159 publish raw-32 and advanceoffset4; terminating0 clears source,2setsFFFFFFFF,other terminators retain postread pointer."\n    },\n    {\n      "address": 24622,\n      "ranges": [\n        [\n          24622,\n          24678\n        ]\n      ],\n      "contract": "Control/data publication order and literals preserved; cursor LONG+2000, replace only lowWORD with low11bits, publish resulting word."\n    },\n    {\n      "address": 25122,\n      "ranges": [\n        [\n          25122,\n          25130\n        ]\n      ],\n      "contract": "Sequential BYTEcopy through zero inclusive, back destination up1; live source/destination memory alias order retained."\n    },\n    {\n      "address": 25130,\n      "ranges": [\n        [\n          25130,\n          25142\n        ]\n      ],\n      "contract": "BYTE+48 wrapping sequential copy, DBF WORD+1iterations including65536; finalcounterFFFF, unrelated bytes retained."\n    }\n  ],\n  "proof": "Reviewed static instruction boundaries and branches; one assertions-enabled optimized native run checks every lowWORD publication input, everyWORD DBF count with overlapping memory propagation, all256raw glyph/control inputs at offset wrap boundaries, centering lengths0..128 and65535/65536, composed gated dispatch and terminal byte copies. NoROMinstructions executed.",\n  "scope": "Local readable bounded native source/destination spans and distinct cursor-reference objects. Text-strip glyph andscroll services are explicit nonmutating observations of caller state in this proof; glyph rasterization5F92, scroll body5EB0, VDP timing, full caller reachability and SDL integration remain separate. Out-of-span inputs reject rather than reading adjacent original memory; not a whole-screen fidelity claim."\n}')
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
