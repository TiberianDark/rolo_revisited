"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "macro_reward_entries",\n  "title": "local breakable macro and rising reward family",\n  "sources": [\n    "src/core/macro_reward_entries.hpp",\n    "tests/macro_reward_entries_verification_tests.cpp"\n  ],\n  "dependencies": [\n    "docs/stage9/leaf-routine-verification.json",\n    "docs/stage9/random-range-verification.json"\n  ],\n  "results": {\n    "passed": true,\n    "state_cases": 4194304,\n    "wrap_cases": 8,\n    "boundary_cases": 100\n  },\n  "cases": 1048576,\n  "data_pins": [\n    [\n      47564,\n      "00014130000141b800014262000142ea00014394000143b6000143d80001441c0001443e00014130000141b800014262000142ea00014394000142ea00014262000141b800014130"\n    ],\n    [\n      47710,\n      "ff01ff01ff01"\n    ],\n    [\n      48004,\n      "0000000c0c0c18181800"\n    ]\n  ],\n  "specs": [\n    {\n      "address": 47114,\n      "ranges": [\n        [\n          47114,\n          47342\n        ]\n      ],\n      "contract": "Zero56activationrequiresattachment/upwardcontrolledmotion/signedYgate. Captureanchor/verticalspeed thenstopcontrolledY; allocationlooppreservesparentA5,setschildcallbackbydefinitionflag,onlysuccessdecrementsBYTE55(0wraps256). Physicsclampsatanchor,clearsfraction/verticalmotion/56;callbackB804and92zero;nonnegative54publishes93andrequestsactualmacrorefresh."\n    },\n    {\n      "address": 47342,\n      "ranges": [\n        [\n          47342,\n          47446\n        ]\n      ],\n      "contract": "First50BYTEinitializescollected0andtimer100. Signedcollected>=3movesintegerYup1unlesszero. OtherwiseBYTE52decrement usesborrow(old0),then signed53clamp<=40to41minus2reload;1474CspawnfullXYwithliveD1context. A5allocationresultnotrestored."\n    },\n    {\n      "address": 47446,\n      "ranges": [\n        [\n          47446,\n          47564\n        ],\n        [\n          47636,\n          47710\n        ]\n      ],\n      "contract": "First46 initializesrandomsixdirectionindexandhalf-pixel1..4speed,up8<<16. Groundedentrytests signedcollected>=3retirement. Activegravity/integrate/floor thennewgroundincrementsglobal;contactBYTE123triggersB7C0/selector4/46zeroandrandom17definitionallocationwithD1=17,fullXY,A5notrestored. SuccesschildcallbackB726."\n    },\n    {\n      "address": 47774,\n      "ranges": [\n        [\n          47774,\n          48004\n        ]\n      ],\n      "contract": "GroupedbreakableentryalsoexcludesBE46callbackmarker. Commonactivation/countloopusesB726only. Physicssettleclearsverticalstate;3groupselectors4whensettled. Everyactiveupdatewrites3groupLONG46=BE46. GroupoffsetusesROMBB84+signedWORD20 BYTE lookup preservingoriginalindexhighBYTE before signed addressaddition;validgroupresolutionexplicit."\n    }\n  ],\n  "proof": "One focused4194304fixture group overall65536patterns,16state/attachment/selfalias/failurepartitions,fourentries; independentrawgravity/integration/RNG/stateoraclecomparesallsixactorrecords,retainedcontext,allocationrequests,serviceentrysnapshots. Additional8fullysuccessfulloopcasescoverinitialBYTEcounts0/1/2/255including256attemptwrap;100explicitdirection/signedY/BE46gatecases addedbeforeadmission andonlychangedfamilyrerun. GrouplookuptestsallWORDindicesagainstpinnedROMdata;source53/52andglobalsignedBYTEbehaviourcovered.",\n  "scope": "Local validstableactors,finiteallocatorreturns,nonnullthreeactorresolvedgroupsandreadablemacrodefinitions. Actualallocator/collision/attachment/floor/contact/macrographicsrefreshandgroupidentityservices remainexternal. ROMlookupsaredatareads,neverCPUexecution. ActualWORD20producerdomain andD1resourceancestry,SDLintegration andfullbreakablerewardgameplayremainunclosed."\n}')
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
