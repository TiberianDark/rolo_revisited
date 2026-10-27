"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/player-startup-followup-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,startup_cases=1024,score_cases=262144)
sources=['src/core/player_startup_followup.hpp','src/core/level_reset_state.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/player_startup_followup_verification_tests.cpp'];exe=root/'work/player_startup_followup_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0x766a,[(0x766a,0x7730)],'Allocate13ECCat420,200/facing0/marker0withretainedinputD1context. Failure selectsboot0200beforelocalresetwrites. SuccessC4E0/C4E4=head,actor68zero,C4E8=4,activecount0,threecompanions0,exactoriginalBYTE/WORD/LONGstateclears,C542=3. Allocationpartialsideeffectsretained.'),(0x9916,[(0x9916,0x9958)],'Sound64 before9958collectionservice,then992Cscorefollowup. OriginalinputD0WORDsavedthroughfirstsound butnotpartoftypedstateAPI; no invented scorequantity.'),(0x992c,[(0x992c,0x9958)],'ReadlivebaseC4E4,allocate14928atfullbaseXY/facing0/marker0withliveretainedD1context. AlwayswriteallocationD0toF2D4includingzero; setC512FFonlyifnonzero,otherwise retainliveC512.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local player startup followup contract'),native_sources=[sources[0]],checked_cases=1024 if start==0x766a else 131072,contract=contract,proof='One focused relatedstartup/followup batch:1024startupcases acrossallBYTEpagefills andsuccess/failure/partialallocation partitions compareall65536statebytes and48records, exactrequestcontext, noresetonfailure.262144scorevariantscoverallWORDvalues,mutable sound/collection allocationcontext/base,andallocationfailurepreservation; serviceorder/callcounts/fullrecords/statecompared. Constantstraightlineresetstores verifiedagainstcomplete37instructionbody; independentaddressoracle.',scope='Local complete resetandservicehandoff contract withvalidstableactors. Allocation/9958/audiochildservicesretainownproofdomains; incomingD1context isexplicittypedinput/livestate. Failurefalse representsoriginalbootcontinuationrequestonly, notbootimplementation. Automaticdeathrestart/retainedcheckpointworldbinding stillunimplemented; no fullrestart/gameclaim.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/player-startup-followup-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three player startup/score-followup contracts verified.')
