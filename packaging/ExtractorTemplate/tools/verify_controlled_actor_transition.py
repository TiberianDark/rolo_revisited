"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "controlled_actor_transition",\n  "title": "local controlled identity transition and preparation contracts",\n  "sources": [\n    "src/core/controlled_actor_transition.hpp",\n    "tests/controlled_actor_transition_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "state_cases": 524288\n  },\n  "cases": 524288,\n  "data_pins": [\n    [\n      38498,\n      "600089346000894a"\n    ]\n  ],\n  "specs": [\n    {\n      "address": 38466,\n      "ranges": [\n        [\n          38466,\n          38498\n        ],\n        [\n          38506,\n          38598\n        ]\n      ],\n      "contract": "Fade black first; save live controlled actor after fade; BYTEC50F0/1 dispatches two original initializers. Restore old liveA5,set116FF/125bit2, then exact eleven ordered continuation services. DMA C9BC->F400,count140,command40000000 explicit; final fade-in then C51A/C516clear."\n    },\n    {\n      "address": 34832,\n      "ranges": [\n        [\n          34832,\n          34844\n        ]\n      ],\n      "contract": "Replace main state with1E20, no other native state changes."\n    },\n    {\n      "address": 16408,\n      "ranges": [\n        [\n          16408,\n          16416\n        ]\n      ],\n      "contract": "Ordered foreground preparation4020 then tail background preparation4030; both see live service mutations."\n    }\n  ],\n  "proof": "One focused524288fixture group covers65536statepatterns,eightidentity/initializationpartitions,fullthreeactorrecordsandallorderedserviceentrysnapshots. Fade can replace controlled identity before snapshot; initializer changes live/controlled; later services mutate identities andglobals. Exact typedtransferargumentschecked. Main-state leaf andtwo-plane ordering checked in same group. Transfer signature was made explicit before registration and only changed group rerun.",\n  "scope": "Local validstableactor identities and selector0/1 at postfade dispatch. Fade/init/retirement/graphics/camera/terrain/scroll/frame/sprite/DMA implementations and timing explicit external service contracts. Does not certify complete control switching, restart or rendering."\n}')
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
