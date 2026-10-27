"""Reviewed player ceiling contact local contract; native data, no ROM execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/player-ceiling-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'8376':524288}
sources=['src/core/player_ceiling_collision.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/player_ceiling_verification_tests.cpp'];exe=root/'work/player_ceiling_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};at=0x8376;items=[]
while at<0x842e:
 assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x842e
record=dict(address=0x8376,hex='008376',end_exclusive=0x842e,original_bytes=rom[0x8376:0x842e].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player ceiling contact',native_sources=['src/core/player_ceiling_collision.hpp'],checked_cases=r['8376'],contract='Clear incoming125bit7 before reload controlled/liveA0. ReachWORD58+62+1. Positive signed122 starts lastprobe; otherwise offsets32,16,0 fromY-height. Missing/too-far/unsigned-below candidates advance originalA2continuations. Accepted surface+height+1 replacesY, fractionzero. Nonpositive direction zeros122/62LONG and sets125bit7; positive preservesmotion. Preserve all other actorfields.',proof='Independent explicit continuation alternatives and integer surface/descriptor calculation; all65536YWORDs x8 terrain/identity/height/shift partitions. All directionBYTEs, signedreach boundaries/wrap, tile solidity and inversion, profileinvalid, fractionalpreservation, incomingdistinct/identicalcontrolled. Compare all48actorrecords andliveidentity. Complete original8376..842E boundaries andbranchesreviewed.',scope='Local stable typed actorpool, canonical ceiling-query table/ring domain andcontrolledkey. Tests use deterministic bounded metadata/profiles; physical terrain producer, actual globalalias/CPUABI andcompleteframe integration remainexternal. Notfulllevel/ceiling integration certification.')
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/player-ceiling-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('8376 local ceiling contact verified.')
