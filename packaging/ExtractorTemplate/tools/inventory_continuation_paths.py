"""Conservative CFG code-pointer provenance; no ROM instruction execution."""
import argparse
import json
import re
from pathlib import Path
from inventory_rom import inventory, ROM_HASH


def split_operands(text):
    depth = 0; start = 0; result = []
    for index, char in enumerate(text):
        depth += (char == '(') - (char == ')')
        if char == ',' and depth == 0:
            result.append(text[start:index]); start = index + 1
    result.append(text[start:])
    return result


def provenance(instruction, register, current):
    mnemonic = instruction['mnemonic']; text = instruction['operands']
    operands = split_operands(text)
    if instruction['flow'] == 'call':
        return None, 'call clobber contract unproved'
    if f'({register})+' in text or f'-({register})' in text:
        return None, 'address register auto-update'
    if mnemonic.startswith('MOVEM'):
        if register in operands[-1].split('/'):
            return None, 'register restored from memory'
        return current, None
    if mnemonic == 'EXG' and register in operands:
        return None, 'register exchange'
    if mnemonic in ('LINK', 'UNLK') and operands[0] == register:
        return None, 'frame register mutation'
    if operands[-1] != register:
        return current, None
    if mnemonic.startswith(('CMP', 'TST')):
        return current, None
    if mnemonic == 'LEA' and len(instruction['references']) == 1:
        target = instruction['references'][0]
        return target, f'LEA code-pointer candidate ${target:06X}'
    # All other explicit writes discard provenance rather than guessing.
    return None, 'explicit register write without checked pointer producer'


def prove(instructions, entries, stop, register, excluded_paths=()):
    by_address = {i['address']: i for i in instructions}
    pending = [(entry, None) for entry in entries]; seen = set(); hits = set(); losses = set(); exits = set()
    while pending:
        address, value = pending.pop()
        if (address, value) in seen: continue
        seen.add((address, value))
        if len(seen) > 100000: raise ValueError('Provenance state budget exceeded')
        if address in excluded_paths:
            exits.add((address, 'explicitly excluded alternate path')); continue
        if address == stop:
            hits.add(value); continue
        instruction = by_address.get(address)
        if instruction is None:
            exits.add((address, 'missing accepted instruction')); continue
        next_value, reason = provenance(instruction, register, value)
        if reason and next_value is None:
            losses.add((address, reason))
        flow = instruction['flow']
        if flow == 'return':
            exits.add((address, 'return before site')); continue
        if flow in ('jump', 'branch'):
            if instruction['target'] is None:
                exits.add((address, 'other unresolved jump')); continue
            pending.append((instruction['target'], next_value))
            if flow == 'jump': continue
        pending.append((address + instruction['size'], next_value))
    return dict(entries=entries, site=stop, register=register,
        excluded_paths=list(excluded_paths),
        targets=sorted(value for value in hits if value is not None), unknown_reaches_site=None in hits,
        visited_state_count=len(seen),
        provenance_losses=[dict(site=site,reason=reason) for site,reason in sorted(losses)],
        other_exits=[dict(site=site,reason=reason) for site,reason in sorted(exits)],
        instruction_sites=sorted({site for site,_ in seen if site in by_address}))


def catalogue(rom, project):
    inv, trace = inventory(rom, project / 'docs')
    cases = [prove(trace['instructions'], [0x4158, 0x417a], 0x4228, 'A4'),
             prove(trace['instructions'], [0x442a], 0x44c2, 'A4', excluded_paths=(0x463c,))]
    cases[1]['precondition']='Normal visual descriptor D0lowword<0400; branch4436 to463C spawn path is explicitly outside this proof.'
    for row, expected in zip(cases, ([0x422c, 0x4270], [0x44c4])):
        if row['unknown_reaches_site'] or row['targets'] != expected or row['provenance_losses']:
            raise ValueError('Canonical continuation prefix no longer proved')
    by_address = {i['address']:i for i in trace['instructions']}
    for row in cases:
        row['instruction_evidence'] = [{key:by_address[site][key] for key in ('address','bytes','mnemonic','operands')}
                                      for site in row['instruction_sites']]
    return dict(rom_sha256=ROM_HASH, cases=cases,
        scope='Intraprocedural CFG provenance from only the listed producer entries to the named jump, subject to explicit excluded alternate paths/preconditions. Calls are opaque returning clobbers; neither callees nor branch conditions execute. No external/computed/mid-entry caller or excluded-path proof.',
        counts=dict(checked_producer_prefixes=len(cases), unknown_targets_in_checked_prefixes=sum(r['unknown_reaches_site'] for r in cases)))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom')
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    result=catalogue(Path(args.rom).read_bytes(),args.project)
    (args.project/'docs/stage9/continuation-path-proofs.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
