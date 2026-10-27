import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/powerup-pickups-results.json';r=json.loads(rp.read_text());assert r['passed'] and all(r[x]==65536 for x in ['9800','9826','984A'])
sources=['src/core/powerup_pickups.hpp','src/core/actor_defeat.hpp','src/core/actor_state.hpp','tests/powerup_pickups_verification_tests.cpp'];exe=root/'work/powerup_pickups_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
dep='docs/stage9/actor-defeat-verification.json';assert json.loads((p/dep).read_text())['records'][0]['address']==0x97ac
records=[]
for a,e,name,contract in [(0x9800,0x9826,'Trunk strength pickup','Sound64;C51Cequals3preserved,allotherBYTEvaluesincrementwrapped. Actor125bit2set,tail97AC.'),(0x9826,0x984a,'Float-mode pickup','Sound64;C513FF,C520zero;actor125bit2set,tail97AC.'),(0x984a,0x989c,'Stored projectile pickup','Sound64;C548!=140CAclearsC547andsetsdefinition140CA. Add3BYTE,Ccarrysets1. Basehead46FF,actor125bit2set,tail97AC.')]:
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e and ins[-1]['target']==0x97ac
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: standalone local '+name+'; world binding pending',verification_status='verified',native_sources=['src/core/powerup_pickups.hpp'],instruction_evidence=ins,checked_cases=r[f'{a:X}'],contract=contract,proof='CompleteoriginalspansreviewedwithBEQexactcapandADDQ.B/BCCcarrysemantics. EveryBYTEcounter/flagpair acrossallthreehelpers; independentfield/constantoraclecomparesall130actor/headbytesandstate. Actualcertified97AChelperexercised; dependencyhashpinned. Currentworld9800inlinebehaviourmatcheshelperbutnotrefactored;9826/984Anotconnected.',scope='Standalonelocaltypedstate/serviceAPI,distinctstablepowerup/head,disjointglobalrefs;97ACsound/allocationservicesremainexplicitboundaries. C547duplicatecountsnapshot/worldbinding and140CAprojectileallocation/graphics remainopen; no shooting/lifecyclestatusclaimed. Wideraliases,scheduler/rawglobalpointer/CPUABI excluded.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/powerup-pickups-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Three standalone powerup local contracts verified; live binding/state gaps remain.')
