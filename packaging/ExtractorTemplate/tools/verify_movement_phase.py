"""Original normal/damage movement phase composed from certified native force APIs."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/movement-phase-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['7748']==524288
sources=['src/core/player_movement_phase.hpp','src/core/player_acceleration.hpp','src/core/player_forces.hpp','src/core/player_position.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/movement_phase_verification_tests.cpp'];exe=root/'work/movement_phase_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
at=0x7748;items=[]
while at<0x785c:
 assert at in accepted
 i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0x785c
record=dict(address=0x7748,hex='007748',end_exclusive=0x785c,original_bytes=rom[0x7748:0x785c].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local shared movement phase',native_sources=['src/core/player_movement_phase.hpp'],checked_cases=524288,contract='SaveinitialXYto20/24andclear46beforeC524gate; deriveC514fromC513/C510. Normalheldrelease/reloadcontrolled/drag/interactions/input;125bit3returnselseacceleration/slope/gravity/position andC515directioncopy. NegativeC519launch65E00/upFF/timer10; damageforces thenunchangedXclears58/121, ground/cameraY+224unsignedgate decrementsC519. NonpositiveexpirysetsC51AFF; type4C5CB/C51Ddeathguards, otherstypeC542=BYTE(3+C50F).',proof='All256actor/globalflagpartitions xall256C519BYTEs x8modepartitions. ComponentforceAPIs separatelycertified; independentbranch/handofforacle changescontrolled/liveidentities inservices andcomparesall48actorrecords,relevantsharedstate,table-slot/serviceeventorder. IncludesC524presnapshotgate,normalpostinputreturn,negativehitlaunch,ground/fallwindow,deathbyteunderflow andcompanionrecovery. Fulloriginalspanreviewed/pinned.',scope='Local typed phase withvalidstableactoridentities andexplicitheld/interactions/input/slope/death services. Fixturesusezero slope acceleration tablewithcertifiedforcecomposition. Complete serviceeffects/admission andcoupledglobalaliases/CPUABI/wholeplayerframe/lifecycle remainexternal. Deathservice contract includes63FAandC444=15AA publication; notwholedeathscene verification.')
deps=['docs/stage9/player-slope-verification.json','docs/stage9/player-physics-batch-verification.json'];report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+deps},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/movement-phase-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('7748 local normal/damage movement phase verified.')
