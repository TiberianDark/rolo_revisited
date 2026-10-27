"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "companion_return_entries",\n  "title": "companion return and literal entry contracts",\n  "sources": [\n    "src/core/companion_return_entries.hpp",\n    "tests/companion_return_entries_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 12288\n  },\n  "cases": 12288,\n  "specs": [\n    {\n      "address": 8334,\n      "ranges": [\n        [\n          8334,\n          8354\n        ]\n      ],\n      "contract": "ClearactionC510, composeverified20A2withlivebasekey, typednormalreturn."\n    },\n    {\n      "address": 8056,\n      "ranges": [\n        [\n          8056,\n          8060\n        ],\n        [\n          8088,\n          8114\n        ]\n      ],\n      "contract": "Returnbasectrl, setfollowmode0, composeB1A8callbackAB28, normalreturn."\n    },\n    {\n      "address": 8060,\n      "ranges": [\n        [\n          8060,\n          8064\n        ],\n        [\n          8114,\n          8142\n        ]\n      ],\n      "contract": "Returnbasectrl, setfollowmode1, composeB1A8callbackAA4A, normalreturn."\n    },\n    {\n      "address": 38498,\n      "ranges": [\n        [\n          38498,\n          38502\n        ],\n        [\n          8088,\n          8114\n        ]\n      ],\n      "contract": "OriginalBRAaliasofgroundfollowreturn1F98, samecomposedstatecontract."\n    },\n    {\n      "address": 38502,\n      "ranges": [\n        [\n          38502,\n          38506\n        ],\n        [\n          8114,\n          8142\n        ]\n      ],\n      "contract": "OriginalBRAaliasoffreefollowreturn1FB2, samecomposedstatecontract."\n    },\n    {\n      "address": 8064,\n      "ranges": [\n        [\n          8064,\n          8068\n        ],\n        [\n          7920,\n          7922\n        ]\n      ],\n      "contract": "LiteralbranchtoRTS, noactor/companionship/globalmutation."\n    },\n    {\n      "address": 33834,\n      "ranges": [\n        [\n          33834,\n          33836\n        ]\n      ],\n      "contract": "LiteralRTS actorcontrolentry, no state mutation."\n    }\n  ],\n  "proof": "RevieweddisjointoriginalBRAaliasesandbodyboundaries. Onepassednative12288cases:256action/actorbytepatterns,8companionrosters,oldcontrolledbasealias/nonalias,3return/followentries;all48x130actorbytescompared toindependentfieldoracle, savedworkrestore/captureand2actorbasechainblinkclear checked. Original20A2/B1A8native helperscomposed, notserviceplaceholder. Compilefixtureimmutabledefinition setter correctedbeforefirstrun.",\n  "scope": "Local validnativepool, basechainfinite, companionsvalid,definitiontype4. Originaloutermenu/interrupt/transitiondispatch andabsoluteCPUregisterreturn0 notexposedbeyondtypednormalreturn; fullSDLfidelity separate. LiteralRTSentries proveonlynostatechanges, nottheircallers."\n}')
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
