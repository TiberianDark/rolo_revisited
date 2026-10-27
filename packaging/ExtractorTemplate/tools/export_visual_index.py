"""Join visual dumps to ROM world nodes, shared layouts and spawn definitions."""
import csv
import hashlib
import html
import json
from collections import defaultdict
from pathlib import Path
from inventory_rom import ROM_HASH
from inventory_spawns import resolve_marker
from rolo_maps import level_inventory, long


def export(rom, out):
    atlas=json.loads((out/'map-atlas'/'manifest.json').read_text())
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH or atlas['rom_sha256']!=ROM_HASH:
        raise ValueError('Unexpected ROM revision')
    levels=level_inventory(rom)
    nodes=defaultdict(list)
    for node in levels['world_nodes']:
        nodes[node['selector']].append(node)
    sharing=defaultdict(list)
    for row in atlas['selectors']:
        sharing[long(rom,0x4ab1a+row['selector']*8)&0xffffff].append(row['selector'])
    rows=[]
    flat=[]
    for row in atlas['selectors']:
        selector=row['selector']
        fg=next(layer for layer in row['layers'] if layer['layer']=='foreground')
        markers=[]
        for marker in fg['markers']:
            relation={**marker,**resolve_marker(rom,marker['type'])}
            markers.append(relation)
            flat.append({'selector':selector,'layout_source':fg['source'],**relation})
        rows.append({'selector':selector,'source':fg['source'],'width':fg['width'],'height':fg['height'],
            'spawn_selector':long(rom,0x4ab1a+selector*8)>>24,
            'shared_foreground_selectors':sharing[fg['source']], 'world_nodes':nodes.get(selector, []),
            'definition_candidates':sorted({m['definition'] for m in markers if 'definition' in m}),
            'markers':markers})
    result={'rom_sha256':ROM_HASH,'selectors':rows,'counts':{
        'selector_slots':len(rows),'unique_foreground_layouts':len(sharing),
        'unique_nonworld_foreground_layouts':levels['distinct_foreground_sources'],
        'world_node_records':len(levels['world_nodes']),'world_node_selectors':len(nodes),
        'marker_instances_across_selectors':len(flat),
        'definition_lookup_instances':sum('definition' in m for m in flat)},
        'scope':'Static ROM relationships. Repeated selectors may duplicate markers. Definition candidates follow traced table lookup only; runtime spawning, gates and final placement remain unproven. World node membership does not prove level completion or total playable-level count.'}
    (out/'visual-inventory.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    fields=['selector','layout_source','offset','x','y','type','category','parameter','definition','handler','status']
    with (out/'visual-marker-relations.csv').open('w',newline='',encoding='utf-8-sig') as file:
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction='ignore')
        writer.writeheader();writer.writerows(flat)
    cards=[]
    for row in rows:
        selector=row['selector']
        actors=' '.join(f'<a href="actor-atlas/index.html#definition-{d:06X}">${d:06X}</a>' for d in row['definition_candidates']) or 'No ordinary definition lookup'
        markerrows=''.join(f'<tr><td>${m["type"]:04X}</td><td>{m["x"]}, {m["y"]}</td><td>'+ (f'<a href="actor-atlas/index.html#definition-{m["definition"]:06X}">${m["definition"]:06X}</a>' if 'definition' in m else '—')+f'</td><td>{html.escape(m["status"])}</td></tr>' for m in row['markers'])
        nodeinfo=', '.join(f'group{n["group"]} row{n["row"]} col{n["column"]}' for n in row['world_nodes']) or 'No node in inspected world tables'
        cards.append(f'<article><h2>Selector {selector:02d}</h2><p>{row["width"]} × {row["height"]}; shared layout selectors {row["shared_foreground_selectors"]}</p><p>World: {nodeinfo}</p><p><a href="map-atlas/selector-{selector:02d}-markers.html">Map and markers</a> · Definitions: {actors}</p><details><summary>{len(row["markers"])} marker records</summary><table><tr><th>Type</th><th>Coordinates</th><th>Definition</th><th>Evidence / gap</th></tr>{markerrows}</table></details></article>')
    (out/'visual-index.html').write_text('<!doctype html><meta charset="utf-8"><title>Rolo visual inventory</title><style>body{background:#101820;color:#eee;font:16px system-ui;margin:24px}article{background:#24323c;padding:16px;margin:16px 0}a{color:#8df}td,th{padding:8px;text-align:left}input{font:inherit;padding:12px;width:80%}</style><h1>Rolo — visual conversion inventory</h1><p>'+html.escape(result['scope'])+'</p><p>'+html.escape(str(result['counts']))+'</p><p><a href="map-atlas/index.html">All map artwork</a> · <a href="actor-atlas/index.html">All actor artwork</a> · <a href="visual-marker-relations.csv">Marker spreadsheet</a></p><input placeholder="Filter by selector, definition, marker type or evidence" oninput="for(const a of document.querySelectorAll(\'article\'))a.hidden=!a.textContent.toLowerCase().includes(this.value.toLowerCase())">'+''.join(cards),encoding='utf-8')
    print(result['counts'])
    return result
