"""Original type16 wall attachment in canonical controlled-actor identity domain."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/companion-wall-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['7CA8']==4194304
sources=['src/core/level2_actor_updates.hpp','src/core/player_side_collision.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/wall_terrain_fixture.hpp','tests/companion_wall_verification_tests.cpp'];exe=root/'work/companion_wall_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
at=0x7ca8;items=[]
while at<0x7d3a:
 assert at in accepted
 i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x7d3a
record=dict(address=0x7ca8,hex='007CA8',end_exclusive=0x7d3a,original_bytes=rom[0x7ca8:0x7d3a].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local type16 wall attachment',native_sources=['src/core/level2_actor_updates.hpp'],checked_cases=4194304,contract='GateincomingA5negative122. ResolvecontrolledC4E0; facing118bit3selectsleft/rightprobeX+/-8 withfallbackX+/-24,Y-8. Targetwall+/-8 musthavewrappedsigneddistance0..2. WriteXinteger only, set125bit3,124maskAFthenbit0, clear122andLONG62; retainXfraction14.',proof='All65536Xwords acrossfourfacing/fourdirectionpartitions/fourheterogeneousterrain/mirror/profile/shiftfixtures; rawterrain/probeoracle andall130bytescompared. Completeoriginalrange andbothsigneddistanceguards reviewed; validdistance0..2 equivalenttounsigneddistance<=2. Sharedwallprobesseparatelycertified.',scope='Local typed canonicaldomainincomingA5==controlledC4E0, stablevalidterrain. Incomingactor/controlidentitymismatch, terrainstreaming/publication, frame/caller aliases andCPUABIremainexternal; notfullcompanionaction/lifecyclecertificate.')
dep='docs/stage9/wall-probe-verification.json';report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/companion-wall-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('7CA8 local controlled companion attachment verified.')
