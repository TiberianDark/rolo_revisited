import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/collected-motion-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['B7D8']==65536;sources=['src/core/level1_collectibles.hpp','src/core/animation.hpp','src/core/actor_state.hpp','tests/collected_motion_verification_tests.cpp'];exe=root/'work/collected_motion_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
dep='docs/stage9/random-range-verification.json';assert json.loads((p/dep).read_text())['records'][0]['verification_status']=='verified'
c=0xb7d8;ins=[]
while c<0xb804:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0xb804 and {i['target'] for i in ins if i['flow']=='call'}=={0x716e} and ins[-1]['mnemonic']=='RTS'
record=dict(address=0xb7d8,hex='00B7D8',end_exclusive=0xb804,original_bytes=rom[0xb7d8:0xb804].hex(),status='verified green: collected-item motion initialization contract',verification_status='verified',native_sources=['src/core/level1_collectibles.hpp'],instruction_evidence=ins,checked_cases=65536,contract='First716E draw[0,3), subtract1fromBYTE thenstore121 asFF/0/1. SpeedLONG58=30000. Secondordered716E draw[3,9), speedLONG62=result<<16 withfraction0;122FF. Advanceone sharedseed twice andpreserveeveryotheractorbyte.',proof='All65536incomingseedstates exhaustively checked using independent64bitseed/rangeoracle, full130bytecomparisons andfinalseedcomparison. Whole13instructionfunctionreviewed includingBYTE-only SUBQ, SWAP/CLR.W andimmediatevelocity. Verified716Edependency andallcurrentnative sources pinned.',scope='Complete local actor/sharedseed contract. Collectioncontact/score/retirement callers, globalscheduler andCPUtemporaryregister/CCR/ABI remainoutside scope.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/collected-motion-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Collecteditemmotioninitializationverified acrossallseedstates.')
