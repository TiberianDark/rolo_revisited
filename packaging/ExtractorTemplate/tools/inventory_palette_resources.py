"""Original direct palette copy and vector normalization contracts; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x6688,0x66cc,'Copy four selected palette banks','F2F6WORD shiftedleft4 withWORDwrap/signextension into4B08A; fourLONGpointers eachcopy32bytes via66CCtoC5EC,C60C,C62C,C64C. Doesnotinitializefadeeffects orpublishdevicepalette. Selector0..79tableboundsconditional; negatives/outofrange notguarded.'),(0x66cc,0x66de,'Copy one palette bank','Eight orderedLONGmoves(A1)+to(A2)+ copy32bytes. Sourceanddestinationadvance32. Sequentialoverlap followsliteralstores; notmemmove semantics. FinalCCRcomeslastMOVE.L, Xretained.'),(0x63a6,0x63fa,'Normalize signed word displacement','SubtractD0WORDfromD2,D1WORDfromD3 withwrap; recordSMIsignsD7/D6 andNEG.Wnegative values. Signedcompare/exchangeputsmajorinD2,minorD3;D5recordsswap. Zero major returnsD0/D1zero. ElseSWAPminor/clearLOWword formsnumerator;DIVU.Wmajor yieldsratio unlessoverflowthenLONG00010000. SuccessmaskLOW16. D0=00010000,D1ratio,swapifD5,negateLONGcomponentsbysaved signs. Signed8000edge andretainedupperWORD inputs are not ordinary floating normalization.'))

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']};ops=[]
    for start,end,name,contract in SPECS:
        at=start;instructions=[]
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
            i=Decoder(rom,at).decode();instructions.append(i);at+=i['size']
        if at!=end:raise ValueError('Instruction extent')
        ops.append(dict(entry=f'{start:X}',end_exclusive=f'{end:X}',name=name,contract=contract,instruction_evidence=instructions,pending='Allcaller/alias/register input domains, native semantic binding and independent original fidelity remain open.'))
    palettes=[];banks={}
    for selector in range(80):
        pointers=[]
        for bank in range(4):
            at=0x4b08a+selector*16+bank*4;pointer=int.from_bytes(rom[at:at+4],'big')
            if pointer+32>len(rom):raise ValueError('Palette bank extent')
            pointers.append(pointer);banks[f'{pointer:X}']=dict(bytes=rom[pointer:pointer+32].hex(),sha256=hashlib.sha256(rom[pointer:pointer+32]).hexdigest())
        palettes.append(dict(selector=selector,pointers=pointers))
    return dict(rom_sha256=ROM_HASH,scope='Three shared palette/vector contracts; exact80fourbank resource rows, conditional selector domain.',operations=ops,table_start='4B08A',table_bytes=1280,palettes=palettes,banks=banks,unique_bank_count=len(banks),
        callers=[c for c in inv['calls'] if c['target'] in [s[0] for s in SPECS]],remaining=['Directbankcopy differs66DEfadeinitialization and22A8publication.','Allselector andregister aliases remain required; vector signed8000/upperword/overflow domains mustnotbe silently approximated.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/palette-resource-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Three shared contracts;80palette rows/29unique32byte banks')
