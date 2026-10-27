"""Batch original Level1 proximity, successor and shared overlap dependencies."""
from pathlib import Path
import hashlib,json
import struct
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
    operations=[]
    for start,end,name,contract in (
        (0x85e8,0x8634,'Horizontal profile sampler returning left-facing boundary',
         '8728tilebit14clear→D1FFFFFFFF/negativeflags. Else87F6collisionpair; D5=(D2WORD>>6) XOR D4WORD,bit6→NOT.WD1. Profileindex=(D4&3F)*16+(D1&15),signednegativeprofileBYTE→failure. ValidD0=(shiftedsampleX&FFF0)-16+biasD3+unsignedprofileD4 WORD;D1zero suppliesnonnegativeflags. D0notfailureindicator. A0/A3/A4/A5/D6 preservedthrough8728/87F6/exactrange; A1/D0/D1/D2/D3/D4/D5 clobbered. Pointers/profileextent/native/reference remainpending.'),
        (0x8634,0x8680,'Horizontal profile sampler returning right-facing boundary',
         '8728tilebit14clear→D1FFFFFFFF/negativeflags. Else87DCpair; D5=(D2WORD>>6) XOR D4WORD,bit6→NOT.WD1. Profileindex=(D4&3F)*16+(D1&15),signednegativeprofileBYTE→failure. ValidD0=(shiftedsampleX&FFF0)+15-biasD3+unsignedprofileD4 WORD;D1zero suppliesnonnegativeflags. A0/A3/A4/A5/D6 preserved; A1/D0/D1/D2/D3/D4/D5 clobbered. ThispinsCE22D6preservationandflag/coordinatecontract,notworld/nativefidelity.'),
        (0x87dc,0x87f6,'Collision pair from descriptor offset4',
         'A1=F2FE+((D2&1FF)<<3)+4;D3zeroextendBYTEbias;D4BYTEshape preservesupperbits. D2/D6/A0/A3/A4/A5 unchanged; A1/D3/D4 modified. Collisiondescriptorextent andpointerproducer domains pending.'),
        (0x87f6,0x8810,'Collision pair from descriptor offset6',
         'A1=F2FE+((D2&1FF)<<3)+6;D3zeroextendBYTEbias;D4BYTEshape preservesupperbits. D2/D6/A0/A3/A4/A5 unchanged; A1/D3/D4 modified. Pairselectionisfixedoffset,notconditionalswitchonvflip; pointerproducer domains pending.'),
        (0x8488,0x84f4,'Actor top-edge horizontal shape1 correction',
         'SampleY=actor16-actor38WORD. Negative121samplesX-8 via8728/87F6;nonnegativeincludingzero samplesX+8 via8728/87DC. Tilebit14and(shapeBYTE&3F)==1 required. Negativebranch writesX=(shiftedsampleX&FFF0)+23,set124bit1;otherwritesX=(shiftedsampleX&FFF0)-8,setbit2. Doesnotclearfraction14,unlikeCE22. Noactor117gate; CE14invokesitevenifCE22skipped. Pointer/shape/fullcaller/native/reference domains pending.'),
        (0xce14,0xce22,'Shared horizontal collision flag reset and position followup',
         'Clearactor124bits1/2withAND.BF9,callCE22then8488unconditionally,RTS. CE22 earlyreturndoesnotbypass8488. Register/flagreturns dependonbothcallees; nativeframebinding and8488effects remainpending.'),
        (0xce22,0xceca,'Direction-dependent paired horizontal terrain probes',
         '117nonzeroor121zero returns. D6WORD=58WORD+1wrapped. Negative121: probe85E8atX+16,Y-8; ifnonnegative andunsignedD0<=X+D6accept; otherwiseprobe85E8atX,Y-8,acceptonlynonnegativeandunsignedD0<=X+D6. AcceptedX=D0+1WORD,clearfraction14,set124bit1. Positive121: probe8634atX-16,Y-8; ifnonnegativeandunsignedD0>=X-D6accept; otherwiseprobe8634atX,Y-8,acceptonlynonnegativeandunsignedD0>=X-D6. AcceptedX=D0-1WORD,clearfraction14,set124bit2. ComparisonsandcoordinatesarewrappedWORD,not signedorfloat. Samplerreturnflags/D0coordinate/D6preservation,allactorvelocity/directiondomains,8488followup andnative/referenceverification remainpending.'),
        (0xcd8e,0xcde4,'Shared vertical velocity update preserving history fallback inputs',
         'SaveD0WORD,maskactor117with0E; nonzero skipsupdate. 122signednegative:SUB.L6000from62,ifresultNclear finish; elseNEG.L62,set122byte1. 122nonnegative:set122byte1; ifsigned62>=F0000finish; elseADD.L6000andcapifsigned>F0000. RestoreD0WORD; highD0WORDnevermodified,soentireD0preserved; A0/A3/D1andotherregistersuntouched, no calls. FinalflagsfromrestoredD0WORD,notvelocity. ThusACAC CD8E preserveshistoryA0/indexD0/controlledA3 beforeACCE; actorvelocity/direction changed. Overflow/flag/specialactor/native/reference domains pending.'),
        (0xcde4,0xce14,'Shared caller-supplied vertical acceleration adjustment',
         'D1=actor62long,D2BYTE=122 preservingD2upperbits. Ifdirectionnegative ADD.LD0,D1 elseSUB.LD0,D1; ifresultNsetNEG.LD1/NEG.BD2. SignedcapD1atF0000;write62long/122byte. D0unchanged,D1/D2clobbered,finalflagsfromBYTEdirectionwrite. IncomingD0acceleration/overflow/calleractor domains remainpending; no inferredfixedgravitysubstitution.'),
        (0x8680,0x86d6,'Terrain floor sample height with profile and flip handling',
         'Call8728 sampletile; tileD2bit14clear→D0FFFFFFFF/negativeflags. Else879A bias/shape, ifshapeD4bit6 setNOT.WsampleX D0. profileindex=(shape&3F)*16+(sampleX&15) into4A71A; signednegativeBYTEprofile→failure. Validprofilezeroextend,alignY D1&FFF0. D2bit12clear→Y=alignedY+16-biasD3+profileD4; bit12set→Y=alignedY+31-bias-profile. SuccessD0zero/nonnegativeflags,D1height. D0originalXnotpreserved; A0/A3/A4/A5 preservedbytheseexactranges,A1/D2/D3/D4/D7 maychange. Terrainpointer/index/storage/profile/callerdomains andnative/originalverification pending.'),
        (0x8728,0x874c,'Read wrapped foreground terrain word at shifted sample position',
         'AddF268WORDtoD0X;A1=longF30A terrainbuffer. Xindex=(D0&03F0) ASR.W3; addtoA1. Yindex=(D1&03F0)<<3. D2WORD=buffer[A1+Yindex]. D1/A0/A3/A4/A5 unchanged; A1/D0/D2modified. Wrapspatialmask isnot a proofworldbounds orinitializedbuffercoverage.'),
        (0x879a,0x87bc,'Read collision bias and shape for sampled tile orientation',
         'A1=F2FEcollisiontable; indexD3=(D2&01FF)<<3,add2ifD2bit12set. AdvanceA1byindex; D3zero thenBYTEbias(A1)+;D4BYTEshape(A1)+ preservingitsupperbits;D7BYTE=D4 preservingitsupperbits. SampleD2unchanged,A0/A3/A4/A5 unchanged. Collisiontableextent/bank/pointer domains andremainingcallers pending.'),
        (0x4eaa,0x4ef4,'Parallax dispatch and output publication for pinned Level1 selector',
         'D2WORD=F2F6; MOVE.B4AEDA[D2.W] replaceslowbyteonly, preservinghighbyte; doubleWORDtwice. D0=F362X→F31C,D1=F366Y→F31E; JSR4EF4+D2.W; returnedD0/D1→F348/F34A,D2byte→C546,D3byte→F286. IfF2F6WORD1 thenhighbyte0,tablebyte3,offset12→4F00BRA4F36. Thisprovesonlypinnedselector1domain, notruntime retention of1/allmutation/genericselectorbounds.'),
        (0x4f00,0x4f04,'Mode3 parallax inline dispatch slot',
         'LiteralBRA4F36 isselectedby4ED6 onlywhenD2scaledWORD12. This inlinebranchslot isnot a standalonegameplayroutine; noentrycount/fidelitypromotion.'),
        (0x4f36,0x4f40,'Mode3 background scroll and downstream terrain flags',
         'LSR.W1 D0 halvesunsignedcameraX, D1zero, D2FFFFFFFF,D3zero,RTS. Through4EAA caller outputsF348=halfX,F34A=0,C546FF,F2860. C546FF affects72A2 backgroundzero-camera/plane22 path; F2860 selects horizontal-scrollmode0 in6960. Nativeconsumer/queue/timing andallcaller domains remainpending.'),
        (0x8fa4,0x8ff2,'Player prior-Y containment contact predicate',
         'D6zero,A0controlledC4E0. ComparecontrolledpriorYword24 againstA5currentY16: unsignedpriorY>A5bottom rejects. Subtractrespectiveheights38; unsignedcontrolledtop<A5top rejects. Computeleft/right withsignedASRhalfwidth36 andwrappedWORDarithmetic. Rejectcontrolledleft<A5left orcontrolledright>A5right. Thus horizontalcontainment, NOT generaloverlap. D6FFFFonmatch,TST.WD6 setsreturnflags. ControlledpriorY versuscurrentY andunsignedwrap/caller domains pending.'),
        (0x8ff2,0x9012,'Temporarily shrink contact dimensions and restore with original return flags',
         'PushD0wordthenD1word, subtractD0fromactorwidth36 andD1fromheight38, call9012. PopheightadjustmentintoD0/add38, popwidthadjustmentintoD0/add36. FinalD0originalwidthadjustment; D1not restoredbythiswrapper. TST.Bactor123 suppliesfinalflags insteadof9012flags. Shrinkunderflow andcontactsideeffects/callerargumentdomains pending.'),
        (0x9514,0x9524,'Clear linked actor blink bits',
         'D0key→A0,clearactor125bit1,loadnext84toD0; repeatwhileD0nonzero. InitialD0mustbenonzero: nodummyheadguard. Pointervalidity/acyclicity andfullcaller/livealiasdomains pending.'),
        (0x9524,0x9534,'Toggle linked actor blink bits',
         'D0key→A0,toggleactor125bit1,loadnext84toD0; repeatwhileD0nonzero. InitialD0mustbenonzero; cyclicchains donotterminate. Preserveoriginalbitandnextlookuporder; caller/nativebindings pending.'),
        (0x7292,0x72a2,'Select foreground terrain descriptor and tailcall shared streamer',
         'A0=F30A,saveactiveplaneA0intoF302long,tailbranch72D0. Foregroundselection isstatepublication, notdirectraster. Existingnativehelpersdonotproveallshared72D0/7424/interrupt/callerdomains.'),
        (0x72a2,0x72d0,'Select background descriptor and optional zero-camera streaming mode',
         'A0=F336,F302=A0. IfC546zero tailbranch72D0. Ifnonzero andplane22wordnonnegative tailbranch7424. Ifnonzero andplane22negative pushplane18long,clear18long,call72D0,restore18long thenbranch7424. Preserveplane/camerawrites evenwhenbackgroundrendererstatic; sharedservice/register/clobber/allgatewriterdomains pending.'),
        (0x2fe8,0x2ff6,'Publish fifteen-colour palette flash through transfer service',
         'D2=15,D3=C0000000,call2468,RTS. D0source/D1destination areincomingcallerarguments; length15 leavesindex0untouchedfortheknown2F3C callers. Othercalleraddress/queue/hardwaredomains remainpending.'),
        (0xb2e6,0xb314,'Initial proximity gate for Level1 definition144A4',
         'Actor117nonzero returns. Setactor70word0. ResolvecontrolledC4E0; wrappedWORD(actorX-controlledX), NEG.W ifNset, thenunsignedcompare100. Difference>100 returns; otherwisecallback42=B314. Inclusive100 threshold, WORDwrapping andunsignedcompare mustbe preserved. Definition144A4 ispresentviaone class04markerparameter5; appearance/species/fulllifecycle pending.'),
        (0xb314,0xb386,'Proximity successor contact and transition handoff',
         '117gate returns. Call8EAA; ifactor70word30 gotoB338; otherwise9012contactZ→B360,contact→96C6 thenif70word30 gotoB338 elseB360. B338 sound8 preservingD0word,70word34,D0word0118,D1word0029,D2longFFFFC550→D2E2 immediatecurvedtransition,RTS. B360 sets70word4;124bit0set→D042withD0=1;thenCD8E/CFCE/CF46/D168. Sharedcontact/terrain/control/progress domains pending. Successor behavior isnot just walkingenemyAI.'),
        (0x8f22,0x8f74,'Unsigned wrapped rectangle overlap across linked actor chain',
         'A5bounds: Xleft=wrap(X-ASR.W(width,1)), Xright=wrap(left+twicehalfwidth), Ybottom=Y,Ytop=wrap(Y-height). ForA0thenlong84linkedchain, unsignedWORD comparisons rejecttop>otherbottom,bottom<othertop,left>otherright,right<otherleft; equalitycountscontact. OnmatchD6=-1 andreturnwithA0hitrecord. OnrejectD6=next84;ifnonzero loop elseRTSwithD6zero. Oddwidth signedASR/WORDwrap andunsigned comparisons areoriginal; replacingwithfloatAABBchangesdomains. Pointeracyclicity, chainvalidity, allcallerbounds and8EBC consumerflags remainpending.'),
    ):
        evidence=[];at=start
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted {at:06X}')
            i=Decoder(rom,at).decode()
            if at+i['size']>end:raise ValueError('Unaligned range')
            evidence.append(dict(address=f'{at:06X}',bytes=rom[at:at+i['size']].hex(),mnemonic=i['mnemonic'],operands=i['operands']));at+=i['size']
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,contract=contract,
            instruction_evidence=evidence,range_sha256=hashlib.sha256(rom[start:end]).hexdigest(),
            pending='Originalcaller/state/definition mutations, chain/control domains, nativeintegration and independentreference verification remain incomplete.'))
    definition=0x144a4
    mode=rom[0x4aeda+1]; selector=1
    replaced=(selector&0xff00)|mode; offset=(replaced*4)&0xffff; slot=0x4ef4+offset
    instruction=Decoder(rom,slot).decode()
    if mode!=3 or slot!=0x4f00 or instruction['mnemonic']!='BRA' or instruction['operands']!='$004F36':raise ValueError('Pinned Level1 parallax target changed')
    return dict(rom_sha256=ROM_HASH,scope='Bounded Level1 handler, sharedcontact andparallax dependency evidence; nofullenemy/nativefidelity claim.',operations=operations,
        pinned_level1_parallax=dict(selector_word=selector,table_address='04AEDB',table_byte=mode,scaled_word=offset,slot=f'{slot:06X}',target='004F36',
            slot_bytes=rom[slot:slot+4].hex(),c546_output=255,f286_output=0,global_dispatch_domain_complete=False),
        definition=dict(address=f'{definition:06X}',bytes=rom[definition:definition+34].hex()),counts=dict(ranges=len(operations)),complete_runtime_domains=False)

def verify(project):
    if json.loads((project/'docs/stage9/level1-enemy-dependencies-contract.json').read_text())!=catalogue(project):raise ValueError('Stale enemy dependency batch')

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];report=catalogue(project)
    (project/'docs/stage9/level1-enemy-dependencies-contract.json').write_text(json.dumps(report,indent=2)+'\n');print(report['counts'])
