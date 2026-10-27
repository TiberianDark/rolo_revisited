"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "ending_scene_entries",\n  "title": "ending scene state and service contracts",\n  "sources": [\n    "src/core/ending_scene_entries.hpp",\n    "tests/ending_scene_entries_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 164609\n  },\n  "cases": 164609,\n  "specs": [\n    {\n      "address": 39560,\n      "ranges": [\n        [\n          39560,\n          39618\n        ]\n      ],\n      "contract": "Initcomplete-endingifhookdiffers, steptextstrip; onlynegativetextsourceandbusywaitrelease triggerfadeblack/state15AA."\n    },\n    {\n      "address": 39618,\n      "ranges": [\n        [\n          39618,\n          39732\n        ]\n      ],\n      "contract": "Hook9A88, orderedplane/palette/font/displayservices, source13A10;clearONLYcursorlowWORD, setrow28/attributes2000/baseC000/mask31/erase20,selectorFFFB/fadein/music3FFFF."\n    },\n    {\n      "address": 39732,\n      "ranges": [\n        [\n          39732,\n          39800\n        ]\n      ],\n      "contract": "Initpartial-endingifneeded;frameprefixreplay/drain/list/present/animate/render thenstrip; sourcezero triggersfadeblack/state15AA."\n    },\n    {\n      "address": 39800,\n      "ranges": [\n        [\n          39800,\n          39906\n        ]\n      ],\n      "contract": "Hook9B34,planeresets/font/palettejobC740/C60C/4B5AA,source13AE6,clearcursorlowWORDONLY,row28/attributesA000/baseC000/mask31/erase0."\n    },\n    {\n      "address": 39906,\n      "ranges": [\n        [\n          39906,\n          39956\n        ]\n      ],\n      "contract": "Initendingentranceifhookdiffers,frameprefixthenwalk,present/animate/render,endingstage."\n    },\n    {\n      "address": 39956,\n      "ranges": [\n        [\n          39956,\n          40054\n        ]\n      ],\n      "contract": "Hook9BE2,fade/resetqueues/planes/title/pools,endingactors,timer500/selectorFFFF/fadein/music16FFFF."\n    },\n    {\n      "address": 40054,\n      "ranges": [\n        [\n          40054,\n          40154\n        ]\n      ],\n      "contract": "Camera100/100; spawn1575E atFA0000/F10000 andretainA5tailtarget;spawn13ECCat1DE0000/F10000facingFF,bindA4headtothreeglobals,set126bit1."\n    },\n    {\n      "address": 40154,\n      "ranges": [\n        [\n          40154,\n          40200\n        ]\n      ],\n      "contract": "ControlledWORDXminus1signedclamp322,selector92andtargetBYTE46FFonarrival,else4; fractions/allunrelatedbytesretained."\n    },\n    {\n      "address": 40200,\n      "ranges": [\n        [\n          40200,\n          40406\n        ]\n      ],\n      "contract": "PositiveWORDtimerdecrements; admitted0/-1/-2selectpaletteinit/actorwait/completionstate nativehelpers viaoriginal4BYTEbranchtable."\n    },\n    {\n      "address": 40220,\n      "ranges": [\n        [\n          40220,\n          40224\n        ],\n        [\n          40232,\n          40346\n        ],\n        [\n          40398,\n          40406\n        ]\n      ],\n      "contract": "Fourordered16colour/rate0palettejobswithoriginalhandles/ROMtargets,thendecrementtimerWORD."\n    }\n  ],\n  "proof": "Staticbranch/WORD/BYTEstorewidths reviewedincludingcursorWORD-onlyclearandfirstspawnA5tailvssecondA4head. Focused164609nativecases:65536walkingWORDs/fullactors,65536cursorhighWORDpreservationpatterns/twosceneinits,all32768nonnegativestagetimers,256actorready/percenttextgatesbusybranches,originalfourpalettejobsandtwoallocrequests. InitialtestmissingActorPoolinclude correctedbeforefirstrun;passedonce. NoROMexecution.",\n  "scope": "Local typedsharedstate/sceneinvocationcontracts; render/font/palettejobcreation/allocator/music areexplicitserviceswithoriginalparameters, notfullendingart/devicefidelity. StagejumpdomainpositiveWORDor0/FFFF/FFFE;othernegativecallerselectorsremainunprovedandreject. Successfulvalidnativeallocatorresults/head/tailrequired; poolfailurecallerbehavioroutside. Busyrequiresfinitehostrelease. Existingverifiednativeendingcompletion/wait/sceneplanescomposed. NonewSDLbinding."\n}')
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
