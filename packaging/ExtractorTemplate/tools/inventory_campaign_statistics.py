"""Original campaign percentage table and new-game initialization, static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
    def span(start,end):
        at=start;out=[]
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
            i=Decoder(rom,at).decode();out.append(i);at+=i['size']
        if at!=end:raise ValueError('Instruction extent')
        return out
    at=0x4baaa;tables=[];selectors=[]
    while True:
        pointer=int.from_bytes(rom[at:at+4],'big');at+=4
        if pointer==0:break
        words=int.from_bytes(rom[at:at+2],'big');ignored=rom[at+2:at+4].hex();at+=4
        count=words*4;data=list(rom[pointer:pointer+count]);selectors.extend(v for v in data if v)
        if len(data)!=count or any(v>=80 for v in data):raise ValueError('Statistics selector extent')
        tables.append(dict(pointer=f'{pointer:X}',count=count,size_word=words,ignored_word=ignored,bytes=data))
        if len(tables)>8:raise ValueError('Statistics table terminator')
    if len(selectors)!=70 or len(set(selectors))!=70:raise ValueError('Campaign selector cardinality')
    operations=[dict(entry='6236',name='Original campaign completion percentage',contract='Walk three pointer/size records at4BAAA; countnonzero nodeBYTEs D2, countC558[node]bit1 D3. ZeroBYTEs ignored; indiceszeroextendedD1. Ifdenominatornonzero MULU100 thenDIVU denominator; returnlowWORDD1=floor100*completed/70 forpinnedtable. Zero denominator returnszero. Doesnotuseentrybit2 orjigsawbit0.',pending='Caller progress-bit producers, flag ownership and native statistic presentation/reference remain open.',instruction_evidence=span(0x6236,0x627e)),dict(entry='634E',name='Initialize new-game lives and persistent fields',contract='SetBYTEC51D=3,C523=0,C51F=FF; LONGC532/C536=FFFFFFFF; clearLONGC52E; call99C6 thenRTS. Selective initialization only; do not clear wholecampaign state.',pending='99C6 body/caller lifecycle and retained-field meaning/native reset ordering remain open.',instruction_evidence=span(0x634e,0x6384))]
    for start,end,name,contract,pending in (
        (0x99c6,0x99d6,'Reset score threshold progression','ClearWORDC52C;copyLONGliteral99D6=1000000toC528;retain scoreC52E andlivesC51D. No sound orallocation; finalCCRfromMOVE.Lpositivevalue.', 'Allresetcallers and C528/C52C overlapping/indexed writers remain required.'),
        (0x9916,0x992c,'Score pickup wrapper with allocation followup','SaveD0WORD,sound40via788AE,restoreWORD;call9958 pickup/score response then992C effectallocation. UpperD0WORDmayinherit soundclobber until9958 loadsdefinitionLONG28. Preserve ordered sideeffects and failure path.', 'A5actor/A4definition identities, soundclobbers and scorecallback/allocator failure domains remain required.'),
        (0x992c,0x9958,'Allocate score followup actor','ResolveC4E4 actor, copyLONGposition12/16toD2/D3;definition14928,D4=0,D7=0;call28B0. Store returnedD0inF2D4 evenzero; ifnonnullsetC512BYTEFF, ifzero retainpreviousC512. Do notclearflagonfailure.', 'C4E4 identity/lifetime, allocator failure/return domains, F2D4 consumers and C512 reset/ownership remain required.'),
    ):
        operations.append(dict(entry=f'{start:X}',name=name,contract=contract,pending=pending,instruction_evidence=span(start,end)))
    return dict(rom_sha256=ROM_HASH,scope='Campaign statistics and reset/score-followup contracts; mapping/game completion are separate.',operations=operations,tables=tables,descriptor_end_exclusive=f'{at:X}',nodes=selectors,node_count=70,
        percentage_cases=[dict(completed=i,denominator=70,percent=100*i//70) for i in range(71)],
        callers=[c for c in inv['calls'] if c['target'] in(0x6236,0x634e,0x99c6,0x9916,0x992c)],remaining=['Campaign percentage tests bit1 on70table nodes; do notsubstitute ROMroutine mapping percentage.','Allprogress producer identities and reset/persistence domains remain required.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/campaign-statistics-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Original campaign statistic:70unique nodes,bit1,integerpercentage; selective new-game reset')
