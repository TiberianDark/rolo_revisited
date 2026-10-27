import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1]
rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/horizontal-direction-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['D168']==8650752
sources=['src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/horizontal_direction_verification_tests.cpp']
exe=root/'work/horizontal_direction_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
dep='docs/stage9/terrain-query-verification.json';assert any(x['address']==0x874c and x['verification_status']=='verified' for x in json.loads((p/dep).read_text())['records'])
c=0xd168;ins=[]
while c<0xd1ca:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0xd1ca and {i['target'] for i in ins if i['flow']=='call'}=={0x874c}
record=dict(address=0xd168,hex='00D168',end_exclusive=0xd1ca,original_bytes=rom[0xd168:0xd1ca].hex(),status='verified green: local horizontal direction terrain gate',verification_status='verified',native_sources=['src/core/actor_terrain.hpp'],instruction_evidence=ins,checked_cases=r['D168'],contract='Signed X<=0 selects right without width/terrain reads. Else signed world width<=X selects left without terrain reads. Otherwise canonical874C(X,Y-16 WORDwrapped), then definitionBYTE26&7 threshold. Class<=threshold preserves direction. Class>threshold selects right if X bit3 set, left otherwise. Right clears118bit3 and writes121=1; left sets118bit3 and writes121=FF. All other actor bytes preserved.',proof='Reviewed complete D168..D1CA boundaries, two RTS exits and signed TST/CMP/BLE guards. Original signed endpoint comparisons remain valid across overflow; class and threshold 0..7 cannot overflow CMP.B. Independent integer-coordinate/ring-index oracle compares all130bytes and service-read ordering. Every WORD X across eight signed width boundaries and16class fixtures; all256ring high bytes and256definition bytes at four bit3 positions. Canonical874C dependency pinned separately.',scope='Complete local actor/services API contract with valid immutable terrain and definition. Live enemy callers already use actor_choose_direction. Caller scheduling, terrain publication, CPU temporary registers/CCR/ABI and malformed service aliases remain outside certificate.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/horizontal-direction-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('Horizontal direction local contract verified.')
