import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/companion-slots-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['B1A8']==81920 and r['B28E']==2097152
sources=['src/core/level1_companions.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/companion_slots_verification_tests.cpp'];exe=root/'work/companion_slots_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for a,e,name,contract,proof,scope in [
 (0xb1a8,0xb1c6,'Companion callback publication','ClearC50E then visit exactly three slots in order; skip null; set each actorLONG42 to suppliedD2 callback; preserve C50F and slots.','All256 C50E,64 null/distinct/alias slot combinations and five fullLONG callback boundaries; compare all48 actor records and shared state. Callback write is identity-independent wholeLONG assignment.','Valid slot identities, disjoint native shared state; caller callback domain/scheduling and CPU register/CCR ABI excluded.'),
 (0xb28e,0xb2d2,'Companion slot detachment','Valid BYTE47 domain0..3. Zero returns unchanged;1..3 clear actor47; shift subsequent nonnull slots until first null or third slot end. For each shifted actor decrementBYTE47,WORD50by192,WORD52by24 wrapped; clear vacated slot; preserve allother actor/state bytes.','All65536 timer WORD values paired with inverse secondWORD, allfour valid slot indices, all8 null patterns; independent source-index compaction oracle compares all48 actor records and shared state. BYTE decrement spans all256 values. Full-width WORD decrements checked exhaustively.','Canonical slot0..3 domain, three distinct companion records and separate detachedactor; aliases/malformed indices outside certificate; original wider BYTE domain not certified. Caller/list scheduling and CPU ABI excluded.')]:
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: local '+name,verification_status='verified',native_sources=['src/core/level1_companions.hpp'],instruction_evidence=ins,checked_cases=r[f'{a:X}'],contract=contract,proof=proof,scope=scope))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/companion-slots-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Two companion slot local contracts verified.')
