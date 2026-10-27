"""Second text renderer byte control domain and command bodies; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x6da8,0x6df4,'Text byte parser and indexed control','ZeroextendBYTE;subtract32andtestsignedBYTE. Glyphs33..159source27040+(byte-32)*32, publishC4AE,call6C56/6BFC,set743ALONG00080000/743EWORD A000. Space32 advancescolumn andcontinues. Controls0..31and160..255restorebyte,multiply4,jump6DF4+offset; no nine-command bound.'),(0x6e18,0x6e26,'Terminate text pointer','ClearC4AE LONG and7438BYTE;return. Doesnotclearothertextfields.'),(0x6e26,0x6e30,'Advance space column','ADDQ.W1C4A8 thenreturnparser6DA8;wordwrapliteral.'),(0x6e30,0x6e40,'Set text byte position','Consume2bytes intoLOWbytesC4A9/C4AB;retainhighbytesC4A8/C4AA. Continueparser, notreturn.'),(0x6eec,0x6efa,'Suspend text by countdown','ConsumeBYTEto7439;publishadvancedA0C4AE;return. Countdowncaller/zero behavior separate.'),(0x6efa,0x6f02,'Decrement text countdown','SUBQ.B1 at7439,wrapwithoutguard;return.'),(0x6f02,0x6f16,'Redirect text stream','Consume4bytes toconstructbigendianLONG inD0;A0=D0,continueparser. Notfallthroughcontrolargumentinterpretedasglyph.'),(0x6f16,0x6f3c,'Load aligned text effect value','RoundA0up toeven byadd1/clearbit0;consumeLONGto743A,publishremainingpointerC4AE;7438=1,743EWORDzero;return.'),(0x6f3c,0x6fb6,'Configure text strip effect','Consume3bytes to743A/B/C;derive743DBYTE=(third<<3)-1wrapped. PublishC4AE,7438=2;26C8fillrequestD2=04FF at0840,devicebyteextentpending;664Cdrawrowfrom4A6CA toC000+Y*128+X*2 withbase6042 andD1lowBYTEthird-1. Ifthirdzero,D1WORD00FF =>256tiles, notzero.'),(0x6fb6,0x7000,'Transfer text to rotating menu state','SaveA0C4B2;readC460BYTEindexD0zeroextended, incrementBYTED1/signedcompare4; valuesabove4resetzero. PublishnewC460. Oldindex*4 loadsPCpointer7000+offset;copyfirstWORDtoF2F0,skip1byte,publishA1toC45CLONG. ClearC458/C459/C45A;BRA1BD8. Oldindex/domain andpointertableextent remaincallerproof.'))

SPECS+=((0x6e40,0x6e52,'Select full text-region clear','SetC494WORD0/C498WORD0FFF thenjoin6E62. FillregisterlengthD2=0FFF;devicebyteextentpending26C8semantics; command8slot6E14.'),(0x6e52,0x6e62,'Select partial text-region clear','SetC494WORD0A00/C498WORD03FF thenjoin6E62;fillregisterlengthD2=03FF,devicebyteextentpending, command2slot6DFC. SharedC494/C498aliases remainrequired.'),(0x6e62,0x6ecc,'Fade selected palette bank then clear text region','SaveA0textpointer; C4B6WORD&6000 thenROL.W6 yields0/8/16/24. Pairtable6ECCsupplieseffectA0/livepaletteA1,copyA1toA3,target32360black,D0=16,D1=4→2FF6. ClearC48DtoallowIRQpalettephases;waitactiveBYTE6zero;STC48D. D0zero,D1=C4AC+C494 WORDwrap,D2=C498,D3=40000080→26C8;call7014 then6688directpalettecopy;restoretextA0 andcontinueparser. No nonblockingwait shortcut.'))

SPECS+=((0x702c,0x7058,'Publish one static font tile','D1WORDminus32plus07B4 ORC4B6;encodeD0lowWORDdestinationcommand40000000 usingrotate/mask3FFF0003;writecommandthenoneWORDtile. Nocharacterbounds/clamp.'),(0x7058,0x7094,'Initialize static text cursor','SaveinitialcolumnC4A8toC4B8,rowC4AAtoC4BA;D0=C4AC+2*column+(rowWORD<<7) wrapped;publishC4BC. A0=C4AE;retaintextpointerfield.'),(0x7094,0x713e,'Render immediate static text stream','Call7058; zeroextendedBYTE0RTS,13newline,8backspace,others702Ctile. AdvancecolumnWORD,2byteaddress; unsignedcolumn>=64 resetscolumn/incrementsrow; unsignedrow>=32 clearsrow/publishesplaneC4BC. Newline restoresinitialcolumn andcalculates((row<<7)+2*column)&0FFE+plane. Backspace signedunderflowclampscolumnzero; elseaddressminus2anddrawspace. SourcecursorA0advancesbutC4AEnotrewritten.'))

SPECS+=tuple((start,start+4,f'Text control command {command} branch slot',f'Literal indexed branch slot targets{target:X} from6DF0command{command}. This is an indexed entry candidate, not an independently completed actor or gameplay routine. Complete source/selector/caller domains remain open.') for command,(start,target) in enumerate(((0x6df4,0x6e18),(0x6df8,0x6e30),(0x6dfc,0x6e52),(0x6e00,0x6eec),(0x6e04,0x6f02),(0x6e08,0x6f16),(0x6e0c,0x6f3c),(0x6e10,0x6fb6),(0x6e14,0x6e40))))

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
    ops=[dict(entry=f'{s:X}',end_exclusive=f'{e:X}',name=n,contract=c,instruction_evidence=span(s,e),pending='Alltextsource/argument/actor/statealias domains, nativebinding and originalfidelity remain open.') for s,e,n,c in SPECS]
    slots=span(0x6df4,0x6e18)
    banks=[dict(offset=i*8,effect=int.from_bytes(rom[0x6ecc+i*8:0x6ed0+i*8],'big'),live_palette=int.from_bytes(rom[0x6ed0+i*8:0x6ed4+i*8],'big')) for i in range(4)]
    domain=sorted({((w&0x6000)<<6 | (w&0x6000)>>10)&65535 for w in range(65536)})
    if domain!=[0,8,16,24]:raise ValueError('Palette selection mask domain')
    return dict(rom_sha256=ROM_HASH,scope='Second text renderer control domain; highBYTE controls mustnotbeomitted. No globalselectorclosure.',operations=ops,branch_slots=slots,palette_bank_pairs=banks,palette_mask_word_cases=65536,palette_pair_offsets=domain,
        byte_cases=[dict(byte=b,kind='glyph' if 33<=b<=159 else 'space' if b==32 else 'control',control_offset=b*4 if b<32 or b>=160 else None,inside_nine_slots=b<9) for b in range(256)],
        control_bytes=list(range(32))+list(range(160,256)),canonical_control_offsets=list(range(0,36,4)),
        remaining=['Paletteclearcommands2/8 share6E62 wait/clear path;26C8/7014/6688caller argumentdomains,selectedpaletteownership andIRQeligibility remain separate.','Nine prefixslots cannotcoverall128 controlbytes; trace immutable streams andredirectedpointer sources beforebounding6DF0.','Menu oldC460index andsignedbytewrap canescape presumed0..4domain; do notinvent modulo behavior.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/text-control-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Text parser controlbytes0..31/160..255; nine-slot domain remains conditional')
