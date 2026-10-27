import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rpath=root/'work/anchor-step-results.json';r=json.loads(rpath.read_text());assert r['passed'];sources=['src/core/actor_anchor_steps.hpp','src/core/actor_state.hpp','tests/anchor_step_verification_tests.cpp'];exe=root/'work/anchor_step_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,count,contract,proof in [(0xdfe6,0xdffe,786432,'If signed incomingWORD<=signed actorY16, setY highword and copy source directionBYTE122 and speedLONG62; otherwise no writes. Preserve other fields and source.','All65536heightinputs across6signedYboundaries and both source alias/disjoint cases. Branch is signed BGT after CMP.W; direct fieldcopy mirrors same write order. Full130byte comparisons, source unchanged. Remaining Y values use identical signed comparison partitions.'),(0xe0b4,0xe0c2,458752,'SetX highword12=inputX; setY highword16=inputY minus22 modulo65536; preserve fractional positions and every other field.','All65536Xvalues and allYvalues across seven modularly shifted sweeps. Independent signed arithmetic thenWORDwrap. No branches/calls, coordinate assignments independent; proof covers crossproduct without enumerating redundant pairs.')]:
 assert r[f'{start:04X}']==count
 c=start;ins=[]
 while c<end:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==end and ins[-1]['mnemonic']=='RTS' and all(i['flow']!='call' for i in ins)
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),status='verified green: standalone local native state contract; live caller binding pending',verification_status='verified',native_sources=['src/core/actor_anchor_steps.hpp'],instruction_evidence=ins,checked_cases=count,contract=contract,proof=proof,scope='Standalone complete local gameplay-state contract. Live original caller binding pending; no playable feature increase claimed. Temporary CPU registers/CCR/ABI excluded.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rpath.read_bytes()).hexdigest());(p/'docs/stage9/anchor-step-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Two anchor state contracts verified.')
