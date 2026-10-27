"""Bounded static address hints from LEA/MOVEA producers within straight-line blocks."""
import argparse
import json
import re
from pathlib import Path
from inventory_rom import inventory
from inventory_ram_schema import operands,accesses,ABSOLUTE

REGISTER=re.compile(r'^A[0-7]$')
DISPLACEMENT=re.compile(r'^\(([+-]?\d+),([A][0-7])\)$')
INDIRECT=re.compile(r'^\((A[0-7])\)$')
IMMEDIATE=re.compile(r'^#\$([0-9A-F]+)$')

def absolute(arg):
    match=ABSOLUTE.fullmatch(arg)
    if not match:return None
    value=int(match[1],16)
    if match[2]=='W' and value&0x8000:value|=0xff0000
    return value&0xffffff

def resolve(arg,aliases):
    match=DISPLACEMENT.fullmatch(arg) or INDIRECT.fullmatch(arg)
    if not match:return None
    if len(match.groups())==1:offset=0;register=match[1]
    else:offset=int(match[1]);register=match[2]
    if register not in aliases:return None
    base,chain=aliases[register]
    return (base+offset)&0xffffff,chain,register

def hints(instructions,entry_addresses=()):
    """Discard hints at entries, branch destinations, gaps, calls and register mutations."""
    entries=set(entry_addresses)
    entries.update(i['target'] for i in instructions if i.get('target') is not None)
    aliases={};previous_end=None;rows=[]
    for instruction in sorted(instructions,key=lambda i:i['address']):
        site=instruction['address'];args=operands(instruction['operands'])
        if site!=previous_end or site in entries:aliases.clear()
        base=instruction['mnemonic'].split('.')[0]
        for index,arg in enumerate(args):
            resolved=resolve(arg,aliases)
            if resolved is None:continue
            address,chain,register=resolved
            if not 0xff0000<=address<=0xffffff:continue
            replaced=list(args);replaced[index]=f'(${address:08X}).L'
            rewritten=dict(instruction,operands=','.join(replaced))
            classified=next(r for r in accesses(rewritten) if r['operand_index']==index)
            rows.append(dict(classified,producer_chain=chain,base_register=register,
                original_operands=instruction['operands'],scope='Straight-line constant address hint; no indexed/postincrement spans, call preservation or cross-branch propagation'))
        destination=args[-1] if args else ''
        produced=None
        if base=='LEA' and len(args)==2 and REGISTER.fullmatch(destination):
            address=absolute(args[0]);chain=[]
            if address is None:
                resolved=resolve(args[0],aliases)
                if resolved is not None:address,chain,_=resolved
            if address is not None and 0xff0000<=address<=0xffffff:produced=(address,chain+[site])
        elif base=='MOVEA' and len(args)==2 and REGISTER.fullmatch(destination):
            match=IMMEDIATE.fullmatch(args[0])
            if match:
                address=int(match[1],16)
                if instruction['mnemonic'].endswith('.W') and address&0x8000:address|=0xff0000
                address&=0xffffff
                if 0xff0000<=address<=0xffffff:produced=(address,[site])
        # Comparisons observe address registers without changing them.
        if REGISTER.fullmatch(destination) and base not in ('CMPA','CMP','TST','BTST'):
            aliases.pop(destination,None)
        if base in ('MOVEM','EXG','LINK','UNLK'):
            aliases.clear()
        # Auto-modified base registers cannot retain a constant address hint.
        for arg in args:
            for register in re.findall(r'\((A[0-7])\)\+|\-\((A[0-7])\)',arg):
                aliases.pop(next(value for value in register if value),None)
        if produced is not None:aliases[destination]=produced
        if instruction.get('flow','next')!='next':aliases.clear()
        previous_end=site+instruction['size']
    return rows

def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    rows=hints(trace['instructions'],[root['address'] for root in inv['root_candidates']])
    return dict(rom_sha256=inv['rom_sha256'],references=rows,
        counts=dict(operand_hints=len(rows),distinct_addresses=len({r['address'] for r in rows}),
            writes=sum(r['access'] in ('write','read_modify_write') for r in rows)),
        scope='Static producer/use hints only. Reset at every known entry/branch target, control transfer, address-register mutation and listing gap. Indexed operands, postincrement/predecrement spans, dynamic pointers and full alias coverage remain pending.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.project)
    (a.project/'docs/stage9/ram-alias-hints.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
