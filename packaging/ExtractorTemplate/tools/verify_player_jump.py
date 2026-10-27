"""Original jump-input state and sound-request contract, not full airborne physics."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/player-jump-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['79BE']==4194304
sources=['src/core/player_jump.hpp','src/core/actor_state.hpp','tests/player_jump_verification_tests.cpp'];exe=root/'work/player_jump_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
at=0x79be;items=[]
while at<0x7a66:
 assert at in accepted
 i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x7a66
record=dict(address=0x79be,hex='0079BE',end_exclusive=0x7a66,original_bytes=rom[0x79be:0x7a66].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player jump input state',native_sources=['src/core/player_jump.hpp'],checked_cases=4194304,contract='Mappedjumpzero clears124bit3thenholdbranch. Mappednonzero124bit4alsoholdbranch. HeldC486nonzero/negative122/C514zero addsLONG62+2EE0 modulo32. Newjumprequires124bit3clear/bit0set/C514zero;selector70==24sets126bit5only. Othernewjumpsset124bits3/4,clearbit0,122FF;type20speedC0000/sound84,others65E00/sound13.',proof='All256actor124flags and256verticaldirectionBYTEs acrossall8mapped/held/blockgatecombinations, normal/type20 selectors0/24 andLONGspeedzero/FFFFFFFF. Independentdecimalconstant/stateoracle andfull130bytecomparison plusexactone/no soundrequest. Completeoriginalspanreviewed; modularaddition linearitycoversinteriorspeedvalues.',scope='Local typed input/actor API andexplicitsound-request service. Mapped/heldinputproducer andframefrequency, gravity/integration/landing composition, rawaliases/CPUABI/audio playback remainexternal; notfulljumpheight/timing orwholeplayercertificate.')
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/player-jump-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('79BE local jump input contract verified.')
