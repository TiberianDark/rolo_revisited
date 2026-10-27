"""Run selected changed verification groups; untouched source-pinned proofs skip.
Default/list mode reads hashes only. It never compiles or reruns native tests.
"""
import argparse,hashlib,json,subprocess,sys,shutil
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[1]
WORKSPACE=PROJECT.parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--batch',action='append',default=[],help='Manifest group name; repeat for a related group.')
 parser.add_argument('--list',action='store_true',help='List current/stale reports without executing tests.')
 parser.add_argument('--force',action='store_true',help='Explicitly rerun selected fresh groups; otherwise current proofs skip.')
 args=parser.parse_args();manifest=json.loads((PROJECT/'tools/verification-batches.json').read_text(encoding='utf-8'));groups={g['name']:g for g in manifest['groups']};unknown=set(args.batch)-groups.keys()
 if unknown:parser.error('Unknown batches: '+', '.join(sorted(unknown)))
 if args.force and not args.batch:parser.error('--force requires explicitly selected --batch groups')
 cache={}
 def digest(path):
  path=path.resolve()
  if path not in cache:cache[path]=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
  return cache[path]
 def status(group):
  reasons=[];path=PROJECT/group['report']
  if not path.is_file():return ['missing report']
  report=json.loads(path.read_text(encoding='utf-8'))
  if not report.get('records'):reasons.append('missing contract records')
  for name,wanted in report.get('source_sha256',{}).items():
   if digest(PROJECT/name)!=wanted:reasons.append(name)
  if digest(PROJECT/group['registrar'])!=group['registrar_sha256']:reasons.append('registrar changed; update reviewed manifest')
  for name,wanted in group['script_sha256'].items():
   if digest(WORKSPACE/name)!=wanted:reasons.append('build script changed: '+name)
  return reasons
 selected=list(dict.fromkeys(args.batch));planned=selected or list(groups)
 statuses={name:status(groups[name]) for name in planned}
 for name in planned:print(('STALE' if statuses[name] else 'CURRENT')+' '+name+(': '+', '.join(statuses[name]) if statuses[name] else ''),flush=True)
 if args.list or not selected:
  print(f'{sum(not v for v in statuses.values())}/{len(planned)} selected reports current; no native tests executed.');return
 executed=[]
 for name in selected:
  group=groups[name]
  if not statuses[name] and not args.force:print('SKIP '+name+' — unchanged proof.',flush=True);continue
  if any('changed;' in reason or 'build script changed:' in reason for reason in statuses[name]):raise SystemExit('Manifest review required before executing changed verification tooling.')
  for script in group['scripts']:
   shell=shutil.which('pwsh')
   if shell:
    command=[shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(WORKSPACE/script)]
   else:
    # Windows PowerShell5 defaults redirected native JSON to UTF16. Existing
    # verification registrars consume ASCII/UTF8; keep their result files valid.
    quoted=str(WORKSPACE/script).replace("'","''")
    command=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',"$PSDefaultParameterValues['Out-File:Encoding']='ascii'; & '"+quoted+"'; exit $LASTEXITCODE"]
   subprocess.run(command,cwd=WORKSPACE,check=True)
  subprocess.run([sys.executable,str(PROJECT/group['registrar'])],cwd=WORKSPACE,check=True);executed.append(name)
 if executed:
  subprocess.run([sys.executable,str(PROJECT/'tools/inventory_rom.py'),str(PROJECT/'local/rolo.md'),'--project',str(PROJECT)],cwd=WORKSPACE,check=True)
  subprocess.run([sys.executable,str(PROJECT/'tools/update_green_progress.py')],cwd=WORKSPACE,check=True)
 print('Completed selected groups: '+(', '.join(executed) if executed else 'none; current proofs skipped.'))
if __name__=='__main__':main()
