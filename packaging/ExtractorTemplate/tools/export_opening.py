"""Pinned opening artwork/palettes; data decoding only, no ROM execution."""
from pathlib import Path
import sys,struct,re,hashlib,json
p=Path(__file__).resolve().parents[1];sys.path.insert(0,str(p/'tools'))
from rolo_codec import decode_backward_lz
from rolo_stage2 import map_pixels
from rolo_sprites import sprite_pixels
from inventory_rom import ROM_HASH
r=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(r).hexdigest()==ROM_HASH
# Bound the original startup LZSS input by decoding its declared output length.
n=int.from_bytes(r[0xc7c:0xc7e],'little');dictionary=bytearray(b' '*4096);cur=0xfee;out=bytearray();at=0xc80
while len(out)<n:
 flags=r[at];at+=1
 for bit in range(8):
  a=r[at];at+=1
  if flags&(1<<bit):values=[a]
  else:
   b=r[at];at+=1;start=a|((b&240)<<4);values=None;count=(b&15)+3
  for j in range(1 if values else count):
   v=values[0] if values else dictionary[(start+j)&4095];out.append(v)
   if len(out)==n:break
   dictionary[cur]=v;cur=(cur+1)&4095
  if len(out)==n:break
startup=bytes(0xc46)+r[0xc46:at]
vram=bytearray(65536)
for a,d in [(0x28a80,0x1540),(0x44f1c,0x7300)]:
 raw,_=decode_backward_lz(r,a);vram[d:d+len(raw)]=raw
lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::opening_data {']
def array(name,raw,typ='std::uint8_t'):
 lines.append(f'inline constexpr std::array<{typ},{len(raw)}> {name}{{{{')
 lines.extend(','.join(map(str,raw[i:i+32]))+',' for i in range(0,len(raw),32));lines.append('}};')
array('startup',startup);array('font',r[0x27040:0x27040+96*32])
for name,sel in [('colour',-1),('photo',-4)]:
 ptr=struct.unpack_from('>4I',r,0x4b08a+sel*16);array(name,[w for a in ptr for w in struct.unpack_from('>16H',r,a)],'std::uint16_t')
for name,src,w,h,base in [('back',0x2b680,40,14,0xaa),('front',0x2bae0,40,14,0x80aa),('logo',0x4592c,40,6,0xe398),('photo_back',0x2bf40,40,14,0xaa),('photo_front',0x2c3a0,40,14,0x80aa)]:
 _,_,pix,_=map_pixels(vram,r[src:src+w*h*2],w,h,base);array(name,pix)
records=[];blob=bytearray()
for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',(p/'src/core/entrance_data.hpp').read_text()):
 _,left,right,_,_,w,h,size=[int(v,0) for v in match.groups()]
 for source in [left,right]:
  if not source or any(q[0]==source and q[1]==w and q[2]==h for q in records):continue
  records.append((source,w,h,len(blob)));blob.extend(sprite_pixels(r[source:source+size],w,h))
array('sprite_pixels',blob);lines+=['struct Sprite{unsigned source,width,height,offset;};',f'inline constexpr std::array<Sprite,{len(records)}> sprites{{{{']
lines.extend('Sprite{%s},'%','.join(map(str,q)) for q in records);lines+=['}};','}']
(p/'src/core/opening_data.hpp').write_text('\n'.join(lines)+'\n')
(p/'docs/stage9/opening-artwork-export.json').write_text(json.dumps(dict(rom_sha256=ROM_HASH,startup_data_end=at,startup_decoded_size=n,sprite_records=len(records),scope='Original indexed artwork, font and palette data only'),indent=2)+'\n')
print('Opening assets exported:',len(records),'sprite records; startup data ends',hex(at))
