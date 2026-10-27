"""Companion controlled-actor selection and normal menu frame-state contracts."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/menu-control-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,**{'20A2':524288,'1E44':524288})
header=(p/'src/core/level1_object_data.hpp').read_text(encoding='utf-8');m=re.search(r'companion_menu_navigation\{\{(.*?)\}\};',header,re.S);assert bytes(map(int,re.findall(r'\d+',m[1])))==rom[0x2224:0x223c]
sources=['src/core/level1_companion_selection.hpp','src/core/level1_companion_menu.hpp','src/core/level1_object_data.hpp','src/core/actor_chain_flag.hpp','src/core/actor_state.hpp','tests/menu_control_verification_tests.cpp'];exe=root/'work/menu_control_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
for start,ranges,contract,scope in [(0x20a2,[(0x20a2,0x20f0)],'Restore old46/50 LONGs first, then save next work LONGs (old/next alias reads restored data). Read new definition type, publish controlled identity and A84C callback, then clear blink through base linked chain.','Local nonzero valid old/next/base identities and finite acyclic chain; immutable definition lookup, five-actor identity aliases and allWORDtypes. Full menu choice admission, arbitrary definition services and actor control gameplay remain external.'),(0x1e44,[(0x1e44,0x1f6c),(0x1f84,0x1f98)],'Opening slide BYTE increments until28; palette ready once. Fresh input=physical AND previous complement, original priority Start/actions/directions. Navigation uses exact24byte table only when ready, rejects negative entries; action sound, choice and close/accept order. Start on exit choice waits input release before exit publication.','Local normal menu frame-state contract, selectors0..5 and original debug/cheat gate C48A!=65. Input stable during services; palette/slide/choice/accept/exit are observable handoffs. Cooperative exit_wait represents original busy-wait across input frames; does not claim literal same CPU call/interrupt scheduling. Begin publication and special223C cheats/queues/graphics remain external.')]:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,original_bytes=rom[start:max(b for a,b in ranges)].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local companion menu/control',native_sources=sources[:2],checked_cases=524288,contract=contract,proof='Selection: allWORD type/work/position patterns and8 old/next/base identity variants, compare all48 records, saved fields, type/key and lookup observation. Menu: all65536 pressed/previous BYTE pairs with8 open/ready/closing/selection-result fixtures; compare full state and ordered events. Sound service can mutate selected item before later reads. Exact original navigation bytes independently pinned. Already green finite-chain blink helper reused as child; actual selection record writes independently modeled.',scope=scope))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/menu-control-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('20A2 and normal1E44 local contracts verified.')
