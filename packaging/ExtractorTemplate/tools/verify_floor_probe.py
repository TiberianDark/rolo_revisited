import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rpath=root/'work/floor-probe-results.json';r=json.loads(rpath.read_text());assert r['passed'] and r['8680']==638976;sources=['src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/floor_probe_verification_tests.cpp'];exe=root/'work/floor_probe_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
ins=[]
for start,end in [(0x8680,0x86d6),(0x8728,0x874c),(0x879a,0x87bc)]:
 c=start
 while c<end:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==end
assert {i['target'] for i in ins if i['flow']=='call'}=={0x8728,0x879a}
record=dict(address=0x8680,hex='008680',end_exclusive=0x87bc,original_bytes=rom[0x8680:0x87bc].hex(),status='verified green: complete local native floor-query contract',verification_status='verified',native_sources=['src/core/actor_terrain.hpp'],instruction_evidence=ins,checked_cases=638976,contract='Canonical8680 entry: shiftedXWORD andYWORD select tile; absentbit14 means nofloor. Descriptor offset=(tile&511)*8+2ifbit12. Shape bit6 mirrors low4X; shape low6 indexes16byteprofile. NegativeprofileBYTE means nofloor. Found surfaceY=alignedY+16-offset+profile, or alignedY+31-offset-profile for invertedtile, WORDwrapped. Returnfound/surface/originalshapeBYTE. Read-only data.',proof='Reviewed all canonical8680 paths and8728/879A callees. Full256shape domain across16Xphases andbothinversionstates verifies indexed profiles and retainedshape; sixprofile sign boundaries. Exhaustive256offsetx256profile acrossbothinversions andfourYboundaries verifies arithmetic. All65536tilewords verify solidity/index/inversion with shiftedcoordinates. The data domains factor: shape/index selection independent of surface offset arithmetic; modular translation establishes interiorY values. 638976nativecases pass.',scope='Complete declared native query contract for valid ring8192/collision4096/profile1024 buffers. Onnotfound, nativeY/shapeareunspecified tocallers andnot compared toCPU scratch state. Globalbufferproduction, callerlandingpolicy, CCR/temporaryregisterABI andscheduler excluded.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rpath.read_bytes()).hexdigest());(p/'docs/stage9/floor-probe-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Canonical floor probe verified with both original dependencies reviewed.')
