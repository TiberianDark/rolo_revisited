"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "indexed_shared_access",\n  "title": "jigsaw plane and actor indexed access",\n  "sources": [\n    "src/core/indexed_shared_access.hpp",\n    "tests/indexed_shared_access_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 1114656\n  },\n  "cases": 1114656,\n  "specs": [\n    {\n      "address": 42606,\n      "ranges": [\n        [\n          42606,\n          42688\n        ]\n      ],\n      "contract": "Typedfourwayjigsawneighborselection fororiginalD4WORDbyteoffset0/2/4/6, dependentWORDoffsetarithmetic, signedneighborEA andzeroextendedBYTEresult."\n    },\n    {\n      "address": 42610,\n      "ranges": [\n        [\n          42610,\n          42612\n        ],\n        [\n          42672,\n          42676\n        ],\n        [\n          42678,\n          42688\n        ]\n      ],\n      "contract": "Literal+1WORDneighboroffset thenreadflagsatbase+signedoffset-1."\n    },\n    {\n      "address": 42612,\n      "ranges": [\n        [\n          42612,\n          42614\n        ],\n        [\n          42676,\n          42688\n        ]\n      ],\n      "contract": "LiteralFFFFWORDneighboroffset(-1) thenreadflagsatbase-2."\n    },\n    {\n      "address": 42614,\n      "ranges": [\n        [\n          42614,\n          42616\n        ],\n        [\n          42648,\n          42672\n        ],\n        [\n          42678,\n          42688\n        ]\n      ],\n      "contract": "WORDminus4+minus2, rownonzerosubtractminus2, rowzerosubtractplus6, signedread."\n    },\n    {\n      "address": 42616,\n      "ranges": [\n        [\n          42616,\n          42648\n        ],\n        [\n          42678,\n          42688\n        ]\n      ],\n      "contract": "Row3usesminus12+minus10,otherrowsminus4+minus2; subtractminus2thennegateWORD, signedread."\n    },\n    {\n      "address": 26918,\n      "ranges": [\n        [\n          26918,\n          26976\n        ]\n      ],\n      "contract": "CopyD0BYTEintobothF2F4/F2F5, classifyinputD1highnibble andD0lownibble, setF2F3."\n    },\n    {\n      "address": 26952,\n      "ranges": [\n        [\n          26952,\n          26976\n        ]\n      ],\n      "contract": "BYTE32->0,64->1,allotherBYTEs->3 fulltypedscalar."\n    },\n    {\n      "address": 62306,\n      "ranges": [\n        [\n          62306,\n          62322\n        ]\n      ],\n      "contract": "Followlink84countWORD+1times withDBEQnullstopbeforecounterdecrement; validfinitebudgetcyclesallowed, resultnext/count."\n    },\n    {\n      "address": 62202,\n      "ranges": [\n        [\n          62202,\n          62234\n        ]\n      ],\n      "contract": "Follow6links, ifnonnulltoggle125bit1thenliveoptionalnext125bit1; selfaliasnaturallytogglestwice."\n    }\n  ],\n  "proof": "Onefocusednative1114656cases:all65536WORDoffsetpatterns x4rowpartitions x4branchselectors withsigned65536BYTEflagwindow;all256x256planebytes;48chainlengthsx6DBFcounts including65535;256selfcyclealiaspatternswithfinite65536hopbudget. Fullactorpayloadpreservedexcept2toggleflags. Originaldisjointbranchesreviewed,notROMexecution.",\n  "scope": "Local signedindex/read and typedstate domains:explicitD4byteoffset0/2/4/6 mappedtofourbranches, validA0metadatawordreads, readableflagwindow. OriginalcallerreachableD4domain remainsunproved; this doesnotresolveglobaluncertaincontrolflow. Actorlinksvalidnativepool, finiteWORDbudget; CPUCCR/registerhighhalves external. PlanedimensionspreserveoriginalbothglobalsD0assignment,notinferredwidth/heightcorrection. NotSDLorwholemapfidelity."\n}')
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
