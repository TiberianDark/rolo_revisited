"""Original left/right wall query local contracts on bounded native terrain data."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
rp=root/'work/wall-probe-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r['passed'] and r['85E8']==262144 and r['8634']==262144
sources=['src/core/player_side_collision.hpp','src/core/actor_terrain.hpp','src/core/actor_state.hpp','tests/wall_probe_verification_tests.cpp'];exe=root/'work/wall_probe_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for start,end,left in [(0x85e8,0x8634,True),(0x8634,0x8680,False)]:
 at=start;items=[]
 while at<end:
  assert at in accepted
  i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local '+('left' if left else 'right')+' wall probe',native_sources=['src/core/player_side_collision.hpp'],checked_cases=r[f'{start:X}'],contract='8728 ring lookup includesF268WORDshift. Rejecttilebit14clear. Descriptor'+('6' if left else '4')+'bytepair useslow9tilebits. MirrorprofileY if(tile>>6 XORshape)&64; index(shape&63)*16+(Y&15). RejectnegativeprofileBYTE. ReturnwrappedalignedX'+('-16+offset+profile.' if left else '+15-offset+profile.')+' Typedfound replacesoriginalD1zero/negative flag.',proof='All65536tilewords withprofile0/127/128/255, allshapeBYTEvaluesandmetadataoffsets, correlatedwrappedXYandshift endpoints. Independentrawdescriptor/profileindex/coordinateoracle; no nativequery usedinoracle. Modularcoordinate transforms andmaskboundaries reviewedagainstcompleteoriginalspans.',scope='Local immutablevalidterrainAPI with8192ring/4096collision/1024profilebytes andstableF268shift. Callerprobeacceptance, streamingidentity/publication, rawmemoryaliases andCPUABI/registerclobbers remainexternal; notfullwallcollisionfeature.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/wall-probe-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two shared wall probe contracts verified.')
