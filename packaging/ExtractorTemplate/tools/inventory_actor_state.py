"""Group syntactic A5 field accesses across accepted instructions, preserving width overlap."""
import argparse,json
from pathlib import Path
from inventory_rom import inventory
from inventory_macro_handlers import actor_accesses

def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs');owners={}
    for routine in inv['routines']:
        for site in routine['blocks']:owners.setdefault(site,[]).append(routine['address'])
    refs=[row for instruction in trace['instructions'] for row in actor_accesses(instruction)]
    for row in refs:row['owners']=owners.get(row['site'],[])
    fields=[]
    for offset in sorted({row['offset'] for row in refs}):
        rows=[row for row in refs if row['offset']==offset]
        fields.append(dict(offset=offset,widths=sorted({row['width'] for row in rows if row['width'] is not None}),references=rows))
    byte_uses=[]
    for offset in range(130):
        overlapping=[row for row in refs if row['width'] is not None and row['offset']<=offset<row['offset']+row['width']]
        if overlapping:byte_uses.append(dict(offset=offset,read_sites=sorted({row['site'] for row in overlapping if row['access'] in ('read','read_modify_write')}),write_sites=sorted({row['site'] for row in overlapping if row['access'] in ('write','read_modify_write')}),overlapping_field_offsets=sorted({row['offset'] for row in overlapping})))
    return dict(rom_sha256=inv['rom_sha256'],fields=fields,byte_overlap_candidates=byte_uses,counts=dict(field_start_offsets=len(fields),operand_candidates=len(refs),actor_bytes_with_known_width_references=len(byte_uses)),scope='Every accepted instruction with plain A5-relative operands; A5 may point to other structures. Ownership does not prove execution or actor identity. Indirect aliases, indexing, postincrement spans and helper effects remain pending.',complete_actor_state_schema=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.project)
    (a.project/'docs/stage9/actor-state-accesses.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    template=(Path(__file__).with_name('actor_state_viewer.html')).read_text(encoding='utf-8')
    (a.project/'docs/stage9/actor-state-accesses.html').write_text(template.replace('PAYLOAD',json.dumps(report).replace('<','\\u003c')),encoding='utf-8')
    print(json.dumps(report['counts']))
if __name__=='__main__':main()
