"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-contact-family-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,actor_cases=3670016)
sources=['src/core/actor_contact_family.hpp','src/core/actor_common_callbacks.hpp','src/core/first_enemy.hpp','src/core/actor_motion.hpp','src/core/actor_state.hpp','tests/actor_contact_family_verification_tests.cpp'];exe=root/'work/actor_contact_family_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
import struct
assert list(rom[0xda6c:0xda72])==[2,1,1,1,2,3]
assert list(struct.unpack_from('>8h',rom,0xd820))==[-4,0,-4,-2,-4,2,-4,0]
assert list(struct.unpack_from('>8h',rom,0xe10a))==[16,39,62,85,108,131,154,177]

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xe5a4,[(0xe5a4,0xe5d0)],'117gate, object/playercontact/conditionaldamage, integerwalk1,direction,gravity,integration,floor inoriginalorder.'),(0xe6d8,[(0xe6d8,0xe712)],'117gate; objectcontact/playercontact. Hitdirecthurt thenselector4/callbackA84C. Missgravity/integration/floor thenactivateonlyifgroundbitset.'),(0xf856,[(0xf856,0xf8aa)],'Playercontact/directhurt; signed46>112 selectsintegerXstep6andhalfY,elseintegerY+6andhalfX. Live122zero inhibits halfpixel,negative subtracts,positiveadds.'),(0xe0c2,[(0xe0c2,0xe10a)],'Clear118bit3 beforecontact/directhurt. LiveBYTE46nonzero gravity/integrates. Else wrappedabsoluteWORDdistance signedcomparedto eightthresholds indexedcontrolled58&7;withinlimit sets46BYTEFF.'),(0xdbbe,[(0xdbbe,0xdc2c)],'117gate/objectcontact/playercontact/directhurt. NonzeroWORD46 gravity/integrates then signedanchor<=YclampsintegerY,setsground,clears46. Zero46 cachesY,clearsground,setsup122FF/speed68000. Original signedabsoluteWORDdistance>7FFFbranch unreachable for everyWORD.'),(0xda22,[(0xda22,0xda6c)],'117gate/contact/damage.114nonzero returns. AdmittedBYTE46phase0..5 increments/wraps6; sixspeedBYTEtable writesWORD58,integerXaddsignedbyfacing,thenD168.'),(0xd7e6,[(0xd7e6,0xd820)],'Selector4earlyreturn. Contact/damage canchangeactor; onhitsetsselector4 thenstillmoves. Admitted48BYTE1..4 selectsfixedWORDXYpair,addsintegers,retainsfractions.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor contact family contract'),native_sources=[sources[0]],checked_cases=524288,contract=contract,proof='One focused sevenroutine batch3670016fullrecordcases. AllWORDphase/positions across8gate/contact/timer partitions; allBYTEdirections/flags, original tables pinned, meaningfulmutatingservices. Complete130byte actorstate plus every serviceentrysnapshot andcallorder checked against independentbranch/arithmetic model. DBBEunreachable signed>7FFF comparison removed byfiniteWORDdomain proof.',scope='Local native state andordered mutable childservice contracts. Contact/damage/gravity/integration/floor/direction services retain their own closure obligations; not wholeenemy fidelity. DA22 phase0..5 aftercontact andD7E6 phase1..4 aftercontact explicitly admitted; invalidstructuralstates rejected. New callbacks await live world binding.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-contact-family-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Seven contact-driven actor contracts verified.')
