"""Pinned bounded world entry/selection evidence; no ROM instruction execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

SPECS=(
 (0x1c46,((0x1c46,0x1c6c),),'Stopped-route level admission',
  'Return when F274 LONG is nonzero. Otherwise A368 resolves current actor node; WORD selector publishes F2F6/F2F0, clear F26D, call1CEE. No direct completed-node or availability rejection occurs here. Caller1A6E requires unpaused F270 and bit0 of OR(C47D,C47E,C47F).',
  'Original input producer and all reachable selector domains; full world route, fade and entry service binding.'),
 (0x1cee,((0x1cee,0x1d94),),'Level entry rebuild and target state',
  'Ordered rebuild63FA,2674,2684,523E,684E,6864; F264=1;3900,3C08,3E8A,3BF6,27DA,3478,766A,3F34,608A,7292,72A2,6960,6AA6; publish C444=1C6C;6750,29EE,FCD4; C542=3;5324,54A0,66DE,5D08. Clear then restore C432 display bit6 around rebuild. Does not reset campaign progress, score or lives.',
  'All called startup services, shared state domains, publication/interrupt order, original palette/music/display comparison.'),
 (0x523e,((0x523e,0x5324),),'Revisit rescue and prior-entry flags',
  'Read C558[F2F6]bit1 into C552 as SNE FF/00; BSETbit2 then SNE old bit into C553. Clears transient control, input, timer and linked state fields; initializes C490=0,C4BE=3,C4D6=250,F2B4=10. Campaign flag array is retained.',
  'All transient-field consumers and exceptional selector domains; C553-conditioned spawn variants and original revisit comparisons.'),
 (0x3e8a,((0x3e8a,0x3ee4),),'Level companion census and empty-level completion',
  'Scan foreground MAP F30A+34 across heightWORD6>>4 rows; count each four-byte marker whose type high byte is12. Publish WORD C556. Zero count sets current selector C558bit1. Does not itself update C552, which startup523E sampled earlier.',
  'Ordering of zero-count rescue latch consumers, all sparse MAP row domains and runtime marker mutation.'),
 (0xa3b4,((0xa3b4,0xa436),),'Completed-node marker coordinate list',
  'Scan world foreground MAP from F30A+34. Marker highbyte0E yields X=recordWORD2+5,Y=row<<4 into C494/C498. A37E resolves node; append XY WORD pair to7188 only if C558[node]bit1 set. End list with WORDFFFF.',
  'MAP0 marker/node correspondence, signed row and selector boundaries, 7188 scratch ownership and every caller refresh domain.'),
 (0xa436,((0xa436,0xa50a),),'Completed-node sprite and transfer publication',
  'Always upload128bytes314E0 toB200. Append 16x16 completed markers from7188 toC9BC beginning at C492*8. Signed-cull X to[F362-16,F362+336],Y to[F366-16,F366+240]. Subtract those LOWER cull bounds before adding hardware X107/Y112; after hardware bias128, pixelX=nodeX-cameraX-5,pixelY=nodeY-cameraY. Size/link WORD starts0500 and links increment; attr4590. Terminate lastlink, updateC492, append spriteDMA command to C434 word-transfer queue: countC492*4,sourceC9BC,destinationF400.',
  'Original SAT capacity, negative-coordinate/framebuffer domains, queue flush ordering and sprite priority; this routine does not decide node admission.'),
 (0x9dd6,((0x9dd6,0x9e2c),(0x1b98,0x1bac)),'World cyclic palette publication',
  'World initialization1B98 buildsA3B4 coordinate list, then F284=0,F285=6. Decrement BYTE F285, return unless zero. Reload6, set F284=(old+2)&7. Source9E2C+phase supplies4words uploaded to CRAM byte offsets20,52,116. Four overlapping source windows use the literal14byte palette strip9E2C..9E3A.',
  'VBlank queue timing and frame count domains; palette strip is data and is excluded from instruction decoding.'),
 (0x9f72,((0x9f72,0x9fee),),'World cursor and pause actor allocation',
  'Allocate13EAA atF27C/F27E integers with zero fractions and marker; failure jumps0200 diagnostic. Publish actorA4 intoC4E0/C4E4; actor126bit1,70=0,48=0,46=2; clear three6402companion slots. Allocate14EDE atzeroXY and publish returnedD0 C5BA without explicit failure branch. C4BE=3.',
  'Graphics/animation packs for both definitions, allocation/capacity and diagnostic contracts, C5BA-null pause-camera caller domain.'),
 (0x9e3a,((0x9e3a,0x9e98),),'World initial camera clamp',
  'ResolveC4E0; signed-clamp integerX-160 to lower224 then upperF330-544, publishF362 WORD. Signed-clamp integerY-112 to lower224 then upperF332-448, publishF366 WORD. ClearC546. Clamp order is literal, including possible upper bound below lower bound.',
  'Upper/lower map extent domains, retained fraction words and smooth camera9E98 handoff; current fixed map viewport is not this camera.'),
)

def catalogue(project):
    directory=project/'docs/stage9';rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
    inventory=json.loads((directory/'inventory.json').read_text())
    accepted={a for routine in inventory['routines'] for a in routine['blocks']}
    operations=[]
    for entry,ranges,name,contract,pending in SPECS:
        instructions=[]
        for start,end in ranges:
            at=start
            while at<end:
                item=Decoder(rom,at).decode()
                if at not in accepted:raise ValueError(f'Unaccepted boundary {at:06X}')
                instructions.append(item);at+=item['size']
            if at!=end:raise ValueError('Instruction range crosses data boundary')
        operations.append(dict(entry=f'{entry:04X}',name=name,contract=contract,pending=pending,
            instruction_evidence=instructions,code_ranges=[dict(start=a,end_exclusive=b,sha256=hashlib.sha256(rom[a:b]).hexdigest()) for a,b in ranges]))
    calls=[dict(owner=o['entry'],address=i['address'],target=i.get('target'),mnemonic=i['mnemonic'],operands=i['operands']) for o in operations for i in o['instruction_evidence'] if i['mnemonic'] in ('BSR','JSR')]
    fields=[('F274',4,'active route pointer admission gate'),('F2F6',2,'selected current level'),('F2F0',2,'last requested selector'),('F26D',1,'foreground packed-selector override gate'),('C444',4,'next main state'),('C492',1,'sprite count after world completed markers'),('C434',4,'word-transfer queue cursor'),('F284',1,'palette byte phase'),('F285',1,'palette six-update countdown'),('C552',1,'rescued latch from current flagbit1'),('C553',1,'prior-entry latch from old flagbit2'),('C558',80,'persistent campaign flags'),('C5BA',4,'pause camera actor key')]
    return dict(rom_sha256=ROM_HASH,scope='Bounded static contracts, no ROM execution. Original route/entry/render dependencies remain pending; no full scene completion claim.',operations=operations,calls=calls,
        immutable_data=[dict(start='9E2C',end_exclusive='9E3A',bytes=rom[0x9e2c:0x9e3a].hex(),words=[int.from_bytes(rom[a:a+2],'big') for a in range(0x9e2c,0x9e3a,2)],scope='Overlapping four-word palette windows; excluded from instructions'),
            dict(start='314E0',length=128,sha256=hashlib.sha256(rom[0x314e0:0x31560]).hexdigest(),scope='Completed marker pattern upload')],
        shared_fields=[dict(address=a,bytes=b,meaning=c) for a,b,c in fields],
        recommended_assessments=[dict(address=o['entry'],name=o['name'],status='bounded static evidence; native binding and caller/fidelity domains pending',path='world-selection-contract.json',scope=o['contract']+' Pending: '+o['pending']) for o in operations])

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];report=catalogue(project)
    (project/'docs/stage9/world-selection-contract.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Verified {len(report['operations'])} bounded world-selection operations; {len(report['calls'])} direct calls")
