"""Ending scene actor setup and countdown dispatch; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x9c76,0x9cda,'Ending actor setup','SetcameraINTEGERwords100,retainfractions. Allocate1575Eat250,241 withD4/D7zero;publishA5toC4DC, notD0. Allocate13ECCat478,241 withD4minus1,D7zero;publishA4toC5D0/C4E0/C4E4 thenBSETactor126bit1. Noexplicit allocationfailureguard; allocatorA4/A5registerhandoff required.'),(0x9cda,0x9d08,'Ending controlled actor walk','ResolveC4E0A5, decrementXWORD1; signedX>322 keepsanimationselector4, otherwiseclamp322/setselector92 andSTfield46ofC4DCactor. WriteX/selector70; retainfractions.'),(0x9d08,0x9d1c,'Ending countdown selector','ReadC494WORD; signedpositive goes9DCEdecrement. OtherwiseNEG.Wthenmultiply4 andindexedJMP9D1C+signedoffset. Canonical0,-1,-2chooseoffset0,4,8; arbitrarynegativevaluesunbounded.'),(0x9d1c,0x9d20,'Ending stage zero branch slot','LiteralBRA9D28. Branchslot only, notindependentgameplayroutine.'),(0x9d20,0x9d24,'Ending stage minus one branch slot','LiteralBRA9D9A. Branchslot only, notindependentgameplayroutine.'),(0x9d24,0x9d28,'Ending stage minus two branch slot','LiteralBRA9DA8. Branchslot only, notindependentgameplayroutine.'),(0x9d28,0x9d9a,'Start ending palette effects','Initializefour16colourinterval0effects; banks1,2,4 target4B7CA, bank3target32360black; source/destinationlivepalette. Branch9DCEdecrementsC494; doesnotwaithere.'),(0x9d9a,0x9da8,'Wait ending fourth palette effect','TestC8E8activeBYTE6;nonzeroreturnwithoutcountdownchange. Zerogoes9DCEdecrement. OriginalIRQeligibility/order remain required.'),(0x9da8,0x9dce,'Select ending from campaign statistic','Call6236; compareD1WORD100. Non100writesmaincallback9B34/returns. Equalcallsblocking63FA thenwrites9A88/returns. Completionmeasurementbit1 over70nodes, notnativeportprogress.'),(0x9dce,0x9dd6,'Decrement ending countdown','SUBQ.W1C494withwrap thenRTS; nootherfieldwrite. SharedC494 lifetime ownership remains required.'))

SPECS+=((0x9a88,0x9ac2,'Full completion text state','IfC466differs9A88call9AC2. Update5E82; onlysignednegativeF2DCandnonzeroC47Centerexitpath. WaituntilC47Creleased, thenblocking63FAandpublish15AAtoC444. InputcontinuesviaIRQ; donotbusyspinSDLthread.'),(0x9ac2,0x9b34,'Initialize full completion text','PublishC4669A88; ordered684E,6864,68AE,6066,6484; textpointer13A10,F2E0zero,offset28,attributes2000,planeC000,rowmask31,textdelay20; F2F6=-5; initialize66DEfade; sounddriver78808D0=3,D1FFFF. Noone-frameatomicreset assumption.'),(0x9b34,0x9b78,'Partial completion text state','C466guard9B78init; ordered260A,25A8,29EE,8838,FCD4,31D6,5E82. ExactlyzeroF2DCthenblocking63FAandpublish15AA. NegativeF2DCnotzerohere, distinct9A88gate.'),(0x9b78,0x9be2,'Initialize partial completion text','PublishC4669B34;684E,6864,6066; initializeonlysecondpaletteeffectC740 target4B5AA. Text13AE6,F2E0zero,offset28,attributesA000,planeC000,rowmask31,textdelayzero. Retainotherpaletteeffects andF2F6.'),(0x9be2,0x9c14,'Ending actor frame state','C466guard9C14init; ordered260A,25A8,29EE,9CDA,8838,FCD4,31D6,9D08. Countdownandactorwalk distinctfromnormalplayerframe.'),(0x9c14,0x9c76,'Initialize ending actor state','PublishC4669BE2;blocking63FA; ordered684E,6864,6AC6,2674,2684,2D68,2D2A,7014,6522,27DA,3478,9C76; countdown500,F2F6=-1,66DEfade,sound78808D0=16,D1FFFF.'),(0x9dd6,0x9e2c,'Cycle three palette ranges','DecrementF285BYTE;nonzeroRTS. Zero reload6,zeroextendF284/add2/mask7/storephase. Source9E2C+phase; three2468calls source same atCRAMbyteoffset20,52,116 length4WORDs. Noinitialcounter/domain prooffromroutinealone.'))

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
    def span(start,end):
        out=[];at=start
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
            i=Decoder(rom,at).decode();out.append(i);at+=i['size']
        if at!=end:raise ValueError('Instruction extent')
        return out
    return dict(rom_sha256=ROM_HASH,scope='Ending scene and canonical countdown lifecycle; shared camera label alone would misidentify this behavior.',
        operations=[dict(entry=f'{s:X}',end_exclusive=f'{e:X}',name=n,contract=c,instruction_evidence=span(s,e),pending='Allcaller/register/actoridentity/sharedstate aliases, nativebinding and independent original fidelity remain open.') for s,e,n,c in SPECS],
        initialization_evidence=span(0x9c22,0x9c76),
        canonical_dispatch=dict(initial_count=500,nonpositive_values=[0,-1,-2],offsets=[0,4,8],condition='Only originalinitializedscene underunchangedC494ownership andcallbackordering. Stage1waitretainsminus1;stage2changesmaincallback. Externalentries/aliasesnotclosed.'),
        palette_targets=[dict(address=f'{a:X}',bytes=rom[a:a+32].hex()) for a in(0x4b7ca,0x32360,0x4b5aa)],
        negative_palette_rows=[dict(selector=s,table_address=0x4b08a+s*16,pointers=[int.from_bytes(rom[0x4b08a+s*16+b*4:0x4b08a+s*16+b*4+4],'big') for b in range(4)]) for s in(-5,-1)],
        palette_cycle_bytes=rom[0x9e2c:0x9e3a].hex(),
        callers=[c for c in inv['calls'] if c['target'] in [s[0] for s in SPECS]],remaining=['C494 issharedcamera/state storage; reaching identity/lifetime proof required.','A4/A5allocationreturnhandoff/failure behavior mustbejoined, notassumedD0only.','9B34/9A88states and63FAcontinuation remain shared dependencies.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/ending-sequence-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Ten ending scene operations; conditional countdown offsets0/4/8')
