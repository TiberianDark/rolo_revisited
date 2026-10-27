"""Export pinned ending display data only; no ROM instruction execution."""
from pathlib import Path
import hashlib,re,struct,sys
import export_entrance
from inventory_rom import ROM_HASH
from rolo_sprites import sprite_pixels

def export(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 old=export_entrance.PROGRAMS
 try:
  export_entrance.PROGRAMS=((0x1575e,(0,)),(0x15780,(0,)),(0x13ecc,(4,92)),(0x13eee,(4,92)))
  animation=project/'src/core/ending_animation_data.hpp';export_entrance.export(rom,animation)
 finally:export_entrance.PROGRAMS=old
 animation.write_text(animation.read_text().replace('rolo::entrance_data','rolo::ending_animation_data'))
 records=[];pixels=[];seen=set()
 for match in re.finditer(r'Frame\{(0x[\da-f]+),(0x[\da-f]+),(0x[\da-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',animation.read_text()):
  descriptor,left,right,ox,oy,width,height,size=[int(v,0) for v in match.groups()]
  for source in (left,right):
   if not source or (source,width,height) in seen:continue
   seen.add((source,width,height));records.append((source,width,height,len(pixels)));pixels.extend(sprite_pixels(rom[source:source+size],width,height))
 lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::ending_data {','struct Sprite{unsigned source,width,height,offset;};',f'inline constexpr std::array<Sprite,{len(records)}> sprites{{{{']
 lines+=['Sprite{%s},'%','.join(map(str,r)) for r in records];lines+=['}};',f'inline constexpr std::array<std::uint8_t,{len(pixels)}> pixels{{{{']
 for i in range(0,len(pixels),128):lines.append(','.join(map(str,pixels[i:i+128]))+',')
 lines+=['}};']
 for name,start in [('good_text',0x13a10),('bad_text',0x13ae6)]:
  data=rom[start:start+1024];data=data[:next(i+1 for i,c in enumerate(data) if c in (0,2))];lines.append(f'inline constexpr std::array<std::uint8_t,{len(data)}> {name}{{'+','.join(map(str,data))+'};')
 for name,start in [('white',0x4b7ca),('black',0x32360),('bad_palette',0x4b5aa)]:lines.append('inline constexpr std::array<std::uint16_t,16> %s{'%name+','.join(map(str,struct.unpack_from('>16H',rom,start)))+'};')
 lines+=['}'];(project/'src/core/ending_data.hpp').write_text('\n'.join(lines)+'\n')
 return {'frames':len(records),'indexed_pixels':len(pixels),'rom_sha256':ROM_HASH}
if __name__=='__main__':print(export(Path(__file__).resolve().parents[1]))
