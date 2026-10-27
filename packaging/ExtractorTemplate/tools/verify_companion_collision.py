import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/companion-collision-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['CECA']==r['B00A']==1048576
sources=['src/core/level1_companion_motion.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/companion_collision_verification_tests.cpp'];exe=root/'work/companion_collision_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
deps=['docs/stage9/companion-query-verification.json','docs/stage9/floor-probe-verification.json'];assert any(x['address']==0x86d6 for x in json.loads((p/deps[0]).read_text())['records']);assert any(x['address']==0x8680 for x in json.loads((p/deps[1]).read_text())['records'])
records=[]
for a,e,callee,name,contract in [
 (0xceca,0xcf46,0x86d6,'Companion ceiling collision','117nonzero skips all writes; otherwiseclear125bit7. Signed WORD reach=58+62;86D6queryatY-height+16thenY-heightonfailure/insufficientreach. Candidate=probeY+height wrapped;distance compared signed toreach, finalcandidate>=originalY unsigned. AcceptintegerY,clearfraction18; if signedBYTE122<=0clear122/LONG62,set125bit7; positive122preservesvelocity.'),
 (0xb00a,0xb058,0x8680,'Companion forward floor probe','X=actorX +/- WORD58 accordingtosignedBYTE121;query8680atYthenY+16onlyifnotfound. WrappedprobeY-originalY BPL/NEG.Wabsolute; signedCMPagainstWORD58rejectsifgreater,including32768wrappednegative. SuccessadoptsintegerYonlyandreturns true;failureunchangedfalse. NativeboolreplacesoriginalD1zero/-1.')]:
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e and {i['target'] for i in ins if i['flow']=='call'}=={callee}
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: local '+name,verification_status='verified',native_sources=['src/core/level1_companion_motion.hpp'],instruction_evidence=ins,checked_cases=r[f'{a:X}'],contract=contract,proof='Complete original span reviewed with signed reach versus unsigned finalY distinctions and wrapped abs. Canonical floor/ceiling query contracts separately verified and hash-pinned. Independent terrain arithmetic oracle uses coordinate division, descriptor/profile tables and wide integers; everyWORD Y across16speed/height/direction/statusfixtures checks fullactorstate andreturnedbool. Includes non-solid tiles, both flips, mirrored profiles andnegativeprofiles. Algebraic wrapper review plus certifiedcallees establisheslocal composition; fixture counts are not an exhaustive claim over all terrain arrays.',scope='Canonical local actor API on valid immutable terrain; service publication, actor scheduling, CPUtemporaryregister/CCR/ABI, aliasing memory andexternallyenteredfragments excluded. Native helpers already bound to shared companion movement.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+deps},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/companion-collision-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Two companion collision local contracts verified.')
