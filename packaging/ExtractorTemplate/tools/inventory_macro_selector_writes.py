"""Accepted displacement writes overlapping macro selector bytes54/55; no alias closure."""
import csv
import hashlib
import json
import re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom = (project / 'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest() != ROM_HASH:
        raise ValueError('ROM mismatch')
    inv = json.loads((project / 'docs/stage9/inventory.json').read_text())
    owners = {}
    for routine in inv['routines']:
        for address in routine['blocks']:
            owners.setdefault(address, set()).add(routine['address'])
    table = next(t for t in inv['dispatch_tables'] if t['dispatch'] == 0xBE56)
    handlers = {slot['target'] for slot in table['slots']}
    by_entry = {r['address']: r for r in inv['routines']}
    reachable = set()
    pending = list(handlers | {0xBE4E})
    while pending:
        entry = pending.pop()
        if entry in reachable:
            continue
        reachable.add(entry)
        routine = by_entry.get(entry)
        if routine:
            pending.extend(edge['target'] for edge in routine['dependency_edges']
                           if edge['evidence'] in ('direct encoded target', 'accepted non-call control-flow transfer between entry candidates'))
    writers = {'MOVE','CLR','ADD','ADDI','ADDQ','SUB','SUBI','SUBQ','AND','ANDI','OR','ORI','EOR','EORI','NEG','NOT','BSET','BCLR','BCHG','ST','SF'}
    rows = []
    for address in sorted(owners):
        instruction = Decoder(rom, address).decode()
        base = instruction['mnemonic'].split('.')[0]
        if base not in writers:
            continue
        match = re.search(r'\(\+([0-9]+),(A[0-7])\)$', instruction['operands'])
        if not match:
            continue
        width = {'B':1,'W':2,'L':4}.get(instruction['mnemonic'].split('.')[-1],1)
        offset = int(match[1])
        if offset > 55 or offset + width <= 54:
            continue
        context = 'macro handler owner' if owners[address] & handlers else 'other owner/alias context pending'
        if address == 0x4A26:
            context = 'canonical initial WORD selector'
        elif address in (0x48AE,0x48B2):
            context = 'B80A callback override path; separate byte meanings'
        rows.append(dict(address=address, hex=f'{address:04X}', mnemonic=instruction['mnemonic'],
                         operands=instruction['operands'], start_offset=offset, width=width,
                         overlapping_bytes=list(range(max(offset,54),min(offset+width,56))),
                         owners=[f'{owner:04X}' for owner in sorted(owners[address])], context=context,
                         direct_dependency_reachable=bool(owners[address] & reachable),
                         instruction_evidence=instruction))
    return dict(rom_sha256=ROM_HASH, writes=rows,
                direct_dependency_entries=[f'{entry:04X}' for entry in sorted(reachable)],
                counts=dict(overlapping_writes=len(rows), macro_handler_owner_writes=sum(r['context']=='macro handler owner' for r in rows),
                            direct_dependency_reachable_writes=sum(r['direct_dependency_reachable'] for r in rows)),
                scope='Accepted explicit displacement destinations only. Macro ownership is a graph-owner indication, not live A5 identity proof. Indexed, absolute, bulk, postincrement and differently based aliases remain open; shared helpers can act on macro actors.',
                next='Review each overlapping write with callback/actor identity. Preserve long writes starting52/53 as selector-overlap candidates; byte52/53 alone cannot change WORD54.')

if __name__ == '__main__':
    project = Path(__file__).resolve().parents[1]
    report = catalogue(project)
    docs = project / 'docs/stage9'
    (docs / 'macro-selector-write-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    fields = ['hex','mnemonic','operands','overlapping_bytes','owners','context']
    with (docs / 'macro-selector-write-audit.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in report['writes']:
            writer.writerow({key: '; '.join(map(str,row[key])) if isinstance(row[key],list) else row[key] for key in fields})
    print(json.dumps(report['counts']))
