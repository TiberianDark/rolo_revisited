"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-bounce-chain-platforms-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,bounce_cases=1048576,chain_cases=1048576)
sources=['src/core/actor_bounce_chain_platforms.hpp','src/core/actor_displacement.hpp','src/core/actor_wave_motion.hpp','src/core/camera_data.hpp','src/core/actor_common_state.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/actor_bounce_chain_platforms_verification_tests.cpp'];exe=root/'work/actor_bounce_chain_platforms_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xbe64,[(0xbe64,0xbe68),(0xbf54,0xc022)],'Supported124bit6and53zero initializesYanchor/power52/56/phase1 andcontrolled124bit3. InitialdeltaWORD includes66+24-Y; retainedincomingD3highWORDbecomesfractionafterSWAP. PhasezeroC95Azero;phase1C988carry/halve52 thenWORD0102whenzero;laterphasecomparesspeedBYTEtodistanceWORD,negativecarry/doublespeedorfinishwithcontrolledlaunch.'),(0xbe8c,[(0xbe8c,0xbe90),(0xc322,0xc3ee)],'116gate; definition26bit3set. First122zero latchesFFandallocates1450AwithfullXY/facing0/marker0 andexplicitretainedD1context. Successfulheadsplicesselfafterhead. Oldphase50WORDcapturedbeforephaseLONGupdate; zero reload56=300/toggle121bit0. Signed56<<8 changesLONG50,56minus16; waveoldphase100/8 spaces sixlinkedchildren thenpositionsselfat seventhstep+LONG38-16pixels.'),(0xbe90,[(0xbe90,0xbe94),(0xc3ee,0xc4ba)],'Same linkedchainplatform with zero-phase56reload380 instead of300.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor bounce chain platforms contract'),native_sources=[sources[0]],checked_cases=1048576,contract=contract,proof='One focused family batch:1048576bouncecases includingcontrolledselfaliases, allWORDanchors/retainedfractioninputs, phase/powerpartitions;1048576chaincases includingbothvariants,116gate,existing/nohead,successful/failedallocation,mutatingallocationservice andall48recordscompared. Completeactor/snapshot/definitionflag/callcountoracle; independenttwoDIVUwaveformula. RetainedD3highWORD andD1context explicit, notinventedzero.',scope='Local slot/target state semantics for validstableactors; chains admit distinctsixsuccessors andstableparentroot. BounceinputincomingD3highWORD andchainincomingD1context are typedcallerinputs whose actualancestry remainsoutsideproof. Definitionmutation/allocation typedservices; allocator failurepoolsideeffects external but preserved. No livecallbackbinding orwholeplatform/gameclaim.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-bounce-chain-platforms-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three bounce/linked-chain platform slot contracts verified.')
