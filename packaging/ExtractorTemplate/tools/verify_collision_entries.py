"""Separate CE22/8488 entries plus CE14 composition verification."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/collision-entries-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'CE14':2097152,'CE22':2097152,'8488':2097152}
sources=['src/core/actor_horizontal_collision.hpp','src/core/player_side_collision.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/collision_entries_verification_tests.cpp'];exe=root/'work/collision_entries_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
ranges=[]
for start,end in [(0xce14,0xce22),(0xce22,0xceca),(0x8488,0x84f4)]:
 at=start;items=[]
 while at<end:
  assert at in accepted
  i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 ranges.append(dict(start=start,end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items))
records=[]
for index,start in [(1,0xce22),(2,0x8488)]:
 original=ranges[index]
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=original['end_exclusive'],original_bytes=original['original_bytes'],instruction_evidence=original['instruction_evidence'],verification_status='verified',status='verified green: standalone collision entry',native_sources=[sources[0]],checked_cases=2097152,contract=('Standalone CE22 leaves side bits intact on entry. Status117/direction121 gates; first shifted-X then fallback probe, unsigned wrapped reach comparison. Accepted wall snaps X+/-1, clears only fraction14, sets relevant side bit.' if start==0xce22 else 'Standalone8488 always queries top corner, including stationary/inactive actors. Direction N selects X-8/+8 and side descriptor. F268 shift retained in snapped coordinate; solid shape1 snaps alignedX+23/-8, sets side bit and retains fraction14.'),proof='Independent raw terrain/profile oracle for each entry, separately from wrapper clears/followup. All65536 reach WORDs,4 direction partitions,2 inactive gates and4 heterogeneous fixtures. Complete130byte state comparison. Same focused executable also verifies CE14 composition on2097152cases, supporting unchanged-wrapper proof rebinding after helper extraction.',scope='Local immutable valid terrain data and stable actor record. No RAM/VDP publication timing, caller ownership or CPU scratch ABI claim. Existing wrapper behaviour reverified once because its implementation was refactored; no broader unrelated suites repeated.'))
deps=['docs/stage9/wall-probe-verification.json'];report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+deps},records=records,wrapper_reverification_cases=2097152,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/collision-entries-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('CE22/8488 verified; CE14 composition reverified.')
