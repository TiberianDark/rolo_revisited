"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "actor_capture_phases",\n  "title": "actor capture and launch phase contracts",\n  "sources": [\n    "src/core/actor_capture_phases.hpp",\n    "tests/actor_capture_phases_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 393216\n  },\n  "cases": 393216,\n  "specs": [\n    {\n      "address": 61524,\n      "ranges": [\n        [\n          61524,\n          61528\n        ],\n        [\n          61536,\n          61666\n        ]\n      ],\n      "contract": "EF28entrylatchusesphase46+1;freezecontrolled,setoffsets/chainpriorities;YWORD+1signedtargetclamporF2FA/relocatecontrolled."\n    },\n    {\n      "address": 61528,\n      "ranges": [\n        [\n          61528,\n          61532\n        ],\n        [\n          61666,\n          61740\n        ]\n      ],\n      "contract": "Relocatecontrolledbeforelivefourthlinkedlookup;openoffsettoward32;secondlinkoffsettracksandthird/fourthhide;missingtargetoroffset32advancesphase."\n    },\n    {\n      "address": 61532,\n      "ranges": [\n        [\n          61532,\n          61536\n        ],\n        [\n          61740,\n          61844\n        ]\n      ],\n      "contract": "Unfreezeandlaunchcontrolledwith38000/65E00forcesandflags;resetphase/callbackF194;firsttwolinkedpriorities3AC8."\n    },\n    {\n      "address": 61858,\n      "ranges": [\n        [\n          61858,\n          61862\n        ],\n        [\n          61870,\n          62046\n        ]\n      ],\n      "contract": "Phaseentryrestorepriorities/hidetail;groundedcontrolledfullrectanglewithinplatform17px/34pxwindowfreezes,advancesphaseandstoresrelativeoffsets."\n    },\n    {\n      "address": 61862,\n      "ranges": [\n        [\n          61862,\n          61866\n        ],\n        [\n          62046,\n          62112\n        ]\n      ],\n      "contract": "Relocatecontrolled,closeoffsettowardFFF4andsettwochainpriorities32C8;missingtargetorcompletedoffsetadvancesphaseandsetsdrive100."\n    },\n    {\n      "address": 61866,\n      "ranges": [\n        [\n          61866,\n          61870\n        ],\n        [\n          62112,\n          62202\n        ]\n      ],\n      "contract": "Togglelinkedpair,accumulateLONGdriveintospeed,subtractspeedfrom16.16Y,drive+100signedupperclampF0000;negativeYzeroesandpublishestransition/reward/exitlatches;relocatecontrolledlast."\n    }\n  ],\n  "proof": "Originalfullboundaries/operandwidths/signedbranches/livechainreadsreviewed. Focused393216nativecasesover65536WORDseeds x6entries,all48actorrecordscomparedagainstindependentstateoracleplusseparateglobals. Finitechains0..7,phaseentry/unchanged,missinglinkednodes,offset32/FFF4withvalidlinks,grounded/un-groundedandrectangleinside/outside,signedY/clampandWORDwrapcovered. ExistingverifiedEF28/F362/F2FA/F31A/8F74helpersareactuallycomposed. Changedonlyfixturecoverageonceforvalidlinkedoffsetboundaries/independentgroundpartitionthenreranthatfamily.",\n  "scope": "Localvalidfinitechainswithdistinctcontrolled/platformactorsandstablepoolidentities. AllWORDseedpartitionsandreviewedmodularLONG/signedbranchformulae;notexhaustiveLONGcartesianproof. CPUregister/CCR/stackABI,hostsceneinit,graphicspublication/caller/runtimeintegrationexternal. Notwholeenemyorlevel fidelity."\n}')
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
