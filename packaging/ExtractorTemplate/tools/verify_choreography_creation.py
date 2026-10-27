"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "choreography_creation",\n  "title": "nine-actor choreography initialization contracts",\n  "sources": [\n    "src/core/choreography_creation.hpp",\n    "tests/choreography_creation_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 66048\n  },\n  "cases": 66048,\n  "specs": [\n    {\n      "address": 47738,\n      "ranges": [\n        [\n          47738,\n          47742\n        ],\n        [\n          48520,\n          48594\n        ]\n      ],\n      "contract": "IncrementheadphaseBYTE50/setdelay16;walk9livesourcechainnodes,allocateoriginalBE1AdefinitionateachLONGXYwithADDI.W16toYfractionONLY(nointegercarry);storeactualA4returnincluding0failure;successfulcallbackA84C."\n    },\n    {\n      "address": 47770,\n      "ranges": [\n        [\n          47770,\n          47774\n        ],\n        [\n          48014,\n          48106\n        ]\n      ],\n      "contract": "ThreeRNG0..6drawschooseoriginal12-bytetriplet;walk9linkedactors/storefullroster,WORD20index0..8,callbackBA9E,LONG46BE3E,LONG50selecteddefinition,BYTE54=16/55=3/WORD56=0."\n    }\n  ],\n  "data_pins": [\n    [\n      48666,\n      "0001443e000143940001446000014394000144600001443e000144600001443e00014394"\n    ],\n    [\n      48106,\n      "00014460000143940001443e0001443e000143940001446000014394000144600001443e0001443e0001446000014394000143940001443e00014460000144600001443e00014394"\n    ]\n  ],\n  "proof": "Fulloriginalboundaries/WORDfractionaddition/livechain/RNGtableandfailurestoresreviewed. Focused66048nativecases:all65536RNGseedscompare3draw/9actorstateagainstindependentRNGandactualROMtriplets;all512allocationgraphicsfailuremasksusingactualnativeallocator/originaldefinitions,all48records/freestack/roster/callbackschecked. FractionFFF0+16wrapverifiedwithoutintegercarry.",\n  "scope": "Valid9-nodefiniteactorchainswithsourcesexcludedfromfreepool,immutableoriginaltablesandstableallocationservices. Allocatorstatus/partialstatecomposedfromverifiednativeallocator;CPUA5return/MOVEM/CCRABI/globalrosterpublicationandSDLsceneadoptionexternal. Notwholechoreographyfidelity."\n}')
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
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: '+CONFIG['title'],native_sources=spec.get('native_sources',[CONFIG['sources'][0]]),checked_cases=spec.get('cases',CONFIG['cases']),contract=spec['contract'],proof=CONFIG['proof'],scope=spec.get('scope',CONFIG['scope'])))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/('docs/stage9/'+slug+'-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(str(len(records))+' local contracts registered: '+slug)
