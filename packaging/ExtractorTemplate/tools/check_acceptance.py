"""Offline acceptance checklist: no AI, network or ROM instruction execution."""
import argparse,ast,datetime,hashlib,html,json,os,re,sys
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parents[1]
D=P/'docs/acceptance'
STATES={'PASS','FAIL','BLOCKED','STALE','NOT TESTED','PARTIAL','MISSING','NOT CONNECTED'}
PENDING=STATES-{'PASS','FAIL','BLOCKED','STALE'}
ROM_SHA='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def validate(m):
 if m.get('schema_version')!=1 or m.get('level')!=1:raise ValueError('Unsupported checklist schema/level')
 rows=m.get('requirements',[]);ids=[r['id']for r in rows]
 if not rows or len(ids)!=len(set(ids)):raise ValueError('Checklist must have unique nonempty requirements')
 for r in rows:
  if not all(isinstance(r.get(k),str)and r[k]for k in ('id','title','area','scope','repair')):raise ValueError('Incomplete requirement '+str(r.get('id')))
  if ('evidence'in r)==('pending'in r):raise ValueError('Requirement needs exactly one evidence or pending field')
  if 'pending'in r and r['pending']not in PENDING:raise ValueError('Pending requirements cannot claim a pass')
  if 'evidence'in r:
   e=r['evidence']
   if e.get('test')not in ('level1_enemy_slice_tests','level1_objects_tests','level1_transport_world_tests')or not e.get('assertions'):raise ValueError('Unreviewed evidence recipe')
 return rows
def summarize(rows,key='status'):
 c=Counter(r[key]for r in rows)
 return dict(passed=c['PASS'],total=len(rows),percent=round(100*c['PASS']/len(rows),1)if rows else 0,counts=dict(sorted(c.items())))
def evaluate(row,checks,review_problems,base=P):
 r=dict(row);r['original_fidelity']='NOT TESTED';r['reference_reason']='No reviewed original-reference comparison scenario is connected for this requirement.'
 if 'pending'in row:r['status']=row['pending'];r['reason']=row['repair'];return r
 name=row['evidence']['test'];source=base/'tests'/(name+'.cpp')
 if review_problems:r['status']='BLOCKED';r['reason']='Native test/runner recipe changed; review required: '+', '.join(review_problems);return r
 try:text=source.read_text(encoding='utf-8-sig')
 except OSError:r['status']='BLOCKED';r['reason']='Native test source missing';return r
 if not all(a in text for a in row['evidence']['assertions']):r['status']='BLOCKED';r['reason']='Required reviewed assertions are missing';return r
 e=checks.get(name,{})
 state=e.get('status','NOT TESTED');r['status']=state if state in STATES else 'BLOCKED'
 if state=='PASS':r['reason']='Current source-pinned native scenario passed; '+row['scope']
 else:r['reason']=e.get('reason','Native scenario '+state+'; inspect its build/run log.')
 r['evidence_test']=name;r['evidence_reused']=bool(e.get('reused'));return r

def exit_status(report):
 statuses=[r['status']for r in report['requirements']]+[r.get('status','BLOCKED')for r in report.get('native_checks',[])]
 if report.get('errors')or any(s in ('BLOCKED','STALE')for s in statuses)or report.get('local_contracts',{}).get('label')in ('BLOCKED','STALE / BLOCKED'):return 2
 return 1 if 'FAIL'in statuses else 0

def write_reports(report):
 e=lambda x:html.escape(str(x),quote=True)
 rows=report['requirements'];summary=report['integration'];fidelity=report['fidelity'];local=report['local_contracts']
 cards=[('Native integration checklist',f"{summary['percent']}%",f"{summary['passed']}/{summary['total']} requirements passed"),('Original-reference comparisons',f"{fidelity['percent']}%",f"{fidelity['passed']}/{fidelity['total']} requirements compared and passed"),('Local routine contracts',str(local.get('label','BLOCKED')),local.get('detail',''))]
 cards_html=''.join('<div class="card"><h2>'+e(a)+'</h2><strong>'+e(b)+'</strong><p>'+e(c)+'</p></div>'for a,b,c in cards)
 tr=[]
 for r in rows:
  status=r['status'];cls='pass'if status=='PASS'else 'fail'if status=='FAIL'else 'pending'
  tr.append('<tr data-status="'+e(status)+'"><td>'+e(r['area'])+'</td><td><b>'+e(r['title'])+'</b><br><small>'+e(r['id'])+'</small></td><td class="'+cls+'">'+e(status)+'</td><td>'+e(r['original_fidelity'])+'</td><td>'+e(r['reason'])+'</td></tr>')
 areas=[]
 for area in dict.fromkeys(r['area']for r in rows):
  s=summarize([r for r in rows if r['area']==area]);areas.append('<tr><td>'+e(area)+'</td><td>'+str(s['passed'])+'/'+str(s['total'])+'</td><td>'+str(s['percent'])+'%</td></tr>')
 identity=report['demo_identity'];demos='Demo '+identity['status']+'. '+identity.get('reason','')
 change=report.get('checklist_change','')
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Rolo Level 1 progress</title><style>body{font:17px system-ui;background:#111820;color:#edf4fa;margin:24px auto;padding:0 18px;max-width:1450px}h1{margin-bottom:5px}h2{font-size:19px}.cards{display:flex;gap:14px;flex-wrap:wrap}.card{flex:1;min-width:230px;padding:18px;background:#1d2a35;border-radius:10px}.card strong{font-size:34px;color:#77db99}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{border:1px solid #465765;padding:10px;text-align:left;vertical-align:top}.pass{color:#77db99}.fail{color:#ff8a8a}.pending{color:#f3c77a}small{color:#b8c7d4}a{color:#96c9ff}button{font:inherit;background:#2d4253;color:white;padding:8px;border:1px solid #6c8091;border-radius:5px}p{line-height:1.5}details{margin:20px 0}.notice{border-left:4px solid #efbf68;padding:10px 15px;background:#202c36}</style><h1>Rolo: Level 1 progress</h1>'''
 page+='<p>Generated '+e(report['time_utc'])+' | Offline: 0 AI calls, 0 network calls.</p><div class="cards">'+cards_html+'</div>'
 page+='<p class="notice">This is checklist '+e(report['checklist_version'])+', not an estimate of whole-game completion. Each of the '+str(len(rows))+' requirements counts once. Missing, partial, blocked and untested items score zero. Passing shared native code does not prove that every SDL screen or original timing matches. Original-reference scenarios are not yet connected, so their 0% means unverified, not 0% visually correct. Pending statuses are reviewed gaps, not failed executable tests.</p>'
 page+='<p>'+e(change)+'</p><p>'+e(demos)+'</p><p><a href="level1-repair-list.md">Open repair list</a> | <a href="level1-acceptance-latest.json">Detailed results</a> | <a href="../stage9/level1-completion-check.html">Previous completion dashboard</a> | <a href="all-level-objects.html">Object audit across all 70 levels</a></p>'
 page+='<h2>By area</h2><table><tr><th>Area</th><th>Passed / required</th><th>Checklist %</th></tr>'+''.join(areas)+'</table><h2>Every requirement</h2><button onclick="document.querySelectorAll(\'[data-status=PASS]\').forEach(r=>r.hidden=!r.hidden)">Show / hide passed items</button><table><tr><th>Area</th><th>Requirement</th><th>Integration</th><th>Original reference</th><th>Evidence or next action</th></tr>'+''.join(tr)+'</table><p>Run Check Game Progress.cmd again after a change. Unchanged passes and failures are reused; only changed reviewed native checks run. This checker does not modify the game, save, ROM or routine greens.</p></html>'
 diagnostics=''.join('<tr><td>'+e(n.get('name','native check'))+'</td><td>'+e(n.get('status','BLOCKED'))+'</td><td>'+e(n.get('reason',n.get('scope','Reviewed native regression; not original fidelity.')))+'</td></tr>'for n in report['native_checks'])
 page=page.replace('</html>','<details><summary>Native check diagnostics</summary><table><tr><th>Check</th><th>Result</th><th>Scope / issue</th></tr>'+diagnostics+'</table></details></html>')
 (D/'level1-progress.html').write_text(page,encoding='utf-8')
 unresolved=[r for r in rows if r['status']!='PASS'];priority={'FAIL':0,'BLOCKED':1,'STALE':2,'NOT CONNECTED':3,'MISSING':4,'PARTIAL':5,'NOT TESTED':6}
 unresolved.sort(key=lambda r:(priority.get(r['status'],9),r['area'],r['id']))
 repair=['# Level 1 repair list','',f"Checklist {report['checklist_version']}: {summary['passed']}/{summary['total']} passed ({summary['percent']}%).",'','Each requirement is counted once. The original-reference comparison layer is still untested.','']
 for n,r in enumerate(unresolved,1):repair +=[f"## {n}. {r['title']} [{r['status']}]",'',f"ID: `{r['id']}` | Area: {r['area']}",'',r['reason'],'',r['repair'],'']
 for n in report['native_checks']:
  if n.get('status')in ('FAIL','BLOCKED'):
   repair+=['## Native check needs attention: '+n.get('name','unknown'),'','Status: '+n['status']+'. Inspect local/gameplay-checks build/run logs before changing code or expected results.','']
 if not unresolved:repair+=['All tracked integration items passed. Original-reference acceptance and scope completeness still need review.','']
 repair+=['## Original-reference work','',f"{fidelity['total']-fidelity['passed']} requirements have no passing original-reference comparison. Add reviewed capture/trace comparison scenarios; native regression passes cannot substitute for them.",'']
 (D/'level1-repair-list.md').write_text('\n'.join(repair),encoding='utf-8')
 (D/'level1-acceptance-latest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-changed',action='store_true');parser.add_argument('--open',action='store_true');args=parser.parse_args(argv)
 manifest_path=D/'level1-requirements.json';m=load(manifest_path);requirements=validate(m)
 previous_path=D/'level1-acceptance-latest.json'
 try:previous=load(previous_path)if previous_path.exists()else{}
 except (OSError,ValueError):previous={}
 review=[name for name,wanted in m['reviewed_native_inputs'].items()if not (P/name).is_file()or sha(P/name)!=wanted]
 rom=P/'local/rolo.md';rom_ok=rom.is_file()and sha(rom)==ROM_SHA
 problems=[];checks={}
 if rom_ok and not review:
  from check_level1_completion import run_native
  try:checks={x['name']:x for x in run_native(args.run_changed)}
  except Exception as error:problems.append('Native checker could not complete: '+str(error))
 else:problems.append('Pinned ROM missing or different.'if not rom_ok else 'Native recipe/source review required.')
 if problems:checks={name:dict(status='BLOCKED',reason='; '.join(problems))for name in ('level1_enemy_slice_tests','level1_objects_tests','level1_transport_world_tests')}
 rows=[evaluate(r,checks,review)for r in requirements]
 try:
  from offline_verifier import inspect_inventory_reports
  freshness=inspect_inventory_reports();inv=load(P/'docs/stage9/inventory.json');verified=sum(r.get('verification_status')=='verified'for r in inv['routines']);current=sum(r['status']=='current'for r in freshness)
  match=re.search(r'for report_name in (\(.*?\)):',(P/'tools/inventory_rom.py').read_text(encoding='utf-8'),re.S)
  expected=ast.literal_eval(match.group(1));missing=[n for n in expected if not (P/'docs/stage9'/n).is_file()]
  trusted=bool(freshness)and current==len(freshness)and not missing and rom_ok
  local=dict(label=f"{verified}/{len(inv['routines'])}"if trusted else 'STALE / BLOCKED',detail=f'{current}/{len(expected)} certificates current; includes 2 native platform substitutions.',current_certificates=current,total_certificates=len(expected),missing_certificates=missing,scope='Declared local domains only; not gameplay completion.')
 except Exception as error:local=dict(label='BLOCKED',detail=str(error))
 demo=P/'bin/Rolo.exe';build=P/'BUILD-ALL-LEVELS-2026-10-16.json';identity=dict(status='NOT CHECKED',reason='No recorded build identity.')
 if demo.exists()and build.exists():
  record=load(build);matches=sha(demo)==record.get('sha256');pins=record.get('source_sha256',{});changed=[n for n,v in pins.items()if not (P/n).exists()or sha(P/n)!=v]
  identity=dict(status='RECORDED BUILD MATCHES'if matches and not changed else 'CHANGED / UNVERIFIED',reason=f'{len(pins)-len(changed)}/{len(pins)} recorded build source pins current. Identity only; native scenario checks do not drive the SDL executable.',sha256=sha(demo),changed_recorded_sources=changed)
 old_ids=[r['id']for r in previous.get('requirements',[])];ids=[r['id']for r in rows];change='Initial checklist baseline.'if not previous else 'Checklist unchanged; percentages remain comparable.'
 if previous and(old_ids!=ids or previous.get('checklist_version')!=m['checklist_version'] or previous.get('checklist_sha256')!=sha(manifest_path)):change=f'Checklist changed: {len(old_ids)} to {len(ids)} requirements. Percentages are not directly comparable; review added/removed requirements.'
 old_by_id={r['id']:r.get('status')for r in previous.get('requirements',[])}
 report=dict(schema_version=1,time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checklist_version=m['checklist_version'],checklist_sha256=sha(manifest_path),checklist_change=change,ai_calls=0,network_calls=0,rom_valid=rom_ok,scope=m['scope'],integration=summarize(rows),fidelity=summarize(rows,'original_fidelity'),local_contracts=local,demo_identity=identity,native_checks=list(checks.values()),requirements=rows,status_changes=[dict(id=r['id'],before=old_by_id.get(r['id'],'NEW'),after=r['status'])for r in rows if old_by_id.get(r['id'])!=r['status']],errors=problems)
 report['exit_code']=exit_status(report)
 write_reports(report)
 print(f"Level 1 integration checklist: {report['integration']['passed']}/{len(rows)} ({report['integration']['percent']}%).")
 print(f"Original-reference checks: {report['fidelity']['passed']}/{len(rows)}. Untested does not mean incorrect.")
 print('Report: '+str(D/'level1-progress.html'));print('Repair list: '+str(D/'level1-repair-list.md'))
 if args.open:os.startfile(str(D/'level1-progress.html'))
 return report['exit_code']
if __name__=='__main__':
 try:sys.exit(main())
 except (OSError,ValueError,KeyError)as error:print('Checker could not complete: '+str(error),file=sys.stderr);sys.exit(2)
