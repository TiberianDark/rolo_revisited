import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/collected-update-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['B7C0']==r['B7B8']==1310720;sources=['src/core/level1_collectibles.hpp','src/core/level1_companions.hpp','src/core/actor_motion.hpp','src/core/actor_state.hpp','tests/collected_update_verification_tests.cpp'];exe=root/'work/collected_update_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
deps=['docs/stage9/collected-motion-verification.json','docs/stage9/leaf-routine-verification.json'];assert json.loads((p/deps[0]).read_text())['records'][0]['address']==0xb7d8;assert {0xcd8e,0xcfce}<={r['address'] for r in json.loads((p/deps[1]).read_text())['records']}
records=[]
for start in [0xb7c0,0xb7b8]:
 c=start;ins=[]
 while c<0xb7d8:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==0xb7d8 and {i['target'] for i in ins if i['flow']=='call'}=={0xb7d8,0xcd8e,0xcfce}
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=0xb7d8,original_bytes=rom[start:0xb7d8].hex(),status='verified green: local collected/released actor update contract',verification_status='verified',native_sources=['src/core/level1_collectibles.hpp']+(['src/core/level1_companions.hpp'] if start==0xb7b8 else []),instruction_evidence=ins,checked_cases=1310720,contract=('First116=FFif117nonzeroelse0. ' if start==0xb7b8 else '')+'IfBYTE46zero writeFF andB7D8motioninit. ThenCD8EgravityfollowedbyCFCEpositionintegration. Preserveexactcallee state changes andsharedseed advancement; noextralanding/reset.',proof='Originalentry..B7D8reviewed including SNEretirementfallthrough onB7B8. Threecallees independentlyreviewed/verifiedandpinned. All65536seedstates acrossinit/sticky/statusmaskpartitions; all256statusx256initgates across16position/speedboundaryfixtures. Independent64bit/modularstateoracle comparesall130bytes/finalsharedseed. Compositionalproof usesexactcallorder andcompletecalleelocal contracts; globalschedulers are separate.',scope='Complete local actor/sharedseed API contract. Lifecycle/list disposal, collision/graphics publication, callerselectors andCPUtemporaryregister/CCR/ABI remainoutside certificate.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+deps},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/collected-update-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Collecteditemandreleasedcontainerlocalupdatesverified.')
