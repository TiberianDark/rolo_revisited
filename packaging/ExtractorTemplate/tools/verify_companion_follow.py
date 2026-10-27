"""Companion terrain follow and grounded history-copy caller contracts."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/companion-follow-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'ACCE':524288,'AB28':524288}
sources=['src/core/level1_companion_motion.hpp','src/core/level1_companions.hpp','src/core/actor_motion.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/companion_follow_verification_tests.cpp','tests/companion_motion_fixture.hpp'];exe=root/'work/companion_follow_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
assert rom[13]==0
for start,end,contract in [(0xacce,0xadd0,'Signed height tiers (-8 and0), radius latch consumption, forward floor retry or stop, facing-only wall branch for -7..-1, airborne history and132pixel jump admission.'),(0xab28,0xac34,'Ground mirror before history decision; live short-circuit global gates; signed wrapped distance and prior XY equality. Copy only specified fields, absolute ROM byte13 to120; optional collision. Inactive restore or gravity/follow/integrate/horizontal/ceiling/land fallback; selector only when46.3clear.') ]:
 at=start;items=[]
 while at<end:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 ranges=[(start,end)]
 if start==0xab28:
  at=0xacac;ranges.append((0xacac,0xacce))
  while at<0xacce:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==0xacce
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: local companion follow',native_sources=[sources[0]],checked_cases=524288,contract=contract,proof='524288 independently branched caller cases each: all flags, WORD Y and wrapped X patterns, all signed height tiers/boundaries, radius/obstacle decisions, floor rings/profiles, matched/mismatched history and short-circuit services. Full48 actor records and ordered service observations compared. Previously verified child motion/follow-speed/probe/jump/mirror/selector used as child contracts, not re-certified. Native ACCE near-height wall correction specifically differs from prior clear-speed behaviour.',scope='Local caller state contracts, valid aligned history records and immutable terrain extents; stable controlled identity throughout. Horizontal/landing/inactive services are explicit handoffs with observed mutations. Full inactive routine, collision service internals and scene admission remain external.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/companion-follow-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('ACCE/AB28 verified.')
