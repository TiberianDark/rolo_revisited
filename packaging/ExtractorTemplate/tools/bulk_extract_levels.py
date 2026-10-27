"""Pinned-ROM bulk MAP/layer/bank extraction. Static data only; no ROM execution."""
import argparse,hashlib,json,shutil,struct
from pathlib import Path
from inventory_rom import ROM_HASH,definitions
from rolo_maps import parse_map,render_foreground,level_inventory,long,word
from rolo_codec import decode_backward_lz
from rolo_stage2 import png_palette
from inventory_spawns import resolve_marker

def digest(data):return hashlib.sha256(data).hexdigest()
def render_layer(rom,layout,tiles,quads,macros):
 width,height=layout['width'],layout['height']
 if width*height<=16_777_216:return render_foreground(rom,layout,tiles,quads,macros)
 if width*height>134_217_728:raise ValueError('Bulk image exceeds assembly budget')
 pixels=bytearray(width*height);strip_height=max(1,min(512,16_777_216//width))
 for y in range(0,height,strip_height):
  h=min(strip_height,height-y)
  pixels[y*width:(y+h)*width]=render_foreground(rom,layout,tiles,quads,macros,viewport=(0,y,width,h))
 return pixels

def repair_previews(project,rom_path):
 rom=rom_path.read_bytes()
 if digest(rom)!=ROM_HASH:raise ValueError('Supplied ROM revision differs')
 out=project/'assets/extracted/all-levels';report=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
 catalog=json.loads((project/'assets/extracted/catalog/manifest.json').read_text(encoding='utf-8-sig'));banks={b['bank']:b for b in catalog['graphics_banks']}
 for row in report['selectors']:
  if all(layer['image'] for layer in row['layers'].values()):continue
  palette=(project/row['palette']['path']).read_bytes();colors=[tuple(((v>>s)&7)*255//7 for s in (1,5,9)) for v in struct.unpack('>64H',palette)]
  for name,layer in row['layers'].items():
   if layer['image']:continue
   layout=parse_map((project/layer['binary']['path']).read_bytes());bank=banks[layer['bank']]
   tiles=(out/'shared'/f"bank-{layer['bank']:02d}"/'graphics.4bpp').read_bytes()
   pixels=render_layer(rom,layout,tiles,bank['quads'],bank['macros']);data=png_palette(layout['width'],layout['height'],pixels,colors)
   path=out/f"selector-{row['selector']:02d}"/(name+'.png');path.write_bytes(data)
   layer['image']=dict(path=path.relative_to(project).as_posix(),size=len(data),sha256=digest(data))
   row['issues']=[issue for issue in row['issues'] if not issue.startswith(name+':')]
  (out/f"selector-{row['selector']:02d}"/'manifest.json').write_text(json.dumps(dict(rom_sha256=ROM_HASH,**row),indent=2)+'\n',encoding='utf-8')
 report['counts']['rendered_layers']=sum(bool(l['image']) for r in report['selectors'] for l in r['layers'].values())
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 from refresh_all_level_coverage import refresh
 refresh(project);print(json.dumps(report['counts']),flush=True)
def run(project,rom_path):
 rom=rom_path.read_bytes()
 if digest(rom)!=ROM_HASH:raise ValueError('Supplied ROM revision differs')
 catalog_root=project/'assets/extracted/catalog'
 catalog=json.loads((catalog_root/'manifest.json').read_text(encoding='utf-8-sig'))
 if catalog['rom_sha256']!=ROM_HASH:raise ValueError('Catalogue revision differs')
 out=project/'assets/extracted/all-levels';out.mkdir(parents=True,exist_ok=True)
 def write(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);return dict(path=path.relative_to(project).as_posix(),size=len(data),sha256=digest(data))
 def checked(artifact):
  data=(catalog_root/artifact['path']).read_bytes()
  if digest(data)!=artifact['sha256'] or len(data)!=artifact['size']:raise ValueError('Stale catalogue asset '+artifact['path'])
  return data
 layouts={row['source']:row for row in catalog['layouts']};banks={row['bank']:row for row in catalog['graphics_banks']};bank_data={};bank_reports=[]
 for bank,row in banks.items():
  if 'artifact' not in row or 'macro_artifact' not in row:continue
  graphics=checked(row['artifact']);macros=checked(row['macro_artifact']);bank_data[bank]=graphics
  directory=out/'shared'/f'bank-{bank:02d}'
  bank_reports.append(dict(bank=bank,graphics=write(directory/'graphics.4bpp',graphics),macros=write(directory/'macros.itms',macros),quad_source=row['quads'],collision_source=row['collision'],scope='Original graphics and ITMS bytes. Quad/collision source pointers retained; runtime interpretation has separate contracts.'))
 defs=definitions(rom);write(out/'shared/actor-definitions.bin',rom[0x13eaa:0x1582a]);(out/'shared/actor-definitions.json').write_text(json.dumps(defs,indent=2)+'\n',encoding='utf-8')
 world=level_inventory(rom);world_ids={node['selector']&127 for node in world['world_nodes']};rows=[];render_cache={}
 for selector in catalog['selectors']:
  sid=selector['selector'];directory=out/f'selector-{sid:02d}';directory.mkdir(parents=True,exist_ok=True);layers={};issues=[]
  palette=checked(selector['palette_artifact']);colors=[tuple(((v>>s)&7)*255//7 for s in (1,5,9)) for v in struct.unpack('>64H',palette)]
  palette_file=write(directory/'palette.cram',palette)
  for name in ('foreground','background'):
   source=selector[name];layout_row=layouts[source];data=checked(layout_row['artifact']);layout=parse_map(data);bank=layout['bank'];row=banks[bank]
   binary=write(directory/(name+'.map'),data);image=None;key=(source,bank,digest(palette))
   try:
    if key in render_cache:
     target=directory/(name+'.png');shutil.copyfile(render_cache[key],target);image=dict(path=target.relative_to(project).as_posix(),size=target.stat().st_size,sha256=digest(target.read_bytes()))
    else:
     pixels=render_layer(rom,layout,bank_data[bank],row['quads'],row['macros']);image=write(directory/(name+'.png'),png_palette(layout['width'],layout['height'],pixels,colors));render_cache[key]=directory/(name+'.png')
   except (ValueError,KeyError) as error:issues.append(name+': '+str(error))
   layers[name]=dict(source=source,bank=bank,width=layout['width'],height=layout['height'],records=len(layout['records']),binary=binary,image=image)
  foreground=layouts[selector['foreground']];markers=[dict(record_offset=r['offset'],x=r['x'],y=r['y'],**resolve_marker(rom,r['type'])) for r in foreground['records'] if not r['visual']]
  (directory/'markers.json').write_text(json.dumps(markers,indent=2)+'\n',encoding='utf-8')
  row=dict(selector=sid,world_referenced=sid in world_ids,kind='overworld' if sid==0 else 'world node selector' if sid in world_ids else 'other/variant selector',layers=layers,palette=palette_file,markers=markers,camera_mode=selector['camera_mode'],spawn_selector=selector['spawn_selector'],background_parameter=selector['background_parameter'],issues=issues)
  (directory/'manifest.json').write_text(json.dumps(dict(rom_sha256=ROM_HASH,**row),indent=2)+'\n',encoding='utf-8');rows.append(row)
  print(f'Selector {sid:02d}: both MAPs extracted; {len(markers)} markers; {len(issues)} image issues',flush=True)
 report=dict(rom_sha256=ROM_HASH,selectors=rows,banks=bank_reports,world_nodes=world['world_nodes'],world_selector_ids=sorted(world_ids),counts=dict(selectors=len(rows),world_referenced_selectors=len(world_ids),shared_banks=len(bank_reports),layers=sum(len(r['layers']) for r in rows),rendered_layers=sum(bool(l['image']) for r in rows for l in r['layers'].values()),actor_definitions=len(defs)),scope='Raw decoded layers and static original-art previews. Dynamic macros, animated tiles, sprites, priority, camera and collision/gameplay are separate; PNGs are not complete runtime scenes. Selector slots include variants/screens and are not assumed to be distinct levels. Actor definitions are dumped; not all actor animation/graphics are yet exported.')
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 from refresh_all_level_coverage import refresh
 refresh(project)
 print(json.dumps(report['counts']),flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--rom',type=Path);parser.add_argument('--repair-previews',action='store_true');args=parser.parse_args();(repair_previews if args.repair_previews else run)(args.project,args.rom or args.project/'local/rolo.md')
