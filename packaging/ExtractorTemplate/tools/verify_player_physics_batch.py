"""Three original shared player force/position state contracts."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/player-physics-batch-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['8100']==92416 and r['8116']==77824 and r['8202']==1769472
sources=['src/core/player_forces.hpp','src/core/player_position.hpp','src/core/actor_state.hpp','tests/player_physics_batch_verification_tests.cpp'];exe=root/'work/player_physics_batch_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
specs=[(0x8100,0x8116,'horizontal drag','src/core/player_forces.hpp','SubtractC4F2fromLONG58 modulo32. Negativewrappedresultclears58and121; exactzeroretainsdirection.'),(0x8116,0x8202,'gravity','src/core/player_forces.hpp','NormalmodewhenC514zeroorC519/C51Anonzero: signedpositive122 accelerates6000towardF0000,zero/negative subtracts6000andreflectsnegativewith1221. SpecialmodeusesC481direction:800toward10000 or6000decelerationfloor10000, literalzero/negative122branchesandwrappedlongsigns preserved.'),(0x8202,0x827a,'position integration','src/core/player_position.hpp','Horizontal121zero skipsX; negative subtractsspeed58then signedX<16WORDclamp,positiveadds andunsignedX>=width-ASR.W(width36,1)WORDclamp. Clampsclear121/LONG58andretainfraction14. Verticalnegative122subtractsandclampsnegativelongpositionto0; zero/positiveaddsandsignedY>heightsetsC516FFonly.')]
records=[]
for start,end,name,native,contract in specs:
 at=start;items=[]
 while at<end:
  assert at in accepted
  i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player '+name,native_sources=[native],checked_cases=r[f'{start:X}'],contract=contract,proof='Independentfull130byteoracle. Dragall256directionBYTEs x19speed x19dragboundaryvalues. Gravityall256directionBYTEs x16globalzero/nonzerobranches x19speedthreshold/sign/wrapvalues. Positionall65536coordinate/actorwidthWORDvaluesacross3x3directionpartitionsand3LONGvelocitywrapvalues, independentASR/signmath andglobalheightflagcheck. Completeoriginalspansreviewed; modularaffinetransformsandsignedthresholdpartitionscoverinteriorvalues.',scope='Local typed actor/explicitglobals API. Frameordering, slope/input/terrain/lifecyclecomposition, width/heightproducer andCPUregister/CCR/rawalias/devicecontracts remainexternal; notcompleteplayerphysics orjumpheightcertificate.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/player-physics-batch-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three player force/position contracts verified.')
