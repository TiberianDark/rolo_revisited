"""Pinned raw sprite patterns for resident menu portraits; no code execution."""
from pathlib import Path
import hashlib,re,json
from inventory_rom import ROM_HASH
def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    frames={}
    for name in ('level1_player_animation_data.hpp','level1_object_animation_data.hpp','first_enemy_animation_data.hpp','world_cursor_data.hpp'):
        content=(project/'src/core'/name).read_text()
        for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',content):
            _,left,right,_,_,width,height,size=[int(x,0) for x in match.groups()]
            for source in (left,right):
                if not source:continue
                required=width*height//2
                if width%8 or height%8 or required>size or source+required>len(rom):raise ValueError('Pattern frame extent')
                frames[(source,width,height)]=rom[source:source+required]
    data=bytearray();records=[]
    for (source,width,height),payload in sorted(frames.items()):
        records.append(dict(source=source,width=width,height=height,offset=len(data),size=len(payload)));data.extend(payload)
    out=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::actor_pattern_data {',f'inline constexpr std::array<std::uint8_t,{len(data)}> bytes{{{{']
    out+= [','.join(map(str,data[i:i+24]))+',' for i in range(0,len(data),24)]
    out+=['}};','struct Frame {std::uint32_t source,width,height,offset,size;};',f'inline constexpr std::array<Frame,{len(records)}> frames{{{{']
    out += ['Frame{%s},'%','.join(str(r[k]) for k in ('source','width','height','offset','size')) for r in records]
    out +=['}};','}']
    (project/'src/core/actor_pattern_data.hpp').write_text('\n'.join(out)+'\n')
    report=dict(rom_sha256=ROM_HASH,records=records,pattern_bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),scope='Immutable column-major 4bpp frames; resident destination uses native actor tile2. This is not a hardware queue implementation.')
    (project/'docs/stage9/actor-pattern-export.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    report=export(Path(__file__).resolve().parents[1]);print(len(report['records']),report['pattern_bytes'])
