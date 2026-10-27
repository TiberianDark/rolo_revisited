"""Turn static gaps into an ordered research worklist; no coverage percentage."""
import argparse
import csv
import json
from collections import deque
from pathlib import Path

def candidate_paths(routines,roots):
    graph={r['address']:r['possible_dependencies'] for r in routines}
    paths={root:[root] for root in sorted(roots)};queue=deque(paths)
    while queue:
        address=queue.popleft()
        for target in sorted(graph.get(address,[])):
            if target in paths:continue
            paths[target]=paths[address]+[target];queue.append(target)
    return paths

def catalogue(inv,states):
    frame=candidate_paths(inv['routines'],[states['normal_frame']['entry']])
    all_states=candidate_paths(inv['routines'],[state['address'] for state in states['states']])
    tasks=[];stops={}
    for stop in inv['unresolved']:
        row=stops.setdefault(stop['address'],dict(address=stop['address'],reasons=set(),assessments=set()))
        row['reasons'].add(stop['reason']);row['assessments'].add(stop['assessment'])
    for row in stops.values():
        address=row['address'];owners=[r['address'] for r in inv['routines'] if address in r['blocks']]
        candidates=[frame[owner] for owner in owners if owner in frame]
        path=min(candidates,key=lambda p:(len(p),p)) if candidates else []
        tasks.append(dict(id='stop-%06X'%address,priority=0,kind='control-flow boundary',address=address,
            status='unresolved control-flow evidence',candidate_path=path,
            contract_links=[link for routine in inv['routines'] if routine['address'] in owners for link in routine.get('contract_links',[])],
            evidence='; '.join(sorted(row['reasons'])),
            next='; '.join(sorted(row['assessments'])),
            acceptance='Establish caller context, target domain and selector/alias bounds from ROM; preserve uncertainty for unproved paths.'))
    for routine in inv['routines']:
        if routine['status']!='unassessed':continue
        address=routine['address'];priority=1 if address in frame else 2 if address in all_states else 3
        path=frame.get(address,all_states.get(address,[]))
        tasks.append(dict(id='routine-%06X'%address,priority=priority,kind='unassessed entry candidate',address=address,
            status=routine['status'],candidate_path=path,
            contract_links=routine.get('contract_links',[]),
            evidence='; '.join(routine['evidence']),
            next=('Continue scoped contracts: '+ '; '.join(link['scope'] for link in routine['contract_links']) if routine.get('contract_links') else
                  'Determine purpose, entry conditions, field widths, register/flag dependencies, side effects and return contract; distinguish shared branches from independent routines.'),
            acceptance='Add consuming-code evidence and scoped native coverage status; original-reference traces are required before claiming behavior fidelity.'))
    tasks.sort(key=lambda task:(task['priority'],len(task['candidate_path']) or 999,task['address']))
    return dict(rom_sha256=inv['rom_sha256'],tasks=tasks,
        priority_rules={'0':'All unresolved control-flow sites',
            '1':'Unassessed candidate linked to normal frame through direct/candidate dependency edges',
            '2':'Unassessed candidate linked to another observed main state',
            '3':'Other unassessed candidates'},
        counts=dict(control_flow_sites=len(stops),unassessed_entry_candidates=sum(t['kind']=='unassessed entry candidate' for t in tasks),
            tasks=len(tasks),priority_counts={str(p):sum(t['priority']==p for t in tasks) for p in range(4)}),
        scope='Planning order only. Dependency paths include candidate indirect targets, not proof of execution. One task per entry candidate does not imply one distinct gameplay routine. This is not an exhaustive list of all future porting tasks.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    out=args.project/'docs/stage9'
    inv=json.loads((out/'inventory.json').read_text(encoding='utf-8'))
    states=json.loads((out/'state-inventory.json').read_text(encoding='utf-8'))
    report=catalogue(inv,states)
    (out/'research-worklist.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with (out/'research-worklist.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(report['tasks'][0]));writer.writeheader();writer.writerows(report['tasks'])
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
