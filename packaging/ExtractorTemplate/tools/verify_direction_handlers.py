"""Original literal left/right handlers on typed actor and acceleration API."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/direction-handler-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['796C']==18432 and r['7994']==18432
sources=['src/core/player_direction_input.hpp','src/core/actor_state.hpp','tests/direction_handler_verification_tests.cpp'];exe=root/'work/direction_handler_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,left in [(0x796c,0x7994,True),(0x7994,0x79be,False)]:
 at=start;items=[]
 while at<end:
  assert at in accepted
  i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player '+('left' if left else 'right')+' input handler',native_sources=['src/core/player_direction_input.hpp'],checked_cases=r[f'{start:X}'],contract=('Set118bit3. Selector24returns; elsepositive121negatesC4EA,zero/negative121sets121FF;addwrappedamounttoLONG46.' if left else 'Clear118bit3. Selector24returns; elsenegative121negatesC4EA,zero/positive121sets1211;addwrappedamounttoLONG46.'),proof='All256directionBYTEs x3selectorpartitions x6accelerationboundarypartitions x4LONG46wrapvalues; independentfull130byteoracle. Completeoriginalspansreviewed; linear32bitmodulartransformscoverinterioracceleration/speedvalues. Liveplayer_direction_input refactoredtousetheseexacthelpers; existingdirectionintegrationtestpassed.',scope='Local typed actor andexplicitC4EAacceleration API. Acceleration/table/inputproducer, full78B8phase/calleridentity, CPUABI/rawaliases remainexternal; notfullplayerinputfidelity.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/direction-handler-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two literal directional handler contracts verified.')
