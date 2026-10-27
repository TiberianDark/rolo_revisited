"""Forest-bank animation and suction sprite state/placement, device-independent."""
import hashlib,json,re,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from verify_forest_animation_artwork import verify as verify_forest_artwork
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/visual-effects-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,FAA0=32768,**{'5348':524288})
art=verify_forest_artwork(p);assert art['different_bytes']==0
header=(p/'src/core/suction_particle_data.hpp').read_text(encoding='utf-8');m=re.search(r'patterns\{\{(.*?)\}\};',header,re.S);patterns=bytes(map(int,re.findall(r'\d+',m[1])));rows=[tuple(map(int,m.groups())) for m in re.finditer(r'^\{(\d+),(\d+),(\d+),(\d+),(\d+)\},$',header,re.M)];assert len(rows)==3;offset=0
for i,row in enumerate(rows):
 at=0x5470+16*i;size=rom[at];width=((size>>2)&3)*8+8;height=(size&3)*8+8;frame=width*height//2;source=struct.unpack_from('>I',rom,at+8)[0];palette=(struct.unpack_from('>H',rom,at+2)[0]>>13)&3
 assert row==(width,height,frame,offset,palette);assert patterns[offset:offset+frame*4]==rom[source:source+frame*4];offset+=frame*4
assert offset==len(patterns)
sources=['src/core/forest_tile_animation.hpp','src/core/forest_tile_animation_data.hpp','src/core/terrain_pattern_storage.hpp','src/core/suction_particles.hpp','src/core/suction_particle_data.hpp','src/core/actor_state.hpp','tests/visual_effects_verification_tests.cpp','tools/verify_forest_animation_artwork.py'];exe=root/'work/visual_effects_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
for start,end,contract,scope in [(0xfaa0,0xfb72,'Forest bank1 six tracks in original table order. Signed BYTE countdown decrement; negative reloads delay3 and advances sentinel-terminated sequence. Advance even when cacheFFFF; mapped entries upload64words at(pattern&7FF)*32 with later tracks winning overlap.','Local FAA0 bank1 typed publication contract, six original tracks and reachable sequence cursors0..count. Immutable mapped destinations0..2044 orFFFF; native byte storage replaces DMA service. Bank dispatch for other themes, queue termination/capacity/timing and VDP wrap remain external.'),(0x5348,0x5470,'Gating uses wrapped BYTE C519+C51A+C51B and base52; inactive clears per-frame native output without timer progress. Signed BYTE countdown reload2, phase0..3 wrap. Original raw SAT positions converted by subtract128, WORD arithmetic/head offsets, left flip, count1..3 with32X/-4Y spacing.','Local reachable phase0..3/count1..3 sprite state and placement contract. C53C..C540 graphics offsets represented by phase*original frame_size; assets independently byte-pinned. F266 SAT allocation/link numbers and C434 DMA queue service/device timing remain external, not claimed as whole routine hardware fidelity.')]:
 at=start;items=[]
 while at<end:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local visual state/publication',native_sources=[sources[0] if start==0xfaa0 else sources[3]],checked_cases=r[f'{start:04X}'],contract=contract,proof='Independent timer/sequence/byte-publication and raw-SAT coordinate models. Forest32768 successive steps across all BYTE timer values, mapped/unmapped/overlapping four-tile destinations and all sequence positions. Suction524288 gate/WORD position/camera/offset/flip/phase/count fixtures including wrapped gate cancellation. Compare full pattern storage, track state, ordered sprite fields and empty output. All generated forest and suction artwork/metadata independently compared to pinned ROM.',scope=scope))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),forest_artwork=art,suction_artwork_bytes=len(patterns))
(p/'docs/stage9/visual-effects-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('FAA0/5348 local visual contracts verified.')
