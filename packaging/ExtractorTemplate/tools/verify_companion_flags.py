import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/companion-flags-results.json';r=json.loads(rp.read_text());assert r['passed'] and (r['AE86'],r['AF80'],r['B2E6'])==(65536,4194304,327680)
sources=['src/core/level1_companion_motion.hpp','src/core/level1_key_actor.hpp','src/core/actor_state.hpp','tests/companion_flags_verification_tests.cpp'];exe=root/'work/companion_flags_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
specs=[(0xae86,0xaeb4,'Ground flag transition mirror','Clear124bit7,copy124bit0into125bit0;set124bit7iffprevious125bit0differs. All65536 input flag pairs; all130bytes compared.'),(0xaf80,0xb00a,'Companion animation selector','Selector priority: jumping8,airborne12,groundwalking4; following flag46bit1 compareswholefacingBYTE,controlledselector24,controlledLONG46anddirection121; fallback24or0. All256flagsx256phasebytesx64control/velocity fixtures. OnlyWORD70written; controlled actor preserved. Unreachable AFF2 selector16 retained as original bytes, no claim of externally entered fragment coverage.'),(0xb2e6,0xb314,'Key actor proximity activation','117nonzeroreturnsunchanged;zero sets70zero thenwrappedXdifference, BPL/NEG.W absolute, unsigned<=100 setscallback42B314. EveryWORDdifference across five representative zero/nonzero status masks; fullactorstate/readcount compared. 32768 remains unsigned32768 and rejects.')]
records=[]
for a,e,name,contract in specs:
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: local '+name,verification_status='verified',native_sources=[sources[1] if a==0xb2e6 else sources[0]],instruction_evidence=ins,checked_cases=r[f'{a:X}'],contract=contract,proof='Reviewed complete canonical-entry instruction span and branches; independent predicate/modular oracle compares all130actorbytes. Tests partition zero/nonzero fields and relevant bit flags; signed/unsigned distinction explicitly preserved.',scope='Canonical local native API with valid separate actor/control state; caller scheduling, sprite publication, definition/lifecycle domains and CPU temporary registers/CCR/ABI excluded. Externally entered inline fragments not certified.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/companion-flags-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Three companion/key local contracts verified.')
