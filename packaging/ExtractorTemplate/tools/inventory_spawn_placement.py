"""Pin marker-to-allocator coordinates and facing; no instruction execution."""
from pathlib import Path
import hashlib,json,csv
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    inventory=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted={a for routine in inventory['routines'] for a in routine['blocks']}
    operations=[]
    for start,end,name,contract in (
        (0x442a,0x443a,'Initial special-descriptor redirect','Unsigned type>=0400 redirects463C before X-shift, macro-width lookup and right-window clip. D3 is raw recordX and D6 is the doubled MAP row index.'),
        (0x446c,0x4476,'Incremental special-descriptor redirect','Unsigned type>=0400 redirects463C before normal macro setup. D3 rawX and D6 doubled MAP row index reach4A48 unmodified.'),
        (0x4a48,0x4a84,'Native table/facing/coordinate allocator handoff','Clear D0bit0, SNE produces oddFF/even00, double word D0 and signed-index definition pointer table. X=(rawX+8) wrappedword; Y=((rowByteIndex+2)<<3)+1 wrappedword; SWAP zero-extended coordinates gives16.16 zero fractions. Facing oddbit XOR nonnegative sign of wrapped(controlledX-spawnX), masked08. D1 source marker passes to28B0. Native actor_spawn_factory_request preserves these arithmetic steps for explicitly checked table domains.'),
        (0x3784,0x382a,'Foreground marker storage identity','Normal nonnegative level selector installs foreground MAP atFFFFCC44 and background MAP atFFFFDC44 before decode/copy. Selector0 background takesA558; this report uses selector1. Actor marker handles therefore identify mutable decoded MAP records, not ROM source pointers.'),
    ):
        evidence=[];address=start
        while address<end:
            if address not in accepted:raise ValueError(f'Unaccepted boundary {address:06X}')
            instruction=Decoder(rom,address).decode();size=instruction['size']
            evidence.append(dict(address=f'{address:06X}',bytes=rom[address:address+size].hex(),mnemonic=instruction['mnemonic'],operands=instruction['operands']))
            address+=size
        if address!=end:raise ValueError('Range does not end on instruction boundary')
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,contract=contract,
            instruction_evidence=evidence,range_sha256=hashlib.sha256(rom[start:end]).hexdigest(),
            pending='All runtime selector domains, original full caller scheduling, mutated markers, allocator failure and lifetime/reference comparisons remain unverified.'))
    roster=json.loads((project/'docs/stage9/first-level-roster.json').read_text())
    rows=[]
    # Roster JSON groups markers by semantic class; flatten only dictionaries
    # with original MAP coordinates/offset. Do not infer objects from visual records.
    def visit(value):
        if isinstance(value,dict):
            if all(key in value for key in ('record_offset','x','y','format','definition')) and value['format'] in ('paired','direct'):
                x=(value['x']+8)&65535;y=(value['y']+17)&65535
                rows.append(dict(record_offset=value['record_offset'],marker_identity=f'{0xffffcc44+value["record_offset"]:08X}',
                    category=value['category'],parameter=value['parameter'],definition=f'{value["definition"]:06X}',
                    raw_x=value['x'],raw_y=value['y'],spawn_x=x,spawn_y=y,
                    odd_facing_bit=(value['parameter']&1) if value['format']=='paired' else 0,
                    facing_contract='odd XOR nonnegative wrapped(controlledX-spawnX), then mask08',
                    scope='Derived table handoff only; class-specific activation/progress gates not established'))
                return
            for child in value.values():visit(child)
        elif isinstance(value,list):
            for child in value:visit(child)
    visit(roster)
    unique={r['record_offset']:r for r in rows};rows=[unique[k] for k in sorted(unique)]
    return dict(rom_sha256=ROM_HASH,operations=operations,level1_table_markers=rows,
        native_sources=['src/core/actor_spawn_factory.hpp','src/core/level1_enemy_slice.hpp'],
        scope='Static marker arithmetic and bounded native first-family binding. Not all level spawns, respawn/lifetime, gameplay completion or independent1:1 verification.')

def verify(project):
    expected=catalogue(project)
    if json.loads((project/'docs/stage9/spawn-placement-contract.json').read_text())!=expected:raise ValueError('Stale spawn placement evidence')

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];report=catalogue(project)
    (project/'docs/stage9/spawn-placement-contract.json').write_text(json.dumps(report,indent=2)+'\n')
    rows=report['level1_table_markers']
    with (project/'docs/stage9/level1-spawn-placements.csv').open('w',newline='') as output:
        writer=csv.DictWriter(output,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print({'pinned_ranges':len(report['operations']),'level1_table_markers':len(rows)})
