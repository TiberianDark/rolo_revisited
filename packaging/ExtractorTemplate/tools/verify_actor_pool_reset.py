import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/actor-pool-reset-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['27F0']==256
sources=['src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/actor_pool_reset_verification_tests.cpp'];exe=root/'work/actor_pool_reset_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
c=0x27f0;ins=[]
while c<0x2816:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0x2816
record=dict(address=0x27f0,hex='0027F0',end_exclusive=0x2816,original_bytes=rom[0x27f0:0x2816].hex(),status='verified green: local actor free-pool reset',verification_status='verified',native_sources=['src/core/actor_allocation.hpp'],instruction_evidence=ins,checked_cases=256,contract='48 records at998C with130BYTEstride: writeonlyBYTE0FF. Publishordered49LONGfree-keyarray starting9804, lastnull. Native cursor0 replacesoriginalC46Epointertoarraystart. Preserveother129bytesperactor.',proof='Complete original boundaries reviewed. MOVEQ47/DBF loop executes48iterations; ST touchesonlybyte0, LEAstride130, finalCLR.Lnull. Independent literal original address/stride oracle checksall48actorrecords,all49keysandcursor over256priorstatepatterns coveringeveryBYTEvalue. Writesconstant/positionderivedanddonotbranchonpriorstate; algebra establishesallpriorstatevalueswithintypedpooldomain.',scope='Local native ActorPool API withdisjointfixed48record/49keyarrays; cursorindex replacesoriginalRAMpointer. Allocatorcallers, publicationtiming, aliasingrawmemory, CPUregister/CCRABI excluded.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/actor-pool-reset-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Actor pool reset local contract verified.')
