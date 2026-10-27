"""Catalogue syntactic actor selector byte/word aliases without assuming register identity."""
import argparse,json,re
from pathlib import Path
from inventory_rom import inventory
from inventory_ram_schema import operands,accesses
RELATIVE=re.compile(r"^\(([+-]?\d+),(A[0-6])\)$")
def selector_accesses(instruction):
    args=operands(instruction['operands']);rows=[]
    for index,arg in enumerate(args):
        match=RELATIVE.fullmatch(arg)
        if not match:continue
        offset=int(match[1]);register=match[2];rewritten=list(args)
        rewritten[index]=f'(${0xff998c+offset:08X}).L'
        row=next(r for r in accesses(dict(instruction,operands=','.join(rewritten))) if r['operand_index']==index)
        width=row['width']
        if width is None or not offset<56 or offset+width<=54:continue
        rows.append(dict(site=instruction['address'],register=register,offset=offset,width=width,access=row['access'],operand_index=index,mnemonic=instruction['mnemonic'],operands=instruction['operands']))
    return rows

def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    rows=[row for instruction in trace['instructions'] for row in selector_accesses(instruction)]
    contexts=json.loads((project/'docs/stage9/selector-contexts.json').read_text(encoding='utf-8'))['contexts']
    by_site={int(site,16):context for context in contexts for site in context['sites']}
    for row in rows:
        row['owners']=[r['address'] for r in inv['routines'] if row['site'] in r['blocks']]
        row['writer_context']=by_site.get(row['site'])

    return dict(rom_sha256=inv['rom_sha256'],references=rows,counts=dict(operand_candidates=len(rows),write_candidates=sum(r['access'] in ('write','read_modify_write') for r in rows)),scope='Plain relative operands overlapping bytes54/55 in any A0..A6 context. Registers may address unrelated structures; this is not proof of actor identity or macro mode mutation. Indexed accesses, bulk copies and generic animation writes remain separate.',complete_macro_selector_domain_proven=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.project)
    (a.project/'docs/stage9/selector-accesses.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))
if __name__=='__main__':main()
