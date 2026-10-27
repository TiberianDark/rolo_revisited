"""Button mapping, slope impact and ordered scroll publication native contracts."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/input-impact-scroll-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'237C':524288,'8C24':1048576,'6960':262144,'6AA6':262144}
for i in range(32):
 command=struct.unpack_from('>I',rom,0x6a26+i*4)[0];address=((command>>16)&0x3fff)|((command&3)<<14);assert address==0xf000+i*32
sources=['src/core/player_input.hpp','src/core/player_slope_impact.hpp','src/core/plane_scroll.hpp','src/core/actor_state.hpp','tests/input_impact_scroll_verification_tests.cpp'];exe=root/'work/input_impact_scroll_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0x237c,0x244e,[(0x237c,0x244e)],'Button edge/hold mapping',sources[0],r['237C'],'Fresh=pressed&previouscomplement; previouscomplement=~pressedBYTE. Clear8physical/8mappedBYTEs; pressedbits7..0 writeto4,5,7,6,3,2,1,0. FreshFF,heldFE,release0. RemapdestinationBYTE0..7; aliasesoverwriteinoriginalMSB→LSBorder. Destinationtableunchanged.'),(0x8c24,0x8c88,[(0x8c24,0x8c88)],'Landing slope impact',sources[1],r['8C24'],'124bit6gate. SignedWORD66>=2sound20; READslope/speed/directionafterservice. shape=(120&63)-1;<=0return. MULUWORDshape*speed,SWAP,ASR.L4. slopebit6/directionBYTE decide32bitnegation orset121FF/1; write46LONG. Allotheractorstatepreservedexceptdeclaredservicewrites.'),(0x6960,0x6980,[(0x6960,0x6980)],'Horizontal scroll mode entry',sources[2],r['6960'],'PreparemodeVDP8Bxx/8F02throughtypedservice; dispatchoriginalvalidmode0..3. Actualporttiming/basecommandbindingexternal.'),(0x6aa6,0x6ac6,[(0x6aa6,0x6ac6)],'Vertical scroll pair publication',sources[2],r['6AA6'],'Preparevertical8F02/40000010service; readforegroundandbackgroundWORDoffsetsbeforepairhandoff; publishinorder withoutnegatingagain.')]
targets=[(0x6990,0x69aa),(0x69a8,0x69aa),(0x69aa,0x6a0a),(0x6a0a,0x6a26)]
contracts=['Mode0readsFG/BGoffsetsafterprepare; publishonepairbyteoffset0,notcoordinatesnegatedagain.','Mode1literalRTSafterprepare; noscrollsource/read/write.','Mode2latchesforegroundoffsetonce;32livesourceWORDsfrom7440,eachNEG.W, publishpairat0/32/...992 inoriginalorder.6A26commandtabledecodedandmatched32offsets.','Mode3request2468source7440/destinationF000/512words/VRAMcommand40000000 throughrequiredservice; nativeAPIdoesnotsubstitutestoragecopy.']
for slot,(lo,hi) in enumerate(targets):
 start=0x6980+slot*4;specs.append((start,start+4,[(start,start+4),(lo,hi)],f'Horizontal scroll slot{slot}',sources[2],65536,contracts[slot]))
for start,end,ranges,name,source,cases,contract in specs:
 items=[];evidence=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi;evidence.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,code_ranges=evidence,verification_status='verified',status='verified green: local '+name,native_sources=[source],checked_cases=cases,contract=contract,proof='All65536previous/pressedBYTEpairs x8mappingpatterns inclall-to-one aliases; independentper-destinationlowest-pressed-bitwinneroracle. All65536impactWORDspeeds x16slope/direction/flag/servicepartitions, independent64bitSWAP/signedfloor division model/full130bytecheck. All65536scrollWORDs x4modes; orderedserviceoracle withprepare/source/publicationmutations verifieslatepairreads,foregroundlatchedonceandlivesourceorder. Entireoriginalrangesand6A26tablepinned.',scope='Local distinctphysical/mappedstorage, validremap0..7; controllerhardware/replayproduceroutside237C. Impacttypedvalidactor/explicitSoundservice. Scrollmode0..3 andtypedWORDoffsetpublication; physicalVDP/IRQ/transferqueue/CPUABI andactualscene/framecalleradmissionremainexternal. No wholeinput/camera/gameplayclaim.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/input-impact-scroll-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Eight input/impact/scroll local contracts verified.')
