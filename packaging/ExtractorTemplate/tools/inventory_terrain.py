"""Extract referenced terrain records; preserves bounds uncertainty, executes no CPU."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from inventory_rom import ROM_HASH

def collision_record(raw):
    if len(raw)!=8:raise ValueError('Collision record must contain eight bytes')
    return [dict(direction=name,offset_byte=raw[offset],shape_byte=raw[offset+1],
                 shape_index=raw[offset+1]&63,mirror_bit=bool(raw[offset+1]&64),
                 bit7=bool(raw[offset+1]&128)) for name,offset in [('floor',0),('ceiling',2),('right',4),('left',6)]]

def catalogue(rom,catalog,out=None):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH or catalog['rom_sha256']!=ROM_HASH:raise ValueError('Unexpected revision')
    if out is not None:out.mkdir(parents=True,exist_ok=True)
    def save(name,data):
        if out is not None:(out/name).write_bytes(data)
        return dict(path=name,size=len(data),sha256=hashlib.sha256(data).hexdigest())
    banks=[];all_shapes=set()
    for bank in catalog['graphics_banks']:
        if 'macro_records' not in bank:continue
        values=set()
        for macro in bank['macro_records']:
            source=bank['macros']+macro['relative']+2;count=macro['width']*macro['height']
            values.update(struct.unpack_from('>'+str(count)+'H',rom,source))
        tile_ids=sorted({value&511 for value in values if value})
        solid_ids=sorted({value&511 for value in values if value&0x4000})
        quads=[];collisions=[]
        for index in tile_ids:
            common=index<28;source=0x6b452+index*8 if common else bank['quads']+(index-28)*8
            raw=rom[source:source+8]
            if len(raw)!=8:raise ValueError('Quad outside ROM')
            patterns=struct.unpack('>4H',raw)
            if not common and any((word&0x7ff)>=bank['pattern_count'] for word in patterns):
                raise ValueError('Referenced quad pattern outside decoded graphics')
            quads.append(dict(index=index,source=source,common=common,raw=raw.hex(),pattern_words=list(patterns)))
        for index in solid_ids:
            source=bank['collision']+index*8;raw=rom[source:source+8]
            directions=collision_record(raw);all_shapes.update(row['shape_index'] for row in directions)
            collisions.append(dict(index=index,source=source,raw=raw.hex(),directions=directions))
        length=(max(solid_ids)+1)*8 if solid_ids else 0
        payload=rom[bank['collision']:bank['collision']+length]
        banks.append(dict(bank=bank['bank'],macro_value_words=sorted(values),quad_records=quads,
            collision_records=collisions,collision_prefix=save('bank-%02d-collision-prefix.bin'%bank['bank'],payload),
            collision_source=bank['collision'],collision_prefix_scope='Prefix covering solid IDs in all inspected ITMS macros; not proof of complete collision table extent or every runtime-generated tile',
            counts=dict(referenced_quads=len(quads),referenced_solid_records=len(collisions))))
    shapes=rom[0x4a71a:0x4ab1a]
    report=dict(rom_sha256=ROM_HASH,banks=banks,shape_profiles=save('shape-profiles.bin',shapes),
        common_quads=save('common-quads.bin',rom[0x6b452:0x6b452+28*8]),
        used_shape_indices=sorted(all_shapes),
        evidence_sites=['3D3C','3D3E','3D42','3D44','3D4A','3D56','3D70','3D74','3870','388A','38A6','38C2','879A','87BC','87DC','87F6'],
        counts=dict(banks=len(banks),referenced_quads=sum(b['counts']['referenced_quads'] for b in banks),
            referenced_solid_records=sum(b['counts']['referenced_solid_records'] for b in banks),shape_profiles=64),
        scope='All inspected macro banks, not all dynamic terrain states. Collision offsets remain unsigned bytes as read by 879A..880E; final directional geometry, flips, shape flags and grid streaming need consuming-code/native/reference verification.')
    if out is not None:(out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    catalog=json.loads((a.project/'assets/extracted/catalog/manifest.json').read_text(encoding='utf-8'))
    report=catalogue(Path(a.rom).read_bytes(),catalog,a.project/'assets/extracted/catalog/terrain')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
