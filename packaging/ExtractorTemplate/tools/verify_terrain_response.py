"""Controlled terrain response dispatcher and eight original surface slots."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/terrain-response-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'9196':65536,'slot_counts':[65536,65536,65536,65536,65536,4096,65536,65536]};assert rom[0x924c:0x9250]==bytes([0,1,2,3]) and rom[0x9472:0x9476]==bytes([0,1,2,1])
sources=['src/core/player_terrain_response.hpp','src/core/actor_terrain.hpp','src/core/actor_contact.hpp','src/core/actor_state.hpp','tests/terrain_response_verification_tests.cpp'];exe=root/'work/terrain_response_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0x9196,0x91d4,[(0x9196,0x91d4)],'Terrain response dispatch','Setdrag3000/override0 before8728lookup. Masktile2E00/subtract2000WORD; negativebypassesdispatch; nonnegative8slots fromWORD>>9 (originalbyteoffset>>7). ReadcurrentF268AFTERhandler andpublishpreviousF26A.',65536)]
targets=[(0x9476,0x9486),(0x9434,0x9472),(0x9250,0x925c),(0x9420,0x9434),(0x920a,0x924c),(0x91f4,0x920a),(0x9488,0x948a),(0x9488,0x948a)]
contracts=['IfC512zero,setC517FF;otherwiseunchanged.','Ifcontrolledtype!=12, effect9420. Type12 clears124bit4/setsbit0,62LONGzero; YalignedFFF0 thenADDBYTEbob0/1/2/1 at((ASRframe3)&3); preservefraction.','C5E8zero invokes9476latch;nonzero nochange.','SetC516FF andactor125bit2; preserveallotherstate.','Setdrag300/override800. If121XOR118bit3set,index0; else signedWORDspeed58clampabove3. LookupBYTE924C index0..3 into115; negativeindexunproved/guarded.','SetdragF0000/override8000;noactor/globalotherwrites.','LiteralRTS noobservabletypedstatechange.','LiteralRTS noobservabletypedstatechange.']
for slot,(lo,hi) in enumerate(targets):
 ranges=[(0x91d4+slot*4,0x91d8+slot*4),(lo,hi)]
 if slot==1:ranges.append((0x9420,0x9434))
 if slot==2:ranges.append((0x9476,0x9486))
 specs.append((0x91d4+slot*4,0x91d8+slot*4,ranges,f'Surface dispatch slot{slot}',contracts[slot],r['slot_counts'][slot]))
for start,end,ranges,name,contract,cases in specs:
 items=[];evidence=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi;evidence.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,code_ranges=evidence,verification_status='verified',status='verified green: local '+name,native_sources=[sources[0]],checked_cases=cases,contract=contract,proof='Onebatch:all65536rawtileWORDs withwrappedXY/F268lookupandhandler-mutatedshiftreadback. All65536BYTE121/118pairs,WORDframe/Ypartitions,allBYTEgate/latch/flags through7boundhandlers; slot5actualdispatch4096tilevariants. Independentshared/actorstateoracle comparesall130actorbytes/contactfields/drag/acceleration/previousshift. Originalfullslots+targetbranches andbothimmutable4BYTEtablespinned.',scope='Local stableboundedterrainring andtypedcontrolledactor/state. Slot4 speedWORD0..7FFF whenfacingagrees; negativeoriginaltableindexnotadmitted. ActualC4E0pointeralias/terrainproducer/tableadmission/CPUABI andcompleteframeintegrationremainexternal. Slotgreensincludehandlersemantics,notjustdispatchBRA.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/terrain-response-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Nine controlled surface dispatcher/handler local contracts verified.')
