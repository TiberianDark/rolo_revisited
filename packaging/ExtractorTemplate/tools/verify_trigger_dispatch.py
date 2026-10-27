"""Original controlled trigger scan and all18 dispatch slots, native handoffs."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/trigger-dispatch-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'925C':262144,'slots':18,'cases_per_slot':4096}
sources=['src/core/player_trigger_dispatch.hpp','src/core/player_trigger_scan.hpp','src/core/player_trigger_pool.hpp','src/core/player_terrain_response.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/trigger_dispatch_verification_tests.cpp'];exe=root/'work/trigger_dispatch_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0x925c,0x92f2,[(0x925c,0x92f2)],'Controlled trigger scan','SnapshotplayerXY. BoundsWORDwrapped referenceX-368..+1056,Y-240..+704; iteratefinite16recordlinkedlistinliveorder. Outsidebounds4ADCrestore/release. Inside17pxinclusivebox:consumeif11nonzero, A1lowWORDfrom4AF4replacesleftbound; read8WORDdispatchAFTERconsume. DispatchpreservesA0/A1etccontext; next2WORDreadAFTERdispatchmutation. Actualplayerpositionchangesdontresnapshot.',r['925C'])]
targets=[(0x93fe,0x9420),(0x9420,0x9434),(0x9434,0x9472),(0x9476,0x9486),(0x9486,0x9488)]+[(0x9488,0x948a)]*11+[(0x933a,0x937a),(0x937a,0x93fe)]
contracts=['Type4onlycopycontrolledinteger12/16toC4FE/C500checkpoint.','Surfaceeffectslot3 via9420.','Surfaceeffectslot1 via9434; typedserviceowns12vsothercontrolledtypebranch.','Surfaceeffectslot0 via9476.']+['LiteralRTS; typedstateunchanged.']*12+['Type4onlynextselector=parameter&127,F26C=parameterbit7,F26D/C522FF; sound1Dafterstatewrites.','3EE4destinationnegative skip; sound1DthenReset63FA. ReloadLIVEcontrolledactor AFTERreset; setdestinationXYandfraction14/18zero,121/122zero,58/62LONGzero. Invoke684E,6864,4CB8,7292,72A2,6960,6AA6,31D6,25A8,66DEorderedservices. Livecontrolledtype4 afterthosecalls invokesAC34.']
assert len(targets)==len(contracts)==18
for slot,(lo,hi) in enumerate(targets):
 start=0x92f2+slot*4;ranges=[(start,start+4),(lo,hi)]
 if slot==2:ranges.append((0x9420,0x9434))
 specs.append((start,start+4,ranges,f'Trigger dispatch slot{slot}',contracts[slot],4096))
for start,end,ranges,name,contract,cases in specs:
 items=[];evidence=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi;evidence.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,code_ranges=evidence,verification_status='verified',status='verified green: local '+name,native_sources=[sources[1] if start==0x925c else sources[0]],checked_cases=cases,contract=contract,proof='All18entries x4096parameter/type/transitionmutationcases. Independentstate/orderedhandoffmodel compares48actorrecords,checkpoint/progressionlatches,controlledidentity/type andsurface/transition/soundevents. Transportresetretargetscontrolledactor; final66DEcanmutatetypebeforeAC34gate.262144scannerWORDcoordinate/finite1..16recordcases comparewholepool andevents; consumeclobbersleftbound/dispatchfield, dispatchmutateslivenext,playerXYchangeskeepssnapshot. Originalslots+targetfullboundariesreviewed;sharedRTSentriesremainseparateoriginalcandidates,notdistinctfeatures.',scope='Local valid18slots andfiniteacyclic16recordscan,validactoridentities. Explicit3EE4destination/surface/transition/soundservices replaceoriginalcallers; fullfade/terrainrebuild/graphics/SFX/AC34semanticsandCPUregisterABI external. ParameterBYTEdomain. ActualPooledunlinkhelpersseparatelyverified; testservicespreserveoriginalA0/A1cursorconventionexceptdeclared4AF4clobber. Notfulltransporter/exit/gameplayfidelity.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/trigger-dispatch-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('19 original trigger scan/dispatch local contracts verified.')
