"""Local Level 1 completion dashboard. No AI/network/ROM execution.
Passed local contracts never imply complete original-game fidelity.
"""
import argparse,datetime,hashlib,html,json,re,shutil,subprocess,sys
from pathlib import Path
from offline_verifier import inspect
from audit_level1_macros import audit
P=Path(__file__).resolve().parents[1]
NATIVE=("level1_enemy_slice_tests","level1_objects_tests","level1_transport_world_tests")
AREAS={
 "Movement and collision":["collision-entries","collision-followups","terrain-response","direct-player-contact"],
 "Enemies, damage and pickups":["actor-contact-family","player-contact-resolution","world-key-binding","world-piece-binding","world-container-binding"],
 "Companions and menu":["companion-follow","companion-modes","companion-waiting","companion-entry-contracts"],
 "Transport and checkpoints":["transporter-alignment"],
 "Level completion and map return":["world-exit-binding","world-jigsaw","world-route","campaign-node-completion"],
}
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def dependencies(test):
 pending=[P/"tests"/(test+".cpp")];seen=set()
 while pending:
  f=pending.pop()
  if f in seen:continue
  seen.add(f)
  for child in re.findall(r'#include "(core/[^"\n]+)"',f.read_text(encoding="utf-8")):pending.append(P/"src"/child)
 seen.add(P/"tools/run_level1_gameplay_check.ps1")
 return {str(f.relative_to(P)):sha(f)for f in sorted(seen)}
def run_native(run):
 folder=P/"docs/stage9/level1-gameplay-checks";folder.mkdir(exist_ok=True)
 results=[]
 for name in NATIVE:
  pins=dependencies(name);record=folder/(name+".json");previous=json.loads(record.read_text())if record.exists()else{}
  if previous.get("input_sha256")==pins and previous.get("status") in ("PASS","FAIL","BLOCKED"):
   results.append(dict(previous,reused=True));print(name+": unchanged "+previous["status"]+" reused");continue
  if not run:results.append(dict(name=name,status="NOT TESTED",reason="Missing/stale native evidence; run --run-changed"));continue
  shell=shutil.which("pwsh")or shutil.which("powershell")
  if not shell:results.append(dict(name=name,status="BLOCKED",reason="PowerShell not found"));continue
  proc=subprocess.run([shell,"-NoProfile","-File",str(P/"tools/run_level1_gameplay_check.ps1"),"-Check",name],capture_output=True,text=True)
  log=(proc.stdout+proc.stderr)[-5000:]
  status="PASS"if proc.returncode==0 else "BLOCKED"if any(t in log.lower()for t in ("application control","failed to run","not found"))else "FAIL"
  result=dict(name=name,status=status,input_sha256=pins,time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),output=log,reused=False,scope="Reviewed native regression assertions only; no full playthrough/original reference comparison")
  record.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");results.append(result);print(name+": "+status)
 return results

def local_status(items):
 if not items:return "NOT TESTED"
 if any(r["status"]=="blocked"for r in items):return "BLOCKED"
 if any(r["status"]!="current"for r in items):return "STALE"
 return "PASS (local contracts only)"
def write_page(report):
 e=lambda s:html.escape(str(s));rows=[]
 for r in report["areas"]:rows.append("<tr><td>"+e(r["area"])+"</td><td>"+e(r["local_result"])+"</td><td>"+e(r["original_fidelity"])+"</td><td>"+e(r["remaining"])+"</td></tr>")
 for r in report["native_checks"]:rows.append("<tr><td>"+e(r["name"])+"</td><td>"+e(r["status"])+(" (cached)"if r.get("reused")else "")+"</td><td>NOT TESTED</td><td>"+e(r.get("reason",r.get("scope","")))+"</td></tr>")
 (P/"docs/stage9/level1-completion-check.html").write_text("<!doctype html><meta charset=utf-8><title>Level 1 completion checks</title><style>body{font:17px system-ui;background:#101820;color:#eef3f7;margin:30px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #526274;padding:10px;text-align:left}h1{color:#ffcd73}li{margin:8px}</style><h1>Level 1: "+e(report["overall"])+"</h1><p>Local offline checker. No AI or network calls. Cached passes are reused; changed reviewed checks run once. Original-reference comparison is separate from regression passes.</p><table><tr><th>Area/check</th><th>Local evidence</th><th>Original fidelity</th><th>Remaining work</th></tr>"+"".join(rows)+"</table><h2>Known gaps</h2><ul>"+"".join("<li>"+e(v)+"</li>"for v in report["known_gaps"])+"</ul><p>See level1-completion-check-latest.json for source-pinned details. No percentages or routine greens are changed.</p>",encoding="utf-8")
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--run-changed",action="store_true");parser.add_argument("--self-test",action="store_true");a=parser.parse_args()
 if a.self_test:
  assert local_status([])=="NOT TESTED";assert local_status([dict(status="current")]).startswith("PASS");assert local_status([dict(status="changed")])=="STALE";assert local_status([dict(status="blocked"),dict(status="current")])=="BLOCKED";print("Four result classification fixtures passed");return 0
 manifest=json.loads((P/"tools/verification-batches.json").read_text());selected=set(n for names in AREAS.values()for n in names);groups=[g for g in manifest["groups"]if g["name"]in selected]
 if a.run_changed:
  # Existing runner refuses changed/unreviewed recipes and skips current proofs.
  command=[sys.executable,str(P/"tools/offline_verifier.py"),"--run-changed"]
  for g in groups:command.extend(["--batch",g["name"]])
  subprocess.run(command,cwd=P.parents[1],check=False)
 freshness=inspect(groups);byname={r["name"]:r for r in freshness};areas=[]
 for area,names in AREAS.items():
  missing=[n for n in names if n not in byname];items=[byname[n]for n in names if n in byname]
  areas.append(dict(area=area,local_result="NOT TESTED: missing recipes "+str(missing)if missing else local_status(items),groups=items,original_fidelity="NOT TESTED",remaining="Full original-reference and live-gameplay coverage is not established by these local helpers."))
 macro=audit(P,run_native=a.run_changed);native=run_native(a.run_changed)
 areas.append(dict(area="Macro artwork and loading",local_result="FAIL"if macro["failures"]else "PASS (structure; native loading separately reported)",original_fidelity="NOT TESTED",remaining="Collision, original image and dynamic behaviour acceptance remain separate."))
 gaps=["Actual sound playback remains unimplemented; sound interface contracts do not certify audio.","Original death/restart fade and game-over artwork/timing remain pending; current game-over display is temporary.","Class10 parameter4 has an original no-op handler; original trigger-list bookkeeping is not connected in the demo.","Complete verified-helper-to-gameplay binding and original-reference playthrough acceptance are still required."]
 areas.extend([dict(area="Sound playback",local_result="NOT IMPLEMENTED",original_fidelity="NOT TESTED",remaining=gaps[0]),dict(area="Original transitions and game-over",local_result="PARTIAL",original_fidelity="NOT TESTED",remaining=gaps[1]),dict(area="Trigger bookkeeping",local_result="NOT CONNECTED",original_fidelity="NOT TESTED",remaining=gaps[2])])
 for result in native:
  if result["status"]=="FAIL":gaps.append("Failed native regression: "+result["name"]+". Inspect local/gameplay-checks/"+result["name"]+"-run.log before changing code or expectations.")
 for area in areas:
  if area["area"]=="Companions and menu" and any(r["name"]=="level1_objects_tests" and r["status"]=="FAIL" for r in native):
   area["local_result"]="FAIL (native companion-selection assertion; local helper certificates separately current)"
 build=P/"BUILD-LIFE-CYCLE-2026-10-16.json";recorded={}
 if build.exists():
  recorded=json.loads(build.read_text());recorded["installed_binary_matches_recorded_build"]=(P/recorded["exe"]).exists()and sha(P/recorded["exe"])==recorded["sha256"]
  recorded["scope"]="Recorded functional death/restart smoke evidence, not a newly source-pinned complete original transition proof"
 report=dict(overall="INCOMPLETE",time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ai_calls=0,network_calls=0,areas=areas,native_checks=native,macro_report="level1-macro-audit-latest.json",known_gaps=gaps,recorded_life_cycle_build=recorded)
 (P/"docs/stage9/level1-completion-check-latest.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8");write_page(report)
 print("Level 1 completion: INCOMPLETE. Known gaps and untested original-reference behaviour remain explicit.");print(P/"docs/stage9/level1-completion-check.html")
 return 1 if any(r["status"]=="FAIL"for r in native)or macro["failures"]else 2 if any(r["status"]=="BLOCKED"for r in native)else 0
if __name__=="__main__":sys.exit(main())
