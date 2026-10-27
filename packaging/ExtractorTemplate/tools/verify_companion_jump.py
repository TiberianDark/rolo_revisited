import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/companion-jump-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['B0D6']==1245184;sources=['src/core/level1_companion_motion.hpp','src/core/actor_state.hpp','tests/companion_jump_verification_tests.cpp'];exe=root/'work/companion_jump_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
c=0xb0d6;ins=[]
while c<0xb114:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0xb114 and ins[-1]['mnemonic']=='RTS' and all(i['flow']!='call' for i in ins)
record=dict(address=0xb0d6,hex='00B0D6',end_exclusive=0xb114,original_bytes=rom[0xb0d6:0xb114].hex(),status='verified green: complete local automatic-companion jump gate',verification_status='verified',native_sources=['src/core/level1_companion_motion.hpp'],instruction_evidence=ins,checked_cases=1245184,contract='Jump only if124bit4clear, selectorWORD70!=24, BYTE49zero, and124bit0orbit7set. Onjump122FF/speedLONG6285000/set124bit4. ClearBYTE49inallpaths. Preserveeveryotherbyte.',proof='WholeB0D6..B114 reviewed; no callees. All65536animationselectorWORDs with8ground/jump/edgeflagfixtures and2BYTE49gatepartitions; all256flagBYTEsx256gateBYTEsx3selectorfixtures. Full130bytecomparison. Gateconjunction factorisesfourindependentpredicates; exactconstantwrites givecompleteinteriorselector/flagcase proof.',scope='Complete local native actor-state contract. Callerfollow/jump requests, input-controlled bunny movement, animation scheduling andCPUtemporaryregister/CCR/ABI remainseparate.',fix='Restored missing original already-jumping/selector24/ground-or-edge gates; BYTE49clear remainsunconditional.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/companion-jump-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Automaticcompanionjumpgatesverified; missingnativegatesrestored.')
