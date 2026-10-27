"""Join player followup/floor semantics to accepted code and native bindings."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x842e,0x8482,'Player tile crossing followup','ResolveC4E0A5;compareold/currentXalignedFFF0signed. Equalreturns. Query8728atcurrentXY;tile14required. Signedcrossdirection selects87F6or87DC;shapeBYTE&3Fmust1. SetYWORD=(Y&FFF0)+1;retainfraction.','src/core/player_collision_followups.hpp'),(0x8482,0x84f4,'Player top corner followup','ResolvecontrolledA5;probeY=Y-height38; signed121BYTE choosesX-8/87F6 orX+8/87DC. Tile14/shape1required. LeftsetsX=(probeX&FFF0)+23/124bit1;rightsetsX=(probeX&FFF0)-8/124bit2. Zerodirectionusesrightpath.','src/core/player_collision_followups.hpp'),(0x84f4,0x85e8,'Player floor collision and landing','ClearincomingA0flags124withBEand120BYTEbeforeC4E0reload. ReachWORD=58+62+1wrapped. Ascending122negative gates62<=58signed;computeC545lowBYTE((62<<4WORD)/58unsigned)if58nonnull,skipfirst32pxprobeinthatcase. ProbeY-32,Y-16,Ywith8680/reachsigned;firstacceptedreachthenunsignedflooraboveYrejectreturns. Tile12togglesD7bit6;ascending signedshape&63versusC545gate. Landingwrites120shape,Y,zeroYfraction18,124groundbit0/clear4,66=62,122zero,62LONGzero; nonzero68clear/set124bit6.','src/core/player_floor_collision.hpp'))

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']};ops=[]
    for start,end,name,contract,source in SPECS:
        at=start;ins=[]
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted collision boundary{at:X}')
            i=Decoder(rom,at).decode();ins.append(i);at+=i['size']
        if at!=end:raise ValueError('Instruction extent')
        ops.append(dict(entry=f'{start:X}',name=name,contract=contract,instruction_evidence=ins,native_source=source,native_sha256=hashlib.sha256((project/source).read_bytes()).hexdigest(),pending='Incoming actor versuscontrolledidentity,8728coordinatehandoff, terrainmetadata/shape ownership, complete movementgates and originalreference remain open.'))
    return dict(rom_sha256=ROM_HASH,scope='Three original collision semantics joined to existing native helpers; no newgameplay orfullfidelity claim.',operations=ops,
        callers=[c for c in inv['calls'] if c['target'] in [s[0] for s in SPECS]],remaining=['Bindings alreadyexist; sourcehash/semanticjoin doesnotreplace allcaller andindependent originalverification.','Preserveincoming124/120writesbeforecontrolledpointerreload.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/player-collision-binding-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Three collision followup/floor contracts joined to existing native sources')
