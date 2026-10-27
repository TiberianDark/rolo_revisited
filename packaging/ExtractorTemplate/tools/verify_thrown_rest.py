"""Original B498 resting transition; explicit terrain/service composition domain."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/thrown-rest-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['B498']==1048832
sources=['src/core/level2_actor_updates.hpp','src/core/actor_motion.hpp','src/core/actor_horizontal_collision.hpp','src/core/actor_state.hpp','tests/thrown_rest_verification_tests.cpp'];exe=root/'work/thrown_rest_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
at=0xb498;items=[]
while at<0xb51e:
 assert at in accepted
 i=Decoder(rom,at).decode();items.append(i);at+=i['size']
assert at==0xb51e
record=dict(address=0xb498,hex='00B498',end_exclusive=0xb51e,original_bytes=rom[0xb498:0xb51e].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local thrown actor resting transition',native_sources=['src/core/level2_actor_updates.hpp'],checked_cases=1048832,contract='Nonzero117 returns. Definition26bit7clear sets119bit4. Signed X lowerclamp8 thenupperclampF330-8 skipphysicsandnegate121. Inrange decelerate/gravity/integrate/land/horizontalcollision, then124mask6turn. Nonzero121returns; zero sets126bit2 thenrestoresdefinition12ifbit7set, elsecallbackB51E/timer250.',proof='All65536Xwords acrossfourwidthpartitions includingwidthbelow16, bothdefinitionbit7states, stopped/negative directions; all256visibilitybytes. Independent arithmetic andfull130byteoracle, pluslandingcallcounts. Signed lowerclamppriority andwrappedupperextent retained. Sharedmotion hasseparateverifiedcontracts.',scope='Local composition withstablevalidactor/definition identity, emptyterrain andexplicitlandingservice, noexternalmutationofactor/definitionidentityduringservices. Populatedwallturn servicecomposition, malformedaliases/lifetime/caller/CPUABI remainexternal; nofullthrown-enemycertificate.')
dep='docs/stage9/leaf-routine-verification.json';report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources+[dep]},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/thrown-rest-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('B498 local resting transition verified.')
