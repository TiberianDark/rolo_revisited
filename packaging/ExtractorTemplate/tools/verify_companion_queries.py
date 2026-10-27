import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
sources=['src/core/level1_companion_motion.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/companion_target_verification_tests.cpp','tests/ceiling_probe_verification_tests.cpp'];records=[];results={}
for start,end,name,count,contract,proof in [(0xc920,0xc95a,'companion-target',2113536,'WORDdelta=targetC494-X12; Signed target<signedX (SUB/BLT overflow included) sets118bit3 anddirection121FF thenWORDnegatesdelta, elseclears118bit3andsets121=1. Compare signeddelta magnitude againstsignedincomingcap; ifsmaller usemagnitudeelserequestedcap. WriteWORD58 andclearfractionWORD60. Return originalSGEboolean. Preserveeveryotheractorbyte.','All65536deltas across8signedcapboundaries and4sourceXwrapboundaries; all256facingbytes across8deltasx8caps. Independent signed-endpointcomparison then WORDnegation/wrapping oracle andall130bytecomparisons. OriginalSUB/BLT compares originalsignedendpoints, not wrapped result sign; NEG.W preserves8000negative case; signedcomparisons anddirectionbitupdates reviewed acrossall17instructions.'),(0x86d6,0x8728,'ceiling-probe',638976,'Canonicalceilingquery: shiftedX/Y selectWORDtile;bit14requiresolid; descriptorpair(tile&511)*8+(bit12?0:2). Shapebit6mirrorsX andshape&63 choosesprofile;negativeprofile rejects. SurfaceY=alignedY-16+bias+profile, or alignedY+bias-profile forinvertedtile; allWORDwrapped. Returnfound/Y only.','Reviewed86D6..8728 plus8728and87BCdependencies. All256shapesx16phasesxbothinversionsx6profilesigncases; exhaustive256biasx256profile across4Yboundaries andbothinversions; all65536tilewords withshiftedcoords. Independantintegerarithmetic/modularoracle, queryread-only signature. Descriptor/profile addressing factorisesfromsurface arithmetic; boundarypartitions/linearity coverinteriorvalues.')]:
 rpath=root/f'work/{name}-results.json';r=json.loads(rpath.read_text());assert r['passed'] and r[f'{start:04X}']==count
 exe=root/f'work/{name.replace("-","_")}_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources[:3]+[f'tests/{name.replace("-","_")}_verification_tests.cpp'])
 ins=[]
 for lo,hi in ([(start,end),(0x8728,0x874c),(0x87bc,0x87dc)] if start==0x86d6 else [(start,end)]):
  c=lo
  while c<hi:
   i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
  assert c==hi
 calls={i['target'] for i in ins if i['flow']=='call'};assert calls==({0x8728,0x87bc} if start==0x86d6 else set())
 pin_end=0x87dc if start==0x86d6 else end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=pin_end,original_bytes=rom[start:pin_end].hex(),status='verified green: local companion target/ceiling contract',verification_status='verified',native_sources=['src/core/level1_companion_motion.hpp'],instruction_evidence=ins,checked_cases=count,contract=contract,proof=proof,scope='Complete declared local native API contract. Ceilingshape metadataisextra nativeinformation, not an originalD7outputcertificate; callersusefound/Y. Validterrainbufferextents required. TargetglobalC494suppliedasnativeparameter. Callerpublication, scheduler, CPUtemporaryregisters/CCR/ABI andfullcompanionbehaviour excluded.'))
 results[name]=dict(executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rpath.read_bytes()).hexdigest())
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,native_evidence=results);(p/'docs/stage9/companion-query-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Two shared companion query/state contracts verified.')
