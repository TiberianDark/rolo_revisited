import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
results_path=root/'work/terrain-query-results.json';results=json.loads(results_path.read_text());assert results['passed']
sources=['src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/terrain_query_verification_tests.cpp'];exe=root/'work/terrain_query_verification_tests.exe'
assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,cases,proof in [(0x8728,0x874c,4128768,'ADD.W x shift wraps to16 bits. Mask03F0 then ASR3 gives even column offset0..126; Y mask03F0 then ASL3 gives row offset0..8064. Their sum selects one of4096 big-endian WORDs. Native coordinate oracle uses independent division/modulo row-column formulation; all65536 X values, seven shift wrap representatives and nine Y row boundaries checked. All remaining Y values partition identically by masked row bits. Ring bytes are read-only; any WORD payload is assembled identically.'),(0x874c,0x879a,16777216,'Canonical entry masks D0 to03F0 then shifts3: upper WORD bits including14 are zero. MOVE.B retains those upper bits, so BTST14 is alwayszero and descriptor path8770..878E cannot execute. If loaded highbyte bit5 set, return0; else return bits1..3. All256 highbytes and65536 X values tested. Masked coordinate indexing is same proven row-column formula; no x_shift applies. Native API certifies return value and read-only terrain state; CPU scratch registers and CCR are outside API.')]:
 assert results[f'{start:04X}']==cases
 c=start;ins=[]
 while c<end:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==end and ins[-1]['mnemonic']=='RTS' and all(i['flow']!='call' for i in ins)
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),status='verified green: complete local native state contract',verification_status='verified',native_sources=['src/core/actor_terrain.hpp'],instruction_evidence=ins,checked_cases=cases,proof=proof,scope='Canonical entry native return/read-only data contract. Valid8192byte terrain ring required. Callers, producer state, CPU temporary registers/CCR and scheduling not certified.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(results_path.read_bytes()).hexdigest(),records=records)
(p/'docs/stage9/terrain-query-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Two terrain-query native contracts verified.')
