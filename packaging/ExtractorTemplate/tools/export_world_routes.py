"""Export immutable world routes, retaining odd pointers and overlapping byte streams."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

DESCRIPTORS_START=0xa22c
POOL_START=0xa2ec
POOL_END=0xa368

def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
    descriptors=[]
    for i in range(32):
        at=DESCRIPTORS_START+i*6;pointer,x,y=struct.unpack_from('>IBB',rom,at)
        if pointer and not POOL_START<=pointer<POOL_END:raise ValueError('Route pointer leaves literal data pool')
        if x not in (0,1) or y not in (0,1):raise ValueError('Unproven route sign flag')
        descriptors.append(dict(index=i,address=at,group=i//4,direction_offset=i%4*6,pointer=pointer,negate_x=x,negate_y=y))
    streams=[]
    for pointer in sorted({d['pointer'] for d in descriptors if d['pointer']}):
        at=pointer;pairs=[]
        while True:
            if at>=POOL_END:raise ValueError(f'Unterminated route {pointer:x}')
            x=rom[at]
            if x&128:break
            if at+1>=POOL_END:raise ValueError('Route Y outside bounded data')
            y=rom[at+1];pairs.append(dict(address=at,x=x,y=y,y_signed_view=y if y<128 else y-256));at+=2
        streams.append(dict(pointer=pointer,offset=pointer-POOL_START,terminator_address=at,
            terminator_byte=rom[at],pairs=pairs,pair_count=len(pairs),bytes=rom[pointer:at+1].hex(),
            descriptor_indices=[d['index'] for d in descriptors if d['pointer']==pointer]))
    lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::world_route_data {',
        'struct Descriptor {std::uint32_t pointer;std::uint8_t negate_x,negate_y;};',
        'inline constexpr std::uint32_t pool_start=0xa2ec,pool_end=0xa368;',
        'inline constexpr std::array<Descriptor,32> descriptors{{']
    for d in descriptors:lines.append(f"Descriptor{{0x{d['pointer']:x},{d['negate_x']},{d['negate_y']}}},")
    lines+=['}};',f'inline constexpr std::array<std::uint8_t,{POOL_END-POOL_START}> route_bytes{{{{']
    raw=rom[POOL_START:POOL_END]
    for i in range(0,len(raw),24):lines.append(','.join(map(str,raw[i:i+24]))+',')
    lines+=['}};','struct Stream {std::uint32_t pointer,terminator;std::uint16_t pairs;};',
        f'inline constexpr std::array<Stream,{len(streams)}> streams{{{{']
    for s in streams:lines.append(f"Stream{{0x{s['pointer']:x},0x{s['terminator_address']:x},{s['pair_count']}}},")
    lines+=['}};','}']
    inventory=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted={a for r in inventory['routines'] for a in r['blocks']};ranges=[]
    for start,end in ((0x8728,0x874c),(0xa0e8,0xa204),(0xa204,0xa22c),
            (0x36ba,0x3730),(0x4694,0x4698),(0x4904,0x4906),(0x1b52,0x1b5a)):
        at=start;instructions=[]
        while at<end:
            item=Decoder(rom,at).decode()
            instructions.append(item);at+=item['size']
        if at!=end:raise ValueError('Instruction/data boundary mismatch')
        ranges.append(dict(start=start,end_exclusive=end,instructions=instructions))
    report=dict(rom_sha256=ROM_HASH,descriptors=descriptors,streams=streams,pool_start=POOL_START,pool_end_exclusive=POOL_END,
        pool_sha256=hashlib.sha256(raw).hexdigest(),code_ranges=ranges,
        scope='Finite literal byte streams, not proof of every runtime route/selector/caller domain. Odd pointers and overlapping streams retained. No path sums or emulation.')
    (project/'src/core/world_route_data.hpp').write_text('\n'.join(lines)+'\n')
    (project/'docs/stage9/world-route-export.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    result=export(Path(__file__).resolve().parents[1]);print(f"Exported {len(result['descriptors'])} descriptors, {len(result['streams'])} finite overlapping streams")
