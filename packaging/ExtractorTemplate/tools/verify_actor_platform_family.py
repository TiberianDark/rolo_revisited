"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-platform-family-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,actor_cases=8388608)
sources=['src/core/actor_platform_family.hpp','src/core/actor_wave_motion.hpp','src/core/camera_data.hpp','src/core/actor_displacement.hpp','src/core/actor_common_state.hpp','src/core/actor_allocation.hpp','src/core/actor_motion.hpp','src/core/actor_state.hpp','tests/actor_platform_family_verification_tests.cpp'];exe=root/'work/actor_platform_family_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
import re,struct
values=list(map(int,re.search(r'sine\{(.*?)\}',(p/'src/core/camera_data.hpp').read_text(encoding='utf-8')).group(1).split(',')));assert values==list(struct.unpack_from('>512h',rom,0x1582a))

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[]
for slot,target,end,contract in [(0xbe84,0xc244,0xc2b4,'Horizontal ellipse: first-anchor init usesphase128,Xanchor+200,Yanchor unchanged. Existinganchor waits for controlled98identity and124bit5 thenlatches56. Wave amplitude200, incrementphase1, arithmeticquarterY.'),(0xbe88,0xc2b4,0xc322,'Vertical ellipse: initphase0,Xanchor unchanged,Yanchor-200. Same support latch; arithmeticquarterX.'),(0xbe94,0xc4ba,0xc51e,'Vertical reversing platform: cooldown52decrement andzerodisplacement. Otherwise supportedrider required. Initialspeed50=-2/cooldown50. Existing speed movesY; clear121,callD168; returned121nonzero negates live50and reloads52.'),(0xbe98,0xc51e,0xc582,'Horizontal reversing platform: same cooldown/support/direction semantics; initialspeed+2 and movesX.'),(0xbeac,0xc7b8,0xc7fc,'F281gates horizontal retraction. Zero50 cachesintegerX-width. Unsigned50<X and signed(originF362-100)<=X enables delta-1integer; otherwisezero displacement. C95A publishes measuredvelocity.'),(0xbeb0,0xc7fc,0xc844,'F281gates vertical retraction. Zero50 cachesintegerY-2height. Same unsignedcache andsignedoriginF366threshold, movesY-1integer.'),(0xbeb4,0xc844,0xc850,'F282gates horizontal retraction bybranchingC7C0, bypassingF281test.'),(0xbeb8,0xc850,0xc85a,'F282gates vertical retraction bybranchingC804,bypassingF281test.')]:
 ranges=[(slot,slot+4),(target,end)]
 if slot==0xbeb4:ranges.append((0xc7c0,0xc7fc))
 if slot==0xbeb8:ranges.append((0xc804,0xc844))
 specs.append((slot,ranges,contract))
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor platform family contract'),native_sources=[sources[0]],checked_cases=1048576,contract=contract,proof='One focused relatedfamily batch:8388608actor variants across all65536WORD inputs and16cooldown/anchor/latch/support/alias partitions. Independent endpoint/position arithmetic, two-DIVU wave oracle and signed floorquarter model. All130actorbytes and directionservice entry snapshots compared, including live50mutation before conditionalnegation. Original slot and full target bodies reviewed.',scope='Complete local target state effects for admitted valid controlled/actor identities; directionD168 is an ordered mutable native service. Wave and displacement have separate green contracts. Actual selector54admission and gameplay callback binding remain external. F281/F282aliases checked by matching targetentry and no secondgate.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-platform-family-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Eight related platform slot/target contracts verified.')
