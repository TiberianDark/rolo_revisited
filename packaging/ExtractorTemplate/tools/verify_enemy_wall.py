"""Complete CE14 local terrain collision API with CE22 and8488 request semantics."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/enemy-wall-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['CE14']==2097152
sources=['src/core/actor_horizontal_collision.hpp','src/core/player_side_collision.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/enemy_wall_verification_tests.cpp'];exe=root/'work/enemy_wall_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
ranges=[]
for start,end in [(0xce14,0xce22),(0xce22,0xceca),(0x8488,0x84f4)]:
 at=start;items=[]
 while at<end:
  assert at in accepted
  i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 ranges.append(dict(start=start,end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items))
record=dict(address=0xce14,hex='00CE14',end_exclusive=0xce22,original_bytes=rom[0xce14:0xce22].hex(),instruction_evidence=ranges[0]['instruction_evidence'],joined_original_ranges=ranges,verification_status='verified',status='verified green: local enemy horizontal terrain collision',native_sources=['src/core/actor_horizontal_collision.hpp'],checked_cases=2097152,contract='Clear124bits1/2. CE22onlywhen117zeroand121nonzero; unsignedwrappedreach58+1 bounds firstprobeX+/-16 thenfallbackX. Acceptedprobe writesX+/-1, clearsfraction14,setssidebit. Always8488followup atX+/-8,Y-height withF268shift; solidtile side-shape1 snapsalignedX+23/-8 andsetssidebit, retainingfraction14.',proof='All65536reachWORDs acrossfourdirectionpartitions,two117gatepartitions,fourheterogeneousterrainfixtures withempty/solid/mirrored/profile-rejected cells andF268wrap. Independentrawterrain/profile/unsignedacceptanceoracle comparesall130actorbytes. FullCE14/CE22/8488 originalranges reviewed andpinned; typedprobehelpers separatelycertified.',scope='Local stablevalidimmutable terrain API andnativeactorfieldstate; ROMstreaming/publication/identity, sharedframe/caller ownership andCPUtemporaryregister/CCR/ABI remainexternal. Populatedterrain included; notwholeenemybehaviour orfulllevelcollisioncertificate.')
deps=['docs/stage9/wall-probe-verification.json'];report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+deps},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/enemy-wall-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('CE14 populated-terrain local collision contract verified.')
