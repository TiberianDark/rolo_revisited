"""Batch original Level1 class06 collection callbacks; static evidence only."""
from pathlib import Path
import hashlib,json,struct
from inventory_rom import ROM_HASH
from m68k_static import Decoder


def catalogue(project):
    directory=project/'docs/stage9';rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    inv=json.loads((directory/'inventory.json').read_text());roster=json.loads((directory/'first-level-roster.json').read_text())
    accepted={a for r in inv['routines'] for a in r['blocks']}
    operations=[]
    for start,end,name,contract in (
        (0xb702,0xb714,'Generic collectible contact callback dispatch',
         'Call9012 contact. IfreturnedZ set, return. OtherwiseA4=actor5.long4 definition,A0=definition.long22,JSR(A0),return. ImmutableLevel1 class06 seven definitions supply9958 or99E2; this is a bounded initial-definition domain, NOT allruntime mutations or globalB710 targets.'),
        (0x9958,0x997e,'Collect score-valued item',
         'Setactorcallback42=B7C0,ORactor125bit2. LoaddefinitionA4.long28 scoreamount,D0→997E originalscoreaward. SaveD0word,call788AE sound0F,restoreD0word,RTS. SiximmutableLevel1 definitions award100/200/300/400/500/10000. Marking/render/collision gates andrepeat suppression dependonsharedframe/lifetime services; no automaticportclaim.'),
        (0x99e2,0x9a04,'Collect extra-life item',
         'SaveD0word,sound40 via788AE,restoreD0word; callback42=B7C0,OR125bit2; D0=1→9A04 lifeADD.B/signedcap helper. This is theone immutableLevel1 definition1443E, whose+28zero isnot a scoreaward. Signedbyteoverflow behavior remainsoriginal9A04 contract.'),
        (0xb7c0,0xb7d8,'Collected-item motion callback',
         'Ifactor46zero,setFF andcallB7D8 once. Everycall thenCD8E andCFCE,return. Doesnot explicitlyrelease/eraseactorhere; offscreen/lifetime/animation services required. Original collectedmark125bit2 andcallback domains remainpending.'),
        (0xb7d8,0xb804,'Initialize collectible drift with shared RNG',
         '716E requestD0=0,D1=3; SUBQ.B1 andstorelowbyte121 (direction); long58=00030000. Then716E D0=3,D1=9; SWAPD0,CLR.WD0,storelong62 velocity; actor122=FF. Inclusive/exclusive RNGbounds dependon716E semantics; do notinfer range fromargument names. CD8E/CFCE terrain effects andnativebinding pending.'),
    ):
        evidence=[];at=start
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted {at:06X}')
            i=Decoder(rom,at).decode()
            if at+i['size']>end:raise ValueError('Unaligned range')
            evidence.append(dict(address=f'{at:06X}',bytes=rom[at:at+i['size']].hex(),mnemonic=i['mnemonic'],operands=i['operands']));at+=i['size']
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,contract=contract,
            range_sha256=hashlib.sha256(rom[start:end]).hexdigest(),instruction_evidence=evidence,
            pending='Fullruntime definition/selector/callback mutations, contact gates, sound/graphics/lifetime integration and independentoriginal verification remain required.'))
    rows=[]
    markers=[m for m in roster['markers'] if m.get('handler')==0xb702]
    for definition in sorted({m['definition'] for m in markers}):
        callback=struct.unpack_from('>I',rom,definition+22)[0];value=struct.unpack_from('>I',rom,definition+28)[0]
        if callback not in (0x9958,0x99e2):raise ValueError('Unexpected Level1 collection callback')
        rows.append(dict(definition=f'{definition:06X}',bytes=rom[definition:definition+34].hex(),callback=f'{callback:06X}',
            behavior='score collection' if callback==0x9958 else 'extra life collection',score_value=value if callback==0x9958 else None,
            marker_count=sum(m['definition']==definition for m in markers)))
    if len(markers)!=53 or len(rows)!=7:raise ValueError('Unexpected pinned collectible roster')
    return dict(rom_sha256=ROM_HASH,scope='Immutable Level1 class06 behavior mapping; no complete runtime/1:1 claim.',operations=operations,definitions=rows,
        counts=dict(ranges=len(operations),definitions=len(rows),markers=len(markers),score_markers=sum(r['marker_count'] for r in rows if r['behavior']=='score collection'),
            extra_life_markers=sum(r['marker_count'] for r in rows if r['behavior']=='extra life collection')),complete_runtime_dispatch_domain=False)


def verify(project):
    if json.loads((project/'docs/stage9/level1-collectibles-contract.json').read_text())!=catalogue(project):raise ValueError('Stale Level1 collectible evidence')


if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];report=catalogue(project)
    (project/'docs/stage9/level1-collectibles-contract.json').write_text(json.dumps(report,indent=2)+'\n');print(report['counts'])
