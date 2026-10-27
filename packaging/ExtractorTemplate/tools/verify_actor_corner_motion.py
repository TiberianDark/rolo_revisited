"""Eight related corner-travel callbacks and their boundary/count mutations."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-corner-motion-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));names=['F75C','F776','F792','F7AE','F6B4','F6B8','F6BC','F6C0'];assert r==dict(passed=True,**{k:524288 for k in names})
sources=['src/core/actor_corner_motion.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/actor_corner_motion_verification_tests.cpp'];exe=root/'work/actor_corner_motion_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xf75c,[(0xf75c,0xf776)],'Floor query currentXY; failure sets119.4 and decrements parent50 BYTE. Found retains all state.'),(0xf776,[(0xf776,0xf792)],'Signed X<=16 sets119.3, clears118.3 and decrements parent50 BYTE.'),(0xf792,[(0xf792,0xf7ae)],'Signed X>304 clears119.3, sets118.3 and decrements parent50 BYTE.'),(0xf7ae,[(0xf7ae,0xf7c4)],'Signed Y<=16 clears119.4 and decrements parent50 BYTE.'),(0xf6b4,[(0xf6b4,0xf6b8),(0xf6c4,0xf6ea)],'Floor boundary then Y+15 only when119.4clear; left boundary then X-15 only when119.3clear.'),(0xf6b8,[(0xf6b8,0xf6bc),(0xf734,0xf75c)],'Floor boundary then Y+15 only when119.4clear; right boundary then X+15 only when119.3set.'),(0xf6bc,[(0xf6bc,0xf6c0),(0xf6ea,0xf710)],'Top boundary then Y-15 only when119.4set; left boundary then X-15 only when119.3clear.'),(0xf6c0,[(0xf6c0,0xf6c4),(0xf710,0xf736)],'Top boundary then Y-15 only when119.4set; right boundary then X+15 only when119.3set.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,original_bytes=rom[start:max(b for a,b in ranges)].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local corner motion',native_sources=[sources[0]],checked_cases=524288,contract=contract+' All integer movement wraps WORD and retains fractions; vertical boundary/move precedes horizontal boundary/move.',proof='All65536 WORD XY patterns across4 immutable terrain fixtures and2 actor/parent alias cases, every BYTEflag/counter value. Independent raw floor ring/descriptor/profile reference and signed boundary arithmetic; compare both complete130byte records for each of8 entries. Includes empty/solid/flipped/profile-rejected terrain and F268wrap. No passed batch repeated.',scope='Local valid immutable terrain and caller-provided A4 parent/A5 actor identities, including self-alias. Child floor query separately green; this batch also independently checks raw query effects. New native callback family available for later state/caller binding, not a complete playable object/animation certificate.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-corner-motion-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Eight corner-motion contracts verified.')
