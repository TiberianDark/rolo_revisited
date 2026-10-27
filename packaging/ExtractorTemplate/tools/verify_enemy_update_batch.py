"""Local passive/roaming update composition proof; external service and terrain domains explicit."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes()
assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/enemy-update-batch-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'))
assert r['passed'] and r['B3C4']==32768 and r['B3F2']==32768
sources=['src/core/level2_actor_updates.hpp','src/core/actor_motion.hpp','src/core/actor_horizontal_collision.hpp','src/core/actor_state.hpp','tests/enemy_update_batch_verification_tests.cpp']
exe=root/'work/enemy_update_batch_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,name in [(0xb3c4,0xb3f2,'passive enemy'),(0xb3f2,0xb440,'roaming enemy')]:
 at=start;items=[]
 while at<end:
  assert at in accepted
  i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local '+name+' update composition',native_sources=['src/core/level2_actor_updates.hpp'],checked_cases=r[f'{start:X}'],contract='Nonzero117 skips. Ordered contact enrollment/query and conditional damage. Roaming signedWORD58<=1 setsinteger speed1, direction service thenfacing-derived121. Trunkpull, deceleration, gravity, integration, landing inoriginalorder; passive thenhorizontalcollision.',proof='All256visibilitybytes,16signed/wrapping/thresholdspeedpartitions,4facingpartitions,bothcontactresults; independentgravity/integration/deceleration oracle andfull130bytecomparison. Service requestsequence andservicefieldmutations checked. Twolevelnative passive order regression separatelypassed.',scope='Local composition withvaliddistinctstableactors, dormantbase52 trunk, emptyterrain ring andexplicitcontact/damage/direction/landing service contracts. Active suction composition, populatedterrain, livecontact allocation/damage identity/lifetime, serviceclobbers andCPUABI remainexternal; notwholeenemybehaviour orfulllevelfidelity.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/enemy-update-batch-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('Two scoped native enemy update composition contracts verified.')
