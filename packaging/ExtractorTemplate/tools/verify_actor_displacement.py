"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-displacement-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,cases_per_entry=1048576)
sources=['src/core/actor_displacement.hpp','src/core/actor_common_state.hpp','src/core/actor_allocation.hpp','src/core/actor_motion.hpp','src/core/actor_state.hpp','tests/actor_displacement_verification_tests.cpp'];exe=root/'work/actor_displacement_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xdd36,[(0xdd36,0xdd74)],'Zero anchor caches current integerX only. Otherwise position=anchor-scroll, selector0/4/8 and unsigned magnitude from wrapped subtraction N. Preserve fractional and unrelated fields.'),(0xc95a,[(0xc95a,0xc988)],'Add full LONG deltas, then publish wrapped integer displacement to velocity highWORDs58/62 including fraction carry; preserve velocity fractions.'),(0xbfe4,[(0xbfe4,0xbff8),(0xc988,0xc9ae)],'Negate only incomingD3lowWORD, SWAP fullLONG and invoke carrying body in original alias order. Restore/negate/double lowWORD, store lowBYTE52. Incoming highWORD retained.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor displacement contract'),native_sources=[sources[0]],checked_cases=1048576,contract=contract,proof='One focused native batch: all65536WORD inputs across16 fractional/zero/scroll/alias partitions. Independent arithmetic oracle compares all130actor bytes and controlled actor, including retained velocity fractions and D3highWORD.',scope='Local valid actor records and typed scalar inputs, including self/separate controlled identity. These helpers await caller binding; this proof does not certify their entire actors or Level1 fidelity. CPU scratch/CCR replaced by typed state effects.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-displacement-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three actor displacement contracts verified.')
