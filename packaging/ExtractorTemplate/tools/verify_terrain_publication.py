"""Original terrain publication wrapper/ordered row contracts, no ROM execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/terrain-publication-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'cases':71680}
files=['src/core/terrain_display.hpp','src/core/terrain_camera_world.hpp','src/core/terrain_streaming.hpp','src/core/terrain_stream_rows.hpp','src/core/actor_state.hpp','tests/terrain_publication_verification_tests.cpp'];exe=root/'work/terrain_publication_verification_tests.exe';assert exe.stat().st_mtime>=max((p/f).stat().st_mtime for f in files)
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
for address,end,prefix,name in [(0x7450,0x74e2,0x4158,'Top row publication'),(0x74e2,0x7588,0x42e4,'Right column publication'),(0x74f6,0x7588,0x42bc,'Left column publication')]:
 at=address;instructions=[]
 while at<end:
  i=Decoder(rom,at).decode()
  if at not in accepted:
   assert at==0x74b6 and i['mnemonic']=='EXG','Unreviewed original boundary'
  instructions.append(i);at+=i['size']
 assert at==end and instructions[0]['target']==prefix and instructions[-1]['mnemonic']=='RTS'
 records.append(dict(address=address,hex=f'{address:06X}',end_exclusive=end,original_bytes=rom[address:end].hex(),verification_status='verified',status='verified green: local ordered '+name,native_sources=['src/core/terrain_display.hpp','src/core/terrain_camera_world.hpp'],instruction_evidence=instructions,checked_cases=65536+2048,contract='Invoke matching row/column preparation before publication. Top:21cells right-to-left fromF374 and(F372+40)&126. Right:15cells bottom-to-top from(F374+0700)&plane8 and(F372+40)&126. Left:same15cellorder withunmaskedF372. Tilelow9quadindex; replicate9000flags intoall4WORDs; bit12swaps two destination rows. Typedoffset=(ringoffset*2)&0F7C,secondoffsetOR128; two ordered row requests percell.',proof='Full source spans reviewed including shared7500tail. All65536tileWORDs exerciseignoredattribute bits, quadindex, flags andverticalswap. Everycanonical32ringrows x64columns x3directionwrappers checkscompleteorderedpublication after actualnativepreparation onemptyMAP. Plane/globalringfields preserved. 74E2span includes74F6entry as unexecutedfallthrough; branch74F4targets7500. Dead74B6EXG review is explicit.',scope='Local ordered publication API forcanonicalF372even0..126,F374128multiples0..1F80,plane8=1F80andvalidbacking/quadtables. Prefill4158/42E4/42BC/MAP sideeffects are delegated services, testedwith emptyMAPonly; fullnonemptyMAP/alias/producer domains, VDPbasecommandbinding/IRQ/queue timing andCPUABI remainexternal. Thisisnot wholeterrainstreamingfidelity.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/terrain-publication-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Three existing terrain publication local contracts verified.')
