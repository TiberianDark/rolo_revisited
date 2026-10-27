"""Attach verified bounded frame contracts to existing routine candidates only."""
import json
from pathlib import Path


def link(project):
    directory=project/'docs/stage9'
    report=json.loads((directory/'player-frame-history-contract.json').read_text())
    inventory=json.loads((directory/'inventory.json').read_text())
    candidates={r['address'] for r in inventory['routines']}
    target=directory/'routine-contract-links.json'
    links=json.loads(target.read_text())
    links=[r for r in links if r.get('generated_by')!='link_player_frame_contracts.py']
    added=[]
    native={0x1c6c:['shared_player_frame.hpp','scheduled_player_frame.hpp'],0x2838:['player_trigger_pool.hpp'],
        0x2f3c:['palette_flash.hpp'],0x6796:['player_frame_history.hpp'],0x6960:['plane_scroll.hpp'],0x6aa6:['plane_scroll.hpp'],
        0x881c:['player_frame_history.hpp'],0x8c88:['player_post_motion.hpp'],0x9196:['player_terrain_response.hpp'],
        0x925c:['player_trigger_scan.hpp','player_trigger_pool.hpp'],0x92f2:['player_trigger_dispatch.hpp'],0xfcd4:['actor_animation_list.hpp','actor_animation.hpp']}
    native[0x4a48]=['actor_spawn_factory.hpp','level1_enemy_slice.hpp']
    for entry in (0x2ff6,0x3060,0x63fa,0x22a8,0x14a4):
        native[entry]=['palette_effect.hpp']
    placement=json.loads((directory/'spawn-placement-contract.json').read_text())
    operations=[('player-frame-history-contract.json',o) for o in report['operations']]
    operations.extend(('spawn-placement-contract.json',o) for o in placement['operations'])
    injury=json.loads((directory/'injury-score-contract.json').read_text())
    for operation in injury['operations']:
        native[int(operation['entry'],16)]=[Path(s).name for s in operation['native_sources']]
        operations.append(('injury-score-contract.json',operation))
    restart=json.loads((directory/'level-restart-contract.json').read_text())
    native[0x1c6c]=native[0x1c6c]+['level1_enemy_slice.hpp','camera.hpp']
    operations.extend(('level-restart-contract.json',o) for o in restart['operations'])
    startup=json.loads((directory/'player-startup-contract.json').read_text())
    operations.extend(('player-startup-contract.json',o) for o in startup['operations'])
    collectibles=json.loads((directory/'level1-collectibles-contract.json').read_text())
    operations.extend(('level1-collectibles-contract.json',o) for o in collectibles['operations'])
    companion=json.loads((directory/'level1-companion-contract.json').read_text())
    operations.extend(('level1-companion-contract.json',o) for o in companion['operations'])
    enemy_dependencies=json.loads((directory/'level1-enemy-dependencies-contract.json').read_text())
    operations.extend(('level1-enemy-dependencies-contract.json',o) for o in enemy_dependencies['operations'])
    for source_path,operation in operations:
        address=int(operation['entry'],16)
        if address not in candidates:continue
        if not operation['instruction_evidence']:raise ValueError('No pinned instruction evidence')
        row={'address':f'{address:04X}','name':operation['name'],
             'path':source_path,
             'scope':operation['contract']+' Pending: '+operation['pending'],
             'status':'Bounded static contract assessed; linked native bindings remain partial and runtime/original-reference fidelity pending',
             'generated_by':'link_player_frame_contracts.py'}
        row['native_sources']=['src/core/'+name for name in native.get(address,[])]
        if not all((project/source).is_file() for source in row['native_sources']):raise ValueError('Missing native source')
        added.append(row)
    links.extend(added)
    target.write_text(json.dumps(links,indent=2)+'\n',encoding='utf-8')
    print(f'{len(added)} verified local contracts linked to existing candidates; no new roots or complete-fidelity statuses')


if __name__=='__main__':link(Path(__file__).resolve().parents[1])
