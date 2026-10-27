"""Build a bounded RGBA asset pack for the native SDL3 entrance preview."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from rolo_extract import font_evidence
from rolo_codec import decode_backward_lz
from rolo_stage2 import target_palettes,map_pixels
from rolo_sprites import sprite_pixels
from romtool import read_rom,extract
MAGIC=b'RLOAS01\0'

def rgba(pixels,colors,transparent=False):
    return bytes(channel for value in pixels for channel in (*colors[value],0 if transparent and value%16==0 else 255))

def build_pack(data,header):
    font_evidence(data);_,colors,_=target_palettes(data);vram=bytearray(65536)
    for source,dest in ((0x28a80,0x1540),(0x44f1c,0x7300)):
        decoded,_=decode_backward_lz(data,source);vram[dest:dest+len(decoded)]=decoded
    records=[]
    for kind,source,w,h,base in ((0,0x2b680,40,14,0xaa),(1,0x2bae0,40,14,0x80aa),(2,0x4592c,40,6,0xe398)):
        width,height,pixels,_=map_pixels(vram,extract(data,source,w*h*2),w,h,base)
        records.append((kind,source,0,width,height,rgba(pixels,colors,kind!=0)))
    # Definition -> palette is traced from the definition attribute word at +6.
    frame_banks={};pending=[];visited=set()
    from export_entrance import PROGRAMS
    for definition,selectors in PROGRAMS:
        bank=(int.from_bytes(data[definition+6:definition+8],'big')>>13)&3
        table=int.from_bytes(data[definition+18:definition+22],'big')
        pending.extend((int.from_bytes(data[table+selector+1:table+selector+4],'big'),bank) for selector in selectors)
    while pending:
        address,bank=pending.pop()
        if (address,bank) in visited:continue
        if len(visited)>1024:raise ValueError('Frame palette graph limit')
        visited.add((address,bank));word=struct.unpack_from('>i',data,address)[0]
        if word>0:
            frame_banks.setdefault(word,set()).add(bank);pending.append((address+4,bank))
        else:
            control=-(word>>16)
            if control in (0,44,64):pending.append((int.from_bytes(data[address+4:address+8],'big'),bank))
            if control in (44,64):pending.append((address+8,bank))
            elif control in (12,40,52):pending.append((address+4,bank))
            elif control not in (0,4,60,68):raise ValueError('Untraced palette control')
    seen=set()
    for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',header):
        descriptor,left,right,ox,oy,width,height,size=[int(x,0) for x in match.groups()]
        if descriptor not in frame_banks:raise ValueError('Generated frame is not reachable')
        for bank in sorted(frame_banks[descriptor]):
            for source in (left,right):
                key=(source,bank,width,height)
                if not source or key in seen:continue
                seen.add(key);pixels=sprite_pixels(extract(data,source,size),width,height)
                records.append((3,source,bank,width,height,rgba(pixels,colors[bank*16:bank*16+16],True)))
    if not seen:raise ValueError('No generated sprite frames found')
    payload=MAGIC+struct.pack('<I',len(records))
    entries=[]
    for kind,source,bank,width,height,raw in records:
        payload+=struct.pack('<6I',kind,source,bank,width,height,len(raw))+raw
        entries.append(dict(kind=kind,source=source,palette_bank=bank,width=width,height=height,sha256=hashlib.sha256(raw).hexdigest()))
    return payload,{'format':'RLOAS01','rom_sha256':hashlib.sha256(data).hexdigest(),'records':entries,
                    'pack_sha256':hashlib.sha256(payload).hexdigest(),'target_palettes':True,'gameplay_ported':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--header',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    payload,manifest=build_pack(read_rom(a.rom),Path(a.header).read_text());out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(payload);out.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Packed',len(manifest['records']),'RGBA textures')
