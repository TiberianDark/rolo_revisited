"""Live actor priority/callback/animation-list handoffs with native services."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-schedule-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'C9AE':524288,'A808':65536,'FCD4':131072}
sources=['src/core/actor_scheduler.hpp','src/core/actor_animation_list.hpp','src/core/actor_definition.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/actor_schedule_verification_tests.cpp'];exe=root/'work/actor_schedule_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0xc9ae,0xca0a,'Priority actor list',sources[0],'Ifcontrolled124bit5 save98LONG beforevisits. Visitbase then3nonnullsecondary; eachlive98nonzero appendsitsvalue,zeros98andclears124bit5. Actoraliasvisits seeearlierclears. Terminalnullonly; preserveunusedprioritytail.'),(0xa808,0xa84c,'Actor callback passes',sources[0],'BuildC9AEpriority first. Visitprioritythenactive withliveentries; old126bit6decidescallback, BSET6beforecallback. Callback42readlive pervisit; aliasesnormallyskipafterfirst, callbackmaycleartag/changefutureentries/callbacks. TypedservicepreservesA6cursor convention.'),(0xfcd4,0xfd44,'Animation-list prefix and parent handoff',sources[1],'SetF280FF; liveactivekeysuntilnull, lookupdefinitiononceperactor andpreserveidentity/reference acrosscallback42ifdefinition7bit5. Re-readdefinitiontype/26/animation18andparent76aftercallback; type24or26bit6skipsinheritance. CopyparentintegerXY/70/118/121/122,retainfractions. InvokeexplicitFD44animationserviceonlyifcacheddefinition18LONGnonzero. FE0A..FE1E loop tailsetsF280zero onterminal.')]
for start,end,name,source,contract in specs:
 ranges=[(start,end)]+([(0xfe0a,0xfe1e)] if start==0xfcd4 else []);items=[];extra=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
  extra.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,code_ranges=extra,verification_status='verified',status='verified green: local '+name,native_sources=[source],checked_cases=r[f'{start:X}'],contract=contract,proof='Independent ordered-list/wholeactorstate models.524288prioritycases variedBYTEflags/aliases/base/control/secondarynulls andstaleoutputtail.65536callbackpasses withmutatedlaterentries,callbackfields,tags andduplicates.131072animationprefixcases withcallbackmutatingcacheddefinitionbytes,actor4identity,parent76,futurelistentries andanimationserviceeffects. All48actorrecords,lists,definitions,phase,eventorderingcompared. Reviewednoncontiguousprefix/tail andexplicitFD44serviceboundary.',scope='Local validfiniteactors/definitions andsentinellists; callbackservicepreservesoriginalA6cursor convention. FCD4green is prefix/loop-tail orchestration ONLY; FD44..FE0A animation command decoder, caller/assetadmission andCPUABI are external. No wholeanimation orcompleteactorframeclaim. Priority98values mustresolve nativeactoridentities.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-schedule-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three actor schedule/animation handoff local contracts verified.')
