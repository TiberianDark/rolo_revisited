import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/bounce-motion-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['B782']==65536;sources=['src/core/actor_bounce_motion.hpp','src/core/animation.hpp','src/core/actor_state.hpp','tests/bounce_motion_verification_tests.cpp'];exe=root/'work/bounce_motion_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
dep='docs/stage9/random-range-verification.json';assert json.loads((p/dep).read_text())['records'][0]['verification_status']=='verified'
c=0xb782;ins=[]
while c<0xb7b2:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0xb7b2 and {i['target'] for i in ins if i['flow']=='call'}=={0x716e} and rom[0xb7b2:0xb7b8]==bytes([255,1,255,1,255,1])
record=dict(address=0xb782,hex='00B782',end_exclusive=0xb7b8,original_bytes=rom[0xb782:0xb7b8].hex(),status='verified green: shared random bounce initialization contract',verification_status='verified',native_sources=['src/core/actor_bounce_motion.hpp'],instruction_evidence=ins,checked_cases=65536,contract='Three ordered shared-seed716E draws: [0,6) selects pinned sixBYTEdirectiontable into121; [1,5) shifted16writesLONG58; [3,9) shifted16writesLONG62; write122FF. Preserve everyotheractorbyte, advance same sharedseedexactlythree times.',proof='All65536incomingseedstates exhaustively compared against independent64bitseed/rangeoracle andfull130byteactorcomparison. OriginaltableB7B2 sixbytespinned. MOVEQ before eachdraw zeroesupperD0WORD, soSWAP yields exact highwordvelocitieswithzero fractionalwords. Originalcalls716Edependencyreviewed/certified and source/reporthashpinned. NativeB714/B726callerbindings added andLevel1/2integrationchecks pass; caller contractsremainpartial.',scope='Complete local actor/sharedseed contract forB782. B714dynamicdispatch andB726lifecycle/caller/frame contracts are not promoted bythisproof. TemporaryCPUregister/CCR/ABI excluded.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/bounce-motion-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('SharedB782bounceinitializationverified; callbacks remainpartial.')
