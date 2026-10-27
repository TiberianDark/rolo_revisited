import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/container-update-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['B2D2']==57344
sources=['src/core/level1_companions.hpp','src/core/actor_motion.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','src/core/level1_enemy_slice.hpp','src/core/first_enemy_combat.hpp','tests/container_update_verification_tests.cpp'];exe=root/'work/container_update_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
deps=['docs/stage9/leaf-routine-verification.json','docs/stage9/actor-land-verification.json'];assert {0xcd8e,0xcfce}<={x['address'] for x in json.loads((p/deps[0]).read_text())['records']};assert json.loads((p/deps[1]).read_text())['records'][0]['address']==0xcf46
c=0xb2d2;ins=[]
while c<0xb2e6:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0xb2e6 and [i['target'] for i in ins if i['flow']=='call']==[0xcd8e,0xcfce,0xcf46]
record=dict(address=0xb2d2,hex='00B2D2',end_exclusive=0xb2e6,original_bytes=rom[0xb2d2:0xb2e6].hex(),status='verified green: local cage gravity/integration/landing update',verification_status='verified',native_sources=['src/core/level1_companions.hpp'],instruction_evidence=ins,checked_cases=r['B2D2'],contract='Any nonzeroBYTE117 returns unchanged and invokes no services. Zero callsCD8Egravity,CFCEintegration,CF46landing in that order, with no intervening or subsequent writes.',proof='Complete original boundaries and direct call order reviewed. Three complete callee contracts independently verified and hash-pinned. Native gate checked across all256status bytes, sevenlandingflags and16signed/fixedpointboundaryfixtures onLevel1/2world terrain. Independent modular motion oracle and final state comparison compose with separately certified CF46. Service sequencing is established by reviewing the short native wrapper alongside the original direct-call order. Composition establishes exact wrapper call sequencing, not a new independent proof of callee semantics.',scope='Local actor contract with companion_land bound to certified CF46 on valid terrain. Native world service binding exercised. Actor scheduling, terrain publication, lifecycle, CPU temporary registers/CCR/ABI remain outside certificate.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+deps},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/container-update-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Cage update local contract verified.')


