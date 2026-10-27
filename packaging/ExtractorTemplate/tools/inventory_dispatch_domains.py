"""Track slot offsets and narrowly proved canonical selector producers."""
import argparse
import json
from pathlib import Path
from inventory_rom import inventory
from m68k_static import Decoder

def local_domain(kind):
    if kind=='terrain_mask':
        return sorted({((word&0x2e00)-0x2000)>>7 for word in range(65536) if word&0x2e00>=0x2000})
    if kind=='actor_flag_mask':return sorted({(byte&0x18)>>1 for byte in range(256)})
    raise ValueError('Unsupported mathematical selector proof')

def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    contracts=json.loads((project/'docs/stage9/dispatch-domain-contracts.json').read_text(encoding='utf-8'))
    inline_contexts={int(c['dispatch'],16):c for c in inv.get('indexed_inline_contexts',[])}
    by_address={int(row['dispatch'],16):row for row in contracts}
    if len(by_address)!=len(contracts) or set(by_address)!={table['dispatch'] for table in inv['dispatch_tables']}:
        raise ValueError('Dispatch domain contracts do not cover current tables')
    accepted={i['address'] for i in trace['instructions']};rows=[]
    for table in sorted(inv['dispatch_tables'],key=lambda t:t['dispatch']):
        contract=by_address[table['dispatch']];offsets=[slot['address']-table['base'] for slot in table['slots']]
        row=dict(contract,slot_offsets=offsets,slot_sizes=[slot['size'] for slot in table['slots']],
            slot_targets=[slot['target'] for slot in table['slots']],status='Complete selector/caller domain pending')
        if table.get('inline_targets'):
            row['inline_targets']=table['inline_targets']
            row['catalogued_entry_offsets']=sorted(set(offsets)|{item['offset'] for item in table['inline_targets']})
            context=inline_contexts[table['dispatch']]
            row['checked_immediate_offset_domain']=sorted({p['value'] for p in context['producer_contexts']})
            row['immediate_domain_scope']=context['scope']
            if not set(row['checked_immediate_offset_domain'])<=set(row['catalogued_entry_offsets']):
                raise ValueError('Checked immediate domain escapes catalogued entries')
        proof=contract.get('local_domain_proof')
        if proof:
            for site,expected in proof['evidence'].items():
                address=int(site,16);decoded=Decoder(rom,address).decode()
                if address not in accepted or [decoded['mnemonic'],decoded['operands']]!=expected:
                    raise ValueError('Canonical selector producer evidence differs')
            domain=local_domain(proof['kind'])
            if not set(domain)<=set(offsets):raise ValueError('Local selector proof escapes branch slots')
            row.update(canonical_offset_domain=domain,status='Canonical producer path bounded; external/computed entry contexts still pending')
        if table['dispatch']==0xe836:
            from inventory_world_bunny_domain import catalogue as bunny_domain
            from inventory_world_bunny_callers import catalogue as bunny_callers
            bounded=bunny_domain(project);callers=bunny_callers(project)
            domain=[selector*2 for selector in bounded['canonical_domain']]
            if not set(domain)<=set(offsets):raise ValueError('World bunny selector escapes recorded slots')
            row.update(canonical_offset_domain=domain,
                canonical_domain_sources=['world-bunny-domain-contract.json','world-bunny-caller-contract.json'],
                canonical_caller_scope=callers['canonical_dependency_status'],
                status='Successful original initialized world-bunny path bounded; exceptional allocation and external entries pending')
        if table['dispatch'] in (0x4ed6,0x697c):
            from inventory_scroll_mode_producers import catalogue as scroll_producers
            scroll=scroll_producers(project)
            if table['dispatch']==0x4ed6:
                domain=sorted({mode*4 for mode in scroll['selector_table']['bytes']})
                scope='F2F6 WORD0..79 only; retained high-byte selectors, trigger mutations and caller bounds remain open.'
            else:
                domain=[0,8]
                scope='Explicit mapped parallax callback D3 outputs0/2 and6AC6clear only; pointer/bulk aliases and complete caller closure remain open.'
            if not set(domain)<=set(offsets):raise ValueError('Mapped scroll producer escapes branch slots')
            row.update(canonical_offset_domain=domain,canonical_domain_sources=['scroll-mode-producer-contract.json'],canonical_caller_scope=scope,
                status='Mapped scroll producer domain bounded; complete writer/caller closure pending')
        if table['dispatch']==0x9d18:
            from inventory_ending_sequence import catalogue as ending_sequence
            ending=ending_sequence(project)['canonical_dispatch']
            if not set(ending['offsets'])<=set(offsets):raise ValueError('Ending countdown domain escapes slots')
            row.update(canonical_offset_domain=ending['offsets'],canonical_domain_sources=['ending-sequence-contract.json'],canonical_caller_scope=ending['condition'],status='Initialized ending countdown bounded; shared state aliases and complete callers pending')
        rows.append(row)
    return dict(rom_sha256=inv['rom_sha256'],tables=rows,
        counts=dict(tables=len(rows),canonical_local_bounds=sum('canonical_offset_domain' in row for row in rows),
            checked_immediate_caller_domains=sum('checked_immediate_offset_domain' in row for row in rows),
            remaining_full_domain_audits=len(rows)),
        scope='Slot offsets are byte offsets, not assumed four-byte indices. Explicit inline targets have recorded immediate contexts. Mask proofs and the initialized world-bunny lifecycle cover their recorded paths only; all-caller closure remains pending.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.project)
    (a.project/'docs/stage9/dispatch-domains.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
