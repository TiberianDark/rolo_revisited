"""Reviewed player ceiling contact local contract; native data, no ROM execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/player-floor-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'84F4':1048576}
sources=['src/core/player_floor_collision.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/player_floor_verification_tests.cpp'];exe=root/'work/player_floor_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};at=0x84f4;items=[]
while at<0x85e8:
 assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x85e8
record=dict(address=0x84f4,hex='0084F4',end_exclusive=0x85e8,original_bytes=rom[0x84f4:0x85e8].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player floor contact',native_sources=['src/core/player_floor_collision.hpp'],checked_cases=r['84F4'],contract='Clear incoming124bits0/6 and120 before controlled/liveA0 reload. Reach58+62+1WORD. Ascending gates signed62>58; otherwise C545=0 and if58nonzero lowBYTE((62<<4WORD)/58), skip32probe. ProbeY-32,-16,0 by signedreach. First accepted reach stops sequence even unsigned surface rejection. Tile12 toggles shape6; ascending compares low6shape signed versus C545. Land writes120,Y/fraction,groundbit0/clear4,66=old62,122/62LONGzero; nonzero68clear/set124bit6.',proof='Independent integer table/profile lookup and explicit alternative probe selection plus full actor-state oracle. All65536YWORDs x16 metadata/identity/height/F268/zero-denominator partitions; signed direction, reach wrap, inversion, invalid profiles, ascending slope BYTE threshold and fractional preservation. Compare all48actorrecords, liveidentity andC545. Complete original84F4..85E8 boundaries and branches reviewed.',scope='Local stable typed actorpool, canonical floor-query table/ring domain andcontrolledkey. Tests use deterministic bounded metadata/profiles; physical terrain producer, actual globalalias/CPUABI andcompleteframe integration remainexternal. Notfulllevel/floor integration certification.')
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/player-floor-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('84F4 local floor contact verified.')
