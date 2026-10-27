"""Pinned Level1 background indices and independent existing-BMP RGB verification."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_maps import long,word,parse_map,render_foreground
from rolo_codec import decode_backward_lz

def extract(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 fg=long(rom,0x4ab22)&0xffffff
 data=rom[fg:fg+4096] if rom[fg:fg+3]==b'MAP' else decode_backward_lz(rom,fg)[0]
 bank=parse_map(data)['bank']
 tiles=decode_backward_lz(rom,long(rom,0x4af2a+bank*4))[0]
 source=long(rom,0x4ab26)&0xffffff
 bg=rom[source:source+4096] if rom[source:source+3]==b'MAP' else decode_backward_lz(rom,source)[0]
 layout=parse_map(bg)
 if (layout['width'],layout['height'])!=(512,272):raise ValueError('Background dimensions')
 indices=bytes(render_foreground(rom,layout,tiles,long(rom,0x4af6e+bank*4),long(rom,0x4afb2+bank*4)))
 palette=[word(rom,long(rom,0x4b09a+b*4)+n*2) for b in range(4) for n in range(16)]
 return source,indices,palette

def catalogue(project):
 source,indices,palette=extract(project)
 bmp=(project/'assets/extracted/maps/map-01/background.bmp').read_bytes()
 offset=struct.unpack_from('<I',bmp,10)[0];w,h=struct.unpack_from('<ii',bmp,18)
 if bmp[:2]!=b'BM' or(w,h)!=(512,272) or struct.unpack_from('<H',bmp,28)[0]!=24:raise ValueError('Original BMP format')
 stride=(w*3+3)&~3;mismatch=0
 for y in range(h):
  for x in range(w):
   color=palette[indices[y*w+x]]
   rgb=bytes(((color>>shift)&7)*255//7 for shift in(1,5,9))
   p=offset+(h-1-y)*stride+x*3
   mismatch+=rgb!=bmp[p:p+3][::-1]
 if mismatch:raise ValueError(f'Original BMP mismatch pixels{mismatch}')
 return dict(rom_sha256=ROM_HASH,source=source,width=w,height=h,indexed_sha256=hashlib.sha256(indices).hexdigest(),palette_words=palette,bmp_sha256=hashlib.sha256(bmp).hexdigest(),compared_pixels=w*h,rgb_mismatches=mismatch,scope='Original512x272 background indices, fixedY0 andunsignedXmodulo512; opaque livepalette raster. FullRGB equality against existing originalBMP, no ROM execution.')

def generate(project):
 report=catalogue(project);_,indices,_=extract(project)
 lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::level1_indexed_background_data {','inline constexpr unsigned width=512,height=272;',f'inline constexpr std::array<std::uint8_t,{len(indices)}> pixels{{{{']
 lines += [','.join(map(str,indices[i:i+64]))+',' for i in range(0,len(indices),64)]
 lines += ['}};','}']
 (project/'src/core/level1_indexed_background_data.hpp').write_text('\n'.join(lines)+'\n')
 (project/'docs/stage9/level1-indexed-background-export.json').write_text(json.dumps(report,indent=2)+'\n')
 return report

if __name__=='__main__':
 r=generate(Path(__file__).resolve().parents[1]);print(f"Background{r['compared_pixels']}pixels; originalBMP mismatches{r['rgb_mismatches']}")
