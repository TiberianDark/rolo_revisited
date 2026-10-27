"""Export immutable rescue-counter artwork and callback wave from the pinned ROM."""
from pathlib import Path
import hashlib,struct
from inventory_rom import ROM_HASH
def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
    lines=['#pragma once','#include "core/actor_definition.hpp"','namespace rolo::level1_hud_data {']
    lines.append('inline constexpr ActorDefinition definition{0x1476e,{'+','.join(map(str,rom[0x1476e:0x1476e+34]))+'}};')
    def array(name,ctype,values):
        lines.append(f'inline constexpr std::array<{ctype},{len(values)}> {name}{{{{')
        for at in range(0,len(values),24):lines.append(','.join(map(str,values[at:at+24]))+',')
        lines.append('}};')
    array('wave','std::int16_t',struct.unpack('>23h',rom[0xd49e:0xd4cc]))
    array('label','std::uint8_t',rom[0x322e0:0x32360])
    array('blank','std::uint8_t',rom[0x32360:0x323a0])
    array('icon','std::uint8_t',rom[0x27bc0:0x27c00])
    array('digits','std::uint8_t',rom[0x27940:0x27bc0])
    lines.append('}')
    (project/'src/core/level1_hud_data.hpp').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':export(Path(__file__).resolve().parents[1])
