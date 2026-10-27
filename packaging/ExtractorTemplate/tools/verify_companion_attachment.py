import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/companion-attachment-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['B1D6']==30720 and r['B1C6']==256
sources=['src/core/level1_companions.hpp','src/core/base_actor_waiting.hpp','src/core/level1_companion_selection.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/companion_attachment_verification_tests.cpp'];exe=root/'work/companion_attachment_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
dep='docs/stage9/rescue-progress-verification.json';assert json.loads((p/dep).read_text())['records'][0]['address']==0xd32a
records=[]
for a,e,name,contract in [(0xb1c6,0xb1d6,'Base actor waiting callback','C4E4base actor suppliedasnativeparameter;writeonlyLONG42=A84E.'),(0xb1d6,0xb28e,'Companion attachment and oldest-slot retirement','D32Arescuefirst. Scanthree6402slotsuntilfirstnull. Fullarrayretireoldest:42ADD0,set125bit2,clear47;shiftsecond/thirdtofirst/secondandrenumber47/50/52by1,192,24. Appendnewactorwithslotindex1..3, distances192/24multiples,clear114,callbackAA4AifC50FnonzeroelseAB28;set124bit0,clearbits1/2. PreserveC50E/C50F.')]:
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: local '+name,verification_status='verified',native_sources=['src/core/base_actor_waiting.hpp'] if a==0xb1c6 else ['src/core/level1_companions.hpp'],instruction_evidence=ins,checked_cases=r[f'{a:X}'],contract=contract,proof='Completeoriginalspansreviewed, postincrementfirst-nullslotandDBFshiftcount2preserved. Independentslot-position/fieldoracle:all256newactorflags,5zero/nonzeroC50Fpartitions,all8nullpatternsand3distinctidentityrotations; comparesall48actorrecords/sharedslots. Null-linkrescuefixtureverifiessound-beforeattachmentandprogresspreservation; fullnonnullrescuecompositiondelegatesseparatelycertifiedD32Arequestcontract. Basecallbackall256priorBYTEpatternschecksall130bytes; nativehelperreplacesidenticalexistingmenuline.',scope='Localtypedactor/pool/slotAPI withvaliddistinctthreepreviousactorsandseparatenewactor, stableidentitythroughrescue. Allocation/HUD/soundservices, rawaliases, actualslot/callerprovenance, lifecycle/frame/animationandCPUABI remainseparate. Notcompletecompanionlifecyclestatus.') )
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/companion-attachment-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Attachment and base-waiting local contracts verified.')
