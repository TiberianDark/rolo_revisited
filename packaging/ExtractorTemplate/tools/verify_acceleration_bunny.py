"""Direction/magnitude acceleration family and bounded world-bunny callback."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/acceleration-bunny-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'family_cases':524288,'slot_cases':65536,'slots':9,'E7BE':524288}
sources=['src/core/actor_acceleration.hpp','src/core/world_bunny.hpp','src/core/actor_motion.hpp','src/core/animation.hpp','src/core/actor_state.hpp','tests/acceleration_bunny_verification_tests.cpp'];exe=root/'work/acceleration_bunny_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[];specs=[]
for start,end,axis,positive in [(0xd06c,0xd094,0,True),(0xd094,0xd0ba,0,False),(0xd0ba,0xd0e2,1,True),(0xd0e2,0xd108,1,False)]:
 specs.append((start,end,[(start,end)],f'Actor acceleration axis{axis} '+('positive' if positive else 'negative'),r['family_cases'],'D0LONGincrement,D1LONGsignedcap. Opposingdirection subtractswith32bitwrap; resultNclear(inclzero)retainsolddirection, Nsetnegatesmagnitudeandsetsnewdirection. Same-direction/zeroaddswrappedincrement, signedspeed>signedcapclamps, setdirection+1/FF. Onlyaxis58/62LONGand121/122BYTEchange.'))
specs.append((0xe7be,0xe912,[(0xe7be,0xe912)],'World bunny update',r['E7BE'],'CFCEintegrationfirst. SignedintegerXYclampsto264..width-264/272..height-256, clampedaxisLONGspeedzero/46BYTEzero,fractionsretained. D0=4000/D1=20000accel. Pausedindependentup/down/left/rightbuttonsruninorder(noautotimer/RNG). Autonomous50WORD--negativeclears46;mode0rolls1..8directionand40..49timerthenredispatch;1..8directionactionswithfacing. Newacceldoesnotmoveuntilnextcallback.'))
targets=[(0xe84c,0xe872),(0xe872,0xe878),(0xe878,0xe888),(0xe888,0xe894),(0xe894,0xe8a4),(0xe8a4,0xe8aa),(0xe8aa,0xe8ba),(0xe8ba,0xe8c6),(0xe8c6,0xe8d6)]
for slot,(lo,hi) in enumerate(targets):
 start=0xe83a+slot*2;specs.append((start,start+2,[(start,start+2),(lo,hi)],f'World bunny direction slot{slot}',65536,'Slot0canonical716E(1,9)/(40,50)selectionandredispatch; other1..8up,up-right,right,down-right,down,down-left,left,up-left. Canonical4000increment/20000cap; leftsets118bit3,rightclears. Originalface-before-vertical orderingcommuteswithvertical-onlytypedacceleration; noexternalobserverbetweenwrites.'))
for start,end,ranges,name,cases,contract in specs:
 items=[];evidence=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi;evidence.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,code_ranges=evidence,verification_status='verified',status='verified green: local '+name,native_sources=[sources[0]] if start<0xe7be else [sources[1]],checked_cases=cases,contract=contract,proof='Independent64bitsigned/moduloarithmetic anddeclarativeaxis-actionoracle. All65536directionBYTEpairs/speedseedpartitions x8increment/capboundariesforeachof4familymembers;32bitcarry/N/zero/negativecap partitions.9dispatchslotsall65536seeds/flags;rootfullactorcallbackpaused/autonomous/coordinateWORD/fraction/counterpartitions. Manual716ELCGoracle, notnativeRNGreuse. Compareall130actorbytes/randomseed. Wholeoriginalranges/slot-targetbranchesreviewed.',scope='Genericfamilytyped32bitincrement/capandaxis0/1; validActorState. Bunnyrootoriginal1280x1280map andinitialmodeBYTE0..8domain, validfinite716Eranges; inputBYTEzero/nonzero. Actualactor/tableproducer/admission,rawregisterABI/IRQandcompleteoverworldactorframe integrationremainexternal. Slotsareoriginalinventoryentrieswithlocaldirectioncontrolsemantics,notdistinctfeatures.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/acceleration-bunny-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('14 acceleration/bunny local contracts verified.')
