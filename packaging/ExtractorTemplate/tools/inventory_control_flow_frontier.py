"""Join unique uncertain sites with owners, contracts and feature dependency frontiers."""
import csv
import hashlib
import json
from pathlib import Path
from inventory_rom import ROM_HASH

DIRECT = {'direct encoded target', 'accepted non-call control-flow transfer between entry candidates'}

def catalogue(project):
    docs = project / 'docs/stage9'
    inv = json.loads((docs / 'inventory.json').read_text())
    if inv['rom_sha256'] != ROM_HASH or hashlib.sha256((project / 'local/rolo.md').read_bytes()).hexdigest() != ROM_HASH:
        raise ValueError('ROM mismatch')
    routines = {r['address']: r for r in inv['routines']}
    owners = {}
    for entry, routine in routines.items():
        for address in routine['blocks']:
            owners.setdefault(address, set()).add(entry)
    level1 = json.loads((docs / 'level1-current-candidates.json').read_text())
    level1_entries = set(level1['candidate_addresses'])
    table = next(t for t in inv['dispatch_tables'] if t['dispatch']==0xBE56)
    roots = {0xBE4E} | {slot['target'] for slot in table['slots']}
    def closure(allow_candidates):
        visited = set()
        pending = list(roots)
        while pending:
            entry = pending.pop()
            if entry in visited:
                continue
            visited.add(entry)
            for edge in routines.get(entry, {}).get('dependency_edges', []):
                if allow_candidates or edge['evidence'] in DIRECT:
                    pending.append(edge['target'])
        return visited
    direct = closure(False)
    possible = closure(True)
    grouped = {}
    for stop in inv['unresolved']:
        grouped.setdefault(stop['address'], []).append(stop)
    calls = {call['address']: call for call in inv['calls']}
    tables = {table['dispatch']: table for table in inv['dispatch_tables']}
    rows = []
    for address, stops in sorted(grouped.items()):
        own = owners.get(address, set())
        call = calls.get(address, {})
        context = next((c for c in inv['indirect_contexts'] if f'{address:04X}' in c['sites']), None)
        targets = set(call.get('possible_targets', []))
        if address in tables:
            targets.update(slot['target'] for slot in tables[address]['slots'])
        if context:
            targets.update(int(target,16) for target in context['targets'])
        kind = 'indexed selector' if address in tables else 'caller continuation' if context else 'callback/state provenance' if 'indirect' in stops[0]['reason'].lower() else 'special excluded/relocated site'
        rows.append(dict(address=address, hex=f'{address:04X}', kind=kind,
                         reasons=sorted({stop['reason'] for stop in stops}),
                         owners=[f'{entry:04X}' for entry in sorted(own)],
                         subsystems=sorted({routines[entry]['subsystem'] for entry in own}),
                         candidate_targets=[f'{target:04X}' for target in sorted(targets)],
                         level1_candidate=bool(own & level1_entries),
                         macro_direct_frontier=bool(own & direct), macro_candidate_frontier=bool(own & possible),
                         evidence=sorted({stop['assessment'] for stop in stops}),
                         contract_artifacts=sorted({link['path'] for stop in stops for link in stop.get('contract_links',[])}),
                         next='Close selector producers and overlapping mutations.' if address in tables else
                              'Close caller register/stack preservation and incoming contexts.' if context else
                              'Close target provenance, aliases and live identity.' if 'indirect' in stops[0]['reason'].lower() else
                              'Maintain separate disposition for excluded data or relocated/self-modified code.'))
    return dict(rom_sha256=ROM_HASH, sites=rows,
                counts=dict(unique_sites=len(rows), raw_stops=len(inv['unresolved']),
                            level1_candidate_sites=sum(row['level1_candidate'] for row in rows),
                            macro_direct_frontier_sites=sum(row['macro_direct_frontier'] for row in rows),
                            macro_candidate_frontier_sites=sum(row['macro_candidate_frontier'] for row in rows),
                            macro_direct_entries=len(direct), macro_candidate_entries=len(possible)),
                scope='Graph dependency frontiers, not execution proof. Candidate closure can expand through uncertain callbacks into unrelated features; direct closure excludes them and cannot establish whole-feature safety.')

if __name__ == '__main__':
    project = Path(__file__).resolve().parents[1]
    report = catalogue(project)
    docs = project / 'docs/stage9'
    (docs / 'control-flow-frontier.json').write_text(json.dumps(report,indent=2)+'\n')
    fields=['hex','kind','level1_candidate','macro_direct_frontier','macro_candidate_frontier','owners','candidate_targets','contract_artifacts','next']
    with (docs / 'control-flow-frontier.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for row in report['sites']:
            writer.writerow({key:'; '.join(row[key]) if isinstance(row[key],list) else row[key] for key in fields})
    print(json.dumps(report['counts']))
