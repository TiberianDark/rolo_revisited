import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/reward-curve-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['D2E2']==524280 and r['B386']+r['excluded_divu_overflow']==4194304
sources=['src/core/level1_reward_curve.hpp','src/core/actor_state.hpp','tests/reward_curve_verification_tests.cpp'];exe=root/'work/reward_curve_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for a,e,name,contract in [(0xb386,0xb3c4,'Reward flight update','Clear118bit3;zeroextendBYTE56minus3WORD. Negative saturates0, incrementscompletionBYTEthroughLONG50pointer andsets116FF. PublishremainingBYTE56,YWORD=target18+remaining, XWORD=target14-unsignedMULU(remaining,46)/unsigned48quotient. Onlydeclaredfields/serviceschanged.'),(0xd2e2,0xd32a,'Reward flight initialization and immediate first update','Set125bit2/126bit4,callback42B386,completionLONG50;targetXWORD14,relativeX46=targetX-currentX+cameraXwrapped;targetY18,relativeY48=-(targetY-currentY+cameraY)wrapped,lowBYTEdistance56. ImmediatelycallB386; no deferred firststep.')]:
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: local '+name,verification_status='verified',native_sources=['src/core/level1_reward_curve.hpp'],instruction_evidence=ins,checked_cases=r[f'{a:X}'],contract=contract,proof='Complete original spans reviewed, BYTE/WORD distinction and unsigned MULU/DIVU explicitly preserved. Independentwideinteger/modularfieldoraclecomparesall130bytes,completionaddress/counter andcamera-readcounts. Update:everyWORDnumerator across8remainingbyte and8divisorpartitions,invalidquotientexcludedandcounted. Initialization:all65535nonzeroWORDdistances across8target/address/camerafixtures. Initialremaining<=distanceprovesquotient<=numerator<=65535; highdistancewithlowBYTE<3stillcompletesimmediatelyasoriginal.',scope='Local actor/serviceAPI withnonzeroDIVUdivisorandquotient<=65535, validdisjointcompletionBYTEservice/camera. OriginalDIVUzero/overflowexception/CCRbehaviour explicitlyoutsidecertificate; native throws oninvaliddomain. Callerpublication, spriteframes, lifetime/retirement scheduling andCPUtemporaryABI excluded.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/reward-curve-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Two reward-flight local contracts verified in explicit DIVU domain.')
