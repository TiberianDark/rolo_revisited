"""Local-only front end for reviewed verification batches. No AI or network calls.

Default: report source/recipe freshness only. --run-changed executes existing
reviewed build/test recipes for stale groups; unchanged groups are never rerun.
New routine translations and new proof recipes still require review.
"""
import argparse
import ast
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[1]
WORKSPACE=PROJECT.parents[1]

def inspect(groups):
    cache={}
    def digest(path):
        path=path.resolve()
        if path not in cache:
            cache[path]=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        return cache[path]
    result=[]
    for group in groups:
        reasons=[]
        blocked=[]
        report_path=PROJECT/group['report']
        if not report_path.is_file():
            reasons.append('missing verification report')
        else:
            try:
                report=json.loads(report_path.read_text(encoding='utf-8'))
                if not report.get('records'):reasons.append('missing contract records')
                for name,wanted in report.get('source_sha256',{}).items():
                    if digest(PROJECT/name)!=wanted:reasons.append('changed source/dependency: '+name)
            except (ValueError,KeyError) as error:
                blocked.append('unreadable verification report: '+str(error))
        if digest(PROJECT/group['registrar'])!=group['registrar_sha256']:
            blocked.append('verification registrar changed; recipe review required')
        for name,wanted in group['script_sha256'].items():
            if digest(WORKSPACE/name)!=wanted:blocked.append('build script changed; recipe review required: '+name)
        result.append(dict(name=group['name'],status='blocked' if blocked else 'changed' if reasons else 'current',reasons=reasons,blocked=blocked))
    return result

def inspect_inventory_reports():
    # Include older certificates that predate the batch manifest. Never hide
    # them behind a claim that all registered groups are current.
    source=(PROJECT/'tools/inventory_rom.py').read_text(encoding='utf-8')
    match=re.search(r'for report_name in (\(.*?\)):',source,re.S)
    names=ast.literal_eval(match.group(1))
    result=[]
    for name in names:
        path=PROJECT/'docs/stage9'/name
        if not path.exists():continue
        try:
            data=json.loads(path.read_text(encoding='utf-8-sig'))
            stale=[]
            for item,wanted in data.get('source_sha256',{}).items():
                file=PROJECT/item
                if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=wanted:stale.append(item)
            result.append(dict(report=name,status='changed' if stale else 'current',reasons=stale))
        except (ValueError,KeyError) as error:result.append(dict(report=name,status='blocked',reasons=[str(error)]))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',action='store_true',help='Only inspect hashes; do not execute native tests.')
    parser.add_argument('--run-changed',action='store_true',help='Run changed batches with unchanged reviewed recipes.')
    parser.add_argument('--batch',action='append',default=[],help='Restrict to named reviewed groups; repeat as needed.')
    args=parser.parse_args()
    if args.report and args.run_changed:parser.error('Choose either report or run-changed.')
    manifest=json.loads((PROJECT/'tools/verification-batches.json').read_text(encoding='utf-8'))
    groups=manifest['groups']
    if args.batch:
        unknown=set(args.batch)-{g['name'] for g in groups}
        if unknown:parser.error('Unknown batch: '+', '.join(sorted(unknown)))
        groups=[g for g in groups if g['name'] in args.batch]
    before=inspect(groups)
    inventory_before=inspect_inventory_reports()
    changed=[item['name'] for item in before if item['status']=='changed']
    blocked=[item['name'] for item in before if item['status']=='blocked']
    print('Rolo offline verifier - local files, C++ compiler and reviewed tests only.',flush=True)
    print(f"{sum(x['status']=='current' for x in before)} unchanged batches skipped; {len(changed)} changed; {len(blocked)} need recipe review.",flush=True)
    print(f"Inventory certificates: {sum(x['status']=='current' for x in inventory_before)}/{len(inventory_before)} source pins current.",flush=True)
    now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
    folder=WORKSPACE/'work/offline-verification';folder.mkdir(parents=True,exist_ok=True)
    log=folder/f'{now}.log'
    code=0
    if args.run_changed and changed:
        command=[sys.executable,str(PROJECT/'tools/run_verification_batches.py')]
        for name in changed:command+=['--batch',name]
        print('Running only changed reviewed batches. Details are written to '+str(log),flush=True)
        with log.open('w',encoding='utf-8') as output:
            code=subprocess.run(command,cwd=WORKSPACE,stdout=output,stderr=subprocess.STDOUT).returncode
        if code:
            print('A focused check failed. Results were not forced green. See the log; no automatic retries.',flush=True)
        else:print('Changed batches passed; the existing runner refreshed the inventory and graphic.',flush=True)
    else:
        log.write_text('Report only; no native tests executed.\n'+json.dumps(before,indent=2)+'\n',encoding='utf-8')
        if not args.run_changed:print('Report only: nothing compiled or rerun.',flush=True)
    after=inspect(groups)
    inventory_after=inspect_inventory_reports()
    remaining=[item['report'] for item in inventory_after if item['status']!='current']
    if remaining:print(f'{len(remaining)} inventory certificates still need attention; they were not forced current.',flush=True)
    if args.run_changed and not code and (remaining or blocked):code=2
    report=dict(time_utc=now,mode='run-changed' if args.run_changed else 'report',ai_calls=0,network_calls=0,exit_code=code,requested_batches=args.batch,selected_changed=changed,recipe_review_required=blocked,remaining_stale_certificates=remaining,before=before,after=after,inventory_before=inventory_before,inventory_after=inventory_after,log=str(log),scope='Freshness and reviewed local regression checks, not automatic decompilation, new proof admission or complete game fidelity.')
    target=PROJECT/'docs/stage9/offline-verification-latest.json'
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Summary: '+str(target),flush=True)
    if blocked:print('Unreviewed recipe changes were left untouched: '+', '.join(blocked),flush=True)
    return code

if __name__=='__main__':raise SystemExit(main())
