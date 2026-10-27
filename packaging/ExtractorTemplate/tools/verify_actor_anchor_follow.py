"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-anchor-follow-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,follow_cases=524288,placement_cases=524288)
sources=['src/core/actor_anchor_follow.hpp','src/core/actor_anchor_steps.hpp','src/core/actor_motion.hpp','src/core/actor_state.hpp','tests/actor_anchor_follow_verification_tests.cpp'];exe=root/'work/actor_anchor_follow_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xdffe,[(0xdffe,0xe014),(0xe02c,0xe094)],'Offset controlledX by-10 through fullE02C body, then store live final integerXY to first anchor.'),(0xe014,[(0xe014,0xe094)],'Offset controlledX by+10 through fullE02C body, then store live final integerXY to second anchor.'),(0xe094,[(0xe094,0xe0a4),(0xe0b4,0xe0c2)],'Load first anchor pair and place integerXY withY-22, preserving fractions.'),(0xe0a4,[(0xe0a4,0xe0c2)],'Load second anchor pair and place integerXY withY-22, preserving fractions.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor anchor follow contract'),native_sources=[sources[0]],checked_cases=262144,contract=contract,proof='One focused batch:65536WORD values across8 alias/direction/wrapper partitions. Full actor and controlled records, anchor pairs, every service-entry snapshot and floor query arguments checked. Includes signed floor status boundary, retained fractions, live alias, gravity/integration/landing mutation order and selector cache.',scope='Local wrapper and target composition with gravity/integration/landing/floor represented by typed ordered services. Includes full target control flow; service implementations, terrain admission, actual gameplay callback binding and CPU scratch ABI remain external. Placement is complete local integer-coordinate contract.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-anchor-follow-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Four anchor wrapper contracts verified.')
