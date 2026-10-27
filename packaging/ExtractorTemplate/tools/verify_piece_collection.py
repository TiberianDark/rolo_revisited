import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/piece-collection-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['9A1A']==1638400
sources=['src/core/level1_progress.hpp','src/core/level1_enemy_slice.hpp','src/core/actor_state.hpp','tests/piece_collection_verification_tests.cpp'];exe=root/'work/piece_collection_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
dep='docs/stage9/reward-curve-verification.json';assert any(x['address']==0xd2e2 for x in json.loads((p/dep).read_text())['records'])
c=0x9a1a;ins=[]
while c<0x9a5e:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0x9a5e
record=dict(address=0x9a1a,hex='009A1A',end_exclusive=0x9a5e,original_bytes=rom[0x9a1a:0x9a5e].hex(),status='verified green: local jigsaw pickup progress and reward request',verification_status='verified',native_sources=['src/core/level1_progress.hpp'],instruction_evidence=ins,checked_cases=r['9A1A'],contract='Requestsound64;setcurrentselectorflagbit3. PreserveD0selectorhighBYTEwhenreplacinglowBYTEbyactor50forrewardflagbit0. Actorselector70=4;immediateD2E2target296/41completionC551. Flagindicesmayalias; actor50readbeforeflightoverwritescompletionLONG50.',proof='Completeoriginalboundariesandread/writeorderreviewed. All80currentselectorsx80destinationselectorsx256priorflag patterns; includesaliasedflagindices,allnonzeroinitialdistances1..256andwrappedcompletioncounter. Independentflag/stateoraclecomposesseparatelycertifiedrewardhelper; comparesall130actorbytes,flagarray,counter,soundandselector.',scope='Localprogress/actor/requestAPI withvalid0..79flagindices, disjointtypedstate, validrewardDIVUdomain. Calleractor50provenance, largerselectorhighBYTEdomains, worldjigsawreveal, sounddevice, retirement/frame/schedulerandCPUABI remainseparate.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/piece-collection-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Jigsaw collection local progress/reward contract verified.')
