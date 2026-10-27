"""Transport companion alignment: original ordered slots and callback helper."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/transporter-alignment-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'AC34':524288,'AC7A':524288}
sources=['src/core/transporter_companions.hpp','src/core/player_frame_history.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/transporter_alignment_verification_tests.cpp'];exe=root/'work/transporter_alignment_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
assert rom[0xaca4:0xacac]==bytes.fromhex('0000a9b00000aa4a')
for start,end,contract in [(0xac34,0xac7a,'Three live slots in original order; null skipped. Air callback helper copies controlled integer XY; otherwise history base=(cursor-delay-16)&1023, reads two big-endian words. Position fractions and all unrelated fields retained.'),(0xac7a,0xaca4,'Compare full callback LONG against A9B0 and AA4A; match copies live controlled integer XY and returns nonnegative classification; miss preserves actor and returns negative classification.')]:
 at=start;items=[]
 while at<end:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local transporter alignment',native_sources=[sources[0]],checked_cases=524288,contract=contract,proof='Independent ordered record model over all WORD positions/cursors, two matching and six nonmatching full callback values, null and repeated slots, controlled/companion aliases. Compare all 48 actor byte records; helper boolean and whole caller both checked. Original callback table pinned.',scope='Local valid pool identities and history read extents; aligned delay offsets admit index+4<=1024. Controlled actor identity stable during this synchronous no-service routine. CPU register/condition-code ABI represented as boolean, not emulated. Transport activation/destination/animation outside this contract.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/transporter-alignment-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AC34/AC7A verified.')
