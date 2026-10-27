"""Export the pinned world MAP0 and jigsaw mask tables, without running ROM code."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_codec import decode_backward_lz
from rolo_maps import long,word,parse_map
from m68k_static import Decoder
def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    foreground=decode_backward_lz(rom,long(rom,0x4ab1a)&0xffffff)[0]
    layout=parse_map(foreground);bank=layout['bank']
    graphics=decode_backward_lz(rom,long(rom,0x4af2a+bank*4))[0]
    palette=b''.join(rom[long(rom,0x4b08a+i*4):long(rom,0x4b08a+i*4)+32] for i in range(4))
    # Follow the same bounded bank tables used by the Level1 terrain export.
    quad=long(rom,0x4af6e+bank*4);macro=long(rom,0x4afb2+bank*4)
    if rom[macro:macro+4]!=b'ITMS':raise ValueError('Missing original macro header')
    offsets=[word(rom,macro+6+i*2) for i in range(word(rom,macro+4))]
    end=max(macro+v+2+rom[macro+v]*rom[macro+v+1]*2 for v in offsets)
    macros=rom[macro:end]
    values=[]
    for offset in offsets:
        p=macro+offset
        values += [word(rom,p+2+i*2)&0x1ff for i in range(rom[p]*rom[p+1])]
    quads=rom[quad:quad+max(0,max(values)-27)*8]
    pieces=[];edge_index=0
    for group in range(3):
        descriptor=0x4baaa+group*8;ptr=long(rom,descriptor);stride=word(rom,descriptor+4);base=word(rom,descriptor+6)
        for row in range(4):
            for col in range(stride):
                node=ptr+row*stride+col;selector=rom[node];edges=rom[0x13e59+edge_index];edge_index+=1
                prevstride=word(rom,descriptor-4);prevbase=word(rom,descriptor-2)
                nextbase=word(rom,descriptor+14)
                deltas=(1,-1,stride if row<3 else stride+base-nextbase,
                    -stride if row else -(prevstride+prevbase-base))
                neighbors=[rom[node+d] for d in deltas]
                for direction,value in enumerate(neighbors):
                    if ((edges>>(direction*2))&3)==2 and value>=80:raise ValueError('Unbound required neighbor flag')
                pieces.append(dict(selector=selector,group=group,row=row,column=col,stride=stride,xbase=base,
                    edges=edges,neighbors=neighbors))
    assets=(('foreground',foreground),('graphics',graphics),('palette',palette),('quads',quads),('macros',macros),
        ('common_quads',rom[0x6b452:0x6b452+28*8]),('common_patterns',rom[0x53dc2:0x54b22]),
        ('return_coordinates',rom[0x4ad9a:0x4ad9a+160]),
        ('completion_selectors',bytes(rom[0x4ab1e+i*8] for i in range(80))),('completed_marker',rom[0x314e0:0x31560]),
        ('palette_cycle',rom[0x9e2c:0x9e3a]))
    lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::world_map_data {']
    for name,data in assets:
        lines.append(f'inline constexpr std::array<std::uint8_t,{len(data)}> {name}{{{{')
        for i in range(0,len(data),24):lines.append(','.join(map(str,data[i:i+24]))+',')
        lines.append('}};')
    lines+=['struct Piece {std::uint8_t selector,group,row,column,stride,xbase,edges;std::array<std::uint8_t,4> neighbors;};',
        f'inline constexpr std::array<Piece,{len(pieces)}> pieces{{{{']
    for p in pieces:lines.append('Piece{%s,{%s}},'%(','.join(str(p[k]) for k in ('selector','group','row','column','stride','xbase','edges')),','.join(map(str,p['neighbors']))))
    lines+=['}};','}']
    (project/'src/core/world_map_data.hpp').write_text('\n'.join(lines)+'\n')
    ranges=[]
    for start,end in ((0xa50a,0xa656),(0xa66e,0xa75a),(0x9a5e,0x9a88),(0x37e8,0x3832)):
        at=start;instructions=[]
        while at<end:
            instruction=Decoder(rom,at).decode()
            instructions.append(instruction);at+=instruction['size']
        if at!=end:raise ValueError('World code/data boundary mismatch')
        ranges.append(dict(start=start,end=end,instructions=instructions))
    report=dict(rom_sha256=ROM_HASH,bank=bank,width=layout['width'],height=layout['height'],quad_address=quad,macro_address=macro,code_ranges=ranges,
        pieces=pieces,assets=[dict(name=n,length=len(d),sha256=hashlib.sha256(d).hexdigest()) for n,d in assets])
    (project/'docs/stage9/world-map-export.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    result=export(Path(__file__).resolve().parents[1]);print(f"Exported {len(result['pieces'])} jigsaw slots, {len(result['assets'])} assets")
