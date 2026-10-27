"""Pinned literal fade interpolation data; no ROM execution."""
from pathlib import Path
import hashlib,json,struct
from inventory_rom import ROM_HASH
def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
    lookup=rom[0x30c6:0x313e];black=list(struct.unpack_from('>16H',rom,0x32360))
    if len(lookup)!=120 or any(black):raise ValueError('Unexpected original fade data')
    return dict(rom_sha256=ROM_HASH,lookup_start='30C6',lookup_end_exclusive='313E',lookup=list(lookup),black_start='32360',black_words=black,
        scope='Literal interpolation lookup and black target for typed2FF6/3060/63FA. Interrupt cadence and full transition/publication remain separately required.')
def export(project):
    report=catalogue(project)
    lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::palette_effect_data {','inline constexpr std::array<std::uint8_t,120> lookup{{']
    values=report['lookup']
    for i in range(0,len(values),24):lines.append(','.join(map(str,values[i:i+24]))+',')
    lines+=['}};','inline constexpr std::array<std::uint16_t,16> black{};','}']
    (project/'src/core/palette_effect_data.hpp').write_text('\n'.join(lines)+'\n')
    (project/'docs/stage9/palette-effect-export.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':export(Path(__file__).resolve().parents[1]);print('Exported original120-byte interpolation table and16 black words')
