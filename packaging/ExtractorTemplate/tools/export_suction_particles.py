"""Pinned $5348 suction particle artwork/templates; no ROM execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_maps import word,long
def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
    patterns=[];records=[]
    for at in (0x5470,0x5480,0x5490):
        size=word(rom,at)>>8;width=((size>>2)&3)*8+8;height=(size&3)*8+8
        frame_size=width*height//2;source=long(rom,at+8);first=len(patterns)
        patterns.extend(rom[source:source+frame_size*4]);records.append(dict(template=at,source=source,width=width,height=height,frame_size=frame_size,first=first,palette=(word(rom,at+2)>>13)&3))
    lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::suction_particle_data {',f'inline constexpr std::array<std::uint8_t,{len(patterns)}> patterns{{{{']
    lines.extend(','.join(map(str,patterns[i:i+32]))+',' for i in range(0,len(patterns),32));lines+=['}};','struct Graphic {unsigned width,height,frame_size,first,palette;};','inline constexpr std::array<Graphic,3> graphics{{']
    lines.extend('{'+','.join(str(r[k]) for k in ('width','height','frame_size','first','palette'))+'},' for r in records);lines+=['}};','}']
    (project/'src/core/suction_particle_data.hpp').write_text('\n'.join(lines)+'\n')
    (project/'docs/stage9/suction-particles.json').write_text(json.dumps(dict(rom_sha256=ROM_HASH,routine='005348..00546E',graphics=records,countdown_reload=2,phases=4,scope='Original artwork and native state/placement; hardware queue/SAT capacity timing remains separate.'),indent=2)+'\n')
if __name__=='__main__':export(Path(__file__).resolve().parents[1])
