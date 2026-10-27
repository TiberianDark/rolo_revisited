"""Pin local injury branches and valid original phase tables; no ROM execution."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
result=root/'work/actor-rescue-presentation-results.json';r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,rescue_cases=2097152,held_cases=524288,probe_cases=393216)
sources=['src/core/actor_rescue_presentation.hpp','src/core/actor_state.hpp','tests/actor_rescue_presentation_verification_tests.cpp'];exe=root/'work/actor_rescue_presentation_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
assert rom[0xdb16:0xdb44].hex()=='00000000fffe00000000fffdfffd00000000fffefffe000000000000000000000000000000000000000000000000'
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xe712,[(0xe712,0xe776)],'Existinglatchsetsselector4. Unlatchedobjectcontactnonzeroorselector8requestslinkedWORD74 actor;definitiontype56required. SetlatchFF,clearlinked58LONG,clear119bit4;E798type56callbackA8BC service; savedlinkedpointergetsE776 callback despite liveA5changes,thenliveA5selector4. Otherpathplayercontact/damage returns withoutfinalselectorwrite.'),(0xda72,[(0xda72,0xdb16)],'F280enabled/C512zero gate publishesactorWORDandzerosentinel. Copyhead118and125bit1. SignedclampheldYfromheadsupportbit5orheld24 toheadY+body34-body38+8. Selector70/2indexesoriginalWORDoffsettable; facingnegatesbody32andtableoffset beforeheadXsum. FinallylivebodyY+34-38+7 writesheld24,includingaliases.'),(0xddaa,[(0xddaa,0xddf4)],'Query8728 at X+ASRwidth36/2+8,Y+34-ASRheight38/2,wrappedWORDs. If tilebit13clear andclassE00returnnegative. Otherwisebit14requires87DCgeometrylowBYTE&3Fnonzero; allotherpathsreturnzero.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),original_bytes=rom[start:max(b for a,b in ranges)].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: local rescue presentation and terrain predicate contract',native_sources=[sources[0]],checked_cases={0xe712:2097152,0xda72:524288,0xddaa:393216}[start],contract=contract,proof='One focused familycheck:2097152rescuefixtures covermutableA5,linkedselfalias,latch/type/contactbranches,fullactorrecords andeveryserviceentry;524288heldfixtures coverall23tableWORDs,head/body/heldaliases,gatesandsignedclamps;393216terrainfixtures coverall65536tileWORDs withsixgeometrymaskclasses,queryarithmetic andshortcircuitservicecounts. Originalheldtablepinned.',scope='Localvalidactors;heldheadselectoraligned0..88 only. Livehead/bodyresolvedbeforeentry,finitevalidlinks andtypeddefinitiontype/roster/contact services. Actualcallerselectorproduction,rosterE798implementation,geometry87DC/terrain8728services andSDLbinding remainexternal. The terrain predicate returns typednegative/zero status; notcompleteCPUCCR.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/'docs/stage9/actor-rescue-presentation-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three rescue/presentation/probe contracts verified.')
