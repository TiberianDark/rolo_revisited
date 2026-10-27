"""Register reviewed local collision followups after one native differential batch."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/collision-followups-results.json';result=json.loads(rp.read_text(encoding='utf-8-sig'));assert result['passed']
sources=['src/core/player_collision_followups.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/collision_followups_verification_tests.cpp'];exe=root/'work/collision_followups_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,key,contract in ((0x842e,0x8482,'842E','Signed aligned old/current X compare; equal returns. 8728 shifted current XY lookup; tile bit14; 87DC for signed greater, otherwise87F6. Shape low6==1 sets only Y WORD=(Y&FFF0)+1, preserving fraction.'),(0x8482,0x84f4,'8482','Top probe Y-height WORD; signed direction BYTE negative selects X-8/87F6 otherwise X+8/87DC includingzero. 8728 returns shifted probeX. Tile14/shape low6==1 sets X WORD aligned probe+23 or-8; sets124bit1 or2, preserves fraction/all other fields.')):
 at=start;items=[]
 while at<end:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end and result[key]==1048576
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player collision followup',native_sources=[sources[0]],checked_cases=result[key],contract=contract,proof='Independent branch/WORD arithmetic model compares all130actorbytes. All65536 X WORDs x16 partitions; old/current equal, positive/negative crossing and sign boundary; all direction/flag/shape BYTE values across matrix; low6 masking, solidity, ring wrapping, F268 shifts0/FFF9, Y/height wrap and fractional preservation.',scope='Local controlled ActorState reference and stable bounded ring/collision table. Canonical8728/87DC/87F6 typed effects; original A5/global pointer admission, physical terrain publication and complete caller/frame/CPUABI integration remain external.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/collision-followups-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two local collision followups verified.')
