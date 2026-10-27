"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/spawn-branch-family-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,cases_per_family=1048576,gate_cases=16777216)
sources=['src/core/spawn_branch_family.hpp','src/core/spawn_branch_data.hpp','src/core/actor_spawn_factory.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/spawn_branch_family_verification_tests.cpp','docs/stage9/bounce-spawn-verification.json'];exe=root/'work/spawn_branch_family_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources if not s.endswith('.json'))
import struct,re
header=(p/'src/core/spawn_branch_data.hpp').read_text(encoding='utf-8');tables=[]
for kind,address,count in [(4,0x46c6,37),(5,0x4762,13),(6,0x47ba,24),(13,0x48fc,2)]:
 values=[int(x,16) for x in re.search(r'kind%d\{\{(.*?)\}\}'%kind,header).group(1).split(',')];assert values==list(struct.unpack_from('>'+str(count)+'I',rom,address));tables.append(dict(kind=kind,address=address,count=count,original_bytes=rom[address:address+count*4].hex()))

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[]
for slot,target,end in [(0x466c,0x46be,0x46c6),(0x4670,0x475a,0x4762),(0x4674,0x4796,0x47ba),(0x4690,0x48d8,0x48fc)]:specs.append((slot,[(slot,slot+4),(target,end),(0x4a48,0x4a84)],'Fixed pinned definition table; paired input for kinds4/5, doubledWORD parameter for6/13. Suppress6/13 iff C5CCzero,C553nonzero,F26Fnegative. Full4A48 request, including incoming marker resource context, handed to allocation service once.'))
for slot,target,end in [(0x4678,0x481a,0x4826),(0x467c,0x4826,0x4832),(0x4680,0x4832,0x483e),(0x4684,0x483e,0x484e)]:specs.append((slot,[(slot,slot+4),(target,end)],'Original trigger dispatch64/68/68/lowBYTE*4; parameterBYTE orzero,consume0/0/FF/0. Unadjusted coordinate,row and full marker passed to existing4A84service.'))
specs.append((0x4688,[(0x4688,0x468c),(0x484e,0x4874),(0x4a48,0x4a84)],'ProgressBYTE indexed before allocation; bit0 suppresses. Otherwise fixed14482 definition via4A48; original parameter lowBYTE stored at returned actor50 only on successful allocation.'))
for slot,target in [(0x4694,0x4904),(0x4698,0x46bc),(0x469c,0x46bc),(0x46a0,0x4906),(0x46a8,0x46bc),(0x46ac,0x46bc),(0x46b0,0x46bc),(0x46b4,0x46bc),(0x46b8,0x4908)]:specs.append((slot,[(slot,slot+4),(target,target+2)],'Literal BRA to RTS; no state or service effect. Entry alias only, not a gameplay feature.'))
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local spawn branch family contract'),native_sources=[sources[0]],checked_cases=1048576,contract=contract,proof='One focused family check:1048576coordinate/parameter/failure partitions plus exhaustive16777216threeBYTEgate combinations. All request fields, call counts, gate order, fixed tables pinned againstROM, progress and postallocationwrite order checked. Literal noops statically BRA/RTS.',scope='Local slot plus complete target body and typed allocation/trigger service boundary. Valid original parameter domains: kind4<74,kind5<26,kind6<24,kind13<2,piece<256. Allocation internals and trigger pool retain separate proofs; whole spawning scheduler and CPU scratch register ABI remain external. Nine aliases are no-op entries.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),table_evidence=tables,literal_noop_entries=9)
(p/'docs/stage9/spawn-branch-family-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('18 spawn branch contracts verified; nine are literal no-op aliases.')
