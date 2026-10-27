"""Scripted player scene movement and exit continuation; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from inventory_ram_schema import accesses
SPECS=((0xe912,0xe91a,'Scripted scene player wrapper','CallE91Ascriptedposition/input path then8838presentation,return. This is notworld-bunnyE7BEupdate.'),(0xe91a,0xe984,'Scripted horizontal and floor gate','ResolveC4E0intoA0; signedX<=102goE984. ElseifC51Enegative skipsecondXgate; ifnonnegativeX>=220goE9F8. NormalpathF330=320,C4F2LONG3000,C4EELONGzero;resolvecontrolledA0/set124bit3;call7748;resolvecontrolledA5,setYWORD152,124bit0set/bit4clear,122BYTEzero,62LONGzero. Preservefractions andotherfields.'),(0xe984,0xe9c8,'Scripted stop and secondary actor setup','Sound78808D0=7,D1=0; thenA0XWORD102,121BYTEzero,58LONGzero,46LONGzero;C4D6WORDzero. A5=F288actor;callCD8E/CFCE. IfYWORD<151set46WORD300andreturn;elsefallthroughE9C8. A0soundclobber andA5identity mustbeproved, notassumedcontrolled.'),(0xe9c8,0xe9f8,'Wait secondary actor and input then transition','SetYWORD151. WORDD0=00F0 thenAND.BC488;nonzerobegins63FA. Otherwisedecrement46WORDandreturnwhileBPL. Negativebeginsblackfade; waitC488BYTEzero, thenC444=165E. Savedcallercontinuation/inputIRQordering required.'),(0xe9f8,0xea06,'Alternate scripted level entry','WriteA5XWORD236;call63FA;JMP1C2A. A5notresolvedlocallyfromA0; incomingwrapper/scheduler actor identity andclobbers required.'),(0xea06,0xea20,'Hide linked part under signed scene flag','IfC51Enonnegative return. ElseA5selector70WORD4,A0=A5linked84,BSET125bit1atlinkedactor. No nullguard; preserveallotherbits. Actor/linkedownership remainsrequired.'))

SPECS+=((0x1522,0x1554,'Scripted player scene frame ordering','C466guard1554initializer. Ordered260A,25A8,29EE,A808,FCD4,31D6,E912. E912runsafteractorcallbacks,animation andspritebuild; incomingA5cannotbeassumedcontrolledwithoutcalleeclobber/identityjoin.'),(0x1554,0x15aa,'Initialize scripted player scene','C466=1522;ordered2D2A,627E,27DA,3478,2746,6750;F2F6=-1;66DEnonblockingfade. IfC51Enegative sound78808D0=9/D1FFFF thenRTS;elseD0=10/D1FFFF andbranch1552RTS. Selectivewrites retaincampaign/scene fields exceptcalledresetservices.'),(0x1c2a,0x1c46,'Begin new game and world state','Call634Eselectivelives/scorethresholdreset;C444=1A6E;STF2C1/F2C0. Returnafterflagwrites. DoesnotdirectlyloadLevel1 orclearallcampaignflags.'))

SPECS+=((0x1bd8,0x1bf2,'Start selected level through menu reset','Call1BF2 input-release/setup;copyF2F0WORDtoF2F6,STC461,call1CEE rebuild thenRTS. Doesnotboundselectedlevel locally.'),(0x1bf2,0x1c2a,'Initialize four continues and menu bounds','WaituntilC47CBYTEzero;writeC51E=4;call9A5E,6384. SetF27C/F278WORDS280,F27E/F27AWORDS472;return. Continuation/inputIRQ required.'),(0x627e,0x6348,'Display then decrement continues','SetC4BEWORD3. IfC51Ezero skipheader;otherwise13C57statictext7094 at13,4,palette6000. ZeroextendoldC51EtoD0,thenSUBQB1liveC51E. Oldindexreads6348columnBYTEandselects13BFC+old*16 label,7094;13C4C7094suffix. Decode40000viaA75AintoFFFF0000;D2=returnedD0LONG, F264WORD=(ASR.L5D0)+1;2468D1=32,D0=FFFF0000,D3=40000000. Draw4045Crows through664C atC380,base1,width40,height14. Oldcount0..4boundsconditional; no guardforotherBYTES.'))

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
        ops.append(dict(entry=f'{start:X}',end_exclusive=f'{end:X}',name=name,contract=contract,instruction_evidence=instructions,pending='Allscene/scheduler/actor identity/register clobber/input/reset domains, nativebinding and independent original comparison remain open.'))
    definitions=[d for d in inv['object_definitions'] if d['handler']==0xea06]
    count_accesses=[row for a in sorted(accepted) for row in accesses(Decoder(rom,a).decode()) if row['width'] is not None and row['address']<=0xffc51e<row['address']+row['width']]
    handoff_sites=[0x3244,0x324a,0x3442,0x3444,0x3448,0x344e,0x154c,0xe912,0xe91a,0xe9f8]
    handoff=[]
    for site in handoff_sites:
        if site not in accepted:raise ValueError(f'Unaccepted A5handoffboundary{site:X}')
        handoff.append(Decoder(rom,site).decode())
    return dict(rom_sha256=ROM_HASH,scope='Scripted player scene/exit contracts and parent state ordering; distinguish C4E0/A0, incoming A5 and secondary F288 actors.',operations=ops,linked_hide_definition_sources=definitions,
        sprite_a5_handoff=dict(evidence=handoff,scope='Normal31D6service withlegal sort opcodes andreturning3440/chunkpaths:3244setsA5=FFFF6F64,3442reads/incrementslowWORDlist throughzero terminator. Finalqueuecursor survivesfinalizer;E912/E91Aprefix resolvescontrolledactorintoA0,notA5. E9F8writes12(A5). This conditionalpath mustnotbe rewritten ascontrolledactorwritewithoutcaller/stateevidence.',pending='Exactqueuecount/overflowcaller andC51Eposition/reachability, callbackmutation/interrupt aliases andalternateE91Aentries remain required.'),
        continues_counter=dict(field='FFC51E',explicit_overlapping_accesses=count_accesses,columns=list(rom[0x6348:0x634d]),labels=[dict(old_count=v,source=0x13bfc+v*16,bytes=rom[0x13bfc+v*16:0x13bfc+(v+1)*16].hex(),new_count=(v-1)&255) for v in range(5)],scope='1BF2sets4;627Edisplaysoldvalue/decrements;old0becomesFFnegative. StartupRAMclear supplies0 only onthatprovenpath. Repeatedentryandregister/bulk aliases remainopen.'),
        callers=[c for c in inv['calls'] if c['target'] in [s[0] for s in SPECS]],
        remaining=['Do notlabelE91A asbunny updater because itsharesnearbycode region.','A0sounddriverhandoff andA5alternateexit identity requirecallerproof.','63FAandinput-release loops require resumable native services, not busySDLspins.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/scripted-player-exit-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Six scripted player/scene exit operations; actor identities kept distinct')
