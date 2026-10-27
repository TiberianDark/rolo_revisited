"""Pinned immutable companion-menu patterns, name table, SAT templates and colors."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

ASSETS=(('patterns',0x53dc2,0x6b0*2),('layout',0x54b22,28*40*2),
        ('static_sprites',0x3aa4,0x3b06-0x3aa4),
        ('selection_sprites',0x3b06,6*32),('companion_sprites',0x3bc6,24),
        ('inactive_sprites',0x3bde,24),('palette',0x4b78a,64))
RANGES=((0x3900,0x3aa4),(0x20f0,0x2158),(0x2158,0x21c6),
        (0x687a,0x6894),(0x3ca2,0x3cd6),(0x22a8,0x22ce))

def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    lines=['#pragma once','#include <array>','#include <cstdint>',
           'namespace rolo::level1_companion_menu_data {']
    assets=[]
    for name,address,length in ASSETS:
        data=rom[address:address+length]
        lines.append(f'inline constexpr std::array<std::uint8_t,{length}> {name}{{{{')
        for index in range(0,length,24):lines.append(','.join(map(str,data[index:index+24]))+',')
        lines.append('}};')
        assets.append(dict(name=name,address=address,length=length,sha256=hashlib.sha256(data).hexdigest()))
    lines.append('}')
    ranges=[]
    for start,end in RANGES:
        at=start;instructions=[]
        while at<end:
            instruction=Decoder(rom,at).decode()
            instructions.append(instruction);at+=instruction['size']
        if at!=end:raise ValueError(f'Range boundary mismatch {at:x}')
        ranges.append(dict(start=start,end=end,instructions=instructions))
    (project/'src/core/level1_companion_menu_data.hpp').write_text('\n'.join(lines)+'\n')
    evidence=dict(rom_sha256=ROM_HASH,assets=assets,ranges=ranges)
    (project/'docs/stage9/level1-companion-menu-export.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return evidence

if __name__=='__main__':
    result=export(Path(__file__).resolve().parents[1])
    print(f"Exported {len(result['assets'])} menu assets and {len(result['ranges'])} code ranges")
