"""Authored contract-to-subsystem grouping; labels never imply completion."""
import json
from pathlib import Path
GROUPS={
 'player collision bindings':['player-collision-binding-contract.json'],
 'ending scenes and state transitions':['ending-sequence-contract.json','scripted-player-exit-contract.json'],
 'startup and shared memory':['startup-ram-clear-contract.json','bulk-write-evidence.json','relocated-operation-contract.json'],
 'input and random state':['input-contract.json','rng-contract.json'],
 'actor lifecycle and scheduling':['object-lifecycle.json','actor-scheduler-contract.json','callback-mutation-contract.json'],
 'player movement and contact':['player-selector-contract.json','ceiling-contact-contract.json','shared-motion-contract.json','actor-contact-contract.json','replacement-height-contract.json','player-presentation-contract.json','player-frame-history-contract.json','player-startup-contract.json'],
 'terrain and spawning':['marker-search-contract.json','macro-rider-contract.json','macro-factory-contract.json','map-descriptor-contract.json','spawn-factory-contract.json','spawn-placement-contract.json','terrain-bank-domain-contract.json'],
 'triggers and shared responses':['trigger-action-contract.json','shared-response-contract.json'],
 'campaign and world map':['world-jigsaw-contract.json','progress-selector-domains.json','world-control-contract.json','world-selection-contract.json','world-pause-actor-contract.json','campaign-statistics-contract.json'],
 'state transitions and resources':['frame-transition-contract.json','level-entry-services-contract.json','level-entry-storage-reset-contract.json','entry-marker-callback-contract.json','loader-storage-display-reset-contract.json','level-restart-contract.json'],
 'companions and menus':['menu-selector-domain.json','level1-companion-contract.json'],
 'enemies and collectibles':['first-enemy-contract.json','level1-collectibles-contract.json','level1-enemy-dependencies-contract.json','injury-score-contract.json','connected-actor-callback-contract.json','spawned-actor-callback-contract.json'],
 'interrupts and palette':['interrupt-palette-clock-contract.json','transport-fade-companion-contract.json','palette-resource-contract.json'],
 'transporters':['level1-transport-contract.json'],
 'sprite ordering and publication':['sprite-frame-contract.json','sprite-list-tail-contract.json','sprite-origin-reserved-contract.json','sorter-installation-contract.json','live-sorter-word-contract.json'],
 'camera and scroll':['scroll-mode-producer-contract.json','level-selector-writer-contract.json'],
 'terrain streaming':['terrain-streaming-contract.json'],
 'graphics transfer publication':['word-transfer-queue-contract.json'],
 'text and tile presentation':['display-utility-contract.json','scrolling-text-contract.json','text-control-contract.json'],
}
CONTRACT_SUBSYSTEM={path:group for group,paths in GROUPS.items() for path in paths}

def catalogue(project):
    inv=json.loads((project/'docs/stage9/inventory.json').read_text())
    rows=[]
    for group,paths in GROUPS.items():
        routines=[r for r in inv['routines'] if any(c['path'] in paths for c in r['contract_links'])]
        addresses={r['address'] for r in routines}
        deps=sorted({a for r in routines for a in r.get('possible_dependencies',[]) if a not in addresses})
        rows.append(dict(name=group,sources=paths,routines=[dict(address=r['hex'],status=r['status'],evidence_sources=sorted({c['path'] for c in r['contract_links'] if c['path'] in paths}),native_sources=r['native_sources']) for r in routines],candidate_dependencies=deps,
            scope='Authored source grouping; dependencies are observed/candidate edges, not all reachable-domain proof.',complete=False))
    uncovered=[dict(address=r['hex'],status=r['status'],subsystem=r['subsystem']) for r in inv['routines'] if not any(c['path'] in CONTRACT_SUBSYSTEM for c in r['contract_links'])]
    unknown_paths=sorted({c['path'] for r in inv['routines'] for c in r['contract_links']} - CONTRACT_SUBSYSTEM.keys())
    if unknown_paths:raise ValueError('New contract sources need authored subsystem assignment: '+str(unknown_paths))
    return dict(rom_sha256=inv['rom_sha256'],scope='Subsystem inventory joins authored contracts, native sources and candidate dependencies. A routine can appear in multiple groups; counts must not be summed as unique completion.',groups=rows,without_authored_contract_group=uncovered,
        counts=dict(groups=len(rows),unique_candidates_with_contract_group=len(inv['routines'])-len(uncovered),candidates_without_contract_group=len(uncovered),fully_complete_groups=0))

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1];r=catalogue(p)
    (p/'docs/stage9/subsystem-inventory.json').write_text(json.dumps(r,indent=2)+'\n')
    lines=['# Evidence-backed subsystem inventory','',r['scope'],'','| Group | Routine candidates | Candidate external dependencies |','|---|---:|---:|']
    lines += [f'| {g["name"]} | {len(g["routines"])} | {len(g["candidate_dependencies"])} |' for g in r['groups']]
    lines += ['','See subsystem-inventory.json for addresses, exact evidence sources, native source links and dependency identities. Ungrouped candidates remain explicit. No subsystem is marked complete.']
    (p/'docs/stage9/SUBSYSTEM-INVENTORY.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(r['counts']))
