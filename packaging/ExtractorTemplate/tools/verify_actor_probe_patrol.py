"""Pin local injury branches and valid original phase tables; no ROM execution."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
result=root/'work/actor-probe-patrol-results.json';r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,state_cases=3145728)
sources=['src/core/actor_probe_patrol.hpp','src/core/actor_state.hpp','tests/actor_probe_patrol_verification_tests.cpp'];exe=root/'work/actor_probe_patrol_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
assert rom[0xdba8:0xdbbe].hex()=='000001010102020303030403030302020101010000ff'
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xe5d0,[(0xe5d0,0xe620),(0xd05a,0xd06c)],'117 gate,object/player contact and damage. Set118bit3; query85E8atWORDX-16,Y; nonzero clearsbit3. D05A sets62highWORD1 and steps integerY by sign122, preserving122 andfractions. D11Aservice then live122sign clears/sets119bit4.'),(0xdb44,[(0xdb44,0xdba8)],'Contacts then selector8bypass. IntegerXstep2 then directionservice. LivephaseBYTE46/2reads original22BYTEtable; negativesentinelsetsselector0. Nonnegativeentryaddsunsignedstep tointegerY,increments46,selector4. Phasezero tests signedwrappedabsoluteXdistance<=200,including8000,then incrementsphase andselector0.'),(0xdcda,[(0xdcda,0xdd36)],'FollowfiniteacyclicLONG84chain,copyeachnextintegerXYintopredecessor,preservefractionsandadvanceA5totail. Playercontact/hurt,live117sets116. Existing46BYTEstartsgravity/integrate/land. Zero46setsFF,direction121by118bit3,and58LONG60000;motionstartsnextcallback.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),original_bytes=rom[start:max(b for a,b in ranges)].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: local probe patrol and chain motion contract',native_sources=[sources[0]],checked_cases=1048576,contract=contract,proof='One focused three-actor family batch,3145728 fixtures over65536seed WORDs and16mutablecontact partitions; comparesallfivecompleteactors,liveA5and every service-entry snapshot,querycoordinates andorder. Original22BYTEtable pinned. Testscoverall44validphaseBYTEs andchainlength0..3,retainedXY/velocityfractions,negativephase sentinel and8000 distance. D05A instruction review caught and corrected an initial119based draft before firsttest; original direction is122,not119.',scope='Localvalidactors,DB44phase0..43 andfiniteacyclicvalidLONG84handles. Callerphaseproduction,greater tableindices,cycliclinks and actualRAMaddressresolution not admitted. Childcontact/damage/query/direction/hurt/motionservices explicit andmutable; their implementations and liveSDLbinding remain separate.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/'docs/stage9/actor-probe-patrol-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three probe/patrol/chain contracts verified.')
