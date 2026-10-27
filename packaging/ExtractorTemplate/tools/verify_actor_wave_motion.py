"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-wave-motion-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,wave_cases=37748736,actor_cases=2621440)
sources=['src/core/actor_wave_motion.hpp','src/core/camera_data.hpp','src/core/actor_displacement.hpp','src/core/actor_common_state.hpp','src/core/actor_allocation.hpp','src/core/actor_motion.hpp','src/core/actor_state.hpp','tests/actor_wave_motion_verification_tests.cpp'];exe=root/'work/actor_wave_motion_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
import re,struct
values=list(map(int,re.search(r'sine\{(.*?)\}',(p/'src/core/camera_data.hpp').read_text(encoding='utf-8')).group(1).split(',')));assert values==list(struct.unpack_from('>512h',rom,0x1582a))

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xccf8,[(0xccf8,0xcd7a)],'Phase doubledWORD and03FFmask select512signedsineWORDs. Signed16x16 product doubledmod32, highWORD signextended. Signed inputdivisor<=1 yieldsinteger16.16; otherwise divide magnitude by divisor-1 usingtwoDIVU steps and restore sign. Return sinefirst,cosinesecond.'),(0xd918,[(0xd918,0xd940)],'Increment50WORD16 before wave(phase,8,1); add returned highWORD offsets to integer anchors20/24, preserve XYfractions and allotherfields.')]
for slot,target,end,kind in [(0xbe74,0xc160,0xc18e,0),(0xbe78,0xc18e,0xc1bc,1),(0xbe7c,0xc1bc,0xc1f8,2),(0xbe80,0xc1f8,0xc244,3)]:specs.append((slot,[(slot,slot+4),(target,end)],f'Wave platform kind{kind}: conditional LONG anchorcache keyedbyanchorintegerWORDzero; old50phase wave80/1 and50increment2; Xonly/Yonly/both/bothwithreflectednegativeY. C95A publishes fullposition andintegerdisplacement retainingvelocityfractions.'))
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor wave motion contract'),native_sources=[sources[0]],checked_cases=37748736 if start==0xccf8 else 524288,contract=contract,proof='One focused batch:37748736wave cases, including all512phases x65536signedamplitudes with8denominatorboundary partitions plus everydivisor at64phases. Two-DIVU quotient/remainder oracle independent of native64bit division. Algebra: two unsigned divisions concatenate integer and fractional quotients exactly; magnitude<=32768 prevents quotientoverflow. All65536phaseWORDs x8anchor/fraction fixtures for fiveactor variants, all130bytes compared. Fixed512WORDtable pinned toROM1582A.',scope='Complete local finite typed wave value contract and listed platform/orbit target state effects. CPU scratch/CCR ABI, selector54admission and live gameplay caller binding remain external. Slot verification includes its full target, not just BRA. Wave phase aliases provable by mask; division formula covers unsampled Cartesian divisor pairs.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-wave-motion-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Six wave/platform/orbit contracts verified.')
