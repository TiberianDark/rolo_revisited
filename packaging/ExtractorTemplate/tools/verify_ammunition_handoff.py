import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
ins=[]
for start,end in [(0x7748,0x785c),(0x7ad8,0x7b74)]:
 c=start
 while c<end:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==end
calls=[i for i in ins if i.get('target') in [0x7b74,0x78b8]];reads=[i for i in ins if any(x&0xffffff==0xffc547 for x in i.get('references',[]))];assert [i['target'] for i in calls]==[0x7b74,0x78b8] and reads
rp=root/'work/ammunition-handoff-integration-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['ammunition_handoff_cases']==1024
sources=['src/core/player_actor_world.hpp','src/core/player_movement_phase.hpp','src/core/rolo_action.hpp','src/core/held_object_release.hpp','tests/ammunition_handoff_integration_tests.cpp'];exe=root/'work/ammunition_handoff_integration_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
report=dict(rom_sha256=PIN,scope='C547 shared-state handoff integration; no new green routine or projectile-allocation certificate',original_call_order=calls,original_c547_reads=reads,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},native_checks=r,result_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
(p/'docs/stage9/ammunition-handoff-evidence.json').write_text(json.dumps(report,indent=2)+'\n');print('C547 handoff integration evidence refreshed.')
