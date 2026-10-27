"""Catalogue manually inspected constant RAM spans with contiguous ROM evidence."""
import argparse
import json
from pathlib import Path
from inventory_rom import inventory, ROM_HASH

# These are local contracts for inspected entry paths, not generic loop inference.
SPECS=[
    (0x1414,0x142a,0x1422,0xff0000,4,16384,'startup RAM clear',
     'Zero long stores after popping the return address into A0. Covers all original RAM; no Windows process-stack clearing.',
     [(0x1416,'LEA','($FFFF0000).L,A1'),(0x141c,'MOVEQ','#0,D0'),(0x141e,'MOVE.W','#$3FFF,D1'),(0x1422,'MOVE.L','D0,(A1)+'),(0x1424,'DBF','D1,$001422')]),
    (0x2158,0x216a,0x2164,0xffc5ee,2,31,'palette word fill',
     'Fill31 words with0EEE. Following ST C48B is outside this span contract.',
     [(0x2158,'LEA','($FFFFC5EE).L,A0'),(0x215e,'MOVE.W','#$0EEE,D0'),(0x2162,'MOVEQ','#30,D1'),(0x2164,'MOVE.W','D0,(A0)+'),(0x2166,'DBF','D1,$002164')]),
    (0x313e,0x3152,0x314a,0xffc3cc,1,102,'immutable startup byte copy',
     'Copy102 bytes from ROM3152, including any reserved or padding bytes; no inferred structure initialization beyond this copy.',
     [(0x313e,'LEA','($003152,PC),A0'),(0x3142,'LEA','($FFFFC3CC).L,A1'),(0x3148,'MOVEQ','#101,D0'),(0x314a,'MOVE.B','(A0)+,(A1)+'),(0x314c,'DBF','D0,$00314A')]),
    (0x3bf6,0x3c08,0x3c00,0xff7410,2,20,'sprite scratch clear',
     'Zero20 words; global ownership and every consumer pending.',
     [(0x3bf6,'LEA','($FFFF7410).L,A0'),(0x3bfc,'MOVEQ','#0,D0'),(0x3bfe,'MOVEQ','#19,D1'),(0x3c00,'MOVE.W','D0,(A0)+'),(0x3c02,'DBF','D1,$003C00')]),
    (0x6384,0x63a6,0x638e,0xffc5a8,1,16,'actor type gate initialization',
     'Clear16 bytes then ST offsets3,4,5,2 relative to saved base A1. End values at offsets2..5 areFF, others0; no global writer closure.',
     [(0x6384,'LEA','($FFFFC5A8).L,A0'),(0x638a,'MOVEA.L','A0,A1'),(0x638c,'MOVEQ','#15,D0'),(0x638e,'CLR.B','(A0)+'),(0x6390,'DBF','D0,$00638E'),(0x6394,'ST','(+3,A1)'),(0x6398,'ST','(+4,A1)'),(0x639c,'ST','(+5,A1)'),(0x63a0,'ST','(+2,A1)')]),
    (0x76a6,0x76b4,0x76ae,0xff6402,4,3,'companion slot clear',
     'Clear exactly three pointer longs6402/6406/640A. Subsequent global C50E clear is a separate instruction.',
     [(0x76a6,'LEA','($FFFF6402).L,A0'),(0x76ac,'MOVEQ','#2,D0'),(0x76ae,'CLR.L','(A0)+'),(0x76b0,'DBF','D0,$0076AE')]),
    (0x9a5e,0x9a88,0x9a74,0xffc558,1,80,'world progress initialization',
     'D1=0; if C5CC nonzero BSET0 D1. Fill80 bytes with0/1, then always BSET0 at C559. Thus selector1 initially available even when C5CCzero; this does not mean completion bit1 is set. Final Z=1 when C5CCzero, otherwise0, reflecting prior bit0 at C559; N/V/C=0 from final MOVE.B fill, X unchanged. C5A8 immediately follows the80-byte span.',
     [(0x9a5e,'LEA','($FFFFC558).L,A0'),(0x9a64,'MOVEQ','#79,D0'),(0x9a66,'MOVEQ','#0,D1'),(0x9a68,'TST.B','($FFFFC5CC).L'),(0x9a6e,'BEQ','$009A74'),(0x9a70,'BSET','#0,D1'),(0x9a74,'MOVE.B','D1,(A0)+'),(0x9a76,'DBF','D0,$009A74'),(0x9a7a,'LEA','($FFFFC558).L,A0'),(0x9a80,'BSET','#0,(+1,A0)')])
]


def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    by_address={i['address']:i for i in trace['instructions']}
    spans=[]
    for start,end,site,address,width,count,name,contract,checks in SPECS:
        for check_site,mnemonic,operands in checks:
            instruction=by_address[check_site]
            if (instruction['mnemonic'],instruction['operands'])!=(mnemonic,operands):
                raise ValueError('Bulk span premise differs from ROM')
        cursor=start; evidence=[]
        while cursor<end:
            instruction=by_address[cursor]
            evidence.append(instruction);cursor+=instruction['size']
        if cursor!=end:raise ValueError('Bulk span end is not instruction boundary')
        spans.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',site=site,
            address=address,width=width,iterations=count,length_bytes=width*count,
            end_address_exclusive=address+width*count,name=name,contract=contract,
            access='write',instruction_evidence=evidence,
            scope='Constant local span on inspected entry path; alternate entry and complete alias audit pending'))
    return dict(rom_sha256=ROM_HASH,spans=spans,complete_bulk_writer_catalogue=False,
        scope='Seven manually inspected DBF spans. Dynamic lengths, index-derived bases, other loops and unresolved code remain pending; these do not close any global field domain.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom',type=Path)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    result=catalogue(args.rom.read_bytes(),args.project)
    (args.project/'docs/stage9/bulk-write-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Inspected constant RAM spans:',len(result['spans']))


if __name__=='__main__':main()
