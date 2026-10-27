"""Pin captured-actor local coordinate contract to original boundaries and native results."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1]
rom=(p/'local/rolo.md').read_bytes()
assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text())
accepted={a for r in inv['routines'] for a in r['blocks']}
at=0xb440;instructions=[]
while at<0xb47c:
 assert at in accepted
 i=Decoder(rom,at).decode();instructions.append(i);at+=i['size']
assert at==0xb47c
result=root/'work/captured-actor-results.json';results=json.loads(result.read_text(encoding='utf-8-sig'))
assert results['passed'] and results['B440']==262144
sources=['src/core/level2_actor_updates.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/captured_actor_verification_tests.cpp']
exe=root/'work/captured_actor_verification_tests.exe'
assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest(),records=[dict(address=0xb440,hex='00B440',end_exclusive=0xb47c,original_bytes=rom[0xb440:0xb47c].hex(),instruction_evidence=instructions,verification_status='verified',status='verified green: local captured actor position',native_sources=['src/core/level2_actor_updates.hpp'],checked_cases=262144,contract='Resolve base C4E4 and head84; X WORD=baseX +/- (head32+12), Y WORD=baseY+head34-3, copybase118. Fractions and allotherfields preserved; no117gate.',proof='All65536headXoffsets withfourfacingBYTEpartitions andwrappedbase/Yvalues; compareall130actorbytes andimmutablebase/head records.',scope='Local typed API with valid stable distinct base/head/target records. Caller identity, chain lifetime, scheduling/CPU ABI and whole capture/release gameplay remain external.')])
(p/'docs/stage9/captured-actor-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('B440 local native coordinate contract verified.')
