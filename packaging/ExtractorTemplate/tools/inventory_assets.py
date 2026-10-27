"""Catalogue and extract traced layout/graphics/music tables, without rendering or CPU execution."""
import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path
from inventory_rom import ROM_HASH,sound_assets
from rolo_codec import decode_backward_lz
from rolo_maps import parse_map

def catalogue(rom,out):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('Unexpected ROM revision')
    out.mkdir(parents=True,exist_ok=True);layouts={};slots=[];banks=[];errors=[]
    def save(relative,data):
        p=out/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        return dict(path=relative,size=len(data),sha256=hashlib.sha256(data).hexdigest())
    for selector in range(80):
        pointers=struct.unpack_from('>II',rom,0x4ab1a+selector*8)
        entry=dict(selector=selector,spawn_selector=pointers[0]>>24,
                   background_parameter=pointers[1]>>24,camera_mode=rom[0x4aeda+selector])
        palette_sources=list(struct.unpack_from('>4I',rom,0x4b08a+selector*16))
        if any(source+32>len(rom) for source in palette_sources):raise ValueError('Palette outside ROM')
        palette=b''.join(rom[source:source+32] for source in palette_sources)
        entry.update(palette_sources=palette_sources,palette_artifact=save('palettes/selector-%02d.cram'%selector,palette))
        for layer,packed in zip(('foreground','background'),pointers):
            source=packed&0xffffff;entry[layer]=source
            if layer=='background' and selector==0:
                entry['background_status']='Generated world-map background via A558';continue
            if source in layouts:continue
            try:
                if rom[source:source+3]==b'MAP':data=rom[source:];codec=None
                else:data,codec=decode_backward_lz(rom,source)
                layout=parse_map(data);data=data[:layout['row_offsets'][-1]]
                artifact=save('maps/%06X.map'%source,data)
                layouts[source]=dict(source=source,width=layout['width'],height=layout['height'],bank=layout['bank'],
                    record_count=len(layout['records']),types=dict(sorted(Counter('%04X'%r['type'] for r in layout['records']).items())),
                    records=layout['records'],codec=codec,artifact=artifact,
                    scope='Sparse layout and marker records; actor semantics pending')
            except ValueError as e:errors.append(dict(selector=selector,layer=layer,source=source,reason=str(e)))
        slots.append(entry)
    for bank in range(17):
        record=dict(bank=bank)
        for name,base in [('graphics',0x4af2a),('quads',0x4af6e),('macros',0x4afb2),('collision',0x4aff6)]:
            record[name]=struct.unpack_from('>I',rom,base+bank*4)[0]
        if bank>=8 and record['graphics']==0x6b452:
            record['status']='Placeholder slot: points at common quad data; not a packed graphics bank; no observed selector uses it'
            banks.append(record);continue
        macros=record['macros']
        if rom[macros:macros+4]!=b'ITMS':raise ValueError('Macro signature differs')
        count=struct.unpack_from('>H',rom,macros+4)[0];macro_records=[];end=6+count*2
        for slot in range(count):
            relative=struct.unpack_from('>H',rom,macros+6+slot*2)[0]
            width,height=rom[macros+relative:macros+relative+2]
            extent=relative+2+width*height*2
            if extent>len(rom)-macros:raise ValueError('Macro data exceeds ROM')
            end=max(end,extent)
            macro_records.append(dict(slot=slot,relative=relative,width=width,height=height))
        record.update(macro_records=macro_records,macro_artifact=save('macros/bank-%02d.itms'%bank,rom[macros:macros+end]))
        try:
            data,codec=decode_backward_lz(rom,record['graphics'])
            record.update(codec=codec,artifact=save('graphics/bank-%02d.4bpp'%bank,data),
                          pattern_count=len(data)//32,pattern_aligned=len(data)%32==0)
        except ValueError as e:errors.append(dict(bank=bank,source=record['graphics'],reason=str(e)))
        banks.append(record)
    music=[];seen=set()
    for asset in sound_assets(rom):
        if asset['kind']!='music':continue
        source=asset['source']
        if source in seen:continue
        seen.add(source)
        data,codec=decode_backward_lz(rom,source)
        music.append(dict(source=source,codec=codec,artifact=save('music/%06X.seq'%source,data),
                          scope='Decoded sequence bytes; command semantics and playback pending'))
    report=dict(rom_sha256=ROM_HASH,selectors=slots,layouts=list(layouts.values()),graphics_banks=banks,
        music_sources=music,unresolved=errors,
        counts=dict(selector_slots=80,unique_layouts=len(layouts),graphics_bank_slots=17,
                    decoded_graphics_banks=sum('artifact' in r for r in banks),
                    music_sources=len(music),palette_rows=80,errors=len(errors)),
        scope='Asset table extraction only; not playable level or sound coverage')
    report['observed_map_banks']=sorted({r['bank'] for r in layouts.values()})
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.out);print(json.dumps(report['counts']))

if __name__=='__main__':main()
