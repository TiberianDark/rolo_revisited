"""Original horizontal slope acceleration and slope vertical motion local APIs."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/player-slope-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['7D3A']==4194304 and r['7DC6']==9535488
sources=['src/core/player_acceleration.hpp','src/core/actor_state.hpp','tests/player_slope_verification_tests.cpp'];exe=root/'work/player_slope_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,name,contract in [(0x7d3a,0x7dc6,'slope acceleration','Defaultlimit30000/accel0. Grounded124bit0selectstableC502/C506 by(slope120 XORdirection121)bit6,slot120&63. Nonzeroaccelwith121zero initializesdirectionfromslopebit6 andlocalspeed0; absoluteaccelbranchgoesdirectpositivepath evenINTMIN. OtherpathaddsLONG46. Nonnegativebranchretainsalready>=limit, otherwiseadds/clamps; negativebranchadds/reflectsnegativeandnegates121.'),(0x7dc6,0x7e58,'slope vertical motion','C514/ground/jumpgates; shape=(120&63)-1 mustbepositive. MULU.Wshape*WORD58,SWAP,ASR.L4; XORfacing/slopebit6 selectsamount+1E000 or-A000. 122zeroinitializesdirectionandlocalspeed0; signmismatchsubtracts/reflectsnegative, otherpathadds/capsF0000. LiteralwrappedLONGarithmetic retained.')]:
 at=start;items=[]
 while at<end:
  assert at in accepted
  i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local player '+name,native_sources=['src/core/player_acceleration.hpp'],checked_cases=r[f'{start:X}'],contract=contract,proof='Independentfull130byteoracle andexacttable-slot/reverse requests. Accelerationallslope/directionBYTEpairs,groundflags,8signed/wrappedtablepartitionsand4speed/limitpartitions. Verticalall64shapes xall65536horizontalWORDs xbothXORbit6states, plus1146880gate/direction/speedboundarycases. SWAP/ASRoracle usesintegerdivision withnegativefloor rounding ratherthannativeshift expression. Originalfullspanspinned; affine/modularbranchpartitions reviewed.',scope='Local typed actor andexplicitstabletable-service API. ActualC502/C506tableproducer/data/admission, terrain/forces/framecomposition, rawaliases/CPUABI andwholeplayerfidelity remainexternal. Notfullmovementphasecertificate.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/player-slope-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two player slope motion contracts verified.')
