"""Decode initial definition rendering operation words without executing them."""
import argparse,json
from pathlib import Path
from inventory_rom import inventory
from m68k_static import Decoder

def catalogue(rom,project):
    inv,_=inventory(rom,project/'docs');groups={}
    for definition in inv['object_definitions']:
        address=definition['address'];word=int.from_bytes(rom[address+8:address+10],'big')
        groups.setdefault(word,[]).append(address)
    rows=[]
    for word,definitions in sorted(groups.items()):
        instruction=Decoder(word.to_bytes(2,'big')+bytes(16),0).decode()
        rows.append(dict(word=f'{word:04X}',definitions=definitions,decoded_mnemonic=instruction['mnemonic'],decoded_operands=instruction['operands'],decoded_size=instruction['size'],scope='Constant first word decoded as an instruction only; never executed. Zero padding is not proof of extension operands for multiword forms.'))
    payload=rom[0x5216:0x523e]
    templates=[dict(index=n//8,source=0x5216+n,bytes=payload[n:n+8].hex(),y=int.from_bytes(payload[n:n+2],'big'),size=payload[n+2],original_link=payload[n+3],tile_attributes=int.from_bytes(payload[n+4:n+6],'big'),x=int.from_bytes(payload[n+6:n+8],'big')) for n in range(0,40,8)]
    return dict(fixed_sprite_templates=templates,rom_sha256=inv['rom_sha256'],scope='Definition+8 constants copied by28EA to actor+0. Static initial sources only; later writes, RAM definitions and aliases remain pending.',rows=rows,counts=dict(definitions=sum(len(r['definitions']) for r in rows),unique_initial_words=len(rows),single_word_instructions=sum(r['decoded_size']==2 for r in rows)),complete_runtime_opcode_domain_proven=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.project)
    (a.project/'docs/stage9/initial-render-operations.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))
if __name__=='__main__':main()
