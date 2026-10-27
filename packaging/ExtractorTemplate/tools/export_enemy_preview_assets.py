"""Export original first-family pixels for native rendering, never ROM execution."""
import hashlib
import json
import re
import struct
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_sprites import sprite_pixels
from export_preview import rgba,MAGIC

def build(rom,header):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('Pinned ROM mismatch')
    palette=[]
    for bank in range(4):
        source=struct.unpack_from('>I',rom,0x4b09a+bank*4)[0]
        palette.extend(tuple(((v>>s)&7)*255//7 for s in (1,5,9)) for v in struct.unpack_from('>16H',rom,source))
    banks={(int.from_bytes(rom[d+6:d+8],'big')>>13)&3 for d in (0x13f98,0x13fba,0x140ec)}
    if banks!={3}:raise ValueError('First-family palette assignments differ')
    seen=set();records=[];manifest=[]
    for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',header):
        descriptor,left,right,ox,oy,width,height,size=map(lambda v:int(v,0),match.groups())
        for source in (left,right):
            if not source or (source,width,height) in seen:continue
            seen.add((source,width,height));raw=rom[source:source+size]
            if len(raw)!=size:raise ValueError('Sprite extent')
            pixels=rgba(sprite_pixels(raw,width,height),palette[48:64],True)
            records.append(struct.pack('<6I',3,source,3,width,height,len(pixels))+pixels)
            manifest.append(dict(source=f'{source:06X}',width=width,height=height,palette=3,
                rgba_sha256=hashlib.sha256(pixels).hexdigest()))
    if not records:raise ValueError('No first-family frames')
    return MAGIC+struct.pack('<I',len(records))+b''.join(records),manifest

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1]
    pack,frames=build((project/'local/rolo.md').read_bytes(),
        (project/'src/core/first_enemy_animation_data.hpp').read_text(encoding='utf-8'))
    (project/'bin/first-enemy-assets.rla').write_bytes(pack)
    (project/'docs/stage9/first-enemy-pixels.json').write_text(json.dumps(dict(rom_sha256=ROM_HASH,
        pack_sha256=hashlib.sha256(pack).hexdigest(),frames=frames,
        scope='Original pixels and first-level palette for exported body/link/score frames. Native rendering resource only; no enemy world integration or fidelity completion.'),indent=2)+'\n',encoding='utf-8')
    print({'variants':len(frames),'bytes':len(pack)})
