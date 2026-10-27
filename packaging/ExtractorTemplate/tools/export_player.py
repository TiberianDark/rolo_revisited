"""Export first-level collision and selected player animation data; no CPU execution."""
import argparse,json,struct,re
from pathlib import Path
from romtool import read_rom
from rolo_extract import font_evidence
from rolo_maps import word,long,parse_map
from rolo_codec import decode_backward_lz
import export_entrance
from export_preview import rgba,MAGIC
from rolo_sprites import sprite_pixels

def export(rom,root):
    font_evidence(rom)
    raw,_=decode_backward_lz(rom,0x4bc56);layout=parse_map(raw)
    width,height=layout['width']//16,layout['height']//16
    grid=[0]*(width*height);base=0x70128
    for record in layout['records']:
        if not record['visual']: continue
        macro=base+word(rom,base+6+(record['type']&127)*2);mw,mh=rom[macro:macro+2]
        flip=bool(record['type']&0xff00)
        for row in range(mh):
            for col in range(mw):
                value=word(rom,macro+2+2*(row*mw+col))
                if not value: continue
                if flip:value^=0x1000
                x=record['x']//16+col;y=record['y']//16+(mh-1-row if flip else row)
                if 0<=x<width and 0<=y<height:grid[y*width+x]=value
    arrays={'grid':('std::uint16_t',grid),'collision':('std::uint8_t',rom[0x74876:0x74876+4096]),
            'shapes':('std::uint8_t',rom[0x4a71a:0x4ab1a]),
            'walk_forward':('std::int32_t',struct.unpack_from('>34i',rom,0x7e58)),
            'walk_reverse':('std::int32_t',struct.unpack_from('>34i',rom,0x7ee0)),
            'run_forward':('std::int32_t',struct.unpack_from('>34i',rom,0x7f68)),
            'run_reverse':('std::int32_t',struct.unpack_from('>34i',rom,0x7ff0))}
    lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::player_data {',
           f'inline constexpr int width={width},height={height};']
    for name,(kind,values) in arrays.items():
        lines.append(f'inline constexpr std::array<{kind},{len(values)}> {name}{{{{')
        for i in range(0,len(values),24):lines.append('  '+','.join(str(v) for v in values[i:i+24])+',')
        lines.append('}};')
    lines.append('}')
    (root/'src/core/player_data.hpp').write_text('\n'.join(lines)+'\n')
    original=export_entrance.PROGRAMS
    try:
        export_entrance.OPS[28]='RepeatWhileNegative'
        export_entrance.PROGRAMS=((0x13ecc,(0,4,8,12,16,20)),(0x13eee,(0,4,8,12,16,20)))
        path=root/'src/core/player_animation_data.hpp'
        result=export_entrance.export(rom,path)
        path.write_text(path.read_text().replace('rolo::entrance_data','rolo::player_animation_data'))
        palette_raw=b''.join(rom[long(rom,0x4b09a+i*4):long(rom,0x4b09a+i*4)+32] for i in range(4))
        colors=[tuple(((v>>s)&7)*255//7 for s in (1,5,9)) for v in struct.unpack('>64H',palette_raw)][32:48]
        records=[];seen=set()
        for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',path.read_text()):
            descriptor,left,right,ox,oy,w,h,size=[int(v,0) for v in match.groups()]
            for source in (left,right):
                if not source or (source,w,h) in seen:continue
                seen.add((source,w,h));pixels=sprite_pixels(rom[source:source+size],w,h)
                raw=rgba(pixels,colors,True);records.append(struct.pack('<6I',3,source,2,w,h,len(raw))+raw)
        (root/'bin/player-assets.rla').write_bytes(MAGIC+struct.pack('<I',len(records))+b''.join(records))
    finally:
        export_entrance.PROGRAMS=original
        export_entrance.OPS.pop(28,None)
    (root/'docs/player-export.json').write_text(json.dumps({'grid_cells':len(grid),'animation':result,
        'scope':'First-level static collision grid, four directional query records per metatile, 64 shape profiles, normal Rolo body/head selectors only'},indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--project',required=True)
    a=p.parse_args();print(export(read_rom(a.rom),Path(a.project)))
