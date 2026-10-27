"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "actor_phase_ending",\n  "title": "actor phase countdown and ending transition",\n  "sources": [\n    "src/core/actor_phase_ending.hpp",\n    "tests/actor_phase_ending_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 524288\n  },\n  "cases": 524288,\n  "specs": [\n    {\n      "address": 47730,\n      "ranges": [\n        [\n          47730,\n          47734\n        ],\n        [\n          48636,\n          48648\n        ]\n      ],\n      "contract": "AdvanceBYTE50 wrapping, setBYTE51=64; retainallotheractorbytes."\n    },\n    {\n      "address": 47746,\n      "ranges": [\n        [\n          47746,\n          47750\n        ],\n        [\n          48462,\n          48480\n        ]\n      ],\n      "contract": "DecrementBYTE51; onzeroadvanceBYTE50andreset51=16; initialzero wrapsFFwithoutadvance."\n    },\n    {\n      "address": 60388,\n      "ranges": [\n        [\n          60388,\n          60406\n        ]\n      ],\n      "contract": "ComparephaseWORD46/48; changedpublishes48andFFFFFFFFreturn, equalpreservesincomingD0highWORD/returnsphase lowWORD, typedchangedrepresentsZ."\n    },\n    {\n      "address": 60052,\n      "ranges": [\n        [\n          60052,\n          60056\n        ],\n        [\n          60360,\n          60388\n        ]\n      ],\n      "contract": "Observephaseentry; changedclears70andsets50=200; decrement50WORD, negativeclears46, preservingallotheractorbytes."\n    },\n    {\n      "address": 40224,\n      "ranges": [\n        [\n          40224,\n          40228\n        ],\n        [\n          40346,\n          40360\n        ],\n        [\n          40398,\n          40406\n        ]\n      ],\n      "contract": "ReadendingactorBYTE6, onlyzerodecrementsC494WORDwithwrap."\n    },\n    {\n      "address": 40228,\n      "ranges": [\n        [\n          40228,\n          40232\n        ],\n        [\n          40360,\n          40398\n        ]\n      ],\n      "contract": "CompletionserviceWORD100 ->fadeblackthenstate9A88; allotherWORDsstate9B34withoutfade; servicemutationbeforefinalstore retained."\n    }\n  ],\n  "proof": "Reviewedoriginalbranchslots/disjointtargets. Native524288cases:all65536BYTEpaircountdowns andWORDpauses,changed/equalphaseentries,full130BYTEpreservation;allWORDendingtimers with4gatevalues;allWORDcompletionpercentincluding100andlivefademutation. Initialoptimizedword-signstore/reloadgaveboundarymismatch32768; equivalentexplicitstoredhighBYTEsignconditioncorrected, onlyfailed/changedfamilyrepeated, passed.",\n  "scope": "Local actor state and explicitcompletion/fadeservicecontracts; validnativeactoridentities. TypedboolphasechangedrepresentsZbranch; otherCPUflags andincomingregistereffects beyondexposedvalue external. Endingdelay andstatewrites verified, notendingart/playbackfidelity orSDLbinding."\n}')
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
