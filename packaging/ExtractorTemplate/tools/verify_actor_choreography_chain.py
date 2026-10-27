"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "actor_choreography_chain",\n  "title": "nine actor choreography and roster phases",\n  "sources": [\n    "src/core/actor_choreography_chain.hpp",\n    "tests/actor_choreography_chain_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 327680\n  },\n  "cases": 327680,\n  "specs": [\n    {\n      "address": 47734,\n      "ranges": [\n        [\n          47734,\n          47738\n        ],\n        [\n          48594,\n          48636\n        ]\n      ],\n      "contract": "TickBYTE51/phase50 then9forwardlinks applysignedoriginalBE08positionWORDoffsets."\n    },\n    {\n      "address": 47766,\n      "ranges": [\n        [\n          47766,\n          47770\n        ],\n        [\n          48594,\n          48636\n        ]\n      ],\n      "contract": "OriginalBRAaliasBDD2, same9nodepositiveoffsetmove."\n    },\n    {\n      "address": 47758,\n      "ranges": [\n        [\n          47758,\n          47762\n        ],\n        [\n          48336,\n          48394\n        ]\n      ],\n      "contract": "TickBYTE51;zero incrementsphase50andsets52/53=1;9chainnodesnegateoriginalsignedBYTEoffsetsthenWORDpositionadd."\n    },\n    {\n      "address": 47750,\n      "ranges": [\n        [\n          47750,\n          47754\n        ],\n        [\n          48428,\n          48462\n        ]\n      ],\n      "contract": "TickBYTE51andoptionalphase50advance, then9liverosterslotsnonnullincrementYWORD, repeatedaliasesretained."\n    },\n    {\n      "address": 47742,\n      "ranges": [\n        [\n          47742,\n          47746\n        ],\n        [\n          48480,\n          48520\n        ]\n      ],\n      "contract": "TickBYTE51;zero incrementsphase50andresets51=50;9nonnullrosterentriesdecrementYWORD."\n    },\n    {\n      "address": 47754,\n      "ranges": [\n        [\n          47754,\n          47758\n        ],\n        [\n          48394,\n          48428\n        ]\n      ],\n      "contract": "AdvancephaseBYTE50,set51=64,9livehandlesretireBYTE116=FF, zeroentriesignored."\n    },\n    {\n      "address": 47762,\n      "ranges": [\n        [\n          47762,\n          47766\n        ],\n        [\n          48178,\n          48336\n        ]\n      ],\n      "contract": "Walk8forwardthen8backcopying32/34;rootwavephase51*2,radius52;radius80negates53;nonzeroradiusadvance52andangle51+10;zeroradiusadvancephase,51=64andpropagate8children."\n    }\n  ],\n  "data_pins": [\n    [\n      48648,\n      "ffff00ff01ffff0000000100ff0100010101"\n    ]\n  ],\n  "proof": "Onefocusednative327680cases:65536phase/countWORDpatterns xpositive/negativeoffsetchainsandup/downrostersincludingduplicate/headaliases/nullslots;all256anglesx256radiusvalues withindependentoriginalsinetablehighWORDoracle,full48actorpayloadcomparisons. Originalslotsanddisjointbodiesreviewed,original18BYTEoffsettablepinned. NoROMexecution.",\n  "scope": "Local9validactorfinitechain,reverseparentchainmatchesforwardforrotation,9validornullrosterhandles (aliasesallowed). No spawner/resourceorouterbossdispatchclaim;waveusesalreadyverifiedCCF8nativehelper. Bytephase/timersandWORDpositionspreserved, notfullbossfidelity orSDLbinding."\n}')
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
