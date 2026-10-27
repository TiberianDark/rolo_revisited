"""Batch existing Level1 candidate dependencies; no ROM execution or closure claim."""
from pathlib import Path
import collections
import csv
import hashlib
import json


def catalogue(project):
    directory=project/'docs/stage9'
    files={name:json.loads((directory/name).read_text()) for name in
           ('inventory.json','first-level-roster.json','research-worklist.json','routine-contract-links.json')}
    inv=files['inventory.json']; roster=files['first-level-roster.json']
    roots={0x1c6c,0x1d94,0x766a,0x3f34,0x7730,0x3784,0x14a4}
    for marker in roster['markers']:
        for key in ('handler','spawn_handler'):
            if isinstance(marker.get(key),int): roots.add(marker[key])
    graph=collections.defaultdict(set)
    for call in inv['calls']:
        targets=set(call.get('possible_targets',[]))
        if isinstance(call.get('target'),int): targets.add(call['target'])
        for owner in call.get('source_owners',[]): graph[owner].update(targets)
    def walk(root, boundaries=frozenset()):
        seen={root}; pending=collections.deque([root]); route={root:[root]}
        while pending:
            owner=pending.popleft()
            if owner in boundaries: continue
            for target in sorted(graph[owner]):
                if target not in seen:
                    seen.add(target); route[target]=route[owner]+[target]; pending.append(target)
        return seen,route
    root_domains={root:walk(root)[0] for root in roots}
    bounded_domains={root:walk(root,{0x200})[0] for root in roots}
    reached=set(roots); queue=collections.deque(sorted(roots)); paths={r:[r] for r in roots}
    while queue:
        owner=queue.popleft()
        for target in sorted(graph[owner]):
            if target not in reached:
                reached.add(target); paths[target]=paths[owner]+[target]; queue.append(target)
    tasks=[]
    for task in files['research-worklist.json']['tasks']:
        # Discovery paths contain shared ancestor roots; intersecting every
        # ancestor wrongly labels unrelated routines as Level1 dependencies.
        candidates={task['address']}
        if task['kind']=='control-flow boundary' and task.get('candidate_path'):
            candidates.add(task['candidate_path'][-1])
        owners=sorted(candidates&reached)
        if owners:
            tasks.append(dict(task,batch='control-flow' if task['kind']=='control-flow boundary' else 'routine assessment',
                candidate_level1_owners=owners,root_path=paths[owners[0]],
                candidate_roots=sorted(root for root in roots if candidates&root_domains[root]),
                roots_without_boot_expansion=sorted(root for root in roots if candidates&bounded_domains[root])))
    groups=[]
    for root in sorted(roots):
        related=[t for t in tasks if root in t['candidate_roots']]
        bounded=[t for t in related if root in t['roots_without_boot_expansion']]
        kind=('shared interrupt' if root==0x14a4 else 'normal frame' if root==0x1c6c else
              'restart' if root==0x1d94 else 'startup' if root in (0x766a,0x3f34,0x7730,0x3784) else 'roster handler')
        groups.append(dict(root=root,kind=kind,candidate_addresses=len(root_domains[root]),unknown_tasks=len(related),
            unknown_tasks_without_boot_expansion=len(bounded),task_ids=[t['id'] for t in related],
            bounded_task_ids=[t['id'] for t in bounded],
            scope='Boundary0200 is a scheduling partition only. Boot/failure dependencies remain in the full batch; their exclusion from normal behavior is not proven.'))
    links=[link for link in files['routine-contract-links.json'] if int(link['address'],16) in reached]
    return dict(scope='Conservative candidate call dependency batch from Level1 roster, normal frame, restart and shared interrupt roots. Not complete Level1 reachability: branch-only successors, mutations, generated definitions, animation spawns and unproved indirect targets remain required. Outside this batch does not mean absent from Level1.',
        inputs={name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in files},
        roots=sorted(roots),candidate_addresses=sorted(reached),tasks=tasks,partial_contract_links=links,root_groups=groups,
        counts=dict(roots=len(roots),candidate_addresses=len(reached),unknown_tasks=len(tasks),
            indirect_or_boundary_tasks=sum(t['batch']=='control-flow' for t in tasks),
            unassessed_routines=sum(t['batch']=='routine assessment' for t in tasks),partial_contract_links=len(links)),
        boot_expansion_boundary=0x200,complete_level1_closure=False,fully_mapped=False)


def verify(project):
    report=catalogue(project)
    if json.loads((project/'docs/stage9/level1-batch.json').read_text())!=report:
        raise ValueError('Stale Level1 batch dependency report')
    with (project/'docs/stage9/level1-batch.csv').open(newline='') as f: rows=list(csv.DictReader(f))
    expected=[{k:str(t[k]) for k in rows[0]} for t in report['tasks']] if rows else []
    if rows!=expected: raise ValueError('Stale Level1 batch CSV')


if __name__=='__main__':
    project=Path(__file__).resolve().parents[1]; report=catalogue(project); directory=project/'docs/stage9'
    (directory/'level1-batch.json').write_text(json.dumps(report,indent=2)+'\n')
    with (directory/'level1-batch.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=('id','batch','address','priority','status','candidate_roots','roots_without_boot_expansion','root_path','next','acceptance'))
        writer.writeheader()
        writer.writerows({k:t[k] for k in writer.fieldnames} for t in report['tasks'])
    print(report['counts'])
