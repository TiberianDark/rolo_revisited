"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "companion_entry_contracts",\n  "title": "local companion history presentation and detached entries",\n  "sources": [\n    "src/core/companion_entry_contracts.hpp",\n    "tests/companion_entry_contracts_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "state_cases": 3145728\n  },\n  "cases": 1048576,\n  "data_pins": [\n    [\n      13,\n      "00"\n    ]\n  ],\n  "specs": [\n    {\n      "address": 43086,\n      "ranges": [\n        [\n          43086,\n          43196\n        ]\n      ],\n      "contract": "WaitingA8BC service before liveC513 signedverticalcap10000. Snapshot controlled/action/hit1/hit2 after waiting. Temporarily controlled=base andthreeBYTESzero for8838; restore hit2,hit1,action,controlled in original order. Otherpresentationmutations retained."\n    },\n    {\n      "address": 44540,\n      "ranges": [\n        [\n          44540,\n          44678\n        ]\n      ],\n      "contract": "Snapshotcontrolled; set46bit0 before first-entrytest. Initialize52/groundflags/directioncontrolled121XORFE/facing. SpeedhighWORD=controlled58+2,signedcap15,retainsfraction.124bit4bypass. Wallstuck comparesold52/liveX;changedpositionjumpservice;unchangedpositionnegates121/togglesfacingthen tests124mask81==80forjump."\n    },\n    {\n      "address": 43836,\n      "ranges": [\n        [\n          43836,\n          44084\n        ],\n        [\n          44204,\n          44238\n        ]\n      ],\n      "contract": "Direct entry clears46bit3, capturesdefinition/controlled, computescurrent/priorhistoryindices. Gates/radius/savedXY authorize exacthistorycopy; BYTE120readsabsoluteROM0D,notrecord13;clearsgroundsupportbit5 thenmirror andconditionalwallservice. FallbackinactiveB058 receivesexact retainedD2:incoming orpriorX/priorY dependinglastcomparison; activeorderedgravity,follow,integrate,horizontal,ceiling,land."\n    }\n  ],\n  "proof": "One focused3145728fixture batch across65536statepatterns,16identity/flagpartitions,threeentrycontracts. Independentlyorderedraw-byte model comparesallthreecompleteactorrecords,globaltransaction,liveA5and every service-entrysnapshot. Historycases coverall1024maskedindices,copyeligibility/mismatchpaths,retainedD2andoriginalabsoluteROMbyte. Detachedentry includescontrolledselfalias,signedspeedwrapandstuck/jumpgates.",\n  "scope": "Localvalidactoridentities,readablehistoryextentthrougheveryqueriedfield andnonoverlappinghistory/actorstorage. OriginalROM0D pinned0; nativeviewpermitsdata-onlybyteparameter for verification. Waiting/presentation andhistoryfallback/mirror/jump services explicit; actualcallerindexalignment,adjacentRAMstorage,fullservicefidelity andSDLintegration remainexternal. Historyfallback services preserve capturedcontrolledidentity/definition context as their original calling contract requires."\n}')
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
