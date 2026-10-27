"""Cross-reference inspected animation controls with field, spawn, RNG and sound effects."""
import argparse
import hashlib
import json
from pathlib import Path
from inventory_rom import ROM_HASH

READ_COMMANDS={16,20,24,28,32,36}
RNG_COMMANDS={40,44,48,100,104}

def effects(control,rom):
    command=control['command'];parameter=control['parameter'];site=control['address']
    raw=int.from_bytes(rom[site:site+4],'big',signed=True)
    if len(rom[site:site+4])!=4 or raw>0 or -(raw>>16)!=command or raw&65535!=parameter:
        raise ValueError('Animation control bytes differ')
    row=dict(control,field_reads=[],field_writes=[],shared_rng=command in RNG_COMMANDS)
    if command in READ_COMMANDS:
        offset=parameter if parameter<0x8000 else parameter-0x10000
        row['field_reads'].append(dict(offset=offset,width=1,condition_command=command))
    if command==56:row['field_writes'].append(dict(offset=parameter>>8,width=1,value=parameter&255))
    if command==80:row['field_writes'].append(dict(offset=70,width=2,value=parameter))
    if command==8:row['field_writes'] += [dict(offset=116,width=1,value=255),dict(offset=125,width=1,set_bits=[2])]
    if command in (108,112):row['field_writes'].append(dict(offset=125,width=1,**({'set_bits':[1]} if command==108 else {'clear_bits':[1]})))
    if command in (84,88):row['field_reads'].append(dict(offset=124,width=1,test_bits=[0]))
    if command==116:row['sound_request']=parameter
    if command in (92,100):
        if site+8>len(rom):raise ValueError('Animation spawn definition truncated')
        row['spawn_definition']=int.from_bytes(rom[site+4:site+8],'big')
        row['spawn_scope']='Candidate sequence reference; allocation depends on runtime execution and pool state'
    row['scope']='Selected explicit side effects only; timing, sequence pointers and complete command semantics are in the command specification'
    return row

def catalogue(rom,animations):
    if animations['rom_sha256']!=ROM_HASH or hashlib.sha256(rom).hexdigest()!=ROM_HASH:
        raise ValueError('Animation revision mismatch')
    controls={};sources={}
    for kind,key in [('default','cases'),('candidate','candidate_programs')]:
        for program in animations[key]:
            source=dict(kind=kind,table=program['table'],selector=program['selector'])
            if kind=='default':source['definition']=program['definition']
            for control in program.get('controls',[]):
                address=control['address']
                if address in controls and controls[address]!=control:raise ValueError('Conflicting animation control')
                controls[address]=control
                bucket=sources.setdefault(address,[])
                if source not in bucket:bucket.append(source)
    rows=[]
    for site,control in sorted(controls.items()):
        row=effects(control,rom);row['program_sources']=sources[site];rows.append(row)
    byte_writes=[write for row in rows if row['command']==56 for write in row['field_writes']]
    return dict(rom_sha256=ROM_HASH,controls=rows,
        generic_byte_write_domains=[dict(offset=offset,values=sorted({w['value'] for w in byte_writes if w['offset']==offset})) for offset in sorted({w['offset'] for w in byte_writes})],
        counts=dict(unique_control_sites=len(rows),observed_commands=len({r['command'] for r in rows}),generic_byte_write_sites=sum(r['command']==56 for r in rows),
            generic_byte_write_offsets=len({w['offset'] for w in byte_writes}),spawn_control_sites=sum('spawn_definition' in r for r in rows),sound_control_sites=sum('sound_request' in r for r in rows)),
        scope='Default-selector and conservative table-prefix control union. No claim all controls execute, all selector programs were found, or field meanings are globally shared. Generic command56 can address any unsigned-byte offset; reported domains are only observed inspected operands.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    animations=json.loads((a.project/'assets/extracted/catalog/animations/manifest.json').read_text(encoding='utf-8'))
    report=catalogue(Path(a.rom).read_bytes(),animations)
    (a.project/'docs/stage9/animation-effects.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
