"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/anchor-follow-offset-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,offset_cases=524288)
sources=['src/core/actor_anchor_follow.hpp','src/core/actor_anchor_steps.hpp','src/core/actor_motion.hpp','src/core/actor_state.hpp','tests/anchor_follow_offset_verification_tests.cpp'];exe=root/'work/anchor_follow_offset_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xe02c,[(0xe02c,0xe094)],'Full input offset WORD is added to controlled integer X. Clear121,copyhorizontalLONG58; nonnegativecontrolled122also copies122/verticalLONG62. Gravity,integration,floor; query8680atliveX,Y-16. NonnegativefloorresultclampsintegerY. Selector0/4fromliveX/cache20,updatecache,ORgroundbitinto livecontrolled124.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor displacement contract'),native_sources=[sources[0]],checked_cases=524288,contract=contract,proof='One new focused directentrycheck acrossall65536offsetWORDs and8alias/flagpartitions. Independentfull130BYTErecordmodel comparesactor/controlled,allserviceentrysnapshots,querycoordinates,negative/nonnegativefloorstatus andretainedfractions. Existingwrapperproofs unchanged; this new group closes the full offset parameter domain instead of retesting only plus/minus10.',scope='Local valid stable actor/controlled identities, including selfalias, andexplicit mutable gravity/integration/landing/floor services. CPU scratch/CCR represented by typed results. Actual caller binding and terrain service fidelity remain separate.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/anchor-follow-offset-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('E02C full-WORD offset contract verified.')
