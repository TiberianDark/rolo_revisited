import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/level-reset-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'cases':20736}
files=['src/core/level_reset_state.hpp','tests/level_reset_verification_tests.cpp'];exe=root/'work/level_reset_verification_tests.exe';assert exe.stat().st_mtime>=max((p/f).stat().st_mtime for f in files)
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']};records=[]
for a,e,cases,name,contract in [(0x523e,0x5324,20480,'Level contact-state reset','Ordered BYTE/WORD/LONGwrites preserve all unlisted state. C511FF. Samplebit1intoC552, sampleoldbit2intoC553andsetbit2 usingselectorF2F6. SetC4BE3,C4D6250,F2B410. Doesnotclearwholecampaign/score/lives/checkpoint.'),(0x5324,0x5348,256,'HUD publication reset request','ClearC551thenC550 before synchronous26C8request D0LONG0,D1LONGB100,D2WORDFF,D3LONG40000000. Retain service mutations after return; no assumedcompletedVRAMfill.')]:
 at=a;ins=[]
 while at<e:
  assert at in accepted
  i=Decoder(rom,at).decode();ins.append(i);at+=i['size']
 assert at==e
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),verification_status='verified',status='verified green: local '+name,native_sources=['src/core/level_reset_state.hpp'],instruction_evidence=ins,checked_cases=cases,contract=contract,proof='Reviewed complete original spans. Independent expected byte footprint compares full65536BYTEstate for all80selectors x256flag/pattern values. HUDall256patterns checks pre-service state, exact request, one call and service-mutation preservation.',scope='Native semantic state-page API with canonical0..79selector and validdistinctstate storage. No instruction interpreter. HUD26C8service behavior, CPUABI, originalaliases/callerprovenance and live typed-world field bindings remain external; these standalonehelpers are not integrated gameplay resets.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/level-reset-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('523E/5324 local reset and ordered request contracts verified')
