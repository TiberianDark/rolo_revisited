"""Per-selector static dependency and verified-local-contract reuse ledger."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path

def refresh(project):
 docs=project/'docs/stage9';assets=project/'assets/extracted/all-levels'
 manifest=json.loads((assets/'manifest.json').read_text(encoding='utf-8'));inv=json.loads((docs/'inventory.json').read_text(encoding='utf-8'))
 if manifest['rom_sha256']!=inv['rom_sha256']:raise ValueError('Coverage ROM revision mismatch')
 animation_path=project/'assets/extracted/catalog/animations/manifest.json'
 animations=json.loads(animation_path.read_text(encoding='utf-8'))
 if animations['rom_sha256']!=inv['rom_sha256']:raise ValueError('Animation revision mismatch')
 programs_by_table=defaultdict(list)
 for program in animations['candidate_programs']:programs_by_table[program['table']].append(program)
 routines={r['address']:r for r in inv['routines']};definitions={d['address']:d for d in inv['object_definitions']};direct=defaultdict(set);possible=defaultdict(set);owners=defaultdict(set)
 for entry,r in routines.items():
  for address in r['blocks']:owners[address].add(entry)
  for edge in r['dependency_edges']:
   possible[entry].add(edge['target'])
   if edge['evidence'] in ('direct encoded target','accepted non-call control-flow transfer between entry candidates'):direct[entry].add(edge['target'])
 def closure(roots,graph):
  seen=set();pending=list(roots)
  while pending:
   address=pending.pop()
   if address in seen:continue
   seen.add(address);pending.extend(graph[address]-seen)
  return seen
 macro=next(t for t in inv['dispatch_tables'] if t['dispatch']==0xbe56);macro_targets={s['address']-macro['base']:s['target'] for s in macro['slots']};rows=[];usage=defaultdict(list)
 for level in manifest['selectors']:
  sid=level['selector'];roots={};definition_ids=set();marker_rows=[]
  if level['world_referenced']:
   for address in (0x1c6c,0x1d94,0x766a,0x3f34,0x7730,0x3784,0x14a4):roots.setdefault(address,[]).append('shared normal-level startup/frame/restart/interrupt candidate')
  for marker in level['markers']:
   linked=dict(marker);targets=set()
   for key in ('handler','spawn_handler'):
    if isinstance(marker.get(key),int):targets.add(marker[key])
   if 'mode' in marker and marker['dispatch_offset'] in macro_targets:targets.add(macro_targets[marker['dispatch_offset']])
   pending=[marker['definition']] if 'definition' in marker else []
   local_defs=set()
   while pending:
    address=pending.pop()
    if address in local_defs or address not in definitions:continue
    local_defs.add(address);definition=definitions[address];targets.add(definition['handler'])
    for field in ('linked','secondary_definition'):
     if definition.get(field) in definitions:pending.append(definition[field])
    if definition['handler']==0xb702 and definition.get('field_22'):targets.add(definition['field_22'])
   definition_ids.update(local_defs)
   for address in targets:roots.setdefault(address,[]).append(f"marker {marker['record_offset']:04X} type {marker['type']:04X}")
   linked['definition_chain']=[f'{a:06X}' for a in sorted(local_defs)];linked['routine_roots']=[f'{a:06X}' for a in sorted(targets)];linked['handler_local_green']=isinstance(marker.get('handler'),int) and routines.get(marker['handler'],{}).get('verification_status')=='verified';linked['semantic_gap']=marker['status'].endswith('pending') or not targets
   marker_rows.append(linked)
  # Actor defaults, linked body/head and candidate animation tables are data
  # dependencies too; they are not encoded calls and were previously omitted.
  pending=[0x13ecc] if level['world_referenced'] else []
  pending.extend(definition_ids);animation_links=[];seen_definitions=set()
  while pending:
   address=pending.pop()
   if address in seen_definitions or address not in definitions:continue
   seen_definitions.add(address);definition=definitions[address]
   for field in ('linked','secondary_definition'):
    if definition.get(field) in definitions:pending.append(definition[field])
   for program in programs_by_table.get(definition['animation_table'],[]):
    for control in program.get('controls',[]):
     slot=0xfe28+control['command']
     if slot in routines:roots.setdefault(slot,[]).append(f"animation definition {address:06X} candidate selector {program['selector']} site {control['address']:06X}")
     animation_links.append(dict(definition=f'{address:06X}',selector=program['selector'],site=f"{control['address']:06X}",command=control['command'],parameter=control['parameter'],routine=f'{slot:06X}',local_green=routines.get(slot,{}).get('verification_status')=='verified',scope='Static table-prefix candidate; runtime selector and command operand admission remain open.'))
   definition_ids.add(address)
  known=closure(roots,direct)&routines.keys();candidate=closure(roots,possible)&routines.keys();green={a for a in known if routines[a].get('verification_status')=='verified'}
  uncertain=[s for s in inv['unresolved'] if owners[s['address']]&known];unique_stops={s['address'] for s in uncertain}
  dependencies=[dict(address=f'{a:06X}',local_green=a in green,status=routines[a]['status'],subsystem=routines[a]['subsystem'],proof=routines[a].get('verification_evidence'),direct_root_reasons=roots.get(a,[])) for a in sorted(known)]
  for address in known:usage[address].append(sid)
  layer_count=sum(bool(layer['image']) for layer in level['layers'].values())
  row=dict(animation_control_sites=len({a['site'] for a in animation_links}),animation_links=animation_links,selector=sid,kind=level['kind'],world_referenced=level['world_referenced'],foreground_size=f"{level['layers']['foreground']['width']}x{level['layers']['foreground']['height']}",bank=level['layers']['foreground']['bank'],raw_layers=2,preview_layers=layer_count,markers=len(marker_rows),definition_count=len(definition_ids),known_routines=len(known),local_green_routines=len(green),known_slice_percent=round(100*len(green)/len(known),1) if known else None,possible_routines=len(candidate),open_call_sites=len(unique_stops),marker_gaps=sum(m['semantic_gap'] for m in marker_rows),native_connected=sid in (1,2,3,4,8),full_fidelity_certified=False,extraction_issues=level['issues'],dependencies=dependencies,marker_links=marker_rows,definition_ids=[f'{a:06X}' for a in sorted(definition_ids)])
  (assets/f'selector-{sid:02d}'/'coverage.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf-8');rows.append(row)
 reuse=[dict(address=f'{a:06X}',local_green=routines[a].get('verification_status')=='verified',selectors=ids,selector_count=len(ids),world_level_count=sum(sid in manifest['world_selector_ids'] for sid in ids),name=routines[a]['note'],proof=routines[a].get('verification_evidence')) for a,ids in usage.items()]
 reuse.sort(key=lambda r:(-r['selector_count'],r['address']))
 compact=[{k:v for k,v in row.items() if k not in ('dependencies','marker_links','definition_ids','animation_links')} for row in rows]
 report=dict(rom_sha256=inv['rom_sha256'],animation_manifest_sha256=hashlib.sha256(animation_path.read_bytes()).hexdigest(),inventory_sha256=hashlib.sha256((docs/'inventory.json').read_bytes()).hexdigest(),levels=compact,routine_reuse=reuse,counts=manifest['counts'],scope='Known-slice percentage is verified LOCAL routines divided by linked call and actor-animation data candidate routines, not level completion. Indirect candidate expansion is separately counted; unresolved calls, marker semantics, runtime overrides, animation spawns, caller domains and subsystem integration can add requirements. Animation table-prefix controls are candidate data dependencies, not proven runtime selector admission. Generic shared roots are conservative candidates for world-referenced selectors. Direct-return markers can have other consumers. Native admission is development availability, not fidelity certification. Selectors include shared layouts, variants and screens.')
 (docs/'all-level-coverage.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 fields=['selector','kind','bank','foreground_size','raw_layers','preview_layers','markers','definition_count','animation_control_sites','local_green_routines','known_routines','known_slice_percent','possible_routines','open_call_sites','marker_gaps','native_connected','full_fidelity_certified']
 with (docs/'all-level-coverage.csv').open('w',newline='',encoding='utf-8-sig') as stream:
  writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(compact)
 html='''<!doctype html><meta charset="utf-8"><title>Rolo: all level extraction and verification</title><style>body{background:#111820;color:#e5edf5;font:16px system-ui;margin:24px}td,th{padding:8px;border-bottom:1px solid #344452;text-align:left}a{color:#8bcdff}input{padding:10px}small{color:#b5c5d3}.green{color:#64d58a}table{border-collapse:collapse}</style><h1>Rolo — all selector coverage</h1><p>Both map layers, markers and shared banks extracted in one batch. Green means a scoped local contract, not completed gameplay.</p><p id="summary"></p><p><small>Known-slice % is a static dependency metric. Actor animation table-prefix references are included as candidates. Possible indirect paths, selector domains and unknown marker consumers remain open. Selector IDs are ROM IDs, not play order; early route is 1 → 2 → 4 → 8.</small></p><input id="search" placeholder="Filter selector, bank or kind"><h2>Per selector</h2><table><thead><tr><th>Selector</th><th>Kind</th><th>Bank</th><th>Layers</th><th>Markers</th><th>Local greens / known</th><th>Known-slice %</th><th>Open calls</th><th>Marker gaps</th><th>Native demo</th></tr></thead><tbody id="rows"></tbody></table><h2>Shared routine reuse</h2><p>New local greens propagate to linked selectors whenever the inventory is regenerated.</p><table><thead><tr><th>Routine</th><th>Status</th><th>World levels / all selectors</th><th>Evidence</th></tr></thead><tbody id="reuse"></tbody></table><script>const D=PAYLOAD;const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));document.getElementById('summary').textContent=JSON.stringify(D.counts);function render(){let q=document.getElementById('search').value.toLowerCase();document.getElementById('rows').innerHTML=D.levels.filter(r=>JSON.stringify(r).toLowerCase().includes(q)).map(r=>{let id=String(r.selector).padStart(2,'0'),base='../../assets/extracted/all-levels/selector-'+id+'/';return '<tr><td><a href="'+base+'coverage.json">'+id+'</a></td><td>'+esc(r.kind)+'</td><td>'+r.bank+'</td><td><a href="'+base+'foreground.png">FG</a> / <a href="'+base+'background.png">BG</a> '+r.preview_layers+'/2</td><td>'+r.markers+'</td><td class="green">'+r.local_green_routines+' / '+r.known_routines+'</td><td>'+esc(r.known_slice_percent)+'%</td><td>'+r.open_call_sites+'</td><td>'+r.marker_gaps+'</td><td>'+(r.native_connected?'connected':'pending')+'</td></tr>'}).join('');}document.getElementById('search').oninput=render;render();document.getElementById('reuse').innerHTML=D.routine_reuse.map(r=>'<tr><td>'+r.address+'</td><td class="'+(r.local_green?'green':'')+'">'+(r.local_green?'local green':'partial')+'</td><td>'+r.world_level_count+' / '+r.selector_count+'</td><td>'+esc(r.proof||r.name)+'</td></tr>').join('');</script>'''
 (docs/'all-level-coverage.html').write_text(html.replace('PAYLOAD',json.dumps(report).replace('<','\\u003c')),encoding='utf-8')
 print(f'Coverage refreshed for {len(rows)} selectors; {len(reuse)} shared routine links',flush=True)
 return report

if __name__=='__main__':refresh(Path(__file__).resolve().parents[1])
