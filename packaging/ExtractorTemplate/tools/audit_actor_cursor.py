"""Static A6-use dependency audit; never executes ROM code or proves preservation."""
import hashlib
import json
import re
from pathlib import Path
from m68k_static import Decoder

def audit(project):
    rom=(project/'local/rolo.md').read_bytes()
    inv=json.loads((project/'docs/stage9/inventory.json').read_text(encoding='utf-8'))
    if hashlib.sha256(rom).hexdigest()!=inv['rom_sha256']:
        raise ValueError('Pinned ROM mismatch')
    routines={r['address']:r for r in inv['routines']}
    reports=[]
    for root in (0xb566,0xa84c,0xef68):
        pending=[root];seen=set();missing=[];uses=[];edges=[];blocks=set();stack=[]
        while pending:
            entry=pending.pop()
            if entry in seen:continue
            seen.add(entry)
            routine=routines.get(entry)
            if routine is None:missing.append(entry);continue
            for address in routine['blocks']:
                blocks.add(address)
                instruction=Decoder(rom,address).decode()
                if re.search(r'\bA6\b',instruction['operands']):
                    uses.append(dict(owner=f'{entry:06X}',**instruction))
                if re.search(r'\bA7\b',instruction['operands']) or instruction['mnemonic'] in ('LINK','UNLK','RTE','RTR'):
                    stack.append(dict(owner=f'{entry:06X}',**instruction))
            for edge in routine.get('dependency_edges',[]):
                edges.append(dict(owner=entry,**edge));pending.append(edge['target'])
        uncertain=[u for u in inv['unresolved'] if u['address'] in blocks]
        indirect=[c for c in inv['calls'] if c['address'] in blocks and c['target'] is None]
        reports.append(dict(root=f'{root:06X}',candidate_dependency_entries=sorted(seen),
            missing_entries=missing,a6_mentions=uses,dependency_edges=edges,
            uncertain_control_flow=uncertain,indirect_calls=indirect,
            explicit_stack_mentions=stack,
            preservation_proved=False))
    diagnostic=[];cursor=0x5998
    while cursor<0x59e0:
        instruction=Decoder(rom,cursor).decode();diagnostic.append(instruction);cursor+=instruction['size']
    expected={0x5998:('MOVE.W','SR,-(A7)'),0x599e:('MOVEM.L','A6/D1/D0,-(A7)'),
        0x59bc:('MOVE.W','#$4FFF,D0'),0x59ca:('DBF','D0,$0059C0'),
        0x59d8:('MOVEM.L','(A7)+,D0/D1/A6'),0x59dc:('MOVE.W','(A7)+,SR'),0x59de:('RTS','')}
    for address,(mnemonic,operands) in expected.items():
        actual=next(i for i in diagnostic if i['address']==address)
        if (actual['mnemonic'],actual['operands'].strip())!=(mnemonic,operands):raise ValueError('Diagnostic proof anchor changed')
    if cursor!=0x59e0 or any(i['flow'] not in ('next','return','branch') for i in diagnostic):
        raise ValueError('Diagnostic instruction/control-flow shape changed')
    if [i['address'] for i in diagnostic if i['flow']!='next']!=[0x59ca,0x59de]:
        raise ValueError('Diagnostic exits changed')
    return dict(rom_sha256=inv['rom_sha256'],roots=reports,
        diagnostic_local_proof=dict(entry='005998',end_exclusive='0059E0',instructions=diagnostic,
            argument='SR word and three long registers pushed before A6 overwrite. The only branch is DBF at59CA to59C0; D0 starts4FFF and is not written in the loop body, giving20480 finite iterations. Every normal return passes the inverse MOVEM at59D8 and SR pop at59DC. No calls or alternate returns occur. A6 is preserved on normal completion; hardware exceptions are outside this local proof.',
            normal_return_a6_preserved=True),
        scope='Accepted instruction blocks and candidate dependency closure. A6 mentions include reads, writes and saved/restored registers. Absence of a mention does not prove preservation through indirect calls. Candidate edges are not proven execution paths; stack balance, restore dominance, unresolved transfers and all callback domains require separate proof.')

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1]
    result=audit(project)
    (project/'docs/stage9/actor-cursor-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print([{ 'root':r['root'],'entries':len(r['candidate_dependency_entries']),
        'a6_mentions':len(r['a6_mentions']),'missing':len(r['missing_entries'])} for r in result['roots']])
