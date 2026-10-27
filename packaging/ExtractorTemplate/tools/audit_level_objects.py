"""Audit all original level placements against native spawn/update paths. Offline only."""
import argparse,csv,datetime,hashlib,html,json,os,re,shutil,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
from rolo_maps import parse_map
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];D=P/'docs/acceptance';W=P/'local/object-audit'
ROM_SHA='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pins():
 pending=[P/'tests/level_object_probe.cpp'];seen=set()
 while pending:
  p=pending.pop()
  if p in seen:continue
  seen.add(p)
  pending.extend(P/'src'/s for s in re.findall(r'#include "(core/[^"\n]+)"',p.read_text(encoding='utf-8-sig')))
 seen.add(P/'tools/build_level_object_probe.ps1')
 return {str(p.relative_to(P)):sha(p)for p in sorted(seen)}
def category(r):
 c=r['category']
 if c>=32:return 'Dynamic terrain / platform'
 return {4:'Enemy',5:'Scenery / level object',6:'Pickup / power-up',7:'Trigger metadata',8:'Transport trigger',10:'Trigger metadata',11:'Jigsaw state object',13:'Other actor (role needs review)',17:'Start / checkpoint metadata',18:'Companion / cage'}.get(c,'Unknown role')
def classify(r,n):
 c=r['category'];out=dict(r,category_label=category(r),native=n)
 if c==17:out.update(presence='NON-SPRITE ROLE',update='NOT CHECKED',art='NOT APPLICABLE',motion='NOT APPLICABLE');return out
 if c in (7,8,10):out.update(presence='NOT PROBED'if n.get('not_probed')else 'BLOCKED'if n.get('error')else 'TRIGGER REGISTERED'if n.get('trigger')else 'TRIGGER UNBOUND',update='NOT CHECKED',art='NOT APPLICABLE',motion='NOT APPLICABLE');return out
 spawned=bool(n.get('spawned'));error=n.get('error','');definition=r.get('definition');mismatch=spawned and isinstance(definition,int)and n.get('definition')!=definition
 presence='SPAWNED'if spawned else 'NOT PROBED'if n.get('not_probed')else 'BLOCKED'if error else 'MISSING / UNBOUND'
 update='ERROR'if error else '4 UPDATES OBSERVED'if n.get('updates')==4 else 'SHORT / UNCHECKED'
 art='MISSING FRAME'if n.get('frame_missing')else 'MACRO ART UNCHECKED'if n.get('macro_art')else 'MACRO RASTERIZED'if n.get('macro_rasterized')else 'FRAME RASTERIZED'if n.get('frame_available')else 'NOT CHECKED'
 motion='POSITION CHANGED'if n.get('moved')else 'NOT PROVEN (may be stationary)'
 out.update(presence=presence,update=update,art=art,motion=motion,definition_review=mismatch)
 return out
def outputs(report):
 e=lambda x:html.escape(str(x),quote=True);levels=report['levels'];summary=[];details=[];issues=[];groups=defaultdict(list)
 for l in levels:
  actors=[r for r in l['placements']if r['category']not in (7,8,10,17)];present=sum(r['presence']=='SPAWNED'for r in actors);enemies=sum(r['category']==4 for r in actors);dynamic=sum(r['category']>=32 for r in actors);runnable=sum(r['presence']=='SPAWNED'and r['update']=='4 UPDATES OBSERVED'for r in actors)
  l['counts']=dict(actor_placements=len(actors),spawned=present,enemy_placements=enemies,dynamic_terrain_placements=dynamic,update_smoke_passed=runnable,non_sprite_records=len(l['placements'])-len(actors));summary.append('<tr><td><a href="#level-'+str(l['selector'])+'">'+str(l['selector'])+'</a></td><td>'+str(l['bank'])+'</td><td>'+str(enemies)+'</td><td>'+str(dynamic)+'</td><td>'+str(present)+' / '+str(len(actors))+'</td><td>'+str(runnable)+'</td><td>'+str(l['normal_terrain_records'])+'</td></tr>')
  rows=[]
  for r in l['placements']:
   n=r['native'];note=n.get('error','')
   if r.get('category')==33:note+=(('; 'if note else '')+'Bounce connected; retained incoming D3 subpixel value unverified. Native baseline zero; NOT full fidelity.')
   if r.get('definition') in (0x1520e,0x153c8):note+=(('; 'if note else '')+'Attack/damage integration tested; retained emitter subpixel caller context unverified. NOT full fidelity.')
   if r.get('definition')==0x1498e:note+=(('; 'if note else '')+'Native attack connected; original retained D2/D3 subpixel spawn values unverified. Native baseline uses zero fractions; NOT full fidelity.')
   if r.get('definition_review'):note+=(('; 'if note else '')+'Definition differs after startup; may be an animation transition. Compare original '+f"{r['definition']:06X}"+' with live '+f"{n['definition']:06X}")
   if r['category']==10:note=(note+'; 'if note else '')+('Original literal-RTS trigger; pooled marker bookkeeping observed, no sprite expected.' if n.get('trigger') else 'Original trigger bookkeeping needs separate review; no-op handlers must not gain invented sprites.')
   bad=r['presence']in ('MISSING / UNBOUND','BLOCKED','DEFINITION MISMATCH','TRIGGER UNBOUND','NOT PROBED')or r['update']=='ERROR'or r['art']=='MISSING FRAME'or r.get('definition_review')
   if bad:
    key=('trigger',r['category'],r.get('parameter'))if r['category']in (7,8,10)else('macro mode',l['bank'],r.get('mode'))if 'mode'in r else('actor',r.get('definition'),r.get('handler'))if r.get('definition')else('unknown actor',r['category'],r.get('parameter'))
    groups[key].append((l['selector'],r))
    issues.append(dict(selector=l['selector'],bank=l['bank'],offset=r['record_offset'],x=r['x'],y=r['y'],type=f"{r['type']:04X}",category=r['category_label'],definition=f"{r['definition']:06X}"if isinstance(r.get('definition'),int)else '',mode=r.get('mode',''),macro=r.get('macro',''),presence=r['presence'],update=r['update'],art=r['art'],motion=r['motion'],error=note))
   rows.append('<tr class="'+('gap'if bad else '')+'"><td>'+e(r['record_offset'])+'</td><td>'+e(f"{r['x']},{r['y']}")+'</td><td>'+e(r['category_label'])+'<br><small>type '+e(f"{r['type']:04X}")+'; '+e('mode '+str(r['mode'])+' macro '+str(r.get('macro'))if 'mode'in r else 'definition '+(f"{r['definition']:06X}"if isinstance(r.get('definition'),int)else 'unresolved'))+'</small></td><td>'+e(r['presence'])+'</td><td>'+e(r['update'])+'</td><td>'+e(r['art'])+'</td><td>'+e(r['motion'])+'</td><td>'+e(note)+'</td></tr>')
  details.append('<details id="level-'+str(l['selector'])+'"><summary>Level selector '+str(l['selector'])+' — '+str(present)+'/'+str(len(actors))+' actor placements spawned</summary><p>'+e(l.get('probe_note',''))+'</p><table><tr><th>Offset</th><th>Original X,Y</th><th>Object role</th><th>Presence</th><th>Updates</th><th>Art</th><th>Motion</th><th>Issue</th></tr>'+''.join(rows)+'</table></details>')
 totals=Counter()
 for l in levels:totals.update(l['counts'])
 report['totals']=dict(totals);report['gap_placements']=len(issues)
 page='''<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width"><title>Rolo objects by level</title><style>body{font:16px system-ui;background:#111820;color:#edf4fa;margin:24px;padding:0 10px}h1{color:#8bdfab}a{color:#a5d6ff}table{border-collapse:collapse;width:100%;margin:15px 0}th,td{border:1px solid #465765;padding:8px;text-align:left;vertical-align:top}summary{padding:12px;background:#20313e;cursor:pointer}details{margin:12px 0}.gap{background:#3a2c26}small{color:#c8d3de}.note{border-left:4px solid #eac16d;padding:12px;line-height:1.5}</style><h1>Rolo: objects across all 70 levels</h1>'''
 page+='<p>'+e(report['time_utc'])+' | Offline, no AI/network/ROM instructions.</p><p class=note>Original foreground placements are compared with the current native dispatcher. A fresh scene starts near each marker, with fresh campaign flags; this is not a natural playthrough. Normal terrain records are counted but not pixel/collision certified here. Four direct callback updates are a smoke check, not full behaviour proof. No observed motion does not imply an object should move. Macro-backed art and original pixel/timing comparisons remain unchecked. Metadata/start markers are not missing sprites. Dynamically generated animation objects can add dependencies beyond this placement list.</p>'
 page+='<p><b>'+str(totals['enemy_placements'])+' enemy markers; '+str(totals['dynamic_terrain_placements'])+' dynamic terrain/platform markers. '+str(totals['spawned'])+'/'+str(totals['actor_placements'])+' actor placements spawned in the probe.</b> This is placement presence, not a completion percentage.</p><p><a href="all-level-object-gaps.csv">Missing/problem placements CSV</a> | <a href="all-level-object-repairs.md">Shared repair batches</a> | <a href="all-level-objects-latest.json">Full JSON</a></p><table><tr><th>Selector</th><th>Bank</th><th>Enemies</th><th>Dynamic blocks/platforms</th><th>Actor placements spawned</th><th>4 updates observed</th><th>Normal terrain records</th></tr>'+''.join(summary)+'</table>'+''.join(details)+'</html>'
 (D/'all-level-objects.html').write_text(page,encoding='utf-8')
 with (D/'all-level-object-gaps.csv').open('w',encoding='utf-8-sig',newline='')as f:
  fields=list(issues[0])if issues else ['selector','offset','presence'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(issues)
 repairs=['# Shared object repair batches','',f"{len(issues)} placements need attention across the70 world-linked levels. This includes missing/unbound entries, runtime errors and frame gaps; it is not a count of unique bugs.",'','Prioritize a shared definition or macro mode used by many levels. Re-run the offline audit after a relevant change.','']
 shared=[]
 for key,items in sorted(groups.items(),key=lambda x:(-len({sid for sid,r in x[1]}),-len(x[1]))):
  selectors=sorted({sid for sid,r in items});first=items[0][1];record=dict(family=list(key),macro_ids=sorted({r['macro']for sid,r in items if 'macro'in r}),selectors=selectors,placements=len(items),example_selector=items[0][0],example_offset=first['record_offset'],presence=first['presence'],error=first['native'].get('error',''));shared.append(record)
  label=('Actor definition $'+f'{key[1]:06X}'+', callback $'+f'{key[2]:06X}')if key[0]=='actor' and isinstance(key[1],int)and isinstance(key[2],int)else str(key)
  repairs+=['## '+label,'',str(len(items))+' placements in selectors '+', '.join(map(str,selectors))+'.','',first['presence']+' / '+first['update']+' / '+first['art']+'. '+first['native'].get('error',''),'']
 report['shared_repair_batches']=shared
 (D/'all-level-object-repairs.md').write_text('\n'.join(repairs),encoding='utf-8');(D/'all-level-objects-latest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--run-changed',action='store_true');a.add_argument('--open',action='store_true');args=a.parse_args();D.mkdir(exist_ok=True);W.mkdir(parents=True,exist_ok=True)
 if sha(P/'local/rolo.md')!=ROM_SHA:raise ValueError('Different supplied ROM revision')
 manifest_path=P/'assets/extracted/all-levels/manifest.json';manifest=load(manifest_path)
 if manifest['rom_sha256']!=ROM_SHA:raise ValueError('Extraction revision mismatch')
 sources=pins();exe=W/'level_object_probe.exe';build_record=W/'build-inputs.json';build=load(build_record)if build_record.exists()else{};build_ok=exe.exists()and build.get('sources')==sources and build.get('exe_sha256')==sha(exe)
 if args.run_changed and not build_ok:
  shell=shutil.which('pwsh')or shutil.which('powershell')
  if not shell:raise ValueError('PowerShell not found')
  proc=subprocess.run([shell,'-NoProfile','-File',str(P/'tools/build_level_object_probe.ps1')],cwd=ROOT,capture_output=True,text=True)
  if proc.returncode:raise ValueError('Native audit build failed: '+(proc.stdout+proc.stderr)[-2000:])
  build=dict(sources=sources,exe_sha256=sha(exe));build_record.write_text(json.dumps(build,indent=2)+'\n',encoding='utf-8');build_ok=True
 levels=[];cached=0;ran=0
 for level in manifest['selectors']:
  if not level['world_referenced']:continue
  sid=level['selector'];layer=level['layers']['foreground'];path=P/layer['binary']['path']
  if sha(path)!=layer['binary']['sha256']:raise ValueError(f'Changed extracted MAP selector {sid}')
  parsed=parse_map(path.read_bytes());actual={(r['offset'],r['type'],r['x'],r['y'])for r in parsed['records']if not r['visual']};expected={(r['record_offset'],r['type'],r['x'],r['y'])for r in level['markers']}
  if actual!=expected or len(expected)!=len(level['markers']):raise ValueError(f'Marker ledger differs from raw MAP selector {sid}')
  text=''.join(f"{r['record_offset']} {r['type']} {r['x']} {r['y']}\n"for r in level['markers']);inputs=dict(sources=sources,rom_sha256=ROM_SHA,manifest_sha256=sha(manifest_path),map_sha256=sha(path),placements_sha256=hashlib.sha256(text.encode()).hexdigest(),exe_sha256=sha(exe)if build_ok else None)
  casefile=W/f'level-{sid:02d}.txt';recordfile=W/f'level-{sid:02d}.json';previous=load(recordfile)if recordfile.exists()else{};note='';observations={}
  if build_ok and previous.get('inputs')==inputs:observations={r['offset']:r for r in previous['observations']};note=previous.get('note','')+' Cached unchanged audit.';cached+=1
  elif args.run_changed and build_ok:
   casefile.write_text(text,encoding='ascii');ran+=1
   try:
    proc=subprocess.run([str(exe),str(sid),str(casefile)],capture_output=True,text=True,timeout=90);(W/f'level-{sid:02d}-stderr.log').write_text(proc.stderr,encoding='utf-8');errors=[]
    for line in proc.stdout.splitlines():
     try:r=json.loads(line)
     except ValueError:errors.append('Malformed native audit output');continue
     if 'level_error'in r:errors.append('Level initialization: '+r['level_error'])
     else:observations[r['offset']]=r
    if proc.returncode:errors.append('Native probe process exited '+str(proc.returncode))
    note='; '.join(errors)
   except subprocess.TimeoutExpired:note='Native probe timed out; level audit incomplete.'
   for r in level['markers']:observations.setdefault(r['record_offset'],dict(offset=r['record_offset'],error=note or 'No native observation returned'))
   recordfile.write_text(json.dumps(dict(inputs=inputs,observations=list(observations.values()),note=note),indent=2)+'\n',encoding='utf-8')
  else:
   note='No current native audit; run Audit All Level Objects.cmd.';observations={r['record_offset']:dict(offset=r['record_offset'],not_probed=True)for r in level['markers']}
  placements=[classify(r,observations.get(r['record_offset'],dict(not_probed=True)))for r in level['markers']]
  levels.append(dict(selector=sid,bank=layer['bank'],normal_terrain_records=sum(r['visual']for r in parsed['records']),placements=placements,probe_note=note,potential_animation_generated_objects='Not fully enumerated; use existing static coverage animation_links/definition chains for candidate dependencies.'))
  if ran and len(levels)%10==0:print(f'Audited {len(levels)}/70 selectors',flush=True)
 if len(levels)!=70:raise ValueError('Expected70 world-linked levels')
 report=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rom_sha256=ROM_SHA,ai_calls=0,network_calls=0,scope='Original foreground placement presence and isolated native callback smoke; not full object behaviour, art/timing fidelity, collision/blocking acceptance or complete animation-generated object closure.',levels=levels,cached_levels=cached,executed_levels=ran)
 outputs(report);print(json.dumps(dict(totals=report['totals'],gap_placements=report['gap_placements'],cached=cached,executed=ran)));print(D/'all-level-objects.html')
 if args.open:os.startfile(str(D/'all-level-objects.html'))
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except (OSError,ValueError,KeyError)as error:print('Object audit could not complete: '+str(error),file=sys.stderr);sys.exit(2)
