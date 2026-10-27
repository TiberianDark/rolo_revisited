"""Pinned world cursor13EAA animation and original palette graphics export."""
import hashlib,json,re,struct
from pathlib import Path
from inventory_rom import ROM_HASH
import export_entrance
from rolo_maps import long
from rolo_sprites import sprite_pixels
from export_preview import rgba,MAGIC

def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
    definition=0x13eaa
    header=project/'src/core/world_cursor_data.hpp'
    old=export_entrance.PROGRAMS
    try:
        export_entrance.PROGRAMS=((definition,(0,4,8,12)),)
        report=export_entrance.export(rom,header)
    finally:export_entrance.PROGRAMS=old
    content=header.read_text().replace('rolo::entrance_data','rolo::world_cursor_data')
    content=content.replace('#include "core/animation.hpp"','#include "core/animation.hpp"\n#include "core/actor_definition.hpp"')
    content=content.replace('inline constexpr AnimationData data',
        'inline constexpr ActorDefinition definition{0x13eaa,{'+','.join(map(str,rom[definition:definition+34]))+'}};\ninline constexpr AnimationData data')
    header.write_text(content)
    palettes=[]
    for i in range(4):
        source=long(rom,0x4b08a+i*4)
        palettes.append([tuple(((v>>s)&7)*255//7 for s in (1,5,9)) for v in struct.unpack_from('>16H',rom,source)])
    records=[];seen=set()
    for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',content):
        descriptor,left,right,ox,oy,w,h,size=[int(v,0) for v in match.groups()]
        for graphics in (left,right):
            if not graphics or(graphics,w,h)in seen:continue
            seen.add((graphics,w,h))
            for bank,colors in enumerate(palettes):
                pixels=rgba(sprite_pixels(rom[graphics:graphics+size],w,h),colors,True)
                records.append(struct.pack('<6I',3,graphics,bank,w,h,len(pixels))+pixels)
    (project/'bin/world-cursor-assets.rla').write_bytes(MAGIC+struct.pack('<I',len(records))+b''.join(records))
    report.update(rom_sha256=ROM_HASH,definition='13EAA',selectors=[0,4,8,12],palette_sources=[long(rom,0x4b08a+i*4) for i in range(4)],graphics_records=len(records),
        scope='Original idle and reachable route movement cursor selectors, using world palette; pause actor14EDE not included')
    (project/'docs/stage9/world-cursor-export.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(export(Path(__file__).resolve().parents[1]))
