"""Pin player creation, startup marker selection and checkpoint writes; static only."""
from pathlib import Path
import csv
import hashlib
import json
import re
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from rolo_maps import word, long, parse_map
from rolo_codec import decode_backward_lz


def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH: raise ValueError('ROM mismatch')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted={a for routine in inv['routines'] for a in routine['blocks']}
    operations=[]
    for start,end,name,contract in (
        (0x2468,0x2510,'Synchronous memory-to-video transfer command publication',
         'PreserveD5long only. SetC432bit4/publishcontrol; setVDPincrement2(8F02),lengthlow/highregisters93/94fromD2WORD. SourceD0long: ASR.L1 low/middlebytes→95/96; originalhighbyte(D0>>16)&FF shifted1→97. D1WORDdestinationpackedintoD4long usingROL.W2/mask3FFF0003,ORI0080,ORD3 mode; saveC462long,publishhighthenlowwords. Pollvideocontrolbit1untilzero; clearC432bit4/publishcontrol; restoreD5,RTS. D0/D1/D2/D3 preserved,D4clobbered; exactregisterwriteorder/sourcealignment/lengthzero semantics/devicecompletion andinterruptclobbers remainpending. Known22A8callerrequests64CRAMwords;2FE8 requests15.'),
        (0x3060,0x30c6,'Advance active palette interpolation and mark publication dirty',
         'Inactivebyte6 returns. Decrementcounter9 BYTE; ifnonnegative returns; else reloadrate8. Forcount7+1 colours, readimmutablecurrent/delta RGBpairs, signextenddelta toindexlookup30C6+signedoffset4, ADD.B lookup tocurrent, assembleWORD andwritepalettepointer0. SetC48BFF; offset4-=15 WORD; ifnegative clearactive6. Initialoffset0070 yields112,97,82,67,52,37,22,7 then-8: eight advancingupdates, not eightmainframes unlessinterruptgate/countdownpermit. Lookupdoesnot mutatepairbytes. Otherinitialoffset/deltadomains pending.'),
        (0x14a4,0x1508,'Interrupt tail gates palette advancement and publication',
         'SetC48CFF, incrementC490word, setvideoA6, call2314. IfF2BFnonzero call78920/788B6. IfC48Dnonzero skipallpaletteupdates/publication; else call3060 forC66C/C740/C814/C8E8 then22A8. Restore15registers andRTE. Interruptentry/prologue, cadence, audioqueues andcaller/C48Dmutations remainpending; cannot substitute oneupdate pergameframe withoutproof.'),
        (0x63fa,0x6484,'Initialize four fade-to-black effects and wait for interrupt completion',
         'Call2FF6 fourtimes with16colours/rate0,currentdestinationpaletteC5EC/C60C/C62C/C64C,target32360. ThenpointA0tolasteffectC8E8, clearC48D sointerruptadvancespalettes; waituntilthatrecordactive6zero, setC48DFF andreturn. Nativecontinuationmust preserveinterrupteffect/publicationordering; notbusywait onmainSDLthread. Targetwords andallgatewriters stillneedverification.'),
        (0x22a8,0x22ce,'Publish dirty palette buffer through transfer service',
         'IfC48Bzero return. ClearC48Bbefore2468 call withD0longFFFFC5EC,D1zero,D2word0040,D3longC0000000. Thisrequests64palettewords fromfourbanks. Transfercompletion, videoqueue/interrupt ordering and2468 service semantics remainpending.'),
        (0x26bc,0x2746,'Normalize byte-fill request and synchronously publish video command',
         '26BC exchangesD0/D1 andD2/D3, duplicatesD0lowbyte intoWORD andsubtracts1fromD2word. 26C8 setsC432bit4,publishescontrol, setsVDPincrement1,lengthlow/highfromD2 andDMAfillmode9780; constructscommandfromD1address masked3FFFC000/ROL.W2 plus0080 andD3, savesC462long/publisheshighthenlowwords; writesD0word tovideo data, pollscontrolbit1 untilzero, clearsC432bit4 andpublishescontrol. Nativevideoaddress/fillsemantics andinterrupt interactions remainpending; polling isnot a nativegamebusyloop requirement.'),
        (0x2ff6,0x3060,'Initialize palette interpolation record from current and target colours',
         'Clearactivebyte6, bytecount7=lowbyte(D0)-1, byte8=lowbyte(D1), counter9=0; storeA3pointerat0 and0070wordat4. D0wordDBF controlscolourcount (66DE supplies16). For eachcurrentA1 andtargetA2 colourWORD, shift1 thenextractthree3bitRGBchannels. Predecrement stores place pairs(currentchannel*2,targetchannel-currentchannel) at10+6*i in BLUE,GREEN,RED order, which3060 assembles back into original0BGR WORD. Finishactivebyte6FF. Negativecount/byteversusWORDcountdomains, allocationextent and30xx updater/queue remainpending.'),
        (0x523e,0x5324,'Reset level contact state and update progress bits',
         'ClearC516/C517/C519/C51A/C51B/C522 andlistedflags; setC511FF (injury/blink latch, NOT zero). ReadC558+signedWORD(F2F6): BTSTbit1→C552FFifsetelse0; BSETbit2 returnsoldbit→C553FFifpreviouslysetelse0. Updateprogressbyteinplace; preserveotherbits. SetC4BEword3, C4D6word250, F2B4byte10; clearlistedHUD/input/statefields. Progressindexbounds andallaliases remainpending; score/lives/checkpoint notdirectlywrittenhere.'),
        (0x6750,0x6794,'Synchronize actor presentation from linked records',
         'Visit48 actorrecords at998C stride130 inascendingorder. Skipnegativeword0 orzero long76. Resolveactor76 andcopyword12/16/70 plusbyte118/121/122 fromlinkedrecord. This runsbeforerestart29EE/list andFCD4/animation; it isnot a globalactorreset. Nonzero pointervalidity andchainproducerdomains remainpending.'),
        (0x684e,0x6864,'Clear foreground video plane',
         'Request26BC tailservice withD0longC000,D1zero,D2long40000080,D3word1000. Video-plane clear request, NOT playerRAM/contactreset; nativebufferextent/completiontiming mustbe established from26BC.'),
        (0x6864,0x687a,'Clear background video plane',
         'Request26BC tailservice withD0longE000,D1zero,D2long40000080,D3word1000. Backgroundvideo request, NOT checkpointreset. Complete26BC service semantics anddisplaytiming remainpending.'),
        (0x5324,0x5348,'Reset HUD publication flags and video range',
         'ClearC551/C550 bytes then26C8 zero-fill request D0zero,D1longB100,D2word00FF,D3long40000000. PreserveoriginalrequestseparatelyfrominferredcompletedVRAMextent. Score/lives RAM notwrittenbythisrange; originalHUDpublication andfillcompletion remainpending.'),
        (0x66de,0x6750,'Initialize four level palette effect records',
         'SignedWORD F2F6 shiftedleft4 selects4B08A descriptor. Fourcalls2FF6: A0effectrecordsC66C/C740/C814/C8E8; A1andA3paletteRAM C5EC/C60C/C62C/C64C; A2successiveROMpalettepointers; D0word16,D1zero. Targetpalettepixels areinsufficientforfade/queuebehavior; 2FF6 effectinitialization/callerbounds/interrupttiming remainpending.'),
        (0x766a,0x7730,'Allocate Rolo and reset selected player state',
         'Allocate definition13ECC at420,200 in16.16, facing0 and marker0 through28B0; allocation failure branches0200. Savehead toC4E0/C4E4, actor68word0, controlledtypeC4E8word4. Clear6000word, threecompanionkey longs6402/6406/640A and listed reset writes. C542word3 is distinct fromlivesC51D. This routine doesnot reset scoreC52E, livesC51D orcheckpointC4FE/C500. Remaining producers and whole restart retention mustbe verified.'),
        (0x7730,0x7748,'Restore checkpoint integer position',
         'ResolveC4E0. CopyC4FEword toactor12 andC500word toactor16. Fractionwords14/18 are untouched here. Do not reconstruct a freshactor orclear fractions as partof thiscall.'),
        (0x3f34,0x3fe0,'Startup MAP scan and class5 factory',
         'Scanforeground MAP F30A+34, height/16 rows, ordered sparse rowrecords. Onlyclass17 andclass5 dispatched; others ignoredin thispass. Class5 clearsparameterbit0 then doublesWORD for4762 lookup. Onlydefinitions14906/148C2/148E4 accepted: setmarker highbyte17 beforeallocation28B0 at0,0 withfacing0/marker0. Allocation failure occursaftermarkerconsumption. Tableextent andthesedefinition behaviors remainpending.'),
        (0x3fe0,0x4018,'Select spawn marker and write checkpoint',
         'Compareclass17 parameterbyte withF26C. Mismatch returns. Match writeswrapped(rawX+8) toactor12, clearsfraction14; writeswrapped(row*16) toactor16, clearsfraction18; copiesintegerXY toC4FE/C500 andcalls4CB8. Noearlystop: allmatchingmarkers areprocessed inMAP order, lastmatch wins. This isstartup placement, differentfrom4A48 streamed enemyY(row*16+17).'),
        (0x37a4,0x37c0,'Choose or retain spawn selector during map setup',
         'NonnegativeF2F6 levelselector iswordshiftedleft3. IfF26D iszero, loadF26Cbyte fromselected4AB1A descriptorhighbyte. IfF26D nonzero, retainexistingF26C. Pointercomesfromsame descriptorlong masked00FFFFFF. Negativelevelselector takesother branch382A beforethisrange.'),
        (0x933a,0x937a,'Player transition overrides destination spawn selector',
         'Onlycontrolledtype4. Readbyte actor10: low7bits→F2F6word, highbit rotatedleft1→F26Cbyte0or1. SetF26DFF toretainoverride at3784; setC522FF andcallsound788AE with1D, restoringD0word. Actor10 producer/domain andtransitioncaller1CEE stillpending.'),
    ):
        evidence=[]; at=start
        while at<end:
            if at not in accepted: raise ValueError(f'Unaccepted boundary {at:06X}')
            i=Decoder(rom,at).decode()
            if at+i['size']>end: raise ValueError('Unaligned end')
            evidence.append(dict(address=f'{at:06X}',bytes=rom[at:at+i['size']].hex(),mnemonic=i['mnemonic'],operands=i['operands']))
            at+=i['size']
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,contract=contract,
            instruction_evidence=evidence,range_sha256=hashlib.sha256(rom[start:end]).hexdigest(),
            pending='Original caller/state domains, allocation failure, all state aliases and independent original comparison remain required; SDL startup/restart bindings are not complete.'))
    reset_writes=[]
    creation=next(o for o in operations if o['entry']=='00766A')
    for i in creation['instruction_evidence']:
        m=re.fullmatch(r'\(\$FFFF([0-9A-F]{4})\)\.L',i['operands'])
        if i['mnemonic'].startswith('CLR.') and m:
            reset_writes.append(dict(site=i['address'],address='FFFF'+m[1],width={'B':1,'W':2,'L':4}[i['mnemonic'][-1]],value=0))
    reset_writes.extend(dict(site='0076AE',address=f'FFFF{a:04X}',width=4,value=0) for a in (0x6402,0x6406,0x640a))
    rows=[]; selectors=[]
    for selector in range(80):
        descriptor=long(rom,0x4ab1a+selector*8); source=descriptor&0xffffff
        data=rom[source:source+4096] if rom[source:source+3]==b'MAP' else decode_backward_lz(rom,source)[0]
        layout=parse_map(data); markers=[r for r in layout['records'] if r['type']>>8==17]
        default=descriptor>>24; matching=[]
        for r in markers:
            match=(r['type']&255)==default
            row=dict(selector=selector,source=f'{source:06X}',record_offset=r['offset'],parameter=r['type']&255,
                default_spawn_selector=default,matches_default=match,x=(r['x']+8)&0xffff,y=r['y']&0xffff)
            rows.append(row)
            if match: matching.append(row)
        selectors.append(dict(selector=selector,default_spawn_selector=default,marker_count=len(markers),
            matching_count=len(matching),final_default_position=([matching[-1]['x'],matching[-1]['y']] if matching else None),
            scope='Static descriptor-default domain only; F26D overrides and repeated startup callers may choose another position.'))
    level1=[r for r in rows if r['selector']==1]
    if [(r['parameter'],r['x'],r['y']) for r in level1]!=[(2,136,528),(0,184,752),(1,296,1296)]:
        raise ValueError('Unexpected pinned Level1 spawn markers')
    direct_writes=[]
    for operation in operations:
        for i in operation['instruction_evidence']:
            suffix=i['mnemonic'].rsplit('.',1)[-1]
            if suffix not in ('B','W','L') and i['mnemonic'] not in ('ST','SNE'): continue
            destination=i['operands'].split(',')[-1]
            m=re.fullmatch(r'\(\$FFFF([0-9A-F]{4})\)\.L',destination)
            if m and (i['mnemonic'].startswith(('CLR.','MOVE.')) or i['mnemonic'] in ('ST','SNE')):
                direct_writes.append(dict(operation=operation['entry'],site=i['address'],address='FFFF'+m[1],
                    width={'B':1,'W':2,'L':4}.get(suffix,1),mnemonic=i['mnemonic'],operands=i['operands']))
    lookup=rom[0x30c6:0x313e]
    steps=[112-i*15 for i in range(8)]
    if len(lookup)!=120 or not all(0<=offset+delta<120 for offset in steps for delta in range(-7,8)):
        raise ValueError('Palette lookup domain outside pinned data')
    return dict(rom_sha256=ROM_HASH,scope='Bounded original player/startup contracts and static spawn-marker domains, not native gameplay completion.',
        operations=operations,reset_writes=reset_writes,spawn_markers=rows,selector_domains=selectors,
        direct_absolute_writes=direct_writes,
        palette_lookup=dict(address='0030C6',end_exclusive='00313E',bytes=lookup.hex(),sha256=hashlib.sha256(lookup).hexdigest(),
            initial_0070_offsets=steps,terminal_offset=-8,channel_delta_domain=list(range(-7,8)),
            scope='Domain from2FF6 initialoffset0070 and3bitRGB differences only; otherrecord writers/callers remainpending.'),
        counts=dict(ranges=len(operations),reset_writes=len(reset_writes),selector_slots=len(selectors),spawn_markers=len(rows),
            direct_absolute_writes=len(direct_writes),
            selectors_without_default_match=sum(s['matching_count']==0 for s in selectors),
            selectors_with_multiple_default_matches=sum(s['matching_count']>1 for s in selectors)))


def verify(project):
    report=catalogue(project)
    if json.loads((project/'docs/stage9/player-startup-contract.json').read_text())!=report: raise ValueError('Stale player startup evidence')
    with (project/'docs/stage9/startup-spawn-markers.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    if rows!=[{k:str(v) for k,v in row.items()} for row in report['spawn_markers']]: raise ValueError('Stale startup marker CSV')


if __name__=='__main__':
    project=Path(__file__).resolve().parents[1]; report=catalogue(project)
    (project/'docs/stage9/player-startup-contract.json').write_text(json.dumps(report,indent=2)+'\n')
    with (project/'docs/stage9/startup-spawn-markers.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(report['spawn_markers'][0])); writer.writeheader(); writer.writerows(report['spawn_markers'])
    print(report['counts'])

