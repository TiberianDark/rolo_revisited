"""Catalogue explicit RAM operands; indirect aliases and bulk ranges remain separate."""
import argparse
import json
import re
from pathlib import Path
from collections import defaultdict
from inventory_rom import inventory

ABSOLUTE=re.compile(r'^\(\$([0-9A-F]+)\)\.(L|W)$')
WIDTHS={'B':1,'W':2,'L':4}
SET_CONDITIONS={'ST','SF','SHI','SLS','SCC','SCS','SNE','SEQ','SVC','SVS','SPL','SMI','SGE','SLT','SGT','SLE'}

def operands(text):
    parts=[];start=0;depth=0
    for index,char in enumerate(text):
        if char=='(':depth+=1
        elif char==')':depth-=1
        elif char==',' and depth==0:
            parts.append(text[start:index]);start=index+1
    if text:parts.append(text[start:])
    return parts

def accesses(instruction):
    mnemonic=instruction['mnemonic'];base=mnemonic.split('.')[0]
    suffix=mnemonic.split('.')[-1];size=WIDTHS.get(suffix)
    args=operands(instruction['operands']);rows=[]
    for index,arg in enumerate(args):
        match=ABSOLUTE.fullmatch(arg)
        if not match:continue
        address=int(match[1],16)
        if match[2]=='W' and address&0x8000:address|=0xff0000
        address&=0xffffff
        if not 0xff0000<=address<=0xffffff:continue
        access='unknown';width=size
        if base in ('LEA','PEA'):access='address';width=None
        elif base in ('MOVE','MOVEA'):access='write' if index==len(args)-1 else 'read'
        elif base in ('CMP','CMPA','CMPI','TST','BTST','ADDA','SUBA','MULS','MULU','DIVS','DIVU'):access='read'
        elif base=='CLR' or base in SET_CONDITIONS:access='write'
        elif base in ('ADD','ADDI','ADDQ','SUB','SUBI','SUBQ','AND','ANDI','OR','ORI','EOR','EORI','NEG','NEGX','NOT','LSL','LSR','ASL','ASR','ROL','ROR','ROXL','ROXR','BSET','BCLR','BCHG','TAS'):
            access='read_modify_write' if index==len(args)-1 else 'read'
        if base in ('BTST','BSET','BCLR','BCHG','TAS') or base in SET_CONDITIONS:width=1
        rows.append(dict(address=address,site=instruction['address'],access=access,width=width,
            mnemonic=mnemonic,operand_index=index,operands=instruction['operands']))
    return rows

def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs');groups=defaultdict(list)
    for instruction in trace['instructions']:
        for row in accesses(instruction):groups[row['address']].append(row)
    fields=[]
    for address,refs in sorted(groups.items()):
        widths=sorted({r['width'] for r in refs if r['width'] is not None})
        fields.append(dict(address=address,hex=f'{address:06X}',observed_widths=widths,
            accesses=refs,owners=sorted({owner['address'] for owner in inv['routines'] if any(r['site'] in owner['blocks'] for r in refs)})))
    return dict(rom_sha256=inv['rom_sha256'],fields=fields,
        counts=dict(explicit_ram_addresses=len(fields),operand_references=sum(len(f['accesses']) for f in fields),
            read=sum(r['access']=='read' for f in fields for r in f['accesses']),
            write=sum(r['access']=='write' for f in fields for r in f['accesses']),
            read_modify_write=sum(r['access']=='read_modify_write' for f in fields for r in f['accesses']),
            address_only=sum(r['access']=='address' for f in fields for r in f['accesses']),
            unknown=sum(r['access']=='unknown' for f in fields for r in f['accesses'])),
        scope='Explicit absolute RAM operands only. Widths can overlap. Pointer-produced indirect accesses, alias propagation, hardware RAM mirrors, bulk clears and complete lifetimes are not inferred. Ownership is static and may be shared. No complete state schema or native implementation claim.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.project)
    (a.project/'docs/stage9/ram-schema.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
