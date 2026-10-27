"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/shared-frame-services-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,replay_cases=2097152,pool_cases=4096,scratch_cases=256)
sources=['src/core/shared_frame_services.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/shared_frame_services_verification_tests.cpp'];exe=root/'work/shared_frame_services_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0x5c58,[(0x5c58,0x5ce6)],'Enabled gate; signedoldmask setsC518 before5C94; invoke input237Cservice with resulting mask. Disabled returns unchanged.'),(0x5c94,[(0x5c94,0x5ce6)],'Ended gate avoids pairread. Load currentmask;FFsetsendedFF,mask0,latchFF without count/cursorchange. Otherwise matchingduration advancespair2andresetscount0; mismatchincrementsBYTEwrap.'),(0x3bf6,[(0x3bf6,0x3c08)],'Clear exactly40bytes at7410 via20WORDstores, retainneighbours.'),(0x6750,[(0x6750,0x6794)],'Traverse48records ascending130bytes, skipnegativeWORD0 andnullparent76; copy integer12/16/70 plus118/121/122 fromliveparent. Fractions andallotherfields retained; self/back/forwardparent identities allowed.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local shared frame services contract'),native_sources=[sources[0]],checked_cases=2097152 if start in (0x5c58,0x5c94) else 4096 if start==0x6750 else 256,contract=contract,proof='Related batch compares all duration/counterBYTE pairs across16gate/terminal/oldmask partitions and checks inputservice-entry state.4096full48actorpool fixtures compare all130bytes peractor, covering self/back/forward links and inactive/nullparents. Scratch guards and allBYTEfills checked. Initial optimized WORD-sign version mismatched inactiveactor preservation although debug passed; equivalent explicit highBYTEsign check corrected optimized native result. Only failed/changed checks repeated.',scope='Local valid immutable replaypairs with nonwrapping admitted cursor and valid native parent identities. Replay input sampling is an explicit service; device polling and playback scheduling external. Helpers await original caller binding; not a full restart/frame fidelity claim.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/shared-frame-services-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Four shared replay/presentation/scratch contracts verified.')
