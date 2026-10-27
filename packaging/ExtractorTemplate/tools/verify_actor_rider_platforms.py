"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-rider-platforms-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,direction_cases=1048576,rider_cases=4194304)
sources=['src/core/actor_rider_platforms.hpp','src/core/actor_direction_result.hpp','src/core/actor_platform_family.hpp','src/core/actor_wave_motion.hpp','src/core/actor_displacement.hpp','src/core/actor_common_state.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/actor_rider_platforms_verification_tests.cpp'];exe=root/'work/actor_rider_platforms_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xd168,[(0xd168,0xd1ca)],'Directionstate plus returnedZpredicate. X<=0 returnsnonzero afterMOVE.B1. RightboundaryBSETreturnsnonzeroiff old118bit3set;STpreservesflags. Terrainclass<=allowed returnsnonzeroiff unequal. Interiorrightmovementreturnsnonzero fromX&8; interiorleftBSETafterclear returnszero.'),(0xbe60,[(0xbe60,0xbe64),(0xbee0,0xbf54)],'Supportedrider cachesY/setsrate1, sinkswhile signed(anchor+8)>Y andmovesXsignedby121thenD168. Releasedanchor belowY rises1; elseclearsanchor. Retains velocity when no displacementcall.'),(0xbe68,[(0xbe68,0xbe6c),(0xc022,0xc08a)],'RiderarmsBYTE50andclearsrate52. Clear121beforeD168; returnedactor121nonzero stops/clearslatch,else wrappedrate+64 signedupperclamp1024, negativeBYTE52 signextendedintegerYdrive.'),(0xbe6c,[(0xbe6c,0xbe70),(0xc08a,0xc0ec)],'Similar downwardplatform but branchesonD168returnedZ, notactor121. PositiveBYTE52 signextendedintegerYdrive.'),(0xbe70,[(0xbe70,0xbe74),(0xc0ec,0xc160)],'Supportedrider cachesY/rate0thenC142positiveverticaldrive. Releasedanchor usesnegativeC142drive; unsignedanchor>newYclampsintegerY,clearsfraction andLONG50 includingrate52.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor rider platforms contract'),native_sources=[sources[0]],checked_cases=1048576,contract=contract,proof='One focused group:1048576directionstate/flag cases and4194304rider variants. AllWORDvalues across16support/alias/latch/direction-service partitions. Independent fullrecord arithmetic and explicit returnedflag oracle; mutable direction service returnsflag deliberately differentfrom121. BSEToldbit/STpreservedZ paths reviewed, signedclamp/negatedBYTEdrive andunsignedreturnclamp checked.',scope='Local valid native records andcanonical874Cterrainclassdomain0..7. D168nonzero predicate explicitly extends prior state-only helper contract; original actor_choose_direction remains unchanged. Platform D168service must supply exactreturnedZ forC08A; actualcallback/selectorbinding remains external. Other CPU scratchflags excluded.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-rider-platforms-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Four rider platform slots plus direction return-flag contract verified.')
