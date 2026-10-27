"""Pin Level1 companion/contact and shared transition callback dependencies."""
from pathlib import Path
import hashlib,json
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted={a for r in inv['routines'] for a in r['blocks']};operations=[]
    for start,end,name,contract in (
        (0xacac,0xacce,'History follow fallback phase with inactive history path',
         '117nonzero tailbranchesB058. OtherwisecallsCD8E,ACCE,CFCE,CE14,CECA,CF46 inthatorder thenRTS. ExactCD8Econtract now confirms incomingA0history/D0index/A3controlled arepreserved beforeACCE; actorvelocity/direction mutate. Thisfallbackisnot a positioncopy.'),
        (0xacce,0xadd0,'History follow vertical-difference branches and conditional jump',
         'D1WORD=historyY(A0+D0+2)-actorY16; signedpartition<=-8→AD68,-7..-1→ACE2,>=0→AD38. EverybranchcallsAEB4 thenBCLR46bit2 andtestsoldbit. Oldbitset usesB00A probe; failedprobe clears121/58long andcopiesA3facing118 (negativebranch124mask6 maycopyfacingwithoutprobe). Oldbitclear: -7..-1 branchjumpsif124mask6nonzero,orcontrolledY unsigned<actorY and(124&81)==80; >=0 jumpsonly124mask6nonzero. <=-8 branchrequirescontrolledY unsigned<actorY, then124mask6 nonzero OR history122byte<=0signed plusactorY-historyY>18signed andwrappedabsX<=132signed. JumphandoffB0D6. Wordwrap/registerclobbers/historyindex/flag producers/nativecomparison pending.'),
        (0xb00a,0xb058,'Probe companion forward terrain and optionally adopt sampled height',
         'D0actorX,D1actorY,D2actor58WORD; if121signednegative NEG.WD2,addstepD0. SavecandidateXYtwoWORDs onstack,call8680. Nonnegativeflags→heightdelta check; negative→reloadsavedXYwords,add16toY,call8680again; ifstillnegative failure. CandidateD1height absolutewrappedWORDdifference fromactorY mustsigned<=actor58WORD; successwriteactorY,discard4stackbytes,D1=0/flags;faildiscard4bytes,D1FFFFFFFF/flags. Xnotwrittenhere. 8680returnheight/clobbers/terrain/samplebounds andWORDversusLONGcaller domains pending.'),
        (0xab3c,0xac34,'Companion history-copy eligibility and exact copied fields',
         'A4definition4,A3controlledC4E0,clear46bit3;A0history6002,D0=(6000-50)&3FF,D1=(unmaskedindex-16)&3FF. C514/F2BC/historybyte14bit5 nonzero→ACACfallback. If124bit4clear andsignedwrappedabsXYdistancesboth<=52→fallback. ElseprevioushistoryXYatD1mustexactcurrentactorXY; mismatchfallback. Matchset46bit3,copyhistoryXY/70/direction121/122/velocity58WORD/62WORD/facing118/124; IMPORTANTactor120readfromabsoluteROM00000D via1B790000000D0078,not historyoffset13. Clear124bit5,AE86. C520signednegativeandC510zero→CE14elseRTS. Fraction60/64 notcopiedhere. Index/alignment/stateproducers/fallback/native/reference remainpending.'),
        (0xac34,0xac7a,'Realign companion slots using callback match or preceding history record',
         'A0history6002,A4slots6402,D7=2→three slots. Skipzerokey. Savekey/D7/A0/A4,callAC7A,restoreMOVEMwithoutchangingflags. BPL skipsfallbackbecauseAC7A matchedcallbackandcopiedcontrolledXY. Negativefailurecomputes(6000-actor50-16)&3FF andcopieshistoryXY. Allslot/key/historyvalidity andcallbackmutationdomains remainpending.'),
        (0xac7a,0xaca4,'Compare companion callback against two-entry realignment table',
         'A0=ACA4,A5callback42→D0,D1=1;CMPtwo successiveLONGsusingDBEQ (equalstopswithoutdecrement). No matchD1FFFFnegative→RTSwithoutXYwrite. MatchresolvescontrolledC4E0,copiesXY12/16toA5,D1=0 withnonnegativeflags,RTS. Immutabletable ACA4..ACAC isA9B0/AA4A; thiscallbacktable isDATA, notORI instructions. Pointer/caller/native domains pending.'),
        (0xadfc,0xae86,'Companion loss movement initialization and stuck response',
         'A3controlledC4E0;BSET46bit0 oldbit gatesfirstupdate:clear52word,set124bit0,clear124bits1/2,121=controlled121XORFE,clear118bit3thenifdirectionnot signedpositive setbit3. Everycall58WORD=min_signed(controlled58WORD+2,15) withWORDwrap andNOlowerclamp; fraction60unchangedhere. If124bit4set return; elsemask6 nonzero savescurrentX12to52 andcomparesprevious52:ifdifferent callB0D6,ifequal NEG.B121/toggle118bit3. Then(124&81)==80→B0D6 elseRTS. Flag/radius/velocity producerdomains pending.'),
        (0xae86,0xaeb4,'Publish companion attachment bit change marker',
         'Clear124bit7 first. Compareold125bit0 withcurrent124bit0; replace125bit0withcurrentattachment preservingotherbits. Ifbitsdiffer set124bit7. Byteoperationorder andold/newbit semantics required; allattachmentwriters/nativealiases pending.'),
        (0xaeb4,0xaf80,'Compute companion facing and bounded horizontal follow step',
         'D2WORD=wrap(A3.58WORD+2),signedclamp2..15. A4controlledC4E0. Ifcontrolled122signedpositive and124bit0clear:targetX=controlled12,D2=controlled62WORD (overridesclamp). Elseifcontrolled124bit5 targetcontrolledX; elsehistoryX A0+D0.W. ForattachedA5 andverticaldistance<=52signed, controlledfacing/radius52mayadjusttarget andset46bit2. signedwrappedtargetX-actorX determines121=1orFF/118bit3,negativeabsNEG.W. Clear46bit1; ifsigneddistance<=D2 reduceD2todistance,copyA3facing118,set46bit1. Write58WORD=D2,60WORDzero. A3/history/index/velocity/radius domains pending.'),
        (0xaf80,0xaff2,'Choose companion animation selector from movement and controlled state',
         'A3controlledC4E0. 124bit4→70word8; bit0clear→12. Attached:124mask6nonzero goescontrolledstate18decision; else46bit1clear with58longnonzero→4. With46bit1set requireequal118facing; controlled70word18→B002,controlled46longnonzero→4,controlled121nonzero→AFFA; otherwise0. Field46testedLONG includesadjacentbytes, notjustoneflag. AFF2..AFFA gap notacceptedbycurrentwalker andexcludedfromthiscontract. Fullselector/animation/native/original domains pending.'),
        (0xaffa,0xb00a,'Companion selector return tails for movement and controlled special state',
         'AFFA setsactor70WORD20 thenRTS. B002sets70WORD18 thenRTS. OriginalAF80branches targettheseaccepted tails. InterveningAFF2..AFFAisoutsidebothverifiedranges; externalstubentrydomainremainsunproved.'),
        (0xaa4a,0xab28,'Companion alternate free movement and follow-mode restoration',
         '117nonzero→B058. Clear46bits1..3(maskF1),B114XY→C494/C498,49FF. signed(slot47-1)<=C50E gates86D6 probesatfollowtargetY-height thenactorY-height-16; onlybothnegative clears49. CD8E thenC86C; sound0A preservingD0word onlywhen124bit4 changesfromclear toset acrossC86C. Ifbit4alreadyset stillcallC86Cwithnosound. CFCE/CE14/CECA/CF46/AF80; 122nonnegative,exacttargetX,signedtargetYwithinY-minus62WORD..Y andsignedslotcount gatesC50E=slot47/callbackA92E. Probe/sound/stateproducers pending.'),
        (0xab28,0xab3c,'Companion history-follow orchestration',
         'CallAE86 thenAB3C. If46bit3set skipAF80,elsecallAF80. Return. ThislocalcallerdoesnotproveAE86/AB3C history/progression/helperdomains orfullfollowerlifecycle; no replacementalgorithm inferred.'),
        (0xadd0,0xadfc,'Companion loss callback phase and visibility publication',
         'TSTactor117;SNEactor116 publishesFFwhen117nonzero else0. CallsCD8E,ADFC,CFCE,CE14,CECA,CF46 inthatorder. Clear46bits1..3(maskF1),callAF80,RTS. ADFC changesmovement/controlstateandmustnot beomitted; flags/pointers/physics/losscaller/nativeintegration pending.'),
        (0xb0d6,0xb114,'Companion conditional jump setup and probe-flag reset',
         'If124bit4set or70word18 or49nonzero gotoB10E. Else124bit0setorbit7set→122FF,62long85000,124bit4set. Alwaysclear49beforeRTS. Originalground/probe/actionflag domains remainpending; do notgeneralizejumpvelocitytoRolo.'),
        (0xa84e,0xa8bc,'Base actor presentation with temporary controlled-state substitution',
         'CallA8BC. IfC513nonzero andsignedactor62long>10000,clamp62to10000. SaveC4E0long/C510byte/C519byte/C51Bbyte; replaceC4E0withC4E4basekey,clearthreeflags,call8838 presentation; restoreflagsandcontrolledkey reverseorder. No independentactorreplacement; nativealiases/interruptvisibility and8838clobberdomains remainpending.'),
        (0xa92e,0xa9b0,'Companion follow record copy and downstream slot callback rewrites',
         'B114 suppliesXY/facing/state→actor12/16/118/70. CopybaseC4E4 direction121/velocity58/122/62,callCE14/CECA. If124bits1or2 set or125bit7set:zeroextendactor47slot intoD0; D1word=3-slot; SUBQ.B1 D0 retainsupperWORD, C50E=lowbyte,offsetD0WORD*4 from6402. DBF D1 writes eachnonzero slotcallback42=A9B0 andclears124bit0. Forvalidslot1..3 thisaffectscurrentandlaterslots; slot0/4 ormutationsneedboundsproof (byteunderflow/DBFcount differ). OtherwiseRTS.'),
        (0xa9b0,0xaa4a,'Companion free movement to follow-mode transition',
         '117nonzero→B058historypath (NOTsimpleRTS). B114XY→C494/C498; CD8E; C920 usingcontrolled58WORD+2;CFCE/CE14/CECA/CF46/AF80. If124bit0 callbackAA4A. Else122negative returns; XmustexactC494, signedtargetYwithinactorY-minus62WORD..actorY. signed(slot47-1)<=C50E thenC50E=slot47,callbackA92E. PreserveWORD/BYTEsignedness; slot/divisor/terrain/currentcontrolled producers remainpending.'),
        (0xb058,0xb0d6,'Companion inactive player-history visibility and detach path',
         'Index=WORD(6000-actor50)&03FF into6002history. ReadD1historyX; signedstrictcameraX<D1<cameraX+320. OnlyifXinside readD2historyY; signedstrictcameraY<D2<cameraY+224. OutsidebranchB0CC copiesD1/D2toactor12/16; anearlyXreject leavesD2incoming, NOTreadhistoryY. Insideif117mask0Eor124bit0 set:callbackA8BC,callB28E detach,125bit2set; elseCD8E/CFCE. Pointer/indexalignment/historyinitialized/callerD2domains remainpending.'),
        (0x54a0,0x5680,'Create or refresh counter HUD actor and append six video transfers',
         'SignedCMP.B F26F withFF(-1): returniflessthan-1; returnifC552nonzero. IfC4D8zero allocate1476E at160,0 through28B0; failure returns beforequeue mutation. SaveD0keyC4D8; actor126bit4,48byte2,50byte50,36word56,38word16,28long/8long5854524E,32/34words0. Existingactor50=50; if48signednegative NEG.B48,clear49,word46+=2. A0=C434 queuecursor; D0zeroextendedactor2 thenASL.W5. Append sixDMArequests: lengths64,32,32,32,32,32 words; sources322E0,32360,27BC0,32360,27940+tens*64,27940+units*64; destinationbyteoffsets0,128,192,256,320,384 fromD0, commandwordpacking40000080/mask3FFF0003. DIVU.W10 splitszeroextendedC556word; digitoffsetASL.W6 canwrap forunprovedlargevalues. Sixrequests each14bytes, trailingCLR.L atcursor+84, savecursor+84toC434 (terminatornotadvanced). Queuecapacity/publication anddigit/countdomains remainpending; thisisnotdecodedSDLHUD.'),
        (0xa8bc,0xa92e,'Companion stationary/contact callback gates',
         'Clearactor121byte/58long/70word everycall. If117nonzero return. CallCD8E/CFCE/CF46. IfC552nonzero gotoA8FE; else ifactor84zero gotoA8FE; else resolve84→definition4,CMPI.W30atdefinition10 thenTST.BC550: TSToverwritescomparisonflags, soBEQA92C dependsC550only, NOT comparison30. AtA8FE ifC510nonzero return;9012contactZreturns. C50Fzero orsignedC50E<3→B1D6; otherwiseD2=A9B0→B1A8 thenB1D6. Exactslot/control/gateproducerdomains andnativecompanionservices remainpending.'),
        (0xd2e2,0xd32a,'Configure shared curved transition and perform immediate update',
         'OR125bit2,BSET126bit4,callback42=B386,long50=D2. StoreD0word14; word46=wrap(D0-actor12+F362). StoreD1word18; word48=negwrap(D1-actor16+F366); byte56=lowbyte48. FallthroughD324 callsB386 immediately thenreturns. Argument/pointer/divisorvalidity andallcallerdomains remainpending; not a genericpositioncopy.'),
        (0xb386,0xb3c4,'Advance shared transition with byte countdown and unsigned division',
         'Clearactor118bit3; zeroextendbyte56toD0,subtract3WORD. Ifnegative:setD0zero,incrementBYTEthroughactor50pointer,actor116FF. StorelowD0byte56. Yword16=wrap(actor18+D0). MULU.W actor46 thenDIVU.W actor48 unsigned; Xword12=wrap(actor14-quotientlowWORD). Divisionbyzero/quotientoverflow originalexceptiondomains remainpending; mustnot clamporreplacewithfloatlinearinterpolation. Thiscallbackalso runsduringD2E2setup.'),
    ):
        evidence=[];at=start
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted {at:06X}')
            i=Decoder(rom,at).decode()
            if at+i['size']>end:raise ValueError('Unaligned range')
            evidence.append(dict(address=f'{at:06X}',bytes=rom[at:at+i['size']].hex(),mnemonic=i['mnemonic'],operands=i['operands']));at+=i['size']
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,contract=contract,
            instruction_evidence=evidence,range_sha256=hashlib.sha256(rom[start:end]).hexdigest(),
            pending='Typedsharedstate aliases, slot/pointer/divisor producers, allcallback transitions/nativeintegration and originalreference verification remain incomplete.'))
    table=rom[0xaca4:0xacac]
    if table.hex()!='0000a9b00000aa4a' or rom[0xac06:0xac0e].hex()!='1b790000000d0078':raise ValueError('History copy/table evidence changed')
    return dict(rom_sha256=ROM_HASH,scope='Bounded companion/contact/transition and shared HUD dependency contracts; not complete companion lifecycle ornativegameplay.',operations=operations,
        history_copy_data=dict(callback_table_address='00ACA4',bytes=table.hex(),targets=['00A9B0','00AA4A'],
            actor120_source_absolute_address='00000D',source_byte=rom[13],instruction_address='00AC06',instruction_bytes=rom[0xac06:0xac0e].hex()),
        counts=dict(ranges=len(operations)),complete_companion_lifecycle=False)

def verify(project):
    if json.loads((project/'docs/stage9/level1-companion-contract.json').read_text())!=catalogue(project):raise ValueError('Stale companion batch')

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];report=catalogue(project)
    (project/'docs/stage9/level1-companion-contract.json').write_text(json.dumps(report,indent=2)+'\n');print(report['counts'])

