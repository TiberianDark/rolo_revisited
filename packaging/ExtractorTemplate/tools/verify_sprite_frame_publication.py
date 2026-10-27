"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/sprite-frame-publication-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,frame_cases=131072)
sources=['src/core/sprite_frame_publication.hpp','src/core/display_setup.hpp','src/core/plane_scroll.hpp','tests/sprite_frame_publication_verification_tests.cpp'];exe=root/'work/sprite_frame_publication_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0x31d6,[(0x31d6,0x328c)],'Copiedresidentrendererrequest first; captureF266lowBYTEtoC492,WORDcount*4toC476,queuewriterC434/SAToffsetcount*8. Clear8BYTEsentinel,invoke7fixedprioritylistsinorderusingmutableSAT/queuewritercontext. ClearlastlinkBYTEcursor-5. PublishC476or4fallback as9300/9400,95DE,96E4,977F,74000083packet; zeroLONGsentinelwithoutadvancingstoredC434pastit.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status='verified green: local sprite-frame publication contract',native_sources=[sources[0]],checked_cases=131072,contract=contract,proof='One focused131072framefixtures:allWORDpostbuildercounts acrossempty/populatedlistpartitions, residentseed0..80, mutatedC434memorydistinctfromlivewritercontext. IndependentSAT/queuebyteoracle comparesfullbuffers/guards,cursors,counters andall7prioritylistkeys/order/entrycounts. Zero-spritecasepreservesoriginalcursor-5writeinprovidedprefix; zeroWORDcountDMAfallback4verified.',scope='Local31D6orchestration/publication only. Canonicalresidentcount0..80,validSATwith5BYTEprefixandboundedqueuewriter. Copiedresidentrendererand3440actorlist/SATchunkbuilders areexplicitnative services; their draw/cull/80spritelimit andSDLbackend equivalence remainexternal. Notfullsprite-renderingcertificate orCPU/VDPemulation.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/sprite-frame-publication-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Local sprite-frame publication contract verified; renderer child services remain external.')
