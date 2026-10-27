"""Audit indexed ROM sprite patterns against original-palette SDL asset packs."""
import hashlib,json,re,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_maps import long,word
MAGIC=b'RLOAS01\0'

def indexed_rgba(raw,w,h,colors):
 out=bytearray()
 for y in range(h):
  cy=(y//32)*32;tile_rows=min(4,(h-cy)//8)
  for x in range(w):
   cx=(x//32)*32
   tile=(cy//8)*(w//8)+(cx//8)*tile_rows+((x-cx)//8)*tile_rows+(y-cy)//8
   packed=raw[tile*32+(y&7)*4+(x&7)//2]
   ink=(packed>>4 if x%2==0 else packed&15)
   out.extend((*colors[ink],255 if ink else 0))
 return bytes(out)

def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 content=(project/'src/core/actor_pattern_data.hpp').read_text()
 body=content.split('bytes{{',1)[1].split('}};',1)[0]
 patterns=bytes(map(int,re.findall(r'\d+',body)))
 records=[tuple(map(int,m.groups())) for m in re.finditer(r'Frame\{(\d+),(\d+),(\d+),(\d+),(\d+)\}',content)]
 frames={(s,w,h):patterns[o:o+n] for s,w,h,o,n in records}
 source_mismatches=[dict(source=s,width=w,height=h) for(s,w,h),raw in frames.items() if raw!=rom[s:s+len(raw)]]
 palettes=[]
 for bank in range(4):
  p=long(rom,0x4b09a+bank*4)
  palettes.append([tuple(((word(rom,p+i*2)>>shift)&7)*255//7 for shift in(1,5,9)) for i in range(16)])
 packs=[];missing=[];differences=[];compared_pixels=0;union=set()
 for name in('level1-player-assets.rla','first-enemy-assets.rla','level1-object-assets.rla'):
  data=(project/'bin'/name).read_bytes()
  if data[:8]!=MAGIC:raise ValueError('Asset pack magic')
  count=struct.unpack_from('<I',data,8)[0];at=12;sprites=0
  for n in range(count):
   kind,source,bank,w,h,size=struct.unpack_from('<6I',data,at);at+=24
   rgba=data[at:at+size];at+=size
   if kind!=3:continue
   sprites+=1;key=(source,w,h);union.add(key)
   if key not in frames:
    missing.append(dict(pack=name,source=source,width=w,height=h,palette=bank));continue
   golden=indexed_rgba(frames[key],w,h,palettes[bank])
   if len(golden)!=len(rgba):raise ValueError('RGBA extent mismatch')
   mismatch=sum(golden[i:i+4]!=rgba[i:i+4] for i in range(0,len(rgba),4));compared_pixels+=w*h
   if mismatch:differences.append(dict(pack=name,source=source,width=w,height=h,palette=bank,pixels=mismatch))
  if at!=len(data):raise ValueError('Trailing asset bytes')
  packs.append(dict(name=name,records=count,sprites=sprites,sha256=hashlib.sha256(data).hexdigest()))
 sparkle_sources=list(range(0x30f60,0x31460,128))
 return dict(rom_sha256=ROM_HASH,packs=packs,indexed_records=len(frames),indexed_bytes=len(patterns),source_mismatches=source_mismatches,missing_pack_records=missing,rgba_differences=differences,compared_pixels=compared_pixels,
  missing_unique_frames=[dict(source=s,width=w,height=h) for s,w,h in sorted(union-frames.keys())],
  sparkle=dict(definition='157E6',graphics=sparkle_sources,coverage=[dict(source=s,indexed=(s,16,16) in frames) for s in sparkle_sources]),
  scope='Independent inverse column-major tile addressing and CRAM RGB conversion compared byte-for-byte against pre-extracted original-Level1-palette RGBA records. Runtime live palette choice/SDL presentation remains parent integration.')

if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/level1-actor-pattern-audit.json').write_text(json.dumps(r,indent=2)+'\n')
 print(f"Indexed{r['indexed_records']}frames; missing{len(r['missing_unique_frames'])}; differing{len(r['rgba_differences'])}; compared{r['compared_pixels']}pixels")

