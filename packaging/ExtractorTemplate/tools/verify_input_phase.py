"""Native input phase composition with separately verified jump/action/direction APIs."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/input-phase-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['78B8']==524288
sources=['src/core/player_input_phase.hpp','src/core/player_direction_input.hpp','src/core/player_jump.hpp','src/core/rolo_action.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/input_phase_verification_tests.cpp'];exe=root/'work/input_phase_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
at=0x78b8;items=[]
while at<0x79be:
 assert at in accepted
 i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x79be
switch=Decoder(rom,0x8810).decode();assert 0x8810 in accepted and switch['operands']=='#$00001E20,($FFFFC444).L'
record=dict(address=0x78b8,hex='0078B8',end_exclusive=0x79be,original_bytes=rom[0x78b8:0x79be].hex(),instruction_evidence=items,switch_service_evidence=switch,verification_status='verified',status='verified green: local shared player input phase',native_sources=['src/core/player_input_phase.hpp','src/core/player_direction_input.hpp'],checked_cases=524288,contract='Mapped4andstate1C6C requests1E20 via8810; jumpusesmapped6alsoC486heldalias. Saveactoraround7A66action; restorebefore125bit3gate. SelectwalkC4EA8000/tables7E58,7EE0 orrun10000/tables7F68,7FF0; nonzeroC4EE overridesaccelerationonly. Mapped0/1noops; leftthenright mapped2/3 appliedonrestoredactor. C487aliasesmapped7.',proof='All256inputbitmasks x256actor/globalflagpartitions x4types x2overridepartitions. Reusesindependentlycertifiedjump/action components; independentdirectionoracle andexplicitoriginalbookend/handoffmodel. Companionserviceschangeactorpointerandpostaction125bit3toexerciserestoration/order. Compareall48actorrecords,state/acceleration/table/mappedidentityandsound/callbackeventorder. Staticwholephaseanddirectionhandlersreviewed; notmerelycomponenttesttotals.',scope='Local typed stablevalidactor/base/head/controlledidentity, immutablemappedarrayduringcall, C486==mapped6/C487==mapped7. Companioncallbacks andsoundoutputsremainexplicitservices. Hardwareinputsampling/IRQ/framefrequency, mismatchedaliases/callers, CPUABI/deviceaudio/fullplayerframestate remainexternal.')
deps=['docs/stage9/player-jump-verification.json','docs/stage9/action-dispatch-verification.json','docs/stage9/direction-handler-verification.json'];report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+deps},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/input-phase-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('78B8 shared local input phase verified.')
