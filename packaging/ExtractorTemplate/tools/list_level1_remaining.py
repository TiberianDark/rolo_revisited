"""Publish the current conservative Level1 remaining-function list; no ROM execution."""
from pathlib import Path
import csv,json

project=Path(__file__).resolve().parents[1]
docs=project/'docs/stage9'
batch=json.loads((docs/'level1-batch.json').read_text(encoding='utf-8'))
inventory=json.loads((docs/'inventory.json').read_text(encoding='utf-8'))
routines={r['address']:r for r in inventory['routines']}
with (docs/'level1-batch.csv').open(encoding='utf-8',newline='') as handle:
    tasks=list(csv.DictReader(handle))
def clean(value):return str(value).replace('|','/').replace('\n',' ')
lines=['# Level 1 remaining functions and gameplay batch','',
       'Generated from the current inventory and Level1 dependency batch. This is the complete current candidate list, not a proven final reachability closure. Shared transitions can include other levels; unresolved targets and generated actors can add requirements. Partially assessed does not mean fully mapped or implemented.','',
       '## Requested gameplay batch','',
       '| Feature | ROM entry points already identified | Work still required |',
       '|---|---|---|',
       '| Second enemy / key interaction | B2E6, B314, D2E2, B386; definition144A4 | Confirm role and key/release relationship from original data; connect spawn, all callbacks, graphics, contacts and outcome. Do not assume species or key identity from the address. |',
       '| Bunnies / companions | A8BC, A92E, A9B0, AA4A, AB28, AB3C, AC34, AC7A, ACAC, ACCE, ADD0, ADFC, AE86, AEB4, AF80, B00A, B058, B0D6, B114, B1A8, B1D6, B28E, D32A | Connect capture/release, history following, jumps, selection and slot management; confirm marker-to-bunny identity and generated links. |',
       '| Point pickups | B702, 9958, 997E, B7C0, B7D8, 716E | Connect original contact callback, score, collection animation, sounds, marker persistence and retirement. Six definitions cover52 immutable pickups. |',
       '| Extra life | B702, 99E2, 9A04; definition1443E | Connect collection, lives, sound, display and disposal; one immutable marker. |',
       '| Jigsaw / exit / level completion | E528, 9534; world-jigsaw-contract.json and progress-selector-domains.json | Resolve exact exit/reward relationship and rescue gates; connect flags, fade, state transition and world-map reveal. A world-map jigsaw reward is not yet proof of a collectible jigsaw actor. |',
       '| Shared world integration | 766A, 3F34, 7730, 1C6C, 1D94, 28B0, 29EE, 2AD8, 2CBC, 34C2, 34F0, 7292, 72A2, 72D0, 7424 | Original startup/reset, shared actor scheduling and resources, streamed terrain/presentation and object re-entry. Extend existing native services rather than reimplementing each level. |',
       '| Presentation and completion proof | 54A0, 2468, 2FF6, 3060, 22A8, 14A4; original sound handoff contracts | HUD, palette/fades, native sound, death/restart and full success/failure reference runs. |','',
       'A single build/extract/test launcher can assemble this batch. It cannot supply missing translations. The existing refresh_level1_batch.py runs the thirteen analysis/verification steps; it does not implement these features.','',
       '## Unassessed routine candidates','',
       '| ROM address | Subsystem / existing note | Required next evidence |','|---|---|---|']
for task in tasks:
    if task['batch']=='control-flow':continue
    address=int(task['address']);r=routines.get(address,{})
    lines.append(f"| ${address:06X} | {clean(r.get('subsystem',''))}: {clean(r.get('note',''))} | {clean(task['next'])} |")
lines+=['','## Uncertain control-flow sites','','| Site | Existing evidence / next action |','|---|---|']
for task in tasks:
    if task['batch']=='control-flow':lines.append(f"| ${int(task['address']):06X} | {clean(task['next'])} |")
lines+=['','## Partially assessed contracts still requiring closure','','Multiple contracts can refer to the same function. This section includes remaining domains even when native helper code already exists. Older contract status text can predate integration; inspect the current native source before treating it as unported.','','| Entry | Function / contract | Remaining scope |','|---|---|---|']
for link in batch['partial_contract_links']:
    lines.append(f"| ${link['address']} | {clean(link['name'])} ([evidence]({link['path']})) | {clean(link['scope'])} |")
lines+=['',f"Snapshot: {batch['counts']['unassessed_routines']} unassessed routine tasks; {batch['counts']['indirect_or_boundary_tasks']} uncertain sites; {len(batch['partial_contract_links'])} partial contract links. No assertion of complete Level1 fidelity.",'']
(docs/'LEVEL1-REMAINING-FUNCTIONS.md').write_text('\n'.join(lines),encoding='utf-8')
print(batch['counts'])
