"""Pinned local player presentation evidence and candidate offset lookup rows."""
import hashlib
import json
from pathlib import Path
from m68k_static import Decoder
from inventory_rom import ROM_HASH

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    operations=[]
    for start,end in ((0x8838,0x8934),(0x8934,0x8a0c),(0xefa8,0xf046),
                      (0x237c,0x244e),(0x79be,0x7a66),(0x7748,0x785c),
                      (0x785c,0x78b8),(0x78b8,0x79be),(0x8100,0x8116),(0x8116,0x8202),(0x8202,0x827a),
                      (0x7d3a,0x7dc6),(0x7dc6,0x7e58),(0x78e4,0x79be),
                      (0x7a66,0x7ad8),(0x7ad8,0x7b74),(0x7b74,0x7c74),(0x8c24,0x8c88),
                      (0x827a,0x8376),(0x85e8,0x8680),(0x87dc,0x8810),
                      (0x8376,0x842e),(0x86d6,0x8728),(0x87bc,0x87dc),
                      (0x842e,0x8482),(0x8482,0x84f4),(0x84f4,0x85e8)):
        cursor=start;instructions=[]
        while cursor<end:
            i=Decoder(rom,cursor).decode();instructions.append(i);cursor+=i['size']
        if cursor!=end:raise ValueError('Instruction boundary mismatch')
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',instructions=instructions))
    selectors=(0,4,8,12,16,20,24,32,36,52,56,60,64,68,72,88)
    rows=[]
    for selector in selectors:
        a=0x1045c+selector;b=0xdb16+selector//2
        rows.append(dict(selector=selector,head_offset_address=f'{a:06X}',
            head_offset_long=int.from_bytes(rom[a:a+4],'big'),
            alternate_x_address=f'{b:06X}',alternate_x_word=int.from_bytes(rom[b:b+2],'big')))
    report=dict(rom_sha256=ROM_HASH,operations=operations,candidate_selector_rows=rows,
        table_scope='Observed local selector outputs plus presentation overrides. Rows are raw indexed reads, not proof of table boundaries, every reached selector, or applicability to all callers.',
        alternate_context='EFA8 acts on incoming A5, not on the controlled or base actor by default. Caller8838 never assigns A5; its provenance from the surrounding frame is required before native binding.',
        native_sources={'00237C':'src/core/player_input.hpp','0079BE':'src/core/player_jump.hpp',
            '008838':'src/core/player_presentation.hpp','008934':'src/core/player_selector.hpp',
            '00EFA8':'src/core/alternate_presentation.hpp','00785C':'src/core/player_collision_phase.hpp',
            '008100':'src/core/player_forces.hpp','008116':'src/core/player_forces.hpp',
            '008202':'src/core/player_position.hpp','007D3A':'src/core/player_acceleration.hpp',
            '007DC6':'src/core/player_acceleration.hpp','0078E4':'src/core/player_direction_input.hpp',
            '007AD8':'src/core/rolo_action.hpp','007748':'src/core/player_movement_phase.hpp',
            '007B74':'src/core/held_object_release.hpp','008C24':'src/core/player_slope_impact.hpp',
            '0078B8':'src/core/player_input_phase.hpp','007A66':'src/core/player_input_phase.hpp',
            '00827A':'src/core/player_side_collision.hpp','0085E8':'src/core/player_side_collision.hpp',
            '0087DC':'src/core/player_side_collision.hpp','008376':'src/core/player_ceiling_collision.hpp',
            '0086D6':'src/core/player_ceiling_collision.hpp','0087BC':'src/core/player_ceiling_collision.hpp',
            '00842E':'src/core/player_collision_followups.hpp','008482':'src/core/player_collision_followups.hpp',
            '0084F4':'src/core/player_floor_collision.hpp'},
        input_context='78B8 assigns A1=C480 before calling79BE. With this caller mappedA1byte6 and absoluteC486 are the same byte. DE68 is another accepted caller. Input producer237C mapsFF fresh/FE held in original overwrite order; polling/replay/remap domains remain pending.',
        movement_order='7748 snapshots positions20/24 and clears acceleration46 before settingC514 fromC513/C510. C524 can skip all movement; C519 selects a separate damage path. Normal path7B74,8100,8C24,78B8; actor125.3 then gates7D3A,7DC6,8116,8202 and C515 direction capture. Collision phase785C is separate and gated byC524/F2BC/actor124.5/125.3. Native preview does not implement all these gates.',
        pending=['Incoming A5 ownership at8838/EFA8 and all callers',
            'F280 gate producer and F2D8 word-root consumers',
            'Full selector domains for1045C andDB16 reads',
            'C511/C512 timer lifecycle and independent original comparisons',
            'Companion action7C74/7CA8 native services and their actor mutations',
            'Bind input phase globals to one shared world without independent snapshots'],
        complete_mapping=False,world_integrated=False)
    for source in report['native_sources'].values():
        if not (project/source).is_file():raise ValueError('Missing native player source '+source)
    return report

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1]
    report=catalogue(project)
    (project/'docs/stage9/player-presentation-contract.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print({'ranges':len(report['operations']),'candidate_rows':len(report['candidate_selector_rows'])})
