"""Shared text and tile publication helpers; accepted static instructions only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from inventory_ram_schema import accesses
SPECS=((0x6222,0x622a,'Append zero-terminated bytes','CopyBYTEs throughandincludingzero fromA0toA1; retreatA1oneBYTE so subsequentappend overwritesterminator. A0pointsafterinputzero. Noextentguard; missingterminatorreads/writesuntilzero.'),(0x622a,0x6236,'Append digit bytes as ASCII','ForDBFD0lowWORD+1iterations, resetD1LONG48 thenADD.Bsourcebyte andwrite wrappedlowBYTEtoA1. No0..9check. D0lowWORDFFFF therefore65536iterations, notzero; A0/A1advancecount.'),(0x664c,0x6688,'Publish masked tile rows','Setincrement2; rowcommandencodesA1lowWORD withrotate/mask3FFF0003 thenOR40000000. Eachrow copiesD1lowWORD+1sourceWORDs, masks07FF thenADD.WD0 withwrap. Attributesfromsourcearestripped; D0suppliesbase/attributes. RestoreD1eachrow; A1ADDA.W0080 rowstride; D2DBFsetsrowcount+1. Noextentguard; FFFFcounts65536.'),(0x71ba,0x71f6,'Format long decimal with leading spaces','UseLONGD1 unsigned repeatedSUB/DBCS divisors71F6 intoC4C0ASCIIbytes, restoringlastborrow subtraction. D7startsFFFFFFFF, NOT.WthenADDIB30 formsdigit. ZeroLONGdivisorterminates; appendzeroBYTE. ReplaceatmosteightleadingASCII0withspaces, preservingfinaldigit. ScratchA0,A1,D1,D2,D7clobbered; boundeddecimaldomain needscallerproof.'))

SPECS+=((0x5f92,0x602e,'Publish four-tile block','Setincrement2; D0WORD*4 ORF2E8, thenincrementbeforewrites toemitindicesbase+2,+3 onfirstrow,+4,+5 onsecondrow. Rowaddress=(ASR.WF2E0,3+F2E6)&F2EC thenWORD<<7 +F2E4+F2EA; secondrowincrementbeforemask. Encodeeachrow intoVDPcommand40000000 withrotate/mask3FFF0003. Wordwrap/signedshift areliteral; no tileextentguard.'),(0x721e,0x7222,'Format hexadecimal long','Entry721EsetsD7=7 thenshared7226formats8nibbles. ROL.LD0by4eachiteration; maskLOWnibble andlookup723EASCII0123456789ABCDEF. C4C0receivesbytespluszero; A0advances9, D0restoredaftereightrotates, D7LOWFFFF, D1lastnibble. Direct7226entrycountdomain remainscaller-dependent.'),(0xb1c6,0xb1d6,'Install controlled companion callback','ReadC4E4LONGintoA0; writecallback42=A84E withoutnull/typeguard. Nootheractorfieldwrite. Actoridentity/lifetime andA84Econtinuation mustbejoinedbefore nativeassignment.'))

SPECS+=((0x7226,0x723e,'Shared hexadecimal formatting loop','ROL.L4 andLOWnibblelookup723E intoC4C0, DBFD7lowWORD countplusone; appendzeroBYTE. Normal721Eentry usescount7. Unaccepted gap7222..7226 is excluded, notdecodedascode.'),)

SPECS+=((0x7014,0x702c,'Request display region zero fill','D0LONGzero,D1LONG0D40,D2WORD07FF retainingupper,D3LONG40000000;call26C8andreturn. Rawlengthrequest anddevicebytecompletion distinct; do notinfer2048WORDextent.'),(0x8c06,0x8c24,'Lookup coordinate tile word','SaveD5LOWWORD. D3WORD=D0X ASR4,D4WORD=D1Y ASR4. D5LONGzero thenBYTE(A0-2)width;MULU.WD5,D4 unsignedlowrow*width. ADD.WrowproducttoD3/doubleWORDwrap;D2WORD=tileatA0+signedD3WORD. RestoreD5LOWWORDonly: upperD5zero fromMOVEQ. D0/D1coordinates/A0 unchanged; D3offset/D4product clobbered. FinalCCRfromrestoredMOVE.WD5,notreturnedtile. Noextentornegativecoordinateguard.'))

SPECS+=((0x879a,0x87bc,'Resolve tile metadata pair','A1=F2FE;D3WORD=(D2&01FF)<<3,add2whenD2bit12. AddsignedWORDoffsettoA1. D3LONGzero,loadmetadataBYTE0toD3;BYTE1toLOWD4retainingupperbits;copyLOWBYTE D4toD7. A1advance2. Maskselects512records, offsets0..4090; actualallocationextent/ownership notproved.'),(0x8bb0,0x8c06,'Query original terrain shape surface','Call8C06tilequery;D2bit14clearr eturnD0minus1. Else879Ametadata,mirrorXwithNOT.WD0ifD4bit6. Shapeindex=(D4&003F)*16+(D0&15),always0..1023. Load4A71ABYTE; signednegativeinvalid→D0minus1. Elsezeroextendheight, D1WORDalignFFF0; D2bit12 selectsD1+31-D3-height, otherwiseD1+16-D3+height. ReturnD0LONGzero/flags fromMOVEQ. Pointer/coordinatecaller andterrainmetadataaliases remainrequired.'))

SPECS+=((0x38c2,0x38de,'Select live terrain metadata pointer','ZeroextendF2F8BYTE,WORDdoubletwice;lookupLONG4AFF6+index*4andwriteF2FE. No17entryguard. Conditionalcataloguedtable andsceneconsumerreachability remainrequired.'),(0x8770,0x8792,'Query tile lateral metadata presence','F2FEA1;maskD0WORD01FF,shift3,addoffset. IfmetadataBYTE5or7nonzeroreturnD0LONG7,otherwisezero. Noextentguard; flagsfromMOVEQ.'),(0x87bc,0x87dc,'Resolve opposite vertical metadata pair','As879A512recordmask,butadd2onlywhenD2bit12clear. D3LONGzero/BYTEfirst,D4LOWBYTEsecondretainingupper;A1advance2. D7unchanged.'),(0x87dc,0x87f6,'Resolve first lateral metadata pair','F2FEA1;index(D2&01FF)<<3;A1+=index+4. D3zeroextendBYTEfirst,D4LOWBYTEsecond retainingupper. Noextentguard.'),(0x87f6,0x8810,'Resolve second lateral metadata pair','F2FEA1;index(D2&01FF)<<3;A1+=index+6. D3zeroextendBYTEfirst,D4LOWBYTEsecond retainingupper. Noextentguard.'))

SPECS+=((0x51d0,0x5216,'Publish fixed resource spans and fill suffix','2468source1602A,destinationAC80,D2WORD00C0,D3LONG40000000; thensource27BC0,destinationAE00,D2WORD0020,samecommand. Then26C8D0zero,D1LONGAE40,D2LONG63,D3LONG40000000. Preserveorderedtransfer/fillrequests; resourceidentity/devicecompletion andcallerclobbers remain required.'),(0x5ce6,0x5d08,'Delayed music command countdown','IfF2C6WORDnegative return. OtherwiseSUBQ.W1; ifnonnegative return; firstnegativezeroextendsF2C1BYTEtoD0,D1LONGminus1,call78808. Futurecallsnegative returnuntilrewritten. Zero firesfirstcall;positiveNfiresN+1calls. SignedWORD8000..FFFFinactive, notunsigneddelay.'))
SPECS+=tuple((start,start+4,f'Horizontal scroll mode {mode} branch slot',f'Literal branch slot at{start:X} targets{target:X}; dispatch6960/697Cbyte-selector context required. Notanindependentgameplayroutine. Originaltargetservice andcompleteproducer/caller domains remainseparate.') for mode,(start,target) in enumerate(((0x6980,0x6990),(0x6984,0x69a8),(0x6988,0x69aa),(0x698c,0x6a0a))))

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH: raise ValueError('ROM revision')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
    ops=[]
    for start,end,name,contract in SPECS:
        at=start;ins=[]
        while at<end:
            if at not in accepted: raise ValueError(f'Unaccepted boundary{at:X}')
            i=Decoder(rom,at).decode();ins.append(i);at+=i['size']
        if at!=end: raise ValueError('Instruction extent')
        ops.append(dict(entry=f'{start:X}',end_exclusive=f'{end:X}',name=name,contract=contract,instruction_evidence=ins,pending='Allcaller argument domains, buffer ownership/aliases and native/reference publication remain incomplete.'))
    divisors=[];at=0x71f6
    while True:
        value=int.from_bytes(rom[at:at+4],'big');divisors.append(value);at+=4
        if value==0:break
        if len(divisors)>12:raise ValueError('Divisor extent')
    if rom[0x723e:0x724e]!=b'0123456789ABCDEF':raise ValueError('Hex digit table changed')
    shape=rom[0x4a71a:0x4ab1a]
    if len(shape)!=1024 or not set(shape)<={*range(16),255}:raise ValueError('Shape table byte domain')
    pointer_refs=[row for a in sorted(accepted) for row in accesses(Decoder(rom,a).decode()) if row['width'] is not None and row['address']<0xfff302 and 0xfff2fe<row['address']+row['width']]
    pointer_rows=[]
    for bank in range(17):
        pointer=int.from_bytes(rom[0x4aff6+bank*4:0x4affa+bank*4],'big')
        pointer_rows.append(dict(bank=bank,pointer=pointer,points_to_accepted_instruction=pointer in accepted))
    return dict(rom_sha256=ROM_HASH,scope='Shared display, control and terrain query contracts; data tables excluded from instruction decoding.',operations=ops,decimal_divisors=divisors,decimal_table_end_exclusive=f'{at:X}',hex_digit_table=dict(start='723E',bytes=rom[0x723e:0x724e].hex()),terrain_shape_table=dict(start='4A71A',bytes=shape.hex(),sha256=hashlib.sha256(shape).hexdigest(),rows=64,columns=16,valid_heights=sorted(set(shape)-{255}),invalid_byte=255,index_domain=[0,1023],scope='64shapeIDs masked to6bits and16Xpositions maskedto4bits; metadata allocation/caller coordinates remain separate.'),terrain_metadata_pointer=dict(explicit_overlapping_accesses=pointer_refs,table_prefix_start='4AFF6',investigated_rows=pointer_rows,scope='17rows usedbyexistingmapextractor; produceracceptsallBYTEs. Rows8..16pointtoaccepted787F6code,so scene-to-consumerbankreachability mustbeprovedbeforetreatingallasmetadata. No4096byteextent inferredfrom512recordmask.'),
        callers=[c for c in inv['calls'] if c['target'] in [s[0] for s in SPECS]],remaining=['DBFcounts are countminusone includingFFFF65536case; do notsilentlyclamp.', 'String/digit and decimal buffers requirecaller length/range proof.','Tiletransfer completion/device ordering and aggregate queue ownership remain separate.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/display-utility-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print(f'{len(SPECS)} shared display/control/query helpers mapped; caller domains remain open')
