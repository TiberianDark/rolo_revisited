"""Original Rolo side collision on stable bounded populated terrain."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/player-wall-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['827A']==4194304
sources=['src/core/player_side_collision.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/wall_terrain_fixture.hpp','tests/player_wall_verification_tests.cpp'];exe=root/'work/player_wall_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
at=0x827a;items=[]
while at<0x8376:
 assert at in accepted
 i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x8376
record=dict(address=0x827a,hex='00827A',end_exclusive=0x8376,original_bytes=rom[0x827a:0x8376].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player side collision',native_sources=['src/core/player_side_collision.hpp'],checked_cases=4194304,contract='Clear124bits1/2; reachWORD58+62+1 wraps. Direction121 selectsleft/right; zero triesleftthenrightunlessleftbitset. FirstX+/-8probe compares signedreachwithwrappeddistance towall+/-8. FallbackoppositeX+/-8 usesunsignedpositionbound. ContactwritesX, clearsfraction14,direction121andLONG58,setssidebit; otherfields retained.',proof='All65536horizontalreachWORDS acrossfourverticalspeedpartitions,fourdirections andfourheterogeneousterrain/mirror/profile/shiftfixtures; independentrawprobe andsigned/unsignedacceptanceoracle comparesall130bytes. Completeoriginalspanincludingbothfallbacks reviewed/pinned; wallprobesseparatelycertified.',scope='Local validstableimmutableterrain andactorfieldAPI. Terrainstreaming/publication/frameownership/calleraliases andCPUtemporaryregister/CCR/ABI remainexternal; nofullplayercollision/lifecyclecertificate.')
dep='docs/stage9/wall-probe-verification.json';report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/player-wall-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('827A local populated-terrain side collision verified.')
