"""Pinned alternate-presentation offset table and accepted EFA8 boundaries."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    values=struct.unpack('>23h',rom[0xdb16:0xdb44])
    (project/'src/core/level1_companion_presentation_data.hpp').write_text('#pragma once\n#include <array>\n#include <cstdint>\nnamespace rolo::companion_presentation_data {\ninline constexpr std::array<std::int16_t,23> head_x{{'+','.join(map(str,values))+'}};\n}\n')
    at=0xefa8;instructions=[]
    while at<0xf046:
        item=Decoder(rom,at).decode()
        instructions.append(item);at+=item['size']
    if at!=0xf046:raise ValueError('Bad code boundary')
    result=dict(rom_sha256=ROM_HASH,instructions=instructions,immutable_data=dict(start='DB16',end_exclusive='DB44',words=values),
        scope='Alternate C512 override presentation, not ordinary selected-bunny rendering; F280 animation-loop gate required')
    (project/'docs/stage9/companion-presentation-export.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':export(Path(__file__).resolve().parents[1]);print('Companion presentation evidence exported')
