"""Waiting companion caller branches and live service handoffs."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/companion-waiting-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'A8BC':524288}
sources=['src/core/level1_companions.hpp','src/core/actor_motion.hpp','src/core/level1_progress.hpp','src/core/actor_state.hpp','tests/companion_waiting_verification_tests.cpp'];exe=root/'work/companion_waiting_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]

for start,end,contract in [(0xa8bc,0xa92e,'Zero direction/speed/selector before inactive gate. Active gravity, integration and landing in order. Read live rescue/key/link/action after landing; contact before live follower mode/count. Signed BYTE c50e>=3 with flight mode resets callbacks then attachment. Linked-definition comparison flags overwritten by key TST, not a type gate.') ]:
 at=start;items=[]
 while at<end:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local waiting companion',native_sources=[sources[0]],checked_cases=524288,contract=contract,proof='524288 caller cases with all signed follower count BYTEs, inactive gates, valid linked containers, full/partial/empty slots, landing mutations to link/key/action, and contact mutations to follower mode/count. Compare full48 actor records, all progress fields/flags, slots/counts and ordered service events. Already verified gravity, integration and attachment are child contracts reused by oracle; independent caller branches and state read order are the subject.',scope='Local A8BC caller contract with valid stable actor identity and linked records; collision/contact/services represented by deterministic observable handoffs. Reward allocation failure domain used, remaining counter3..9. Full reward child implementation separately green; arbitrary service ABI and scene admission external.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/companion-waiting-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('A8BC verified.')
