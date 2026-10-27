"""Export pinned original normal-frame status HUD assets and boundary evidence."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

ASSETS=(('sprite_templates',0x5216,40),('portrait',0x1602a,384),
        ('life_label',0x27bc0,64),('digits',0x27940,640),
        ('key',0x2f1e0,128),('piece',0x2eac0,128))

def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    lines=['#pragma once','#include <array>','#include <cstdint>',
           'namespace rolo::level1_status_hud_data {']
    assets=[]
    for name,address,length in ASSETS:
        data=rom[address:address+length]
        lines.append(f'inline constexpr std::array<std::uint8_t,{length}> {name}{{{{')
        for index in range(0,length,24):lines.append(','.join(map(str,data[index:index+24]))+',')
        lines.append('}};')
        assets.append(dict(name=name,address=address,length=length,sha256=hashlib.sha256(data).hexdigest()))
    lines.append('}')
    (project/'src/core/level1_status_hud_data.hpp').write_text('\n'.join(lines)+'\n')
    inventory=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted={address for routine in inventory['routines'] for address in routine['blocks']}
    instructions=[];at=0x5060
    while at<0x5216:
        instruction=Decoder(rom,at).decode()
        if at not in accepted:raise ValueError(f'Unaccepted instruction boundary {at:x}')
        instructions.append(instruction);at+=instruction['size']
    if at!=0x5216:raise ValueError('HUD code overlaps sprite-template data')
    evidence=dict(rom_sha256=ROM_HASH,entry=0x5060,end=0x5216,assets=assets,instructions=instructions,
        contracts={'sprite_count':'append five before status updates',
        'initialization':'C523 zero sets FF then 51D0',
        'lives':'C51D byte compared against C51F; signed-negative skips digit upload',
        'score':'C52E long converted by719A to eight digits atC4C0, cachedC532',
        'key':'signed-positive C550 becomes FF, sound37, upload B100',
        'piece':'signed-positive C551 becomes FF, sound37, upload B180'})
    (project/'docs/stage9/level1-status-hud-export.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return evidence

if __name__=='__main__':
    result=export(Path(__file__).resolve().parents[1])
    print(f"Exported {len(result['assets'])} HUD assets; {len(result['instructions'])} accepted instructions")
