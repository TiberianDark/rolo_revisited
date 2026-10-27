"""Audit original normal-frame and Level1 restart dependencies, static only."""
from pathlib import Path
import json,hashlib,csv
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text())
    routines={r['address']:r for r in inv['routines']}
    accepted={a for r in inv['routines'] for a in r['blocks']}
    operations=[]
    for start,end,name,contract in (
        (0x1d94,0x1e20,'Rolo death-level rebuild',
         '63FA fade first. ClearC432bit0040 andpublishdisplay control throughA6+4. Orderedservices2674,2684,523E,36BA,3E8A,3BF6,27DA,3478,3784,766A,3F34,7730,4CB8,684E,6864,7292,72A2,6960,6AA6,6750,29EE,FCD4,5324,54A0,66DE. SetC432bit0040,publishthroughA6+4,RTS. This is rebuild within current level context, NOT resetting a fresh Level1EnemySlice with hardcoded spawn/score/progress/lives. State/checkpoint/RAM writers andhardware equivalents mustbe bound.'),
        (0x1c6c,0x1cee,'Normal-level frame audit',
         'Original28-call order is authoritative. Native scene binds14 calls in a supported subset, notthecompleteframe. Current camera update4D54 precedes948A blink/FCD4 animation;2C4C precedes7292 streaming;9534 contact resolution followsstreaming. Unboundprefix,8C88,925C,graphics/HUD/background/queue phases remainrequired. Count is bindings, notmappedpercentage orfidelityproof.'),
    ):
        evidence=[];at=start
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted boundary {at:06X}')
            i=Decoder(rom,at).decode();evidence.append(dict(address=f'{at:06X}',bytes=rom[at:at+i['size']].hex(),mnemonic=i['mnemonic'],operands=i['operands']));at+=i['size']
        if at!=end:raise ValueError('Unaligned end')
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,contract=contract,instruction_evidence=evidence,
            range_sha256=hashlib.sha256(rom[start:end]).hexdigest(),pending='Complete caller/state initialization, checkpoint/score/progress retention, allnative service bindings and independentoriginal comparison remainpending.'))
    core=(project/'src/core/level1_enemy_slice.hpp').read_text()
    bindings={0x7748:'player_movement_phase',0x29ee:'rebuild_active_actor_list',0xa808:'update_actor_callbacks',
        0x785c:'player_collision_phase',0x6796:'record_player_frame_history',0x881c:'player_airborne_count',
        0x9196:'update_player_terrain_response',0x8838:'update_player_presentation',0x4d54:'update_camera',
        0x948a:'update_player_contact_blink',0xfcd4:'update_actor_animation_list',0x2c4c:'update_deferred_markers',
        0x7292:'update_foreground_terrain_camera',0x9534:'resolve_player_contact'}
    if not all(name+'(' in core for name in bindings.values()):raise ValueError('Scene binding missing')
    def calls(start,end,scene):
        rows=[]
        for c in inv['calls']:
            if not start<=c['address']<end:continue
            target=c['target'];r=routines.get(target,{})
            rows.append(dict(order=len(rows)+1,site=f'{c["address"]:06X}',target=f'{target:06X}',
                assessment=r.get('status','Entry not separately catalogued'),native_sources=r.get('native_sources',[]),
                scene_binding=bindings.get(target,'UNBOUND') if scene else 'REBUILD_SERVICE_NOT_BOUND',
                next='Bind complete original producer/consumer/state domains and compare original reference'))
        return rows
    normal=calls(0x1c6c,0x1cee,True);restart=calls(0x1d94,0x1e20,False)
    if len(normal)!=28 or len(restart)!=26:raise ValueError(f'Unexpected call counts {len(normal)}/{len(restart)}')
    return dict(rom_sha256=ROM_HASH,operations=operations,normal_frame=normal,restart_calls=restart,
        counts=dict(normal_calls=len(normal),bounded_scene_bindings=sum(r['scene_binding']!='UNBOUND' for r in normal),restart_calls=len(restart)),
        native_scope='Bounded normal-frame ordering corrected; actual1D94 restart remains unbound and currentdeath emits pause. Allpending services remainvisible.')

def verify(project):
    if json.loads((project/'docs/stage9/level-restart-contract.json').read_text())!=catalogue(project):raise ValueError('Stale restart/frame audit')

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];report=catalogue(project)
    (project/'docs/stage9/level-restart-contract.json').write_text(json.dumps(report,indent=2)+'\n')
    for name,rows in [('normal-frame-bindings',report['normal_frame']),('level-restart-dependencies',report['restart_calls'])]:
        with (project/f'docs/stage9/{name}.csv').open('w',newline='') as out:
            writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(report['counts'])
