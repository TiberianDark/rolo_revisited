"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "actor_remaining_motion",\n  "title": "local contact dispatch parent parts and child emitters",\n  "sources": [\n    "src/core/actor_remaining_motion.hpp",\n    "tests/actor_remaining_motion_verification_tests.cpp",\n    "tests/remaining_actor_reference.hpp"\n  ],\n  "dependencies": [\n    "docs/stage9/actor-displacement-verification.json",\n    "docs/stage9/leaf-routine-verification.json"\n  ],\n  "results": {\n    "passed": true,\n    "state_cases": 4194304,\n    "boundary_cases": 196\n  },\n  "cases": 1048576,\n  "data_pins": [\n    [\n      58256,\n      "6000000e6000003c600000826000009c"\n    ],\n    [\n      60564,\n      "000fffe40024ffe4fff1ffe4ffdcffe40014ffdaffecffda0014ffff0029ffffffecffffffd7ffff0019fff6ffe7fff6"\n    ],\n    [\n      58106,\n      "ff0300000103"\n    ]\n  ],\n  "specs": [\n    {\n      "address": 58178,\n      "ranges": [\n        [\n          58178,\n          58256\n        ],\n        [\n          58376,\n          58378\n        ]\n      ],\n      "contract": "117gate;125bit6forcesselector8. Elsetrunk/decelerate/horizontal;wallbitsforce8;contactdirecthurtthen8. Selector8bypassesdispatch;otherstateszeroextend46BYTE*4selectfourpinnedtargetservices. Fourphasebodyimplementationsremainoutsidecallercontract."\n    },\n    {\n      "address": 60406,\n      "ranges": [\n        [\n          60406,\n          60564\n        ]\n      ],\n      "contract": "Contact/damage thenliveparentLONG46resolution. Signedparentphase<12copiestableoffsetintegerXY;phase4/timer>50toggles125bit1otherwiseclears. Otherparentphase:offscreenorsignedpartindex>3retires;otherwisegravity/integrate/snapshotverticalspeed/floor,clearoldgroundbitandifsetrestoresarithmetichalfspeed/up122FF. OriginalWORDindex*4wrap/signedROMaddressdatareads retained."\n    },\n    {\n      "address": 63982,\n      "ranges": [\n        [\n          63982,\n          64160\n        ]\n      ],\n      "contract": "VisitedC553retires. Mark125bit2;capD1literal60000 andincrement4000. BeforethirdchildpursueplayerX;afterthirdforceleft. Integrate;count<3timerdecrementorwrappedabsdistance<=32triggerreload100/incrementcountBEFORE1443Eallocate. ParentA5restoredonfailure/success;childB726/46FF/copiedliveparenthorizontalmotion. Failedallocationconsumescount."\n    },\n    {\n      "address": 57846,\n      "ranges": [\n        [\n          57846,\n          58094\n        ]\n      ],\n      "contract": "117/selector8gates;object/playercontact. Rowfarpatrolrate6/speed1/direction. Nearrowrate3,facesplayer;distance>=60reloads3<<16thensub1800untilnegativeemit. Emitselector8andup tothree14D8AattemptsD1counter2/1/0;A5NOTsaved,velocity/direction/speedBYTE59writes liveallocationreturnedA5. Failurebreaks; finalphysicsacts onliveA5."\n    }\n  ],\n  "proof": "One focused4194304fixture family overall65536statepatterns,16gate/contact/parent-selfalias/allocatorpartitions,fourentries. Independentrawgravity/integration/acceleration/stateoracle comparesalleightactorrecords,liveA5,fullretainedcontext,typedallocations andeveryserviceentrysnapshot.196explicitX/Ythresholdand8000signedwrapfixtures. E1F6returnedA5andF9EErestoredA5arecontrastedinactualallocationevents; failedspawnsretainoriginalcount mutations.",\n  "scope": "Local validactors,readableoriginalROMlookupwindow,validresolvedparentidentity andE342phaseBYTE0..3. Trunk/contact/damage/hurt/direction/horizontal/floor/allocator andfour E342targetbodies remain explicitservice contracts. Actualselectorproducer/parent-pointerancestry,retainedregistercontextandSDLadoptionremainexternal;noclaimwholeenemycompletion."\n}')
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
