"""Parallax callback and horizontal-scroll mode producers, static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x4f1c,0x4f26,'Half X and Y',0),(0x4f26,0x4f30,'Half X and Y with fixed-plane flag',0),(0x4f30,0x4f36,'Identity camera',0),(0x4f36,0x4f40,'Half X and zero Y',0),(0x4f40,0x4f46,'Identity camera with fixed-plane flag',0),(0x4f46,0x4f70,'Counter-driven trigonometric background',0),(0x4f70,0x4f82,'Scroll-offset camera accumulation',0),(0x4f82,0x4fc8,'Stepped horizontal band producer',2),(0x4fc8,0x5028,'Camera and interrupt-counter band producer',2),(0x5028,0x5060,'Two-band horizontal producer',2))

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH: raise ValueError('ROM revision')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted={a for r in inv['routines'] for a in r['blocks']}
    def span(start,end):
        result=[];at=start
        while at<end:
            if at not in accepted: raise ValueError(f'Unaccepted boundary {at:X}')
            i=Decoder(rom,at).decode();result.append(i);at+=i['size']
        if at!=end: raise ValueError('Instruction extent')
        return result
    operations=[]
    for start,end,name,mode in SPECS:
        instructions=span(start,end)
        if not any(i['mnemonic']=='MOVEQ' and i['operands']==f'#{mode},D3' for i in instructions): raise ValueError('Mode producer changed')
        operations.append(dict(entry=f'{start:X}',name=name,end_exclusive=f'{end:X}',instruction_evidence=instructions,
            contract=f'Original callback returns horizontal-scroll mode D3={mode}; D0/D1 supply background camera and D2 supplies fixed-plane flag. Exact signed shifts, word overflow, scratch writes and counter side effects are retained in instruction evidence.',
            pending='Incoming register/selector domains, signed arithmetic and shared scratch/counter aliases require native translation and original-reference verification.'))
    references=[Decoder(rom,a).decode() for a in sorted(accepted) if 0xfff286 in [v&0xffffff for v in Decoder(rom,a).decode().get('references',[])]]
    if [i['address'] for i in references]!=[0x4eec,0x6962,0x6ac6]: raise ValueError('Explicit mode references changed')
    slots=span(0x4ef4,0x4f1c)
    return dict(rom_sha256=ROM_HASH,scope='Ten original parallax callbacks and explicit scroll-mode producer census; complete caller and alias closure not claimed.',operations=operations,
        dispatch_evidence=span(0x4eaa,0x4ef4),branch_slots=slots,mode_references=references,
        selector_table=dict(start='4AEDA',bytes=list(rom[0x4aeda:0x4aeda+80]),domain='Conditional F2F6 WORD0..79. MOVE.B replaces only lowD2 byte; negative/high-byte selectors are not covered.'),
        bands=[dict(entry='4F82',words=32,end_exclusive='7480',start='7440',reverse_runs='14 halfX,3 quarterX,2 eighthX,1 sixteenthX,12 zero'),dict(entry='4FC8',words=32,end_exclusive='7480',start='7440',reverse_runs='16 halfX,12 eighthX,2 halfC490,2 C490'),dict(entry='5028',words=32,end_exclusive='7480',start='7440',reverse_runs='24 halfX,8 quarterX')],
        remaining=['Known callbacks publish modes0 or2; clear6AC6 publishes0. Consumer mode1/3 support is not evidence of a current producer.',
            'Do not globally resolve4ED6 or697C from this conditional domain; F2F6 caller bounds and pointer/bulk aliases remain open.',
            '4F46 callsCCF8: trigonometric helper return/clobber domains and timing remain separate.',
            '7440 scratch consists32 words here; other writers and consumer mode3 length512words require independent ownership evidence.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/scroll-mode-producer-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Ten parallax callbacks; known mode producers0/2; three32word band writers')
