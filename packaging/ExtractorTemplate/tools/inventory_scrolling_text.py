"""Scrolling text commands, pointer sentinels and publication; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from rolo_codec import decode_backward_lz
SPECS=((0x5e82,0x5eb0,'Scrolling text frame','ReadF2E0LONG&000FFFFF. Atzero:clear20blocks5F38; negativeF2DCreturnswithoutscroll;zeroF2DCskipstext;positivecenters5F0Aanddraws5F56. Otherpositionsskiplinework. Then5EB0clearand602Escroll. Endsentinel2negativefreezesonlyatnextlineboundary, notimmediately.'),(0x5eb0,0x5f0a,'Clear scrolling text row','OnlywhenF2E0LONG&0007FFFFzero andF2EEWORDnonzero:row=(ASR.WF2E0,3+F2EE)&F2EC,WORD<<7+F2EA;encodecommand;write32LONGzeros=128bytes. Noheight/capacityguard.'),(0x5f0a,0x5f38,'Center upcoming text line','ScanA0fromF2DCuntilBYTE1 usingDBEQD0startedFFFFFFFF; negativecountformula giveslinebytesbefore1. CenterWORD(20-length),ASR1then*4,add2iflengthodd;writeF2E4. Original65536scanlimit/absentdelimiter behavior literal, nofontwidth metric.'),(0x5f38,0x5f56,'Clear twenty glyph blocks','SetF2E4zero;20iterationsD1=19call5F92D0zero andADDIoffset4. Save/restoreD1WORDaroundcall. FinalF2E4=80WORD.'),(0x5f56,0x5f92,'Consume text bytes and sentinels','ZeroextendBYTEthenSUBIB20; signednonnegative32..159drawglyph0..127via5F92,advanceF2E4by4. Otherbytesbreakline:restorebyte;0setsA0zero,2setsA0FFFFFFFF,othersretainadvancedA0. StoreA0F2DC. BYTE1isnormalnewline;160..255alsoenterbreakbranch, notglyphs.'),(0x602e,0x6066,'Advance text scroll publication','Setincrement2,zeroF000foreground/backgroundhorizontalpair;VSRAMcommand40000010. ADDIL2000F2E0 thenmaskLOWWORD07FF/storeLOWWORDonly,retainfraction. WriteWORDverticalvalue. Devicecompletion andclockcaller remain separate.'))

SPECS+=((0x6066,0x608a,'Load scrolling text glyph bank','Source46D4C,A1FFFF0000;callsemanticbackwardLZA75A. D2=ASR.W1ofreturnedD0lowWORD; D1=64 destinationbyteoffset,D3=40000000;D0=A1afterloader;call2468. Transfer/loader registerhandoff mustbejoined; noROMcodeexecution.'),)

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
        ops.append(dict(entry=f'{start:X}',end_exclusive=f'{end:X}',name=name,contract=contract,instruction_evidence=instructions,pending='Alltextsource/delimiter/count/fieldaliases, nativepublication and originalreference remain open.'))
    streams=[]
    for start in(0x13a10,0x13ae6):
        at=start
        while rom[at] not in(0,2):
            at+=1
            if at-start>4096:raise ValueError('Ending text terminator extent')
        raw=rom[start:at+1];lines=raw[:-1].split(b'\x01')
        streams.append(dict(start=f'{start:X}',end_exclusive=f'{at+1:X}',bytes=raw.hex(),sha256=hashlib.sha256(raw).hexdigest(),terminator=raw[-1],line_lengths=[len(x) for x in lines],non_glyph_bytes=sorted({v for v in raw if not 32<=v<=159})))
    decoded,metadata=decode_backward_lz(rom,0x46d4c)
    if len(decoded)%32:raise ValueError('Glyph pattern tile alignment')
    refs=[Decoder(rom,a).decode() for a in sorted(accepted) if any((v&0xffffff)==0xfff2dc for v in Decoder(rom,a).decode().get('references',[]))]
    return dict(rom_sha256=ROM_HASH,scope='Scrolling text helpers, glyph resource and bounded ending source streams; global text command domain remains incomplete.',operations=ops,ending_streams=streams,
        glyph_bank=dict(source='46D4C',codec_metadata=metadata,decoded_bytes=len(decoded),decoded_sha256=hashlib.sha256(decoded).hexdigest(),tiles=len(decoded)//32,destination_byte_offset=64,first_tile=2,exclusive_last_tile=2+len(decoded)//32,meaning='Fourtilesperglyph; onlyresource-backedindices areestablished. Consumer128glyphbytecases do notprove128completeglyphresources.'),
        explicit_text_pointer_references=refs,
        byte_cases=[dict(byte=v,glyph=32<=v<=159,glyph_index=v-32 if 32<=v<=159 else None,pointer_result='zero' if v==0 else 'FFFFFFFF' if v==2 else 'advance') for v in range(256)],
        callers=[c for c in inv['calls'] if c['target'] in [s[0] for s in SPECS]],remaining=['F2DCzero andnegative sentinel are distinct sceneconditions; preserveboth.','Alltextinitializers/aliases andglyphresource extent remain required.','NoROMinstructions areexecuted; sourcesdecodedasdata only.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/scrolling-text-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Six scrolling text helpers;256bytecases;two original ending streams')
