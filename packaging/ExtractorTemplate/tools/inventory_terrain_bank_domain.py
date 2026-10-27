"""All80 descriptor MAP bank bytes and explicit live bank producer; data only."""
import hashlib,json,collections
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from inventory_ram_schema import accesses
from rolo_maps import long,parse_map
from rolo_codec import decode_backward_lz

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted=sorted({a for r in inv['routines'] for a in r['blocks']})
    maps=[]
    for selector in range(80):
        packed=long(rom,0x4ab1a+selector*8);source=packed&0xffffff
        data=rom[source:source+4096] if rom[source:source+3]==b'MAP' else decode_backward_lz(rom,source)[0]
        layout=parse_map(data)
        if not 0<=layout['bank']<=7:raise ValueError('Canonical map bank domain changed')
        maps.append(dict(selector=selector,source=source,bank=layout['bank'],decoded_bytes=len(data),decoded_sha256=hashlib.sha256(data).hexdigest(),width=layout['width'],height=layout['height'],record_count=len(layout['records'])))
    refs=[row for a in accepted for row in accesses(Decoder(rom,a).decode()) if row['width'] is not None and row['address']<=0xfff2f8<row['address']+row['width']]
    if 0x3754 not in accepted:raise ValueError('Map bank producer boundary')
    producer=Decoder(rom,0x3754).decode()
    if producer['operands']!='(+3,A2),($FFFFF2F8).L':raise ValueError('Producer source changed')
    operations=[]
    for start,end,name,contract in (
        (0x36ba,0x3784,'Initialize planes and publish MAP header fields','A0F30Aforeground/A1F336background;initializegeometry/ringfields;call3784thenreloadforegroundA2=A0.long34,copyBYTE3toF2F8 anddimensions4/6toA0.words38/40;backgrounddimensionsfromA1.long34;clearF362LONG,call4018. Negative3784returnretainspriorheaderpointers, notnewloads.'),
        (0x3784,0x384a,'Publish and load foreground/background MAP headers','A2/A3saveplanes;F2F6negativeRTSwithoutpointerloads. NonnegativeoffsetWORDselector*8 into4AB1A, optionalF26Cbyteupdate;masksource24bits,foregrounddestinationCC44,publishplane34beforeload. Saveoffset/PEA37E8, rawMAPcopy1024LONGsorA75Asemanticdecoder. Backgroundsource/flagdescriptor+4,DC44publishbeforeload;selector0usesA558,othersraw512LONGsorA75A. RestoreplaneA0/A1at3826. No80descriptorupperbound, noresourceallocationendguard.'),
    ):
        at=start;instructions=[]
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted loader boundary{at:X}')
            instruction=Decoder(rom,at).decode();instructions.append(instruction);at+=instruction['size']
        if at!=end:raise ValueError('Loader extent')
        operations.append(dict(entry=f'{start:X}',end_exclusive=f'{end:X}',name=name,contract=contract,instruction_evidence=instructions,pending='Allselector/negativeentry/register/codec handoff/planealias domains and native/reference loading remain open.'))
    jigsaw_path=project/'docs/stage9/world-jigsaw-contract.json'
    jigsaw=json.loads(jigsaw_path.read_text())
    joined=[op for op in jigsaw['operations'] if op['entry'] in ('A558','A57A','A6C0','A720','A744')]
    if len(joined)!=5:raise ValueError('World background source contracts')
    native_paths=['src/core/world_map.hpp','src/core/world_map_raster.hpp']
    return dict(rom_sha256=ROM_HASH,scope='All80 immutable foreground MAP descriptor bank bytes and live plane-header loading; conditional original loaded-map domain, not allruntime/alias closure.',operations=operations,maps=maps,max_foreground_decoded_bytes=max(m['decoded_bytes'] for m in maps),bank_counts=dict(sorted(collections.Counter(str(m['bank']) for m in maps).items())),canonical_banks=list(range(8)),producer_evidence=[Decoder(rom,a).decode() for a in(0x3750,0x3754)],explicit_overlapping_accesses=refs,
        special_world_background=dict(loader_call=Decoder(rom,0x382c).decode(),original_contract_source='world-jigsaw-contract.json',original_contract_sha256=hashlib.sha256(jigsaw_path.read_bytes()).hexdigest(),joined_operations=[dict(entry=op['entry'],name=op['name'],contract=op['contract'],pending=op['pending']) for op in joined],native_source_sha256={p:hashlib.sha256((project/p).read_bytes()).hexdigest() for p in native_paths},scope='Selector0 synthesizesbackgroundratherthandecodingordinarydescriptor source. A558copiesforegroundfirst8headerbytesCC44→DC44,builds/patchesstructure andpreserves15D/Aregisters; thenloader3826restoresplaneA0/A1. Existingnativehelpers listedasbindings, notnewimplementationorfullfidelityproof.'),
        metadata_sources=[dict(bank=b,pointer=long(rom,0x4aff6+b*4)) for b in range(8)],
        conclusion='On originaldescriptor0..79foregroundheaderproducer, F2F8bank0..7 selects onlyfirst8collisionpointerrows. Investigatedrows8..16pointing787F6 are not reachedbythisboundeddata path.',
        remaining=['ProveplaneA0+34headeridentity/loaderpublication andeveryreachable selector beforeglobalcallerclosure.','Register/indexed/bulk aliases andexternal MAP mutation remain separate.','Metadata buffer/ROMrecordextents andactual tileIDdomains cannotbe inferredfrombankcountalone.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1];r=catalogue(p)
    (p/'docs/stage9/terrain-bank-domain-contract.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(maps=len(r['maps']),banks=r['bank_counts'])))
