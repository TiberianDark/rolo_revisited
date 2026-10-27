import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
results_path=root/'work/integer-y-results.json';r=json.loads(results_path.read_text());assert r['passed'] and r['all_fields_checked']==130
sources=['src/core/actor_integer_y_step.hpp','src/core/actor_state.hpp','tests/integer_y_verification_tests.cpp'];exe=root/'work/integer_y_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,offset in [(0xd05a,0xd06c,16),(0xd108,0xd11a,24)]:
 assert r[f'{start:04X}']==16777216
 c=start;ins=[]
 while c<end:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==end and [i['mnemonic'] for i in ins]==['MOVE.W','TST.B','BPL','NEG.W','ADD.W','RTS']
 assert ins[0]['operands']=='D0,(+62,A5)' and ins[1]['operands']=='(+122,A5)' and ins[4]['operands']==f'D0,(+{offset},A5)' and ins[2]['target']==start+12
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),status='verified green: standalone local native state contract; live caller binding pending',verification_status='verified',native_sources=['src/core/actor_integer_y_step.hpp'],instruction_evidence=ins,checked_cases=16777216,contract=f'Write input WORD to speed highword62; add input or its WORD negation to position highword{offset} according to signed directionBYTE122. Preserve fractions and all other fields.',proof='All65536step values and all256direction bytes checked against independent signed arithmetic then WORD wrapping, comparing all130 actorbytes. Arbitrary position addition is modular-linear; sampled position traverses all byte-derived patterns. Original six instructions have one sign branch and no calls.',scope='Complete local native game-state contract. Standalone translation not yet connected to original live callers; no additional playable functionality claimed. CPU scratch register/CCR/ABI replaced by API.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(results_path.read_bytes()).hexdigest())
(p/'docs/stage9/integer-y-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Two standalone native integer-Y contracts verified; caller bindings pending.')
