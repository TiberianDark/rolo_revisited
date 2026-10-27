"""Export bank4 FAA0 animation data from the pinned ROM; static extraction."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_maps import long,word
def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
    table=long(rom,0xfb82);tracks=[];payload=[];sequences=[]
    for index in range(20):
        at=table+index*12;source=long(rom,at)
        if not source:break
        sequence_source=long(rom,at+4);seq=[]
        for i in range(256):
            value=rom[sequence_source+i]
            if value&128:break
            seq.append(value)
        else:raise ValueError('Unbounded animation sequence')
        if not seq:raise ValueError('Empty animation sequence')
        count=(max(seq)+1)*128;start=len(payload);payload.extend(rom[source:source+count])
        first=len(sequences);sequences.extend(seq)
        tracks.append(dict(source=source,sequence_source=sequence_source,cache_byte_offset=word(rom,at+8),delay=rom[at+10],first=start,bytes=count,sequence_first=first,sequence_count=len(seq)))
    if len(tracks)!=4:raise ValueError('Desert animation table changed')
    out=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::desert_tile_animation_data {']
    for name,values in [('patterns',payload),('sequences',sequences)]:
        out.append(f'inline constexpr std::array<std::uint8_t,{len(values)}> {name}{{{{')
        out.extend(','.join(map(str,values[i:i+32]))+',' for i in range(0,len(values),32));out.append('}};')
    out+=['struct Track {unsigned cache_byte_offset,delay,first,bytes,sequence_first,sequence_count;};','inline constexpr std::array<Track,4> tracks{{']
    out.extend('{'+','.join(str(t[k]) for k in ('cache_byte_offset','delay','first','bytes','sequence_first','sequence_count'))+'},' for t in tracks)
    out+=['}};','}']
    (project/'src/core/desert_tile_animation_data.hpp').write_text('\n'.join(out)+'\n')
    report=dict(rom_sha256=ROM_HASH,table=table,tracks=tracks,scope='FAA0 bank4 four tracks; signed BYTE countdown, sequence sentinel and128byte frame upload. Device queue timing remains separate.')
    (project/'docs/stage9/desert-tile-animation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Exported four original desert animation tracks')
if __name__=='__main__':export(Path(__file__).resolve().parents[1])
