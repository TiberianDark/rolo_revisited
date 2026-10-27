"""Original world route step and two-substep orchestration, native data/services."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/world-route-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'A02A':1048576,'9FEE':1048576}
sources=['src/core/world_route.hpp','src/core/actor_state.hpp','tests/world_route_verification_tests.cpp'];exe=root/'work/world_route_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0xa02a,0xa204,'World route step',[(0xa02a,0xa092),(0xa09a,0xa204)],'117nonzeroskip; comparealignedX usingwrappedsubtractionN then signedBGT, XprecedenceoverY. Crossingcheckssectionavailability; missingrestoresanchorand reversesdirection. QueryA204, loadgroup+direction6descriptor. Anchorssetbeforeconsume. FirstrouteBYTEnegative terminateswithoutYread; YBYTEzeroextended. Applynegationflags/WORDXY, selection70hysteresis46/48. Pointerzero inputpriorityup/down/left/right: candidatepathpermission thenFIXEDgroup144load, noimmediatemovement.'),(0x9fee,0xa02a,'World route two substeps',[(0x9fee,0xa02a)],'Clearactor70WORD evenpaused. NonzeroF270pause returnswithoutmovement/snapshot. Otherwiseexactly2 A02Acalls, eachwithtemporaryYWORD-2 then+2; snapshotcurrentXYaftereach; fraction14/18andotherfieldsunchangedexceptroutehelperwrites.')]
for start,end,name,ranges,contract in specs:
 items=[];evidence=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi;evidence.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,code_ranges=evidence,verification_status='verified',status='verified green: local '+name,native_sources=[sources[0]],checked_cases=r[f'{start:X}'],contract=contract,proof='Independent signed/WORD arithmetic, explicitdirection/reversal andorderedservice-event models. All65536coordinate/routeBYTE/tileWORDpartitions x16input/pointer/anchor/negation/timer/visibility/pause cases. Compareall130actorbytes,allroutefields andquery/descriptor/readorder; secondcomposed2substepcaseincludespoststepstateandpause. InlineA092..A09A reversaldataexcludedfrominstructiondecoding andfullrawspanpinned. Completeoriginalbranchesreviewed.',scope='Local typedstableworldrouteservices,validdescriptor/routebytes andF268=0 worldMAPdomain. CPUregisterclobber/rawpointerABI, actualroutepooladmission, sectionflagproducer andfullrenderer/cursorframeintegrationremainexternal. CanonicalservicehidesA368/8728scratchregisters. No wholeoverworldclaim.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/world-route-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two original world route local contracts verified.')
