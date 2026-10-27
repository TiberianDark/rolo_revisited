"""Sound animation control's exact command handoff and next-frame continuation."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/animation-sound-control-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'FE9C':65536}
sources=['src/core/actor_animation.hpp','src/core/animation.hpp','src/core/actor_state.hpp','tests/animation_sound_control_verification_tests.cpp'];exe=root/'work/animation_sound_control_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};items=[];ranges=[(0xfe9c,0xfea0),(0x1014c,0x1015a)]
for lo,hi in ranges:
 at=lo
 while at<hi:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==hi
record=dict(address=0xfe9c,hex='00FE9C',end_exclusive=0xfea0,code_ranges=ranges,original_bytes=rom[0xfe9c:0xfea0].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local animation sound control',native_sources=[sources[0]],checked_cases=65536,contract='Send full operandWORD to788AE native sound service before advancing one4byte control record; continueFD94 through next frame. Timer114 already reloaded from115; geometry/graphics published only after sound request.',proof='Every65536commandWORD checked. Service observes old102/graphics/geometry and reloaded114, then complete130byte final record compared to independent frame/facing/offset-protection model. Original branch slot and full target body reviewed, not a trampoline-only check.',scope='Local immutable valid predecoded control/frame graph, underflow-triggered update and unchangedselector. Sound request contract only: audio generation, mixer/driver implementation and device timing remain external; this does not certify sound fidelity.')
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/animation-sound-control-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('FE9C sound request control verified; audio generation remains external.')
