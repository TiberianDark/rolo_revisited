"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-scene-rewards-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,actor_cases=1572864,reveal_cases=2048)
import re
sources=['src/core/actor_scene_rewards.hpp','tests/actor_scene_rewards_verification_tests.cpp'];pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
sources.append('docs/stage9/reward-curve-verification.json')
exe=root/'work/actor_scene_rewards_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources if not s.endswith('.json'))

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xe300,[(0xe300,0xe342)],'117gate/contact/damage,integerwalk1,direction. Decrement46WORD; negative wrappedresultreload100andallocate14D46atfullXY/facing0/marker0withliveretainedD1context. AllocationchangesliveA5totailincludingfailure;no rollback.'),(0xea20,[(0xea20,0xea2c)],'F2B8zero invokesB702defaultcollectionservice; nonzero returnswithoutservice oractorwrites.'),(0xdd74,[(0xdd74,0xddaa)],'DDAAnegative earlyreturn. Thencontrolled122negativeor124bit4clear return.8FF2contactwith32/16shrinks; onhitF2BCFF,actor50BYTEFF,C511zero. Childqueryeffects retained.'),(0xd3fe,[(0xd3fe,0xd452)],'SignedF26FBYTEabsolute0..128 selectsC558index;setbit0beforealready-settest. Newflagallocates14482atcontrolledfullXY/facing0/marker0/retainedcontext. FailedallocretainsflagandreturnedA5tail. SuccessfulA5=head,selector4,startD2E2rewardto296,41,C551withimmediatefirststep.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status='verified green: local scene reward/contact contract',native_sources=[sources[0]],checked_cases=2048 if start==0xd3fe else 524288,contract=contract,proof='One focused familybatch:1572864projectile/gatedcollectible/latchcases acrossallWORDtimers and8contact/gatepartitions;2048revealfixturescoverall256signedselectorBYTEs,oldflagbits,allocationfailure andfull65536statepage/48actorrecords. Mutabledirectionchangesretainedcontextbeforeallocation. IndependentrewardfirststeporaclechecksactualD2E2helperoutputwithvaliddivisor32. LiveA5tail/headandnonrollbackflagbehaviourcompared.',scope='Local stablecurrent/controlled/newactor identities andexplicitmutablequery/contact/allocation/collection services. DDAA/8FF2/B702implementations andactualincomingD1ancestry remainexternal. Sharedstatepageallowsoriginal0..128flagaddresseswithoutinvented80entryclamp; actualcallerselectordomainunclosed. Notwholeenemy/sceneorallocationfidelity.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-scene-rewards-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Four scene reward/contact contracts verified.')
