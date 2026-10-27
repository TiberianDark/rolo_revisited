"""Original shared collision orchestration and controlled-height restoration."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/collision-phase-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['785C']==589824
sources=['src/core/player_collision_phase.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/collision_phase_verification_tests.cpp'];exe=root/'work/collision_phase_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
at=0x785c;items=[]
while at<0x78b8:
 assert at in accepted
 i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x78b8
record=dict(address=0x785c,hex='00785C',end_exclusive=0x78b8,original_bytes=rom[0x785c:0x78b8].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local shared collision phase',native_sources=['src/core/player_collision_phase.hpp'],checked_cases=589824,contract='C524/F2BCnonzeroskip; controlled124bit5/125bit3skip. SaveWORD38; definitiontype20temporarilysetsheight32. Invoke8376/84F4/827A/842E/8482inorderwithmutableliveactor. Reloadcurrentcontrolledidentityafterhelpersandrestoreoriginalsavedheightthere, notnecessarilyinitialactor.',proof='All65536savedheights x2definitiontypepartitions x3live/controlidentityroutes; all65536actorflagBYTEpairs x3globalgatepartitions. Servicesmutateliveactor/height/controlidentitymidphase; independentorderedservice/handoffmodelcomparesall48actorrecords,sharedcontrolstateandevents includingheightatentry. Completeoriginalspanreviewed/pinned.',scope='Local typed validstableactor/definitionlookup andexplicitcollisionservice contracts. Physicalterrainquery effects, storage/streaming/publication, actualcallers/alias/CPUABI remainexternal; notfullterraincollision/framefidelity.')
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/collision-phase-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('785C local collision orchestration verified.')
