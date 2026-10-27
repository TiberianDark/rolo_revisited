"""Link definition handlers to calls, fields, marker records and animation evidence."""
import argparse
import json
from collections import Counter,defaultdict
from pathlib import Path
from inventory_macro_handlers import actor_accesses

def catalogue(inv,spawns,animations):
    revisions={report['rom_sha256'] for report in (inv,spawns,animations)}
    if len(revisions)!=1:raise ValueError('Actor evidence revisions differ')
    by_handler=defaultdict(list);cases={case['definition']:case for case in animations['cases']}
    routines={routine['address']:routine for routine in inv['routines']}
    marker_counts=Counter(marker.get('definition') for marker in spawns['markers'] if 'definition' in marker)
    layouts=defaultdict(set)
    for marker in spawns['markers']:
        if 'definition' in marker:layouts[marker['definition']].add(marker['layout_source'])
    definition_rows=[]
    for definition in inv['object_definitions']:
        address=definition['address'];handler=definition['handler'];by_handler[handler].append(address)
        forwarded=definition['field_22']&0xffffff if handler==0xb702 else None
        definition_rows.append(dict(address=address,initial_handler=handler,
            linked_definition=definition['linked'],forwarded_callback=forwarded,
            default_animation_case=cases.get(address),
            observed_definition_marker_records=marker_counts[address],
            observed_layout_sources=sorted(layouts[address]),
            secondary_definition=definition['secondary_definition'],secondary_selector=definition['secondary_selector'],
            scope='Initial static definition contract; linked allocation, callback overrides, animation spawns and activation paths must be integrated separately'))
    handlers=[]
    for handler,definitions in sorted(by_handler.items()):
        routine=routines.get(handler);blocks=set(routine['blocks']) if routine else set()
        calls=[call for call in inv['calls'] if handler in call['source_owners']]
        fields=[reference for reference in inv['object_field_references'] if reference['address'] in blocks]
        unique_instructions={reference['address']:reference for reference in fields}
        typed_fields=[access for site,reference in sorted(unique_instructions.items()) for access in actor_accesses(reference)]
        handlers.append(dict(address=handler,definitions=definitions,
            status=routine['status'] if routine else 'entry not accepted',
            note=routine['note'] if routine else '',local_calls=calls,
            syntactic_a5_field_references=fields,field_access_candidates=typed_fields,
            possible_dependencies=routine['possible_dependencies'] if routine else [],
            observed_services=routine['observed_services'] if routine else [],
            observed_definition_marker_records=sum(marker_counts[address] for address in definitions),
            scope='Owned instruction candidate region only; branch continuations and shared helpers are separate. Calls and A5 references do not establish complete AI or object identity.'))
    return dict(rom_sha256=inv['rom_sha256'],handlers=handlers,definitions=definition_rows,
        counts=dict(initial_definition_handlers=len(handlers),definitions=len(definition_rows),
            typed_field_access_candidates=sum(len(row['field_access_candidates']) for row in handlers),
            definitions_with_observed_marker_lookups=sum(row['observed_definition_marker_records']>0 for row in definition_rows),
            forwarded_callback_definitions=sum(row['forwarded_callback'] is not None for row in definition_rows),
            observed_definition_marker_records=sum(marker_counts.values())),
        scope='Cross-reference inventory, not enemy count, verified AI behavior or complete runtime spawning. No semantic species/type names are invented.',
        all_actor_behaviors_ported=False)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    out=a.project/'docs/stage9'
    report=catalogue(json.loads((out/'inventory.json').read_text(encoding='utf-8')),
        json.loads((out/'spawn-inventory.json').read_text(encoding='utf-8')),
        json.loads((a.project/'assets/extracted/catalog/animations/manifest.json').read_text(encoding='utf-8')))
    (out/'actor-contracts.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
