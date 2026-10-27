"""Reviewed offscreen retirement and timed callback restoration local contracts."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/retirement-timer-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['B47C']==65536 and r['B51E']==1048576
sources=['src/core/actor_offscreen_retirement.hpp','src/core/level2_actor_updates.hpp','src/core/actor_motion.hpp','src/core/actor_state.hpp','tests/retirement_timer_verification_tests.cpp']
exe=root/'work/retirement_timer_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,name,contract,scope in [
 (0xb47c,0xb498,'offscreen retirement','Always integrate CFCE. Nonzero117 sets116=FFwhen126bit3clear,0whenbitset; then sets126bit2. Zero117 retains116/126.','Standalone typed actor API. Allstatus/flagBYTEpairs comparedacrossall130bytes withwrappedmotion; integration separatelycertified. Schedulerbinding, disposal/lifetime andCPUABI remainexternal.'),
 (0xb51e,0xb566,'timed callback restoration','Trunkpull,deceleration,integration,gravity,landing inoriginalorder. DecrementWORD46 modulo16. Exactlyzero restoresdefinition12callback andclears119bit4. Otherwise signedtimer<=50and124bit0 sets122FFandWORD62=2, retainingfraction64. No117gate.','Local composition withstablevaliddistinctactor/definition identities,dormanttrunkbase52 andexplicitlandingservice. EverytimerWORD acrossstatusmask/groundflagpartitions checksall130bytes. Activecapture,populatedterrain/livemutatingservices,alias/lifetime/CPUABI remainexternal. Existinglivehelper; nowholethrowlifecyclestatus.')]:
 at=start;items=[]
 while at<end:
  assert at in accepted
  i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local '+name,native_sources=['src/core/actor_offscreen_retirement.hpp'] if start==0xb47c else ['src/core/level2_actor_updates.hpp'],checked_cases=r[f'{start:X}'],contract=contract,scope=scope,proof='Original full spans and signed/zero branch order reviewed; independentfield/motionoracle andfullrecord comparison. Timerzero underflowsFFFF anddoesnotrestore; timerone restores. Constant-modular transforms andpreviouslyverifiedmotionservices retainfullspeed domains beyondsample fixturevalues.'))
deps=['docs/stage9/leaf-routine-verification.json']
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+deps},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/retirement-timer-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Two local retirement/timer contracts verified.')
