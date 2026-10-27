"""Inventory main-state pointer writes and local call sites; no CPU execution."""
import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from inventory_rom import inventory

POINTERS={0xffffc444:'main_dispatch',0xffffc466:'initialization_marker'}
IMMEDIATE=re.compile(r'^#\$([0-9A-F]{8}),\(\$([0-9A-F]{8})\)\.L$')

def immediate_state_write(instruction):
    if instruction['mnemonic']!='MOVE.L':return None
    match=IMMEDIATE.fullmatch(instruction['operands'])
    if not match:return None
    target,pointer=(int(value,16) for value in match.groups())
    if pointer not in POINTERS:return None
    return dict(address=instruction['address'],pointer=pointer,role=POINTERS[pointer],target=target)

def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    owners=defaultdict(list)
    for routine in inv['routines']:
        for address in routine['blocks']:owners[address].append(routine['address'])
    writes=[];candidates=[]
    for instruction in trace['instructions']:
        write=immediate_state_write(instruction)
        if write:
            write['source_owners']=owners[instruction['address']];writes.append(write)
        elif instruction['mnemonic'].startswith(('MOVE.','MOVEA.')) and any(
                '($%08X).L'%pointer in instruction['operands'].split(',')[-1] for pointer in POINTERS):
            candidates.append(dict(address=instruction['address'],operands=instruction['operands'],
                scope='Other syntactic pointer write; source/alias context pending'))
    by_address={routine['address']:routine for routine in inv['routines']}
    states=[]
    for address in sorted({write['target'] for write in writes}):
        routine=by_address.get(address);state=dict(address=address,
            incoming_writes=[write for write in writes if write['target']==address],
            roles=sorted({write['role'] for write in writes if write['target']==address}),
            status=routine['status'] if routine else 'entry not accepted by reachable inventory',
            local_call_sites=[call for call in inv['calls'] if address in call['source_owners']],
            local_pointer_writes=[write for write in writes if address in write['source_owners']],
            scope='Calls sorted by address, not an execution sequence. Shared ownership and conditional paths preserved.')
        states.append(state)
    level=[]
    # This specific state is straight-line: reject silent control-flow changes.
    instructions={instruction['address']:instruction for instruction in trace['instructions']}
    address=0x1c6c
    while True:
        instruction=instructions[address]
        if instruction['mnemonic']=='RTS':break
        if instruction['flow']=='call':level.append(dict(site=address,target=instruction['target']))
        elif instruction['flow']!='next':raise ValueError('Normal frame is no longer straight-line')
        address+=instruction['size']
        if address>0x1cec:raise ValueError('Normal frame did not terminate at expected return')
    if address!=0x1cec or len(level)!=28:raise ValueError('Normal frame call contract differs')
    report=dict(rom_sha256=inv['rom_sha256'],pointer_writes=writes,other_syntactic_writes=candidates,
        states=states,normal_frame=dict(entry=0x1c6c,return_site=address,calls_in_order=level,
            scope='One entry call order only; called routines, interrupts and state changes still need integrated native conversion'),
        counts=dict(state_entry_candidates=len(states),main_dispatch_writes=sum(w['role']=='main_dispatch' for w in writes),
            initialization_marker_writes=sum(w['role']=='initialization_marker' for w in writes),
            other_syntactic_writes=len(candidates),normal_frame_calls=len(level)),
        scope='Immediate absolute main-state writes only; computed/aliased writes and semantic state names remain pending')
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom')
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    report=catalogue(Path(args.rom).read_bytes(),args.project);out=args.project/'docs/stage9'
    (out/'state-inventory.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with (out/'state-transitions.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=['address','pointer','role','target','source_owners'])
        writer.writeheader();writer.writerows(report['pointer_writes'])
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
