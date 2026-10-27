"""Connect all macro dispatch slots to marker/matrix evidence and local field accesses."""
import argparse
import json
import re
from pathlib import Path
from inventory_rom import inventory
from inventory_ram_schema import operands,accesses

ACTOR_FIELD=re.compile(r'^\((?:([+-]?\d+),)?A5\)$')

def actor_accesses(instruction):
    args=operands(instruction['operands']);rows=[]
    for index,arg in enumerate(args):
        match=ACTOR_FIELD.fullmatch(arg)
        if not match:continue
        offset=int(match[1] or 0);rewritten=list(args)
        rewritten[index]=f'(${0xff998c+offset:08X}).L'
        classified=next(row for row in accesses(dict(instruction,operands=','.join(rewritten))) if row['operand_index']==index)
        rows.append(dict(site=instruction['address'],offset=offset,width=classified['width'],access=classified['access'],
            mnemonic=instruction['mnemonic'],operands=instruction['operands'],operand_index=index,
            scope='Syntactic A5-relative field reference only; caller identity and intervening helper clobbers remain pending'))
    return rows

def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    dynamic=json.loads((project/'docs/stage9/dynamic-macro-inventory.json').read_text(encoding='utf-8'))
    if dynamic['rom_sha256']!=inv['rom_sha256']:raise ValueError('Macro evidence revision mismatch')
    table=next(table for table in inv['dispatch_tables'] if table['dispatch']==0xbe56)
    routines={r['address']:r for r in inv['routines']};instructions={i['address']:i for i in trace['instructions']}
    rows=[]
    for mode,slot in enumerate(table['slots']):
        routine=routines[slot['address']];markers=[m for m in dynamic['markers'] if m['dispatch_offset']==slot['address']-table['base']]
        fields=[reference for site in sorted(routine['blocks']) for reference in actor_accesses(instructions[site])]
        rows.append(dict(mode=mode,dispatch_offset=slot['address']-table['base'],slot=slot['address'],target=slot['target'],
            observed_marker_records=len(markers),observed_layout_sources=sorted({m['layout_source'] for m in markers}),
            matrix_cases=[dict(bank=bank,macro=macro) for bank,macro in sorted({(m['bank'],m['macro']) for m in markers})],
            instruction_count=routine['instruction_count'],status=routine['status'],
            local_calls=[call for call in inv['calls'] if slot['address'] in call['source_owners']],
            field_access_candidates=fields,possible_dependencies=routine['possible_dependencies'],
            common_pre_dispatch='BE4E calls90A0 before loading word54',
            common_post_dispatch='BE5A calls8A0C after indexed mode call returns',
            scope='Owned branch candidate region; called helpers and inter-entry transfers remain separate. No semantic platform/hazard type inferred from mode number.'))
    return dict(rom_sha256=inv['rom_sha256'],modes=rows,
        counts=dict(branch_modes=len(rows),modes_with_observed_markers=sum(r['observed_marker_records']>0 for r in rows),
            observed_macro_markers=sum(r['observed_marker_records'] for r in rows),
            field_access_candidates=sum(len(r['field_access_candidates']) for r in rows)),
        scope='RAM macro dispatcher cross-reference only. Original word54 can mutate; initial marker modes do not prove every future target or complete dynamic behavior.',full_macro_behaviors_ported=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.project)
    (a.project/'docs/stage9/macro-handler-inventory.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
