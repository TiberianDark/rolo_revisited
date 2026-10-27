"""Export immutable bindings for the bounded first-enemy integration slice."""
from pathlib import Path
import hashlib
from export_level1_terrain import ROM_HASH
import export_entrance
import re,struct
from rolo_sprites import sprite_pixels
from export_preview import rgba,MAGIC

def generate(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH: raise ValueError('ROM mismatch')
    keys=(0x13ecc,0x13eee,0x13f98,0x13fba,0x140ec)
    lines=['#pragma once','#include "core/actor_definition.hpp"','namespace rolo::level1_world_data {',
           'inline constexpr std::array<ActorDefinition,5> definitions{{']
    for key in keys:
        lines.append('  ActorDefinition{'+str(key)+',{'+','.join(map(str,rom[key:key+34]))+'}},')
    lines += ['}};','inline constexpr std::array<std::uint32_t,6> head_offsets{{']
    lines.append(','.join(str(int.from_bytes(rom[0x1045c+i*4:0x10460+i*4],'big')) for i in range(6)))
    lines += ['}};','}']
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1]
    (project/'src/core/level1_world_data.hpp').write_text(generate(project),encoding='utf-8')
    export_entrance.PROGRAMS=((0x13ecc,(0,4,8,12,16,20,24,32,36,52,56,60,64,68,72,88)),
        (0x13eee,(0,4,8,12,16,20,24,32,36,44,52,56,60,64,68,72,88)))
    destination=project/'src/core/level1_player_animation_data.hpp'
    export_entrance.export((project/'local/rolo.md').read_bytes(),destination)
    destination.write_text(destination.read_text().replace('rolo::entrance_data','rolo::level1_player_animation_data'),encoding='utf-8')
    rom=(project/'local/rolo.md').read_bytes()
    source=int.from_bytes(rom[0x4b0a2:0x4b0a6],'big')
    colors=[tuple(((v>>s)&7)*255//7 for s in (1,5,9)) for v in struct.unpack_from('>16H',rom,source)]
    records=[];seen=set()
    for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',destination.read_text()):
        descriptor,left,right,ox,oy,w,h,size=[int(v,0) for v in match.groups()]
        for graphics in (left,right):
            if not graphics or (graphics,w,h) in seen:continue
            seen.add((graphics,w,h));pixels=rgba(sprite_pixels(rom[graphics:graphics+size],w,h),colors,True)
            records.append(struct.pack('<6I',3,graphics,2,w,h,len(pixels))+pixels)
    (project/'bin/level1-player-assets.rla').write_bytes(MAGIC+struct.pack('<I',len(records))+b''.join(records))

