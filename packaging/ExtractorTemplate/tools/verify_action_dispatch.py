"""Original full action dispatch/release and type4 action path local API."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/action-dispatch-verification-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['7A66']==983040
sources=['src/core/player_input_phase.hpp','src/core/rolo_action.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/action_dispatch_verification_tests.cpp'];exe=root/'work/action_dispatch_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
at=0x7a66;items=[]
while at<0x7b74:
 assert at in accepted
 i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x7b74
record=dict(address=0x7a66,hex='007A66',end_exclusive=0x7b74,original_bytes=rom[0x7a66:0x7b74].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player action dispatch and type4 action',native_sources=['src/core/player_input_phase.hpp','src/core/rolo_action.hpp'],checked_cases=983040,contract='Clearincoming125bit3. Mappedaction routescontrolledtype4 toguardedbasepress,8/16 tocompanions,othersreturn. Unpressed type8controlled53clearstate126bit1/70whenoldbitset. Releasechangesliveactor tobase; clearbase52andconditional72FFFF/LONG106clear. Type4C520/C487guards beforebasehandoff; headmode/global/strength/capture/timer/headselector gatespreserveBYTEsumwrap andordered23/56soundrequests.',proof='All256headmodeBYTEs and256combinedglobal/actorflagpartitions across5typecases and3mappedactionpartitions. Independentfull48actor-record oracle,soundsequence,companionrequesttype andservice-mutatedliveactorhandoff. Companionserviceeffects explicitlydelegated; live type8releaseintegration separatelypassed1572864cases.',scope='Local typed API withvalidstable distinctincoming/base/head actors, controlled==incoming fortype8 release, companioncallbacks andsoundeffects suppliedbyexplicitservices. Mappedinput producer, CPUregister/stack ABI, mismatchedactoraliases, deviceaudio andfullcompanioncallback/frame/lifetime remainexternal. Notwholeactionfeature fidelity.')
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/action-dispatch-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('7A66 full local action dispatch contract verified.')
