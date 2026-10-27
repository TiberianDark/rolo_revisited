"""Pin local injury branches and valid original phase tables; no ROM execution."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
result=root/'work/actor-phase-mechanism-results.json';r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,wave_cases=1048576,actor_cases=1572864)
sources=['src/core/actor_phase_mechanism.hpp','tests/actor_phase_mechanism_verification_tests.cpp'];pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
exe=root/'work/actor_phase_mechanism_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
assert rom[0xd554:0xd558]==bytes([100,100,100,194])
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xd4cc,[(0xd4cc,0xd554)],'Once per changed low frame BYTE: cache frame, F330=640. Completed bypasses phase. Else phase=(phase+2)&511; zero wraps quadrant, original amplitude table100/100/100/194 feeds certified CCF8 divisor1; integerX+448 writes F268. Sound61 when frame masked by3,or1for quadrant3,is zero.'),(0xd57e,[(0xd57e,0xd624)],'D4CC first; zero anchor captures integerX then D558 reset. Otherwise X=anchor-offset preserving fraction. Gates/third latch guard contact. Contact sets timer0 and gates8, then live selector4 latches completed before reveal/sceneallocation. Scene14E78 at2300000/2010000, zero context/facing/marker; afterward allfour gates1,timer0 even allocation changes liveA5.'),(0xd624,[(0xd624,0xd6c6)],'Shared wave and anchor. Gatezero contact may set gates8; live selector12 latches second and returns. Nonzero48 tailcalls D77C service. Otherwise quadrantnot3 and frame&127==63 select4/8 by signedwrapped actorY+34 vs controlledY-38.'),(0xd6c6,[(0xd6c6,0xd77a)],'Shared wave/anchor; gatezero and second latch enable contact, selector12 latches third. Nonzero48 tailcalls D77C. Otherwise quadrant3requiresoffset&FFF8==130; otherquadrantsrequireframe&127==0. Signedwrapped actorY+34-38 vs controlledY selects4/8.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),original_bytes=rom[start:max(b for a,b in ranges)].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: local shared phase mechanism contract',native_sources=[sources[0]],checked_cases=1048576 if start==0xd4cc else 524288,contract=contract,proof='One focused family run:1048576 wave fixtures across all input WORDs and16frame/phase partitions;1572864 actor fixtures compare all three complete actor records, globals, mutable service-entry snapshots and live A5. Independent wave integer formula and ordered branch oracle exercise wrap, contact result versus mutated selector, preserved fractions, signed comparison and initialization/reward bypasses.',scope='Local stable actor identities, valid original quadrant0..3 (or wrapped producer) and explicit contact/reveal/allocator/emitter/sound boundaries. D77C is not implemented or certified by its callers; retained allocation context is explicitly zero in these scene calls. CCF8 already certified native helper used within its admitted divisor1 domain. Actual caller/data production, SDL integration and original-reference scene comparison remain external.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/'docs/stage9/actor-phase-mechanism-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Four shared phase mechanism contracts verified.')
