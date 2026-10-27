"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "actor_phase_emitters",\n  "title": "local jumping and emission phase bodies",\n  "sources": [\n    "src/core/actor_phase_emitters.hpp",\n    "tests/actor_phase_emitters_verification_tests.cpp"\n  ],\n  "dependencies": [\n    "docs/stage9/actor-common-state-verification.json"\n  ],\n  "results": {\n    "passed": true,\n    "state_cases": 2097152\n  },\n  "cases": 1048576,\n  "data_pins": [\n    [\n      60920,\n      "ff0270000009000001027800000900000103000000040000ff03000000040000"\n    ],\n    [\n      61112,\n      "080000015274f0d400100000fffc10000001527418ec08000004fffc10000001527418f4040000040000100000015274180c0810000400040c0000015274f81c000000000004100800015274e8140818fffc0004100800015274e8f40408fffc0000100800015274e8ec0808fffcfffc"\n    ]\n  ],\n  "specs": [\n    {\n      "address": 60778,\n      "ranges": [\n        [\n          60778,\n          60782\n        ],\n        [\n          60816,\n          60920\n        ]\n      ],\n      "contract": "Forwarded actual ED90body. EF28phasechange invokes sound60 then liveBYTE53 selects oneof four8BYTEjump records;advanceindex8mod32,set122FF,121direction,58LONG24bitmagnitude,62LONG. Nochange plusgrounded advances46by4 andclearsXYfractions/velocities."\n    },\n    {\n      "address": 60782,\n      "ranges": [\n        [\n          60782,\n          60786\n        ],\n        [\n          60952,\n          61112\n        ]\n      ],\n      "contract": "Forwarded actual EE18body. Phasechangezeros51,sets52timer8;decrementBYTE includingnegativeunderflow. Emissionreload8,51==112resetsphase46. Eight14BYTErecords setparentselector/facingandspawnrequest;D2/D3EXT.WretainupperWORDs beforeSWAP. A5restoredonallocationfailure/success;childBYTE71/118/119andvelocityhighWORDs copied;successsound58;liveparent51increments14evenfailure. Timer<=4clearsselector70."\n    }\n  ],\n  "proof": "One focused2097152fixturegroup over65536statepatterns,16cache/ground/allocator/aliaspartitions andtwo actualforwardedbodies. Originaldatarecords pinned. Independentlyorderedmodelcomparesallfouractorrecords,liveparentidentity,fullretainedcontext,typedallocationrequests andeveryserviceentrysnapshot. Failedallocation stillconsumesrequest; successfulchildmayaliasparent; lastentry112resetcovered.",\n  "scope": "Local stablevalidactors,ED90index0/8/16/24 andEE18index0/14/.../112 withreadableimmutableoriginaltables. EF28nativehelperalreadycertified. RetainedD1,D2,D3contextismutableexplicitdata; actualproducerancestry,allocator/soundimplementation andliveSDLbindingremainexternal."\n}')
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
