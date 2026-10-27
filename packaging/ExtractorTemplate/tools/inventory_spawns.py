"""Relate sparse markers to traced definition tables; no invented entity names."""
import argparse
import csv
import hashlib
import json
import struct
from pathlib import Path
from inventory_rom import ROM_HASH,definitions

# Counts end at the following inspected code entry, not a blind pointer scan.
TABLES={4:(0x46c6,37,'paired'),5:(0x4762,13,'paired'),6:(0x47ba,24,'direct'),
        11:(0x4874,1,'progress_gate'),13:(0x48fc,2,'direct'),18:(0x4948,4,'companion')}
SPAWN_HANDLERS=[0x46be,0x475a,0x4796,0x481a,0x4826,0x4832,0x483e,0x484e,
                0x4878,0x48d8,0x4904,0x46bc,0x46bc,0x4906,0x490a,0x46bc,
                0x46bc,0x46bc,0x46bc,0x4908]

def resolve_marker(rom,kind):
    category,parameter=kind>>8,kind&255
    result=dict(type=kind,category=category,parameter=parameter,
                status='Special marker path requires semantic tracing')
    if 4<=category<=23:
        result.update(dispatch_slot=0x466c+(category-4)*4,spawn_handler=SPAWN_HANDLERS[category-4])
    # 4648 masks the high byte; 4650 is signed BLT after comparing 2000.
    if 32<=category<128:
        result.update(status='Macro-derived RAM definition via 4958',handler=0xbe4e,
                      mode=category-32,macro=parameter,dispatch_offset=(category-32)*4)
    elif category==17:result['status']='Player spawn-selector marker via 3FE0'
    elif 7<=category<=10:
        result.update(status='16-byte terrain-list record via 4A84; interaction semantics pending',
            resource_pool=0xff6936,resource_stride=16,
            field8=64 if category==7 else 68 if category in (8,9) else parameter*4,
            field10=parameter if category!=10 else 0,field11=255 if category==9 else 0)
    elif category==12:
        result.update(status='RAM macro definition with B80A callback override via 4878; descriptor bounds pending',
            handler=0xb80a,descriptor_table=0x48c8,descriptor_offset=parameter*8)
    elif category in (14,15,16,19,20,21,22,23):
        result['status']='Spawn dispatcher returns directly; other marker consumers pending'
    elif category in TABLES:
        base,count,format=TABLES[category]
        index=parameter//2 if format=='paired' else parameter
        if format=='progress_gate':index=0
        result.update(table=base,index=index,format=format)
        if index<count:
            definition=struct.unpack_from('>I',rom,base+index*4)[0]
            result.update(definition=definition,handler=struct.unpack_from('>I',rom,definition+12)[0],
                          status='Definition table lookup traced; activation/state gates pending')
        else:result['status']='Index outside inspected table extent; needs trace'
    return result

def catalogue(rom,assets,out=None):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH or assets['rom_sha256']!=ROM_HASH:raise ValueError('Unexpected revision')
    defs={d['address'] for d in definitions(rom)};tables=[];markers=[]
    for category,(base,count,format) in TABLES.items():
        pointers=list(struct.unpack_from('>'+str(count)+'I',rom,base))
        if not set(pointers)<=defs:raise ValueError('Spawn table pointer outside definition catalogue')
        tables.append(dict(category=category,base=base,count=count,format=format,definitions=pointers))
    for layout in assets['layouts']:
        for record in layout['records']:
            if record['visual']:continue
            markers.append(dict(layout_source=layout['source'],record_offset=record['offset'],
                                x=record['x'],y=record['y'],**resolve_marker(rom,record['type'])))
    report=dict(rom_sha256=ROM_HASH,tables=tables,markers=markers,
        counts=dict(markers=len(markers),definition_lookups=sum('definition'in m for m in markers),
                    macro_objects=sum('mode'in m for m in markers),
                    terrain_records=sum('resource_pool'in m for m in markers),
                    direct_return_markers=sum(m['status'].startswith('Spawn dispatcher returns') for m in markers),
                    player_spawn_markers=sum(m['category']==17 for m in markers)),
        scope='Static layout-to-definition relation; spawn timing, mutation, activation, facing, AI and interactions unported')
    if out is None:return report
    out.mkdir(parents=True,exist_ok=True)
    (out/'spawn-inventory.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with (out/'spawn-inventory.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=['layout_source','record_offset','x','y','type','category','parameter','definition','handler','mode','status'],extrasaction='ignore')
        w.writeheader();w.writerows(markers)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    assets=json.loads((a.project/'assets/extracted/catalog/manifest.json').read_text(encoding='utf-8'))
    print(json.dumps(catalogue(Path(a.rom).read_bytes(),assets,a.project/'docs/stage9')['counts']))

if __name__=='__main__':main()
