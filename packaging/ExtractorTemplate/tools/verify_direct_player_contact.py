"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/direct-player-contact-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'976C':327680,'passed':True}
sources=['src/core/actor_direct_contact.hpp','src/core/actor_contact.hpp','src/core/actor_defeat.hpp','src/core/actor_state.hpp','tests/direct_player_contact_verification_tests.cpp','docs/stage9/player-damage-verification.json'];exe=root/'work/direct_player_contact_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources if not s.endswith('.json'))

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0x976c,[(0x96f2,0x97ac)],'Directentry bypassesground/vertical chooser. C512nonzero takesprimaryinjury96F2 includingactor129/hitgates. Otherwise definition7bit0/actiongate/hitgatesblock; elseC517FF,return1. Primaryinjuryuses existing96C6bodywithoverridealready nonzero, preservingall actor/global/parentandserviceeffects.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local direct player contact contract'),native_sources=[sources[0]],checked_cases=327680,contract=contract,proof='One focused native check:256gatepartitions x256counterbytes x4relevantdefinitionbits plus65536positionfixtures. Independent directentryoracle comparesall130bytesofactor/control/parent,allglobals,return,sound/definition/parent/defeateventcounts. Actualexistingdefeathelper exercised. Primary delegation has overridealreadyset, making96C6chooser irrelevant without mutatingcontrolledstate.',scope='Local direct contact/latch/injury contract for distinct stable records and immutabledefinitionservice. Explicit sound/defeatservice boundaries retain existing96C6proof domains; audio, wideralias, allocation and gameplay scheduler external. This is the direct976Centry, not a new hit-detection implementation.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/direct-player-contact-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Direct976Ccontact contract verified.')
