"""Supported original animation dispatch slots and typed control contracts."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/animation-extra-controls-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,**{x:262144 for x in ['FE70','FE74','FE78','FE7C','FE80','FE88','FE94','FE98']})
sources=['src/core/actor_animation.hpp','src/core/animation.hpp','src/core/actor_state.hpp','tests/animation_extra_controls_verification_tests.cpp'];exe=root/'work/animation_extra_controls_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));entries={x['address'] for x in inv['routines']};accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0xfe70,0xffee,0xfffa,'Clear freeze','Clear C524 BYTE then continue next record.'),(0xfe74,0xfffa,0x10016,'Counted jump','Existing nonzero128 decrements; zero result advances8, otherwise jumps. Initial zero reloads operand lowBYTE and jumps even if reload zero.'),(0xfe78,0x10016,0x10020,'Set selector','Write full operandWORD70 and return immediately without publishing current frame.'),(0xfe7c,0x10020,0x1003e,'Repeat airborne','Repeat previous frame with114zero while124bit0clear; otherwise restore115andadvance.'),(0xfe80,0x1003e,0x1005c,'Repeat grounded','Repeat previous frame with114zero while124bit0set; otherwise restore115andadvance.'),(0xfe88,0x1009c,0x100a2,'Skip','Advance4 and continue next record.'),(0xfe94,0x10134,0x10140,'Set blink','Set125bit1 preserving all other bits and continue.'),(0xfe98,0x10140,0x1014c,'Clear blink','Clear125bit1 preserving all other bits and continue.')]
for slot,start,end,name,contract in specs:
 assert slot in entries
 items=[];ranges=[]
 for lo,hi in [(slot,slot+4),(start,end)]:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi;ranges.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 records.append(dict(address=slot,hex=f'{slot:06X}',end_exclusive=slot+4,original_bytes=rom[slot:slot+4].hex(),instruction_evidence=items,code_ranges=ranges,verification_status='verified',status='verified green: local animation control '+name,native_sources=['src/core/actor_animation.hpp'],checked_cases=262144,contract=contract,proof='Eight controls each checked across65536operandWORDs and four prior counter partitions, comparing all130actor bytes and external freeze byte against independent command/frame oracle. Original slot and complete target instruction boundaries reviewed.',scope='Local immutable valid predecoded graphs, unchanged selector entry and underflow-triggered timer. Includes control target semantics and frame continuation; selector decoder, exporter admission, external world bindings and full animation pipeline remain outside this proof.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/animation-extra-controls-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Eight extra animation control contracts verified.')
