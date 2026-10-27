"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "enemy_phase_entries",\n  "title": "enemy fall bob and burst phase contracts",\n  "sources": [\n    "src/core/enemy_phase_entries.hpp",\n    "tests/enemy_phase_entries_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 655680\n  },\n  "cases": 655680,\n  "specs": [\n    {\n      "address": 58256,\n      "ranges": [\n        [\n          58256,\n          58260\n        ],\n        [\n          58272,\n          58322\n        ]\n      ],\n      "contract": "FloorqueryatX/Y+59nonnegativeincrementsphasehighBYTE,gravity,signedupper50000forceclamp,integrate."\n    },\n    {\n      "address": 58260,\n      "ranges": [\n        [\n          58260,\n          58264\n        ],\n        [\n          58322,\n          58396\n        ]\n      ],\n      "contract": "Floorcontactservicefirst/liveactorstate;selector4,verticalforce4000/integrate;zero47negative122usesnativeRNG3..9store47/48;otherwiseBYTE47countdown0incrementsBYTE46andWORDtimer250."\n    },\n    {\n      "address": 58264,\n      "ranges": [\n        [\n          58264,\n          58268\n        ],\n        [\n          58396,\n          58426\n        ]\n      ],\n      "contract": "Gravity;negative122integratesandreturns;nonnegativeclears122/62andBYTEphase46increments."\n    },\n    {\n      "address": 58268,\n      "ranges": [\n        [\n          58268,\n          58272\n        ],\n        [\n          58426,\n          58472\n        ],\n        [\n          58376,\n          58378\n        ]\n      ],\n      "contract": "Integrate,clearLONG62;16entrysignedBYTEboboffsetindexedby(frame+BYTE48)&15;WORDtimerdecrementzerochangesselector8."\n    },\n    {\n      "address": 60036,\n      "ranges": [\n        [\n          60036,\n          60040\n        ],\n        [\n          60056,\n          60138\n        ]\n      ],\n      "contract": "PhaseWORD+4/selector4,6originaldefinition/bytepayloadspawns;allocationfailurescontinue;successfulchildparentLONG46,reverseindexWORD50,negative122andfourpayloadBYTEwrites."\n    },\n    {\n      "address": 60040,\n      "ranges": [\n        [\n          60040,\n          60044\n        ],\n        [\n          60186,\n          60234\n        ]\n      ],\n      "contract": "EBE4phaseentryinitializes100timer;frame&7zero requests53;WORDtimerdecrementnegativeadvancesphase."\n    },\n    {\n      "address": 60044,\n      "ranges": [\n        [\n          60044,\n          60048\n        ],\n        [\n          60234,\n          60314\n        ]\n      ],\n      "contract": "Phaseentrytimer25/counter4;counterbit0choosesselector0/4,changequeues21;negativeWORDtimerresets25/decrementsBYTEcounter,negativecounteradvancesphase."\n    },\n    {\n      "address": 60048,\n      "ranges": [\n        [\n          60048,\n          60052\n        ],\n        [\n          60318,\n          60360\n        ]\n      ],\n      "contract": "Phaseentryselector4/timer50/sound17;negativeWORDtimerdecrementadvancesphase."\n    }\n  ],\n  "data_pins": [\n    [\n      58472,\n      "00000100010100010000ff00ffff00ff"\n    ],\n    [\n      60138,\n      "000151a800000000000151ca0000000000015164ff03000600015186ff01000600015164010300060001518601010006"\n    ],\n    [\n      60314,\n      "00000004"\n    ]\n  ],\n  "proof": "Originalfullboundaries/literaldatareviewed. Focused655680nativecases:all65536WORDseeds xphasechanged/unchanged x3burststatesand4fall/bobstates;all64allocationfailuremaskscompareall48records;256newmutatingfloorcallbackfixturesverifyread-afterservice andactualnativeRNG. Thisnewcoveragechangedtestsource;recompiled/ransameoriginalpathlegitimately,passedwithoutpolicybypass. Componentgravity/force/integration/phase/RNGhelpersalreadyverifiedandactuallycomposed.",\n  "scope": "Validstableactoridentities,finiteoriginalspawnrecordsandtypedfloor/allocationservices. Floorservicecanmutateactorbeforecallerreadsit;spawnfixturesusevaliddistinctchildren/failure0. CPUtemporaryregister/CCR/stackABI/hostsceneoriginalreferenceandSDLadoptionexternal. Notwholeenemyfidelity."\n}')
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
