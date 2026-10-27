"""Inventory default selectors of all ROM definitions; preserve unsupported sequence gaps."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from inventory_rom import ROM_HASH,definitions
from rolo_sprites import sequence_frames,frame_record
from romtool import extract

def table_candidates(rom,table,ceiling):
    """Conservative valid-pointer prefix, bounded by earliest referenced sequence.

    The format has no length field. This produces candidates, not proof that all
    possible selectors are valid or that this is the complete table.
    """
    rows=[];bound=ceiling
    for selector in range(0,512,4):
        address=table+selector
        if address+4>bound:break
        row=extract(rom,address,4);sequence=int.from_bytes(row[1:],'big')
        if not max(0x1015a,address+4)<=sequence<0x13eaa or sequence%2:break
        bound=min(bound,sequence)
        rows.append(dict(table=table,selector=selector,delay=row[0],sequence=sequence,
                         scope='Valid-pointer prefix candidate; selector bounds require routine evidence'))
    return rows

def catalogue(rom,out):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('Unexpected ROM revision')
    out.mkdir(parents=True,exist_ok=True);cases=[];frames={};issues=[]
    def collect_frames(descriptors):
        for address in descriptors:
            if address in frames:continue
            if extract(rom,address,18)==bytes(18):
                frame=dict(descriptor=address,graphics=[0,0],offset_x=0,offset_y=0,width=0,height=0,byte_count=0,
                           status='Zero-filled descriptor preserved; visibility and pipeline behavior require original trace')
            else:frame=frame_record(rom,address)
            frame['variants']=[]
            for direction,source in enumerate(frame['graphics']):
                if not source:continue
                raw=extract(rom,source,frame['byte_count']);name='frames/%06X-%d.4bpp'%(address,direction)
                target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
                frame['variants'].append(dict(source=source,path=name,size=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
            frames[address]=frame
    for definition in definitions(rom):
        entry=dict(definition=definition['address'],handler=definition['handler'],
                   table=definition['animation_table'],selector=definition['selector'],
                   scope='Default selector only; runtime selector writes and conditional execution pending')
        if entry['table']==0:
            entry['status']='No ordinary animation table; special/list membership trace required'
            cases.append(entry);continue
        try:
            row=extract(rom,entry['table']+entry['selector'],4)
            entry.update(delay=row[0],sequence=int.from_bytes(row[1:],'big'))
            descriptors,controls=sequence_frames(rom,entry['sequence'])
            entry.update(descriptors=descriptors,controls=controls,status='Known-control static frame union')
            collect_frames(descriptors)
        except (ValueError,struct.error) as error:
            entry['status']='Needs sequence/descriptor tracing';entry['issue']=str(error)
            issues.append(dict(definition=entry['definition'],issue=str(error)))
        cases.append(entry)
    tables=sorted({c['table'] for c in cases if c['table']});candidates=[];candidate_issues=[]
    for index,table in enumerate(tables):
        ceiling=tables[index+1] if index+1<len(tables) else 0x13eaa
        for row in table_candidates(rom,table,ceiling):
            try:
                descriptors,controls=sequence_frames(rom,row['sequence'])
                row.update(descriptors=descriptors,controls=controls,status='Known-control static frame union')
                collect_frames(descriptors)
            except (ValueError,struct.error) as error:
                row['issue']=str(error);candidate_issues.append(dict(table=table,selector=row['selector'],issue=str(error)))
            candidates.append(row)
    report=dict(rom_sha256=ROM_HASH,cases=cases,candidate_programs=candidates,candidate_issues=candidate_issues,
        frames=list(frames.values()),unresolved=issues,
        counts=dict(definitions=len(cases),default_selectors_traced=sum('issue' not in c and 'sequence' in c for c in cases),
                    no_ordinary_animation_table=sum(c['table']==0 for c in cases),
                    candidate_programs=len(candidates),unresolved_candidates=len(candidate_issues),
                    descriptor_count=len(frames),graphics_variants=sum(len(f['variants']) for f in frames.values()),
                    unresolved_defaults=len(issues)),
        scope='Default-selector evidence plus conservative table-prefix candidates; no complete animation or behavior coverage claim')
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    print(json.dumps(catalogue(Path(a.rom).read_bytes(),a.out)['counts']))

if __name__=='__main__':main()
